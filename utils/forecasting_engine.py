"""
Machine Learning Sales & Revenue Forecasting Engine.
Trains Time-Series Supervised Models (RandomForest, GradientBoosting, Ridge)
to predict daily revenue, demand trends, and future 30-90 day performance with metrics.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

class SalesForecaster:
    """Supervised Time-Series Forecasting Model for E-Commerce Revenue and Order Volume."""

    def __init__(self, model_type: str = "gradient_boosting"):
        self.model_type = model_type.lower()
        if self.model_type == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.model_type == "ridge":
            self.model = Ridge(alpha=1.0)
        else:
            self.model = GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, random_state=42)

        self.feature_cols = []
        self.is_trained = False

    def prepare_daily_series(self, df_master: pd.DataFrame) -> pd.DataFrame:
        """Aggregates daily sales, order count, item volume, and creates time-series lag features."""
        df_valid = df_master[df_master["order_status"] != "Cancelled"].copy()
        df_valid["order_date"] = pd.to_datetime(df_valid["order_date"], format="mixed", errors="coerce")
        df_valid["date"] = df_valid["order_date"].dt.date

        daily = df_valid.groupby("date").agg({
            "net_amount": "sum",
            "order_id": "nunique",
            "quantity": "sum"
        }).reset_index()

        daily.columns = ["date", "revenue", "order_count", "item_quantity"]
        daily["date"] = pd.to_datetime(daily["date"])

        # Fill missing calendar dates with 0
        full_idx = pd.date_range(start=daily["date"].min(), end=daily["date"].max(), freq="D")
        daily = daily.set_index("date").reindex(full_idx).fillna(0).reset_index()
        daily.rename(columns={"index": "date"}, inplace=True)

        # Feature Engineering: Calendar features
        daily["year"] = daily["date"].dt.year
        daily["month"] = daily["date"].dt.month
        daily["day"] = daily["date"].dt.day
        daily["dayofweek"] = daily["date"].dt.dayofweek
        daily["dayofyear"] = daily["date"].dt.dayofyear
        daily["is_weekend"] = daily["dayofweek"].isin([5, 6]).astype(int)
        daily["is_holiday_month"] = daily["month"].isin([11, 12]).astype(int)

        # Feature Engineering: Lags & Rolling Moving Averages
        for lag in [1, 7, 14, 30]:
            daily[f"rev_lag_{lag}"] = daily["revenue"].shift(lag)
            daily[f"orders_lag_{lag}"] = daily["order_count"].shift(lag)

        for window in [7, 14, 30]:
            daily[f"rev_roll_mean_{window}"] = daily["revenue"].shift(1).rolling(window=window).mean()
            daily[f"rev_roll_std_{window}"] = daily["revenue"].shift(1).rolling(window=window).std()

        daily = daily.dropna().reset_index(drop=True)
        return daily

    def train_and_eval(self, daily_df: pd.DataFrame, test_days: int = 30) -> Dict[str, Any]:
        """Trains ML forecaster on historical daily series and evaluates on out-of-sample test split."""

        exclude = ["date", "revenue", "order_count", "item_quantity"]
        self.feature_cols = [c for c in daily_df.columns if c not in exclude]

        train_df = daily_df.iloc[:-test_days].copy()
        test_df = daily_df.iloc[-test_days:].copy()

        X_train = train_df[self.feature_cols]
        y_train = train_df["revenue"]
        X_test = test_df[self.feature_cols]
        y_test = test_df["revenue"]

        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Test predictions
        y_pred = self.model.predict(X_test)
        y_pred = np.clip(y_pred, a_min=0, a_max=None)

        # Compute Metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # MAPE calculation (avoid division by 0)
        non_zero_mask = y_test > 0
        mape = np.mean(np.abs((y_test[non_zero_mask] - y_pred[non_zero_mask]) / y_test[non_zero_mask])) * 100

        eval_results = {
            "metrics": {
                "RMSE": round(rmse, 2),
                "MAE": round(mae, 2),
                "MAPE_pct": round(mape, 2),
                "R2_Score": round(r2, 4)
            },
            "test_dates": test_df["date"],
            "y_actual": y_test.values,
            "y_predicted": y_pred,
            "feature_importance": self._get_feature_importance()
        }

        return eval_results

    def predict_future(self, daily_df: pd.DataFrame, forecast_horizon_days: int = 60) -> pd.DataFrame:
        """Generates future day-by-day iterative forecasts for N days into the future."""

        if not self.is_trained:
            self.train_and_eval(daily_df, test_days=30)

        history_df = daily_df.copy()
        last_date = history_df["date"].max()

        future_records = []
        for i in range(1, forecast_horizon_days + 1):
            next_date = last_date + pd.Timedelta(days=i)

            # Build single row for future date based on history
            temp_row = {"date": next_date}
            temp_row["year"] = next_date.year
            temp_row["month"] = next_date.month
            temp_row["day"] = next_date.day
            temp_row["dayofweek"] = next_date.dayofweek
            temp_row["dayofyear"] = next_date.dayofyear
            temp_row["is_weekend"] = int(next_date.dayofweek in [5, 6])
            temp_row["is_holiday_month"] = int(next_date.month in [11, 12])

            # Extract lag values from accumulated history_df
            for lag in [1, 7, 14, 30]:
                temp_row[f"rev_lag_{lag}"] = history_df["revenue"].iloc[-lag]
                temp_row[f"orders_lag_{lag}"] = history_df["order_count"].iloc[-lag]

            for window in [7, 14, 30]:
                temp_row[f"rev_roll_mean_{window}"] = history_df["revenue"].iloc[-window:].mean()
                temp_row[f"rev_roll_std_{window}"] = history_df["revenue"].iloc[-window:].std()

            # Predict next day revenue
            x_input = pd.DataFrame([temp_row])[self.feature_cols]
            pred_rev = float(self.model.predict(x_input)[0])
            pred_rev = max(0.0, pred_rev)

            # Estimate confidence bands (+/- 15% std error)
            std_err = pred_rev * 0.12
            lower_bound = max(0.0, pred_rev - std_err)
            upper_bound = pred_rev + std_err

            future_records.append({
                "date": next_date,
                "forecast_revenue": round(pred_rev, 2),
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2)
            })

            # Append to history for next iteration lag step
            new_hist_row = temp_row.copy()
            new_hist_row["revenue"] = pred_rev
            new_hist_row["order_count"] = int(pred_rev / 85.0) # approximate orders
            history_df = pd.concat([history_df, pd.DataFrame([new_hist_row])], ignore_index=True)

        return pd.DataFrame(future_records)

    def _get_feature_importance(self) -> Dict[str, float]:
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            fi_df = pd.DataFrame({"feature": self.feature_cols, "importance": importances})
            fi_df = fi_df.sort_values("importance", ascending=False).head(10)
            return dict(zip(fi_df["feature"], fi_df["importance"].round(4)))
        return {}

if __name__ == "__main__":
    from etl_pipeline import ETLPipeline
    from data_generator import EcommerceDataGenerator

    gen = EcommerceDataGenerator()
    raw = gen.generate_all(num_orders=1500)
    etl = ETLPipeline()
    cleaned = etl.run_pipeline(raw)

    forecaster = SalesForecaster(model_type="gradient_boosting")
    daily = forecaster.prepare_daily_series(cleaned["master_fact_table"])
    eval_res = forecaster.train_and_eval(daily, test_days=30)
    print("Forecasting Metrics:", eval_res["metrics"])

    future_df = forecaster.predict_future(daily, forecast_horizon_days=30)
    print("Future 30-Day Forecast Sample:\n", future_df.head())
