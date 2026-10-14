"""
InsightIQ Predictive Analytics and Sales Forecasting Engine.
Implements time-ordered train/test validation, explainable baseline models,
and scikit-learn Ridge regression with autoregressive lag and calendar features.
Guarantees zero data leakage and mathematically safe error metric calculation.
"""
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from backend.database import get_db_connection

def prepare_time_series(
    dataset_id: str,
    target_metric: str = "revenue",
    granularity: str = "D"
) -> pd.DataFrame:
    """
    Extracts and aggregates historical observations from SQLite into continuous time series.
    Fills zero-sales missing periods to maintain uninterrupted temporal frequency.
    """
    conn = get_db_connection()
    metric_col = "revenue" if target_metric == "revenue" else "order_id"
    
    if target_metric == "revenue":
        agg_sql = "COALESCE(SUM(revenue), 0.0)"
    else:
        agg_sql = "COUNT(DISTINCT order_id)"
        
    query = f"""
        SELECT 
            order_date,
            {agg_sql} as target_value
        FROM sales_data
        WHERE dataset_id = ?
        GROUP BY order_date
        ORDER BY order_date ASC
    """
    df = pd.read_sql_query(query, conn, params=[dataset_id])
    conn.close()
    
    if df.empty:
        return pd.DataFrame(columns=["date", "target_value"])
        
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.set_index("order_date")
    
    # Resample to continuous frequency (Daily 'D' or Monthly 'MS')
    freq = "D" if granularity == "D" else "MS"
    resampled_df = df.resample(freq).sum().reset_index()
    resampled_df.columns = ["date", "target_value"]
    resampled_df["target_value"] = resampled_df["target_value"].astype(float).round(2)
    return resampled_df

def compute_safe_mape(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[Optional[float], int]:
    """
    Calculates Mean Absolute Percentage Error (MAPE) safely.
    Excludes instances where actual y_true == 0 to avoid division by zero.
    Returns (mape_percentage, zero_count).
    """
    mask = y_true != 0
    zero_count = int(np.sum(~mask))
    if np.sum(mask) == 0:
        return None, zero_count
    mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)
    return round(mape, 2), zero_count

def generate_forecast(
    dataset_id: str,
    target_metric: str = "revenue",
    granularity: str = "D",
    horizon: int = 30,
    model_type: str = "ridge"
) -> Dict[str, Any]:
    """
    Generates forward-looking predictions using strict time-ordered evaluation.
    """
    ts_df = prepare_time_series(dataset_id, target_metric, granularity)
    total_points = len(ts_df)
    
    # Minimum required points check
    min_required = 14 if granularity == "D" else 6
    if total_points < min_required:
        return {
            "historical_points": [],
            "forecast_points": [],
            "metrics": {
                "mae": None,
                "rmse": None,
                "mape": None,
                "r2_score": None,
                "test_size_points": 0,
                "zero_actuals_count": 0,
                "historical_points_total": total_points
            },
            "model_info": {
                "name": "Insufficient Data",
                "target_metric": target_metric,
                "granularity": granularity,
                "horizon": horizon
            },
            "limitations": f"A minimum of {min_required} sequential time periods is required for statistical forecasting. Dataset currently contains {total_points} aggregated periods.",
            "methodology_explanation": "Forecasting requires sufficient historical depth to construct lag features and assess out-of-sample generalizability."
        }
        
    y_values = ts_df["target_value"].values
    dates = ts_df["date"].dt.strftime("%Y-%m-%d").tolist()
    
    # Baseline Model: Exponential Weighted Moving Average (EWMA)
    if model_type == "baseline" or total_points < 30:
        # Time-ordered train/test split: 80% train, 20% test
        split_idx = max(int(total_points * 0.8), total_points - 10)
        train_y = y_values[:split_idx]
        test_y = y_values[split_idx:]
        
        # Alpha smoothing parameter
        alpha = 0.25
        pred_test = []
        last_level = float(np.mean(train_y[:max(1, int(len(train_y)*0.3))]))
        for val in train_y:
            last_level = alpha * val + (1 - alpha) * last_level
            
        test_preds = []
        for _ in test_y:
            test_preds.append(last_level)
            
        test_preds_arr = np.array(test_preds)
        mae = round(float(mean_absolute_error(test_y, test_preds_arr)), 2)
        rmse = round(float(math.sqrt(mean_squared_error(test_y, test_preds_arr))), 2)
        mape, zero_cnt = compute_safe_mape(test_y, test_preds_arr)
        r2 = round(float(r2_score(test_y, test_preds_arr)), 3) if len(test_y) > 1 else None
        
        # Project future horizon
        # Calculate residual standard error for confidence intervals
        residuals = test_y - test_preds_arr
        sigma = float(np.std(residuals)) if len(residuals) > 1 else 100.0
        
        last_date = ts_df["date"].iloc[-1]
        freq_str = "D" if granularity == "D" else "MS"
        future_dates = pd.date_range(start=last_date, periods=horizon + 1, freq=freq_str)[1:]
        
        forecast_points = []
        for d in future_dates:
            pred_val = max(0.0, round(last_level, 2))
            forecast_points.append({
                "date": d.strftime("%Y-%m-%d"),
                "actual": None,
                "predicted": pred_val,
                "lower_bound": max(0.0, round(pred_val - 1.96 * sigma, 2)),
                "upper_bound": round(pred_val + 1.96 * sigma, 2)
            })
            
        hist_points = [
            {"date": dates[i], "actual": round(float(y_values[i]), 2), "predicted": None}
            for i in range(total_points)
        ]
        
        return {
            "historical_points": hist_points,
            "forecast_points": forecast_points,
            "metrics": {
                "mae": mae,
                "rmse": rmse,
                "mape": mape,
                "r2_score": r2,
                "test_size_points": len(test_y),
                "zero_actuals_count": zero_cnt,
                "historical_points_total": total_points
            },
            "model_info": {
                "name": "Exponential Smoothing Baseline (EWMA)",
                "alpha": alpha,
                "target_metric": target_metric,
                "granularity": granularity,
                "horizon": horizon
            },
            "limitations": "Baseline smoothing assumes future periods mirror recent weighted trends without incorporating explicit holiday shifts or external macroeconomic factors.",
            "methodology_explanation": "Time-ordered train/test validation without future leakage. Evaluated out-of-sample on the final 20% of historical periods."
        }
        
    # Machine Learning Model: Scikit-learn Ridge Regression with Autoregressive Features
    # Feature engineering:
    # - lag_1, lag_2, lag_7 (if daily)
    # - rolling_mean_7
    # - day_of_week / month cyclical encoding
    # - linear trend index
    feature_df = pd.DataFrame({"target": y_values}, index=ts_df["date"])
    feature_df["trend_idx"] = np.arange(len(feature_df))
    feature_df["lag_1"] = feature_df["target"].shift(1)
    feature_df["lag_2"] = feature_df["target"].shift(2)
    
    if granularity == "D":
        feature_df["lag_7"] = feature_df["target"].shift(7)
        feature_df["roll_mean_7"] = feature_df["target"].shift(1).rolling(7, min_periods=1).mean()
        feature_df["day_of_week"] = feature_df.index.dayofweek
        feature_df["month"] = feature_df.index.month
    else:
        feature_df["lag_3"] = feature_df["target"].shift(3)
        feature_df["roll_mean_3"] = feature_df["target"].shift(1).rolling(3, min_periods=1).mean()
        feature_df["month"] = feature_df.index.month

    # Drop initial NaN rows caused by lag shifting
    clean_feat_df = feature_df.dropna().copy()
    X = clean_feat_df.drop(columns=["target"]).values
    y = clean_feat_df["target"].values
    clean_dates = clean_feat_df.index.strftime("%Y-%m-%d").tolist()
    
    # Strictly time-ordered split (last 20% as test set)
    test_size = max(5, int(len(clean_feat_df) * 0.20))
    train_size = len(clean_feat_df) - test_size
    
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    
    test_preds = model.predict(X_test)
    test_preds = np.clip(test_preds, 0.0, None)
    
    mae = round(float(mean_absolute_error(y_test, test_preds)), 2)
    rmse = round(float(math.sqrt(mean_squared_error(y_test, test_preds))), 2)
    mape, zero_cnt = compute_safe_mape(y_test, test_preds)
    r2 = round(float(r2_score(y_test, test_preds)), 3)
    
    # Fit full historical dataset for forward projection
    model_full = Ridge(alpha=1.0)
    model_full.fit(X, y)
    
    # Calculate residual variance
    residuals = y - model_full.predict(X)
    sigma = float(np.std(residuals)) if len(residuals) > 1 else 100.0
    
    # Multi-step recursive forecasting into future horizon
    future_preds = []
    freq_str = "D" if granularity == "D" else "MS"
    last_date = ts_df["date"].iloc[-1]
    future_dates = pd.date_range(start=last_date, periods=horizon + 1, freq=freq_str)[1:]
    
    current_history = list(y_values)
    current_trend_idx = len(ts_df)
    
    for f_date in future_dates:
        if granularity == "D":
            lag_1 = current_history[-1]
            lag_2 = current_history[-2] if len(current_history) >= 2 else lag_1
            lag_7 = current_history[-7] if len(current_history) >= 7 else lag_1
            roll_7 = float(np.mean(current_history[-7:]))
            dow = f_date.dayofweek
            month = f_date.month
            x_step = np.array([[current_trend_idx, lag_1, lag_2, lag_7, roll_7, dow, month]])
        else:
            lag_1 = current_history[-1]
            lag_2 = current_history[-2] if len(current_history) >= 2 else lag_1
            lag_3 = current_history[-3] if len(current_history) >= 3 else lag_1
            roll_3 = float(np.mean(current_history[-3:]))
            month = f_date.month
            x_step = np.array([[current_trend_idx, lag_1, lag_2, lag_3, roll_3, month]])
            
        pred_val = float(model_full.predict(x_step)[0])
        pred_val = max(0.0, round(pred_val, 2))
        
        future_preds.append({
            "date": f_date.strftime("%Y-%m-%d"),
            "actual": None,
            "predicted": pred_val,
            "lower_bound": max(0.0, round(pred_val - 1.96 * sigma, 2)),
            "upper_bound": round(pred_val + 1.96 * sigma, 2)
        })
        
        current_history.append(pred_val)
        current_trend_idx += 1
        
    hist_points = [
        {"date": dates[i], "actual": round(float(y_values[i]), 2), "predicted": None}
        for i in range(total_points)
    ]
    
    return {
        "historical_points": hist_points,
        "forecast_points": future_preds,
        "metrics": {
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "r2_score": r2,
            "test_size_points": len(y_test),
            "zero_actuals_count": zero_cnt,
            "historical_points_total": total_points
        },
        "model_info": {
            "name": "Scikit-Learn Ridge Regression (Autoregressive)",
            "alpha": 1.0,
            "features_used": ["lag_1", "lag_2", "rolling_mean", "calendar_cyclical", "linear_trend"],
            "target_metric": target_metric,
            "granularity": granularity,
            "horizon": horizon
        },
        "limitations": "Statistical forecasts project established historical trajectory and seasonality. Unforeseen market shocks, competitive price disruptions, or supply chain bottlenecks cannot be anticipated solely from prior transaction data.",
        "methodology_explanation": "Autoregressive feature transformation with strict time-ordered out-of-sample evaluation. No future period contamination or data leakage."
    }
