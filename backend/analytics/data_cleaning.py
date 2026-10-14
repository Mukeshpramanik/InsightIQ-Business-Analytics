"""
InsightIQ Data Quality Profiler and Cleaning Engine.
Provides comprehensive data validation, automated schema inference,
canonical column mapping, formula injection prevention, and deterministic quality scoring.
"""
import io
import re
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional

CANONICAL_SYNONYMS = {
    "order_id": ["order_id", "order id", "invoiceno", "invoice_no", "order_number", "id", "order_no"],
    "order_date": ["order_date", "order date", "date", "invoicedate", "invoice_date", "sale_date", "transaction_date"],
    "customer_id": ["customer_id", "customer id", "customerid", "cust_id", "client_id"],
    "customer_name": ["customer_name", "customer name", "customer", "client_name", "client"],
    "segment": ["segment", "customer_segment", "cust_segment", "market_segment"],
    "region": ["region", "territory", "zone", "area", "market"],
    "country": ["country", "nation"],
    "city": ["city", "town"],
    "state": ["state", "province"],
    "category": ["category", "dept", "department", "product_category"],
    "sub_category": ["sub_category", "sub-category", "subcategory", "item_group"],
    "product_id": ["product_id", "product id", "productid", "item_id", "sku"],
    "product_name": ["product_name", "product name", "product", "item_name", "description", "item"],
    "quantity": ["quantity", "qty", "units", "count", "volume"],
    "unit_price": ["unit_price", "unit price", "price", "unitprice", "rate"],
    "discount": ["discount", "disc", "discount_rate", "rebate"],
    "shipping_cost": ["shipping_cost", "shipping", "freight"],
    "revenue": ["revenue", "sales", "total", "amount", "turnover", "total_amount", "gross_sales"],
    "cost": ["cost", "cogs", "total_cost", "unit_cost"],
    "profit": ["profit", "margin", "net_profit", "net_income", "earnings"]
}

def sanitize_formula_injection(val: Any) -> Any:
    """
    Prevent Spreadsheet Formula Injection (CSV injection).
    Prepends a single quote if a text value starts with =, +, -, @, \\t, \\r
    """
    if isinstance(val, str):
        val = val.strip()
        if len(val) > 0 and val[0] in ('=', '+', '-', '@', '\t', '\r'):
            return f"'{val}"
    return val

def infer_canonical_mapping(columns: List[str]) -> Dict[str, str]:
    """
    Maps uploaded column names to canonical internal field names.
    Returns mapping: {uploaded_col: canonical_field}
    """
    mapping = {}
    normalized_cols = {re.sub(r'[^a-z0-9_]', '', col.lower().replace(' ', '_')): col for col in columns}
    
    for canonical, synonyms in CANONICAL_SYNONYMS.items():
        found = False
        for syn in synonyms:
            clean_syn = re.sub(r'[^a-z0-9_]', '', syn.lower().replace(' ', '_'))
            if clean_syn in normalized_cols:
                mapping[normalized_cols[clean_syn]] = canonical
                found = True
                break
        if not found:
            # Substring match fallback
            for norm_key, original_col in normalized_cols.items():
                if norm_key not in mapping.values() and canonical in norm_key:
                    mapping[original_col] = canonical
                    break
    return mapping

def calculate_data_quality_score(df: pd.DataFrame, mapped_fields: Dict[str, str]) -> Tuple[float, str, Dict[str, float]]:
    """
    Computes a mathematically documented Data Quality Score between 0.0 and 100.0.
    
    Formula:
    - Missing Cells Penalty: max 25 points (rate = total_missing / total_cells)
    - Duplicate Rows Penalty: max 20 points (rate = duplicate_rows / total_rows)
    - Outlier Ratio Penalty: max 20 points (rate = total_outliers / (numeric_cols * rows))
    - Unmapped Critical Fields Penalty: max 20 points (checks order_date, revenue, quantity)
    - Type Inconsistency Penalty: max 15 points
    
    Score = 100 - (missing_penalty + duplicate_penalty + outlier_penalty + mapping_penalty + type_penalty)
    """
    total_rows, total_cols = df.shape
    total_cells = max(1, total_rows * total_cols)
    
    # 1. Missing penalty
    total_missing = int(df.isna().sum().sum())
    missing_ratio = total_missing / total_cells
    missing_penalty = round(min(25.0, missing_ratio * 100.0), 2)
    
    # 2. Duplicate penalty
    duplicate_rows = int(df.duplicated().sum())
    duplicate_ratio = duplicate_rows / max(1, total_rows)
    duplicate_penalty = round(min(20.0, duplicate_ratio * 100.0), 2)
    
    # 3. Outlier penalty via IQR
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    total_outliers = 0
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) > 4:
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                total_outliers += int(((series < lower) | (series > upper)).sum())
                
    num_num_cells = max(1, len(numeric_cols) * total_rows)
    outlier_ratio = total_outliers / num_num_cells
    outlier_penalty = round(min(20.0, outlier_ratio * 150.0), 2)
    
    # 4. Critical canonical field mapping penalty
    critical_fields = {"order_date", "revenue", "quantity"}
    mapped_canonical_values = set(mapped_fields.values())
    missing_critical = len(critical_fields - mapped_canonical_values)
    mapping_penalty = round((missing_critical / len(critical_fields)) * 20.0, 2)
    
    # 5. Type anomaly penalty
    type_penalty = 0.0
    # Check if dates can be parsed
    if "order_date" in mapped_canonical_values:
        date_col = [col for col, canon in mapped_fields.items() if canon == "order_date"][0]
        parsed_dates = pd.to_datetime(df[date_col], errors='coerce')
        invalid_dates = int(parsed_dates.isna().sum() - df[date_col].isna().sum())
        if invalid_dates > 0:
            type_penalty += min(15.0, (invalid_dates / max(1, total_rows)) * 100.0)
            
    score = round(max(0.0, min(100.0, 100.0 - (missing_penalty + duplicate_penalty + outlier_penalty + mapping_penalty + type_penalty))), 1)
    
    if score >= 90.0:
        grade = "A (Excellent)"
    elif score >= 75.0:
        grade = "B (Good)"
    elif score >= 60.0:
        grade = "C (Fair)"
    else:
        grade = "D (Poor - Requires Cleaning)"
        
    breakdown = {
        "missing_penalty": missing_penalty,
        "duplicate_penalty": duplicate_penalty,
        "outlier_penalty": outlier_penalty,
        "mapping_penalty": mapping_penalty,
        "type_penalty": round(type_penalty, 2),
        "final_score": score
    }
    
    return score, grade, breakdown

def profile_dataset(df: pd.DataFrame, dataset_name: str = "Uploaded Dataset") -> Dict[str, Any]:
    """Generates detailed data quality report and schema profile."""
    total_rows, total_cols = df.shape
    duplicate_rows = int(df.duplicated().sum())
    missing_cells = int(df.isna().sum().sum())
    
    columns_profile = []
    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        unique_count = int(series.nunique(dropna=True))
        
        # Inferred type
        if pd.api.types.is_numeric_dtype(series):
            inferred = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            inferred = "datetime"
        else:
            inferred = "text"
            
        sample_vals = series.dropna().head(3).tolist()
        columns_profile.append({
            "name": col,
            "inferred_type": inferred,
            "null_count": null_count,
            "null_percentage": round((null_count / max(1, total_rows)) * 100.0, 2),
            "unique_count": unique_count,
            "sample_values": [str(v) for v in sample_vals]
        })
        
    suggested_mappings = infer_canonical_mapping(list(df.columns))
    score, grade, breakdown = calculate_data_quality_score(df, suggested_mappings)
    
    # Safe sample preview
    preview_df = df.head(10).fillna("")
    preview_data = preview_df.to_dict(orient="records")
    
    return {
        "dataset_name": dataset_name,
        "quality_score": score,
        "quality_grade": grade,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": round((duplicate_rows / max(1, total_rows)) * 100.0, 2),
        "missing_cells": missing_cells,
        "missing_percentage": round((missing_cells / max(1, total_rows * total_cols)) * 100.0, 2),
        "columns_profile": columns_profile,
        "suggested_mappings": suggested_mappings,
        "preview_data": preview_data,
        "score_breakdown": breakdown
    }

def clean_and_normalize_dataset(
    df: pd.DataFrame,
    mappings: Dict[str, str],
    remove_duplicates: bool = True,
    impute_missing_numeric: str = "median",
    impute_missing_categorical: str = "Unknown",
    trim_strings: bool = True,
    normalize_dates: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw DataFrame according to user rules and maps to canonical schema.
    Returns cleaned DataFrame and cleaning audit summary.
    """
    rows_before = len(df)
    score_before, grade_before, _ = calculate_data_quality_score(df, mappings)
    
    cleaned_df = df.copy()
    
    # 1. Rename columns according to mapping
    if mappings:
        cleaned_df = cleaned_df.rename(columns=mappings)
        
    # 2. String trimming & Formula Injection prevention
    if trim_strings:
        for col in cleaned_df.select_dtypes(include=["object"]):
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            # replace 'nan' string with actual NaN
            cleaned_df[col] = cleaned_df[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan})
            cleaned_df[col] = cleaned_df[col].apply(sanitize_formula_injection)
            
    # 3. Remove duplicates
    duplicates_removed = 0
    if remove_duplicates:
        dups_count = int(cleaned_df.duplicated().sum())
        cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)
        duplicates_removed = dups_count
        
    # 4. Handle date normalization
    if normalize_dates and "order_date" in cleaned_df.columns:
        cleaned_df["order_date"] = pd.to_datetime(cleaned_df["order_date"], errors='coerce')
        # If dates are missing or invalid, forward fill or set default
        cleaned_df["order_date"] = cleaned_df["order_date"].fillna(pd.Timestamp("2024-01-01"))
        cleaned_df["order_date"] = cleaned_df["order_date"].dt.strftime("%Y-%m-%d")
        
    # 5. Missing values imputation
    nulls_handled = int(cleaned_df.isna().sum().sum())
    
    # Numeric columns
    num_cols = cleaned_df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        if cleaned_df[col].isna().any():
            if impute_missing_numeric == "median":
                fill_val = cleaned_df[col].median()
            elif impute_missing_numeric == "mean":
                fill_val = cleaned_df[col].mean()
            elif impute_missing_numeric == "zero":
                fill_val = 0.0
            else: # drop
                cleaned_df = cleaned_df.dropna(subset=[col])
                continue
            cleaned_df[col] = cleaned_df[col].fillna(fill_val)
            
    # Categorical columns
    cat_cols = cleaned_df.select_dtypes(include=["object"]).columns
    for col in cat_cols:
        if col != "order_date" and cleaned_df[col].isna().any():
            if impute_missing_categorical == "mode":
                mode_val = cleaned_df[col].mode()
                fill_val = mode_val.iloc[0] if len(mode_val) > 0 else "Unknown"
            else:
                fill_val = impute_missing_categorical
            cleaned_df[col] = cleaned_df[col].fillna(fill_val)
            
    # 6. Ensure mandatory fields exist with mathematical integrity
    if "quantity" in cleaned_df.columns:
        cleaned_df["quantity"] = pd.to_numeric(cleaned_df["quantity"], errors="coerce").fillna(1).astype(int)
        cleaned_df["quantity"] = cleaned_df["quantity"].apply(lambda q: max(1, abs(q)))
    else:
        cleaned_df["quantity"] = 1
        
    if "unit_price" in cleaned_df.columns:
        cleaned_df["unit_price"] = pd.to_numeric(cleaned_df["unit_price"], errors="coerce").fillna(10.0).astype(float)
        cleaned_df["unit_price"] = cleaned_df["unit_price"].apply(lambda p: max(0.01, abs(p)))
    else:
        cleaned_df["unit_price"] = 10.0
        
    if "discount" in cleaned_df.columns:
        cleaned_df["discount"] = pd.to_numeric(cleaned_df["discount"], errors="coerce").fillna(0.0).astype(float)
        cleaned_df["discount"] = cleaned_df["discount"].clip(0.0, 0.9)
    else:
        cleaned_df["discount"] = 0.0
        
    if "shipping_cost" in cleaned_df.columns:
        cleaned_df["shipping_cost"] = pd.to_numeric(cleaned_df["shipping_cost"], errors="coerce").fillna(0.0).astype(float)
    else:
        cleaned_df["shipping_cost"] = 5.0
        
    # Recalculate or verify revenue
    if "revenue" not in cleaned_df.columns or cleaned_df["revenue"].isna().any():
        cleaned_df["revenue"] = (cleaned_df["quantity"] * cleaned_df["unit_price"] * (1.0 - cleaned_df["discount"])).round(2)
    else:
        cleaned_df["revenue"] = pd.to_numeric(cleaned_df["revenue"], errors="coerce").fillna(
            (cleaned_df["quantity"] * cleaned_df["unit_price"] * (1.0 - cleaned_df["discount"])).round(2)
        )
        
    # Cost & Profit
    if "cost" not in cleaned_df.columns or cleaned_df["cost"].isna().any():
        cleaned_df["cost"] = (cleaned_df["revenue"] * 0.65).round(2)
    else:
        cleaned_df["cost"] = pd.to_numeric(cleaned_df["cost"], errors="coerce").fillna(cleaned_df["revenue"] * 0.65).round(2)
        
    if "profit" not in cleaned_df.columns or cleaned_df["profit"].isna().any():
        cleaned_df["profit"] = (cleaned_df["revenue"] - cleaned_df["cost"] - cleaned_df["shipping_cost"]).round(2)
    else:
        cleaned_df["profit"] = pd.to_numeric(cleaned_df["profit"], errors="coerce").fillna(
            cleaned_df["revenue"] - cleaned_df["cost"] - cleaned_df["shipping_cost"]
        ).round(2)
        
    # Fill standard identifiers if missing
    if "order_id" not in cleaned_df.columns:
        cleaned_df["order_id"] = [f"ORD-GEN-{i:05d}" for i in range(1, len(cleaned_df) + 1)]
    if "customer_id" not in cleaned_df.columns:
        cleaned_df["customer_id"] = [f"CUST-{abs(hash(str(o))) % 1000:04d}" for o in cleaned_df["order_id"]]
    if "customer_name" not in cleaned_df.columns:
        cleaned_df["customer_name"] = cleaned_df["customer_id"]
    if "category" not in cleaned_df.columns:
        cleaned_df["category"] = "General Merchandise"
    if "sub_category" not in cleaned_df.columns:
        cleaned_df["sub_category"] = "Standard"
    if "region" not in cleaned_df.columns:
        cleaned_df["region"] = "National"
    if "segment" not in cleaned_df.columns:
        cleaned_df["segment"] = "Standard"
    if "product_name" not in cleaned_df.columns:
        cleaned_df["product_name"] = "Commercial Product"
    if "product_id" not in cleaned_df.columns:
        cleaned_df["product_id"] = "PROD-GEN-01"
    if "city" not in cleaned_df.columns:
        cleaned_df["city"] = "Metropolis"
    if "state" not in cleaned_df.columns:
        cleaned_df["state"] = "State"
    if "country" not in cleaned_df.columns:
        cleaned_df["country"] = "United States"

    rows_after = len(cleaned_df)
    
    # Recalculate score after cleaning
    clean_mappings = {c: c for c in cleaned_df.columns}
    score_after, grade_after, _ = calculate_data_quality_score(cleaned_df, clean_mappings)
    
    summary = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "duplicates_removed": duplicates_removed,
        "nulls_handled": nulls_handled,
        "outliers_flagged": 0,
        "quality_score_before": score_before,
        "quality_score_after": score_after,
        "quality_grade_before": grade_before,
        "quality_grade_after": grade_after,
        "cleaned_at": pd.Timestamp.now().isoformat()
    }
    
    return cleaned_df, summary
