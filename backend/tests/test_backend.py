"""
Comprehensive Automated Test Suite for InsightIQ Backend.
Covers API health, idempotent seeding, KPI formulas, data cleaning,
formula injection defense, forecasting safety, RFM segmentation,
and SQL injection / AST security enforcement.
"""
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, get_db_connection
from backend.seed_data import seed_sample_data
from backend.analytics.kpis import get_dashboard_kpis
from backend.analytics.data_cleaning import (
    sanitize_formula_injection, infer_canonical_mapping,
    calculate_data_quality_score, clean_and_normalize_dataset
)
from backend.analytics.sql_lab import validate_sql_query, execute_safe_query
from backend.analytics.forecasting import generate_forecast, compute_safe_mape
from backend.analytics.segmentation import calculate_customer_segmentation

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure database is initialized and sample data is seeded for testing."""
    init_db()
    seed_sample_data(force=False)

# 1. Health and System Verification
def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_records"] > 0

def test_list_datasets():
    response = client.get("/api/datasets")
    assert response.status_code == 200
    datasets = response.json()
    assert len(datasets) >= 1
    assert any(d["id"] == "sample_superstore" for d in datasets)

# 2. KPI Calculations and Math Integrity
def test_kpi_calculations_and_formulas():
    kpis = get_dashboard_kpis("sample_superstore")
    assert kpis["total_revenue"] > 1000000.0
    assert kpis["total_profit"] > 100000.0
    assert kpis["total_orders"] > 1000
    assert kpis["total_customers"] > 100
    
    # Verify Average Order Value formula: total_revenue / total_orders
    expected_aov = round(kpis["total_revenue"] / kpis["total_orders"], 2)
    assert abs(kpis["average_order_value"] - expected_aov) < 0.05
    
    # Verify Profit Margin formula: (total_profit / total_revenue) * 100
    expected_margin = round((kpis["total_profit"] / kpis["total_revenue"]) * 100.0, 2)
    assert abs(kpis["profit_margin_pct"] - expected_margin) < 0.05

def test_kpi_zero_denominator_safety():
    # Query non-existent region to ensure safe 0.0 values without ZeroDivisionError
    kpis = get_dashboard_kpis("sample_superstore", region="NonExistentRegion999")
    assert kpis["total_revenue"] == 0.0
    assert kpis["total_profit"] == 0.0
    assert kpis["total_orders"] == 0
    assert kpis["average_order_value"] == 0.0
    assert kpis["profit_margin_pct"] == 0.0

# 3. Data Cleaning and Formula Injection Prevention
def test_formula_injection_defense():
    # Threats: strings starting with =, +, -, @, \t, \r
    assert sanitize_formula_injection("=cmd|' /C calc'!A0") == "'=cmd|' /C calc'!A0"
    assert sanitize_formula_injection("+SUM(A1:A10)") == "'+SUM(A1:A10)"
    assert sanitize_formula_injection("-12345") == "'-12345"
    assert sanitize_formula_injection("@SUM(1,2)") == "'@SUM(1,2)"
    assert sanitize_formula_injection("Normal Text") == "Normal Text"

def test_canonical_mapping_inference():
    cols = ["InvoiceNo", "Order Date", "Customer ID", "Sales", "Profit", "Qty"]
    mapping = infer_canonical_mapping(cols)
    assert mapping["InvoiceNo"] == "order_id"
    assert mapping["Order Date"] == "order_date"
    assert mapping["Customer ID"] == "customer_id"
    assert mapping["Sales"] == "revenue"
    assert mapping["Profit"] == "profit"
    assert mapping["Qty"] == "quantity"

def test_data_cleaning_pipeline():
    dirty_data = {
        "order_id": ["ORD-1", "ORD-1", "ORD-2", "ORD-3"],  # has duplicate
        "order_date": ["2024-05-01", "2024-05-01", "2024-05-02", "invalid-date"],
        "customer_id": ["C1", "C1", "C2", "C3"],
        "revenue": [100.0, 100.0, None, 250.0],  # has null
        "quantity": [2, 2, -5, 3],  # has negative quantity typo
        "unit_price": [50.0, 50.0, 40.0, 80.0]
    }
    raw_df = pd.DataFrame(dirty_data)
    mappings = {c: c for c in raw_df.columns}
    
    cleaned_df, summary = clean_and_normalize_dataset(
        raw_df,
        mappings=mappings,
        remove_duplicates=True,
        impute_missing_numeric="median",
        trim_strings=True,
        normalize_dates=True
    )
    
    # Verify duplicate dropped
    assert summary["duplicates_removed"] == 1
    assert len(cleaned_df) == 3
    # Verify negative quantity corrected
    assert (cleaned_df["quantity"] > 0).all()
    # Verify null revenue imputed
    assert cleaned_df["revenue"].isna().sum() == 0
    # Verify quality score improved
    assert summary["quality_score_after"] >= summary["quality_score_before"]

# 4. SQL Analytics Lab & Security Enforcement
def test_sql_lab_allowed_query():
    query = "SELECT region, SUM(revenue) as rev FROM sales_data GROUP BY region ORDER BY rev DESC;"
    res = execute_safe_query(query)
    assert res["success"] is True
    assert len(res["rows"]) > 0
    assert "region" in res["columns"]
    assert "rev" in res["columns"]

def test_sql_lab_rejects_disallowed_dml():
    # DROP TABLE
    drop_res = execute_safe_query("DROP TABLE sales_data;")
    assert drop_res["success"] is False
    assert "Security Violation" in drop_res["error_message"] or "Only SELECT" in drop_res["error_message"]
    
    # DELETE
    del_res = execute_safe_query("DELETE FROM sales_data WHERE id = 1;")
    assert del_res["success"] is False
    
    # UPDATE
    upd_res = execute_safe_query("UPDATE sales_data SET revenue = 0;")
    assert upd_res["success"] is False
    
    # INSERT
    ins_res = execute_safe_query("INSERT INTO sales_data (id) VALUES (99999);")
    assert ins_res["success"] is False

def test_sql_lab_rejects_multiple_statements():
    multi_sql = "SELECT * FROM sales_data; DROP TABLE sales_data;"
    res = execute_safe_query(multi_sql)
    assert res["success"] is False
    assert "Multiple statements" in res["error_message"]

def test_sql_lab_rejects_unauthorized_tables():
    # Attempting to read sqlite internal master catalog
    unauth_sql = "SELECT * FROM sqlite_master;"
    res = execute_safe_query(unauth_sql)
    assert res["success"] is False
    assert "Access Denied" in res["error_message"]

# 5. Forecasting and Mathematical Correctness
def test_safe_mape_calculation():
    import numpy as np
    y_true = np.array([100.0, 200.0, 0.0, 300.0])
    y_pred = np.array([110.0, 190.0, 50.0, 315.0])
    mape, zero_count = compute_safe_mape(y_true, y_pred)
    assert zero_count == 1
    assert mape is not None
    assert 0.0 < mape < 50.0

def test_forecasting_pipeline():
    forecast_res = generate_forecast("sample_superstore", target_metric="revenue", granularity="M", horizon=3, model_type="ridge")
    assert len(forecast_res["historical_points"]) > 0
    assert len(forecast_res["forecast_points"]) == 3
    assert forecast_res["metrics"]["mae"] is not None
    assert forecast_res["metrics"]["rmse"] is not None
    assert "limitations" in forecast_res

# 6. Customer Segmentation (RFM)
def test_rfm_segmentation():
    seg_res = calculate_customer_segmentation("sample_superstore")
    assert seg_res["total_customers_analyzed"] > 50
    assert len(seg_res["segments_summary"]) > 0
    seg_names = [s["segment_name"] for s in seg_res["segments_summary"]]
    assert "Champions" in seg_names or "Loyal Customers" in seg_names
    # Customer percentages sum to approximately 100%
    total_pct = sum(s["customer_percentage"] for s in seg_res["segments_summary"])
    assert 99.0 <= total_pct <= 101.0

# 7. Reports and Exports
def test_csv_export_endpoint():
    response = client.get("/api/export/csv?dataset_id=sample_superstore")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert b"order_id,order_date" in response.content

def test_pdf_export_endpoint():
    response = client.get("/api/export/pdf?dataset_id=sample_superstore")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 1000
    assert response.content.startswith(b"%PDF")
