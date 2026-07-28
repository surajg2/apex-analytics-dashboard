"""
Seed Data & Database Initialization Script.
Generates synthetic data, populates SQLite database, runs ETL pipeline,
computes RFM metrics, exports Power BI datasets, and trains ML models.
"""

import os
import sys
import pickle

# Force UTF-8 output encoding for Windows command line compatibility
sys.stdout.reconfigure(encoding='utf-8')

from utils import (
    EcommerceDataGenerator,
    DatabaseManager,
    ETLPipeline,
    RFMAnalytics,
    SalesForecaster,
    PowerBIExporter
)

def main():
    print("==========================================================")
    print("[START] Starting End-to-End E-Commerce Data Pipeline...")
    print("==========================================================")

    # 1. Generate Synthetic Relational Data
    generator = EcommerceDataGenerator(seed=42)
    raw_data = generator.generate_all(
        num_customers=3500,
        num_products=150,
        num_sellers=40,
        num_orders=22000,
        start_date="2023-01-01",
        end_date="2025-12-31"
    )

    # 2. Populate SQLite Database
    db = DatabaseManager(db_path="data/ecommerce.db")
    db.populate_database(raw_data)
    print("[SUCCESS] Relational tables & SQL views populated in SQLite database.")

    # 3. Run ETL Data Cleaning & Feature Engineering
    etl = ETLPipeline()
    cleaned_data = etl.run_pipeline(raw_data)

    # Save cleaned master fact table to CSV for instant Streamlit caching
    os.makedirs("data/processed", exist_ok=True)
    cleaned_data["master_fact_table"].to_csv("data/processed/master_fact_table.csv", index=False)
    cleaned_data["customers"].to_csv("data/processed/cleaned_customers.csv", index=False)
    cleaned_data["products"].to_csv("data/processed/cleaned_products.csv", index=False)

    # 4. Compute RFM Analytics & Customer Segments
    rfm_engine = RFMAnalytics()
    rfm_df = rfm_engine.compute_rfm(cleaned_data["master_fact_table"])
    rfm_df.to_csv("data/processed/rfm_customer_segments.csv", index=False)
    print("[SUCCESS] RFM Customer Segmentation completed.")

    # 5. Export Star Schema for Power BI & Tableau
    exporter = PowerBIExporter(export_dir="data/powerbi_exports")
    exporter.export_star_schema(cleaned_data, rfm_df=rfm_df)

    # 6. Train & Serialize ML Sales Forecasting Model
    print("[INFO] Training ML Sales & Revenue Forecasting Model...")
    forecaster = SalesForecaster(model_type="gradient_boosting")
    daily_df = forecaster.prepare_daily_series(cleaned_data["master_fact_table"])
    eval_results = forecaster.train_and_eval(daily_df, test_days=30)
    
    os.makedirs("models", exist_ok=True)
    with open("models/forecaster_model.pkl", "wb") as f:
        pickle.dump(forecaster, f)

    daily_df.to_csv("data/processed/daily_sales_series.csv", index=False)

    print("==========================================================")
    print("[SUCCESS] Pipeline Execution Complete!")
    print(f"[METRICS] Model Performance -> RMSE: ${eval_results['metrics']['RMSE']}, MAE: ${eval_results['metrics']['MAE']}, R2: {eval_results['metrics']['R2_Score']}")
    print("==========================================================")

if __name__ == "__main__":
    main()
