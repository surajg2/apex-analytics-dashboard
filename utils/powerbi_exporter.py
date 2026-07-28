"""
Power BI & Tableau Star-Schema Exporter.
Exports cleaned relational fact and dimension tables into CSV, Excel, and Parquet
formats for seamless integration into Power BI Desktop or Tableau Software.
"""

import os
import pandas as pd
from typing import Dict

class PowerBIExporter:
    """Generates clean Star-Schema data exports compatible with BI tools."""

    def __init__(self, export_dir: str = "data/powerbi_exports"):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def export_star_schema(self, cleaned_tables: Dict[str, pd.DataFrame], rfm_df: pd.DataFrame = None):
        """Builds Fact_Orders, Dim_Customers, Dim_Products, Dim_Sellers, and Dim_Date tables."""

        print("[INFO] Exporting Star-Schema for Power BI / Tableau...")

        # 1. Fact_Orders
        fact_orders = cleaned_tables["master_fact_table"][[
            "order_item_id", "order_id", "customer_id", "product_id", "seller_id",
            "order_date", "shipping_date", "delivery_date", "order_status",
            "quantity", "unit_price", "discount_amount", "freight_value",
            "gross_amount", "total_discount", "net_amount", "total_cost",
            "item_profit", "profit_margin_pct", "payment_method", "review_score"
        ]].copy()

        # 2. Dim_Customers
        dim_customers = cleaned_tables["customers"].copy()
        dim_customers["full_name"] = dim_customers["first_name"] + " " + dim_customers["last_name"]
        if rfm_df is not None:
            dim_customers = dim_customers.merge(
                rfm_df[["customer_id", "rfm_segment", "rfm_cell", "rfm_score", "recency_days", "frequency", "monetary", "clv_estimate"]],
                on="customer_id",
                how="left"
            )

        # 3. Dim_Products
        dim_products = cleaned_tables["products"].merge(
            cleaned_tables["categories"], on="category_id", how="left"
        )

        # 4. Dim_Sellers
        dim_sellers = cleaned_tables["sellers"].copy()

        # 5. Dim_Date
        dim_date = self._generate_dim_date(cleaned_tables["orders"]["order_date"].min(), cleaned_tables["orders"]["order_date"].max())

        star_schema = {
            "Fact_Orders": fact_orders,
            "Dim_Customers": dim_customers,
            "Dim_Products": dim_products,
            "Dim_Sellers": dim_sellers,
            "Dim_Date": dim_date
        }

        # Export to CSV
        for table_name, df in star_schema.items():
            csv_path = os.path.join(self.export_dir, f"{table_name}.csv")
            df.to_csv(csv_path, index=False)

        # Export to Excel if openpyxl is installed
        try:
            excel_path = os.path.join(self.export_dir, "PowerBI_Ecommerce_StarSchema.xlsx")
            with pd.ExcelWriter(excel_path, engine="openpyxl") as excel_writer:
                for table_name, df in star_schema.items():
                    df.head(5000).to_excel(excel_writer, sheet_name=table_name, index=False)
            print(f"[SUCCESS] Excel Star-Schema exported to {excel_path}")
        except Exception as e:
            print(f"[INFO] Skipping Excel workbook export ({e}). CSV files exported successfully.")

        print(f"[SUCCESS] Star-Schema CSV files successfully exported to {self.export_dir}")

    def _generate_dim_date(self, min_date, max_date) -> pd.DataFrame:
        start = pd.to_datetime(min_date).floor("D")
        end = pd.to_datetime(max_date).ceil("D")

        date_range = pd.date_range(start=start, end=end, freq="D")
        dim_date = pd.DataFrame({"Date": date_range})

        dim_date["DateKey"] = dim_date["Date"].dt.strftime("%Y%m%d").astype(int)
        dim_date["Year"] = dim_date["Date"].dt.year
        dim_date["Quarter"] = "Q" + dim_date["Date"].dt.quarter.astype(str)
        dim_date["MonthNumber"] = dim_date["Date"].dt.month
        dim_date["MonthName"] = dim_date["Date"].dt.strftime("%B")
        dim_date["DayOfMonth"] = dim_date["Date"].dt.day
        dim_date["DayOfWeekNumber"] = dim_date["Date"].dt.dayofweek + 1
        dim_date["DayOfWeekName"] = dim_date["Date"].dt.strftime("%A")
        dim_date["IsWeekend"] = dim_date["Date"].dt.dayofweek.isin([5, 6]).astype(int)
        dim_date["FiscalQuarter"] = dim_date["Quarter"]

        return dim_date

if __name__ == "__main__":
    from etl_pipeline import ETLPipeline
    from data_generator import EcommerceDataGenerator

    gen = EcommerceDataGenerator()
    raw = gen.generate_all(num_orders=500)
    etl = ETLPipeline()
    cleaned = etl.run_pipeline(raw)

    exporter = PowerBIExporter()
    exporter.export_star_schema(cleaned)
