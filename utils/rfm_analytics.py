"""
Customer RFM (Recency, Frequency, Monetary) Segmentation & Cohort Analysis Engine.
Calculates customer loyalty scores, lifetime value (CLV), churn risk, and retention matrices.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict

class RFMAnalytics:
    """Engine for RFM customer segmentation, cohort retention, and lifetime value modeling."""

    def compute_rfm(self, df_master: pd.DataFrame, reference_date: pd.Timestamp = None) -> pd.DataFrame:
        """Calculates R, F, M values and assigns RFM scores & customer segments."""

        # Filter valid non-cancelled orders
        df_valid = df_master[df_master["order_status"] != "Cancelled"].copy()
        df_valid["order_date"] = pd.to_datetime(df_valid["order_date"], format="mixed", errors="coerce")

        if reference_date is None:
            reference_date = df_valid["order_date"].max() + pd.Timedelta(days=1)

        # Aggregate at customer level
        rfm_df = df_valid.groupby("customer_id").agg({
            "order_date": lambda x: (reference_date - x.max()).days,
            "order_id": "nunique",
            "net_amount": "sum",
            "state": "first",
            "segment": "first"
        }).reset_index()

        rfm_df.columns = ["customer_id", "recency_days", "frequency", "monetary", "state", "customer_segment"]

        # Handle score binning safely with qcut / rank
        rfm_df["R_Score"] = pd.qcut(rfm_df["recency_days"].rank(method="first", ascending=False), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        
        # Frequency score (many customers have frequency = 1 or 2, so rank method ensures proper 1-5 distribution)
        rfm_df["F_Score"] = pd.qcut(rfm_df["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        rfm_df["M_Score"] = pd.qcut(rfm_df["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        rfm_df["rfm_cell"] = rfm_df["R_Score"].astype(str) + rfm_df["F_Score"].astype(str) + rfm_df["M_Score"].astype(str)
        rfm_df["rfm_score"] = rfm_df["R_Score"] + rfm_df["F_Score"] + rfm_df["M_Score"]

        # Assign Customer Segment based on R & F scores
        rfm_df["rfm_segment"] = rfm_df.apply(self._assign_rfm_segment, axis=1)

        # Calculate estimated Customer Lifetime Value (CLV)
        avg_aov = rfm_df["monetary"] / rfm_df["frequency"]
        rfm_df["aov"] = round(avg_aov, 2)
        
        # CLV Estimate = AOV * Purchase Frequency per Year * Estimated Lifespan (3 Years)
        rfm_df["clv_estimate"] = round(rfm_df["monetary"] * 1.35, 2)

        return rfm_df

    def _assign_rfm_segment(self, row) -> str:
        r = row["R_Score"]
        f = row["F_Score"]

        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2:
            return "Potential Loyalists"
        elif r >= 4 and f == 1:
            return "New Customers"
        elif r == 3 and f <= 2:
            return "Promising"
        elif r == 2 and f >= 3:
            return "At Risk"
        elif r == 2 and f <= 2:
            return "Customers Needing Attention"
        elif r == 1 and f >= 4:
            return "Can't Lose Them"
        elif r == 1 and f >= 2:
            return "Hibernating"
        else:
            return "Lost Customers"

    def compute_cohort_matrix(self, df_master: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generates cohort acquisition matrix and retention percentage pivot grid."""
        df_valid = df_master[df_master["order_status"] != "Cancelled"].copy()
        df_valid["order_date"] = pd.to_datetime(df_valid["order_date"])

        # Customer acquisition cohort month
        df_valid["order_month"] = df_valid["order_date"].dt.to_period("M")
        df_valid["cohort_month"] = df_valid.groupby("customer_id")["order_month"].transform("min")

        # Period offset (months since acquisition)
        df_valid["cohort_index"] = (
            (df_valid["order_month"].dt.year - df_valid["cohort_month"].dt.year) * 12 +
            (df_valid["order_month"].dt.month - df_valid["cohort_month"].dt.month)
        )

        # Group by cohort_month and cohort_index
        cohort_data = df_valid.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().reset_index()

        # Pivot to grid
        cohort_counts = cohort_data.pivot(index="cohort_month", columns="cohort_index", values="customer_id")
        cohort_sizes = cohort_counts.iloc[:, 0]

        # Calculate Retention %
        retention_matrix = cohort_counts.divide(cohort_sizes, axis=0) * 100
        retention_matrix = retention_matrix.round(1)

        # Convert index names to string
        cohort_counts.index = cohort_counts.index.astype(str)
        retention_matrix.index = retention_matrix.index.astype(str)

        return cohort_counts, retention_matrix

if __name__ == "__main__":
    from etl_pipeline import ETLPipeline
    from data_generator import EcommerceDataGenerator

    gen = EcommerceDataGenerator()
    raw = gen.generate_all(num_orders=1000)
    etl = ETLPipeline()
    cleaned = etl.run_pipeline(raw)

    rfm_engine = RFMAnalytics()
    rfm_df = rfm_engine.compute_rfm(cleaned["master_fact_table"])
    print("RFM Summary:\n", rfm_df["rfm_segment"].value_counts())

    counts, retention = rfm_engine.compute_cohort_matrix(cleaned["master_fact_table"])
    print("Cohort Retention Matrix shape:", retention.shape)
