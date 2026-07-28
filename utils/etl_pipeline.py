"""
ETL Data Cleaning and Feature Engineering Pipeline.
Cleans raw data, handles missing values & outliers, performs type casting,
and creates engineered features for analytical modeling and dashboard reporting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple

class ETLPipeline:
    """Production ETL Pipeline for data transformation and feature engineering."""

    def run_pipeline(self, tables_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Runs full end-to-end ETL cleaning and feature engineering."""
        print("[INFO] Running ETL Data Cleaning & Feature Engineering...")

        cleaned_tables = {}
        for name, df in tables_dict.items():
            cleaned_tables[name] = df.copy()

        # 1. Clean & transform individual tables
        cleaned_tables["customers"] = self._clean_customers(cleaned_tables["customers"])
        cleaned_tables["products"] = self._clean_products(cleaned_tables["products"])
        cleaned_tables["orders"] = self._clean_orders(cleaned_tables["orders"])
        cleaned_tables["order_items"] = self._clean_order_items(cleaned_tables["order_items"], cleaned_tables["products"])
        cleaned_tables["payments"] = self._clean_payments(cleaned_tables["payments"])
        cleaned_tables["reviews"] = self._clean_reviews(cleaned_tables["reviews"])

        # 2. Master analytical dataset (Fact Table join)
        cleaned_tables["master_fact_table"] = self._build_master_fact_table(cleaned_tables)

        print("[SUCCESS] ETL Cleaning & Feature Engineering Complete!")
        return cleaned_tables

    def _clean_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates(subset=["customer_id"])
        df["signup_date"] = pd.to_datetime(df["signup_date"], format="mixed", errors="coerce")
        df["email"] = df["email"].str.lower().str.strip()
        df["state"] = df["state"].str.title()
        return df

    def _clean_products(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates(subset=["product_id"])
        df["price"] = df["price"].apply(lambda x: max(0.99, float(x)))
        df["cost"] = df["cost"].apply(lambda x: max(0.49, float(x)))
        # Engineered feature: Base product profit margin percentage
        df["base_profit_margin_pct"] = round(((df["price"] - df["cost"]) / df["price"]) * 100, 2)
        return df

    def _clean_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates(subset=["order_id"])

        date_cols = ["order_date", "shipping_date", "estimated_delivery", "delivery_date"]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")

        # Feature Engineering on Orders
        df["order_year"] = df["order_date"].dt.year
        df["order_month"] = df["order_date"].dt.month
        df["order_month_name"] = df["order_date"].dt.strftime("%b")
        df["order_dayofweek"] = df["order_date"].dt.day_name()
        df["is_weekend"] = df["order_date"].dt.dayofweek.isin([5, 6]).astype(int)
        df["is_holiday_season"] = df["order_date"].dt.month.isin([11, 12]).astype(int)

        # Shipping & Delivery performance features
        df["shipping_lead_days"] = (df["shipping_date"] - df["order_date"]).dt.total_seconds() / 86400.0
        df["shipping_lead_days"] = df["shipping_lead_days"].apply(lambda x: max(0.0, x) if pd.notnull(x) else np.nan)

        df["actual_delivery_days"] = (df["delivery_date"] - df["shipping_date"]).dt.total_seconds() / 86400.0
        df["delivery_delay_days"] = (df["delivery_date"] - df["estimated_delivery"]).dt.total_seconds() / 86400.0
        df["is_delivery_delayed"] = (df["delivery_delay_days"] > 0).astype(int)

        return df

    def _clean_order_items(self, df_items: pd.DataFrame, df_products: pd.DataFrame) -> pd.DataFrame:
        df_items = df_items.drop_duplicates(subset=["order_item_id"])

        # Merge product cost for exact item profit calculations
        prod_cost_map = dict(zip(df_products["product_id"], df_products["cost"]))
        df_items["unit_cost"] = df_items["product_id"].map(prod_cost_map).fillna(0.0)

        # Outlier handling via winsorization (capping extreme quantities or prices)
        q_high = df_items["quantity"].quantile(0.999)
        df_items["quantity"] = df_items["quantity"].clip(upper=q_high)

        # Engineered monetary metrics
        df_items["gross_amount"] = round(df_items["quantity"] * df_items["unit_price"], 2)
        df_items["total_discount"] = round(df_items["quantity"] * df_items["discount_amount"], 2)
        df_items["net_amount"] = round(df_items["gross_amount"] - df_items["total_discount"], 2)
        df_items["total_cost"] = round(df_items["quantity"] * df_items["unit_cost"], 2)
        df_items["item_profit"] = round(df_items["net_amount"] - df_items["total_cost"], 2)
        df_items["profit_margin_pct"] = np.where(
            df_items["net_amount"] > 0,
            round((df_items["item_profit"] / df_items["net_amount"]) * 100, 2),
            0.0
        )

        return df_items

    def _clean_payments(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates(subset=["payment_id"])
        df["payment_value"] = df["payment_value"].apply(lambda x: max(0.0, float(x)))
        df["installments"] = df["installments"].fillna(1).astype(int)
        return df

    def _clean_reviews(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates(subset=["review_id"])
        df["review_score"] = df["review_score"].clip(lower=1, upper=5).astype(int)
        df["review_title"] = df["review_title"].fillna("No comment title")
        df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
        return df

    def _build_master_fact_table(self, tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Denormalized master fact dataframe joining orders, items, products, customers, and payments."""
        df_ord = tables["orders"]
        df_items = tables["order_items"]
        df_cust = tables["customers"]
        df_prod = tables["products"]
        df_cat = tables["categories"]
        df_pay = tables["payments"]
        df_rev = tables["reviews"]

        # Join Order Items with Products & Categories
        df_master = df_items.merge(df_prod[["product_id", "product_name", "category_id"]], on="product_id", how="left")
        df_master = df_master.merge(df_cat[["category_id", "category_name", "department"]], on="category_id", how="left")

        # Join with Orders
        df_master = df_master.merge(
            df_ord[["order_id", "customer_id", "order_status", "order_date", "shipping_date",
                    "delivery_date", "order_year", "order_month", "order_month_name", "order_dayofweek",
                    "is_weekend", "is_holiday_season", "delivery_delay_days", "is_delivery_delayed"]],
            on="order_id",
            how="left"
        )

        # Join with Customers
        df_master = df_master.merge(
            df_cust[["customer_id", "first_name", "last_name", "email", "city", "state", "signup_date", "segment"]],
            on="customer_id",
            how="left"
        )

        # Join with Payments & Reviews
        df_master = df_master.merge(df_pay[["order_id", "payment_method", "payment_status"]], on="order_id", how="left")
        df_master = df_master.merge(df_rev[["order_id", "review_score"]], on="order_id", how="left")

        # Customer tenure at time of order
        df_master["customer_tenure_days"] = (df_master["order_date"] - df_master["signup_date"]).dt.days
        df_master["customer_tenure_days"] = df_master["customer_tenure_days"].apply(lambda x: max(0, x) if pd.notnull(x) else 0)

        return df_master

if __name__ == "__main__":
    from data_generator import EcommerceDataGenerator
    gen = EcommerceDataGenerator()
    raw = gen.generate_all(num_orders=500)
    etl = ETLPipeline()
    cleaned = etl.run_pipeline(raw)
    print("Master Fact Table Shape:", cleaned["master_fact_table"].shape)
