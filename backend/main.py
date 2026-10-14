"""
InsightIQ FastAPI Main Application.
REST API Server integrating data ingestion, data cleaning,
business intelligence analytics, predictive forecasting, customer segmentation,
interactive SQL execution, and multi-format reporting.
"""
import os
import io
import time
import logging
import pandas as pd
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from backend.database import init_db, get_db_connection, db_session, DB_PATH
from backend.seed_data import seed_sample_data, DATA_DIR
from backend.models import (
    DashboardData, KPISummary, CategoryBreakdown, RegionBreakdown, TrendPoint,
    ProductPerformance, OrderRecord, DataQualityReport, CleaningRequest, CleaningResult,
    EDAResponse, ForecastRequest, ForecastResponse, SegmentationResponse,
    InsightsResponse, SQLQueryRequest, SQLQueryResponse, SampleQuery, DatasetInfo
)
from backend.analytics.kpis import (
    get_dashboard_kpis, get_category_breakdown, get_region_breakdown,
    get_trend_data, get_product_rankings, get_recent_orders, get_filter_options
)
from backend.analytics.data_cleaning import (
    profile_dataset, clean_and_normalize_dataset, sanitize_formula_injection
)
from backend.analytics.eda import get_eda_summary
from backend.analytics.forecasting import generate_forecast
from backend.analytics.segmentation import calculate_customer_segmentation
from backend.analytics.insights import generate_business_insights
from backend.analytics.sql_lab import execute_safe_query, SAMPLE_SQL_QUERIES
from backend.analytics.reports import (
    generate_filtered_sales_csv, generate_segmentation_csv,
    generate_insights_csv, generate_executive_pdf_report
)

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("InsightIQ")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database schema exists and default sample data is seeded safely across multi-worker processes."""
    logger.info("Initializing InsightIQ database and verifying seed data...")
    lock_path = f"{os.path.abspath(DB_PATH)}.init.lock"
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    try:
        import fcntl
        with open(lock_path, "w") as lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            except (AttributeError, OSError):
                pass
            init_db()
            seed_sample_data(force=False)
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            except (AttributeError, OSError):
                pass
    except Exception as e:
        logger.warning(f"File locking encountered warning: {e}. Executing idempotent initialization...")
        init_db()
        seed_sample_data(force=False)
    logger.info("InsightIQ backend initialized successfully.")
    yield

app = FastAPI(
    title="InsightIQ API",
    description="Enterprise Business Intelligence & Predictive Analytics Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS for frontend communication (configurable via CORS_ORIGINS)
cors_origins_env = os.environ.get("CORS_ORIGINS", "*")
if cors_origins_env.strip() == "*":
    origins = ["*"]
else:
    origins = [orig.strip() for orig in cors_origins_env.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    """Inject standard HTTP security headers into every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch unhandled errors, log traceback, and return standard JSON error."""
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None)
        )
    logger.exception(f"Unhandled server error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please inspect server logs."}
    )

# --- System & Datasets ---
@app.get("/api/health")
def health_check():
    """Health check endpoint for API, database connectivity, and environment verification."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales_data")
    count = cursor.fetchone()[0]
    conn.close()
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database_records": count,
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

@app.get("/api/datasets", response_model=List[DatasetInfo])
def list_datasets():
    """Returns catalog of all registered datasets."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, row_count, column_count, is_sample, created_at FROM datasets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/datasets/reset-sample")
def reset_sample_dataset():
    """Restores the pristine deterministic sample retail dataset."""
    sample_id = seed_sample_data(force=True)
    return {"message": "Sample dataset reseeded successfully.", "dataset_id": sample_id}

@app.delete("/api/datasets/{dataset_id}")
def delete_dataset(dataset_id: str):
    """Deletes an uploaded dataset and cascades to associated transactional records and disk files."""
    if dataset_id == "sample_superstore":
        raise HTTPException(status_code=400, detail="Cannot delete default built-in sample dataset. You may reset it instead.")
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        if row and row["file_path"] and os.path.exists(row["file_path"]):
            try:
                os.remove(row["file_path"])
            except Exception as e:
                logger.warning(f"Could not remove dataset file {row['file_path']}: {e}")
        cursor.execute("DELETE FROM sales_data WHERE dataset_id = ?", (dataset_id,))
        cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
    return {"message": f"Dataset '{dataset_id}' deleted successfully."}

# --- Data Import & Cleaning ---
@app.post("/api/upload/preview")
async def preview_csv_upload(file: UploadFile = File(...)):
    """
    Receives CSV file, validates format/size, extracts schema profile,
    computes preliminary Data Quality Score, and returns canonical column suggestions.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are accepted.")
        
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:  # 25 MB limit
        raise HTTPException(status_code=400, detail="File size exceeds maximum upload limit of 25MB.")
        
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")
        
    if df.empty or len(df.columns) < 2:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty or lacks sufficient tabular columns.")
        
    profile = profile_dataset(df, dataset_name=file.filename)
    # Save temporary raw preview file
    temp_path = os.path.join(DATA_DIR, f"temp_{int(time.time())}_{file.filename}")
    df.to_csv(temp_path, index=False)
    profile["temp_file_token"] = os.path.basename(temp_path)
    return profile

@app.post("/api/upload/clean")
def clean_and_save_upload(
    temp_file_token: str = Form(...),
    dataset_name: str = Form(...),
    remove_duplicates: bool = Form(True),
    impute_missing_numeric: str = Form("median"),
    impute_missing_categorical: str = Form("Unknown"),
    trim_strings: bool = Form(True),
    normalize_dates: bool = Form(True),
    column_mappings_json: str = Form("{}")
):
    """
    Applies user-configured cleaning transforms to raw CSV,
    persists cleaned records in SQLite, and logs audit metrics.
    """
    import json
    temp_path = os.path.join(DATA_DIR, os.path.basename(temp_file_token))
    if not os.path.exists(temp_path):
        raise HTTPException(status_code=404, detail="Upload session expired. Please re-upload your file.")
        
    try:
        raw_df = pd.read_csv(temp_path)
        mappings = json.loads(column_mappings_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid cleaning configuration: {str(e)}")
        
    cleaned_df, summary = clean_and_normalize_dataset(
        raw_df,
        mappings=mappings,
        remove_duplicates=remove_duplicates,
        impute_missing_numeric=impute_missing_numeric,
        impute_missing_categorical=impute_missing_categorical,
        trim_strings=trim_strings,
        normalize_dates=normalize_dates
    )
    
    dataset_id = f"ds_{int(time.time())}"
    clean_csv_path = os.path.join(DATA_DIR, f"{dataset_id}_clean.csv")
    cleaned_df.to_csv(clean_csv_path, index=False)
    
    # Ingest into SQLite
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO datasets (id, name, description, row_count, column_count, is_sample, file_path)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (
            dataset_id,
            dataset_name,
            f"User dataset cleaned and imported with Quality Score {summary['quality_score_after']}/100",
            len(cleaned_df),
            len(cleaned_df.columns),
            clean_csv_path
        ))
        
        # Batch insert
        records = []
        for _, r in cleaned_df.iterrows():
            records.append((
                dataset_id,
                str(r.get("order_id", f"ORD-{_}")),
                str(r.get("order_date", "2024-01-01")),
                str(r.get("customer_id", "CUST-001")),
                str(r.get("customer_name", "Customer")),
                str(r.get("segment", "Consumer")),
                str(r.get("region", "National")),
                str(r.get("country", "United States")),
                str(r.get("city", "City")),
                str(r.get("state", "State")),
                str(r.get("category", "General")),
                str(r.get("sub_category", "Standard")),
                str(r.get("product_id", "PROD-001")),
                str(r.get("product_name", "Product Item")),
                int(r.get("quantity", 1)),
                float(r.get("unit_price", 10.0)),
                float(r.get("discount", 0.0)),
                float(r.get("shipping_cost", 0.0)),
                float(r.get("revenue", 10.0)),
                float(r.get("cost", 7.0)),
                float(r.get("profit", 3.0))
            ))
            
        cursor.executemany("""
            INSERT INTO sales_data (
                dataset_id, order_id, order_date, customer_id, customer_name, segment,
                region, country, city, state, category, sub_category, product_id,
                product_name, quantity, unit_price, discount, shipping_cost, revenue, cost, profit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        
        # Log cleaning audit
        cursor.execute("""
            INSERT INTO cleaning_history (
                dataset_id, rows_before, rows_after, duplicates_removed,
                nulls_handled, outliers_flagged, quality_score_before, quality_score_after, cleaning_log
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dataset_id,
            summary["rows_before"],
            summary["rows_after"],
            summary["duplicates_removed"],
            summary["nulls_handled"],
            summary["outliers_flagged"],
            summary["quality_score_before"],
            summary["quality_score_after"],
            f"Cleaning applied with {impute_missing_numeric} numeric imputation."
        ))
        
    # Safely clean up raw preview temporary file
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception as cleanup_err:
        logger.warning(f"Could not remove temp file {temp_path}: {cleanup_err}")

    summary["dataset_id"] = dataset_id
    summary["dataset_name"] = dataset_name
    return summary

# --- Overview Dashboard ---
@app.get("/api/analytics/filter-options")
def filter_options(dataset_id: str = "sample_superstore"):
    """Returns dynamic unique filter values for the active dataset."""
    return get_filter_options(dataset_id)

@app.get("/api/analytics/dashboard", response_model=DashboardData)
def dashboard_metrics(
    dataset_id: str = "sample_superstore",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
):
    """Calculates all headline executive KPIs, breakdowns, and trend charts."""
    kpis = get_dashboard_kpis(dataset_id, start_date, end_date, region, category, segment, product)
    cat_sales = get_category_breakdown(dataset_id, start_date, end_date, region, category, segment, product)
    reg_sales = get_region_breakdown(dataset_id, start_date, end_date, region, category, segment, product)
    trend = get_trend_data(dataset_id, start_date, end_date, region, category, segment, product)
    top_p, bottom_p = get_product_rankings(dataset_id, start_date, end_date, region, category, segment, product)
    recent = get_recent_orders(dataset_id, start_date, end_date, region, category, segment, product, limit=25)
    f_opts = get_filter_options(dataset_id)
    
    return {
        "kpis": kpis,
        "category_sales": cat_sales,
        "regional_sales": reg_sales,
        "trend_data": trend,
        "top_products": top_p,
        "bottom_products": bottom_p,
        "recent_orders": recent,
        "active_filters": {
            "dataset_id": dataset_id,
            "start_date": start_date,
            "end_date": end_date,
            "region": region,
            "category": category,
            "segment": segment,
            "product": product
        },
        "filter_options": f_opts
    }

# --- Exploratory Data Analysis (EDA) ---
@app.get("/api/analytics/eda", response_model=EDAResponse)
def eda_analysis(dataset_id: str = "sample_superstore"):
    """Returns comprehensive statistical distributions, box plot metrics, and correlation matrix."""
    return get_eda_summary(dataset_id)

# --- Sales Performance Analytics ---
@app.get("/api/analytics/sales")
def sales_performance_analytics(
    dataset_id: str = "sample_superstore",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
):
    """Detailed sales performance deep-dive with MoM growth and product ranking tables."""
    kpis = get_dashboard_kpis(dataset_id, start_date, end_date, region, category, segment, product)
    trend = get_trend_data(dataset_id, start_date, end_date, region, category, segment, product)
    top_p, bottom_p = get_product_rankings(dataset_id, start_date, end_date, region, category, segment, product)
    orders = get_recent_orders(dataset_id, start_date, end_date, region, category, segment, product, limit=100)
    
    # Calculate MoM growth for trend periods
    for i in range(1, len(trend)):
        prev_rev = trend[i-1]["revenue"]
        curr_rev = trend[i]["revenue"]
        if prev_rev > 0:
            trend[i]["mom_growth_pct"] = round(((curr_rev - prev_rev) / prev_rev) * 100.0, 2)
        else:
            trend[i]["mom_growth_pct"] = None
    if len(trend) > 0:
        trend[0]["mom_growth_pct"] = None
        
    return {
        "kpis": kpis,
        "monthly_trends": trend,
        "top_products": top_p,
        "bottom_products": bottom_p,
        "order_records": orders
    }

# --- Predictive Forecasting ---
@app.post("/api/analytics/forecast", response_model=ForecastResponse)
def run_forecast(req: ForecastRequest):
    """Generates sales or order volume predictions using time-ordered train/test validation."""
    return generate_forecast(
        dataset_id=req.dataset_id,
        target_metric=req.target_metric,
        granularity=req.granularity,
        horizon=req.horizon,
        model_type=req.model_type
    )

# --- Customer Segmentation ---
@app.get("/api/analytics/segmentation", response_model=SegmentationResponse)
def run_segmentation(dataset_id: str = "sample_superstore", use_kmeans: bool = True):
    """Executes deterministic RFM quintile segmentation and K-Means clustering."""
    return calculate_customer_segmentation(dataset_id=dataset_id, use_kmeans=use_kmeans)

# --- Business Insights ---
@app.get("/api/analytics/insights", response_model=InsightsResponse)
def get_insights(
    dataset_id: str = "sample_superstore",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
):
    """Executes rule-based analytical checks to surface actionable business findings."""
    items = generate_business_insights(
        dataset_id=dataset_id,
        start_date=start_date,
        end_date=end_date,
        region=region,
        category=category,
        segment=segment,
        product=product
    )
    return {
        "insights": items,
        "total_insights": len(items),
        "generated_at": pd.Timestamp.now().isoformat(),
        "dataset_analyzed": dataset_id
    }

# --- SQL Analytics Lab ---
@app.get("/api/sql-lab/samples", response_model=List[SampleQuery])
def get_sql_samples():
    """Returns curated library of business analyst interview SQL queries."""
    return SAMPLE_SQL_QUERIES

@app.post("/api/sql-lab/execute", response_model=SQLQueryResponse)
def run_sql_query(req: SQLQueryRequest):
    """Validates and executes read-only SELECT query against SQLite database."""
    return execute_safe_query(req.query)

# --- Exports & Reports ---
@app.get("/api/export/csv")
def export_filtered_csv(
    dataset_id: str = "sample_superstore",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
):
    """Downloads filtered transaction dataset as sanitized CSV."""
    csv_str = generate_filtered_sales_csv(dataset_id, start_date, end_date, region, category, segment, product)
    filename = f"insightiq_export_{dataset_id}.csv"
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/segmentation-csv")
def export_segmentation_csv(dataset_id: str = "sample_superstore"):
    """Downloads customer RFM segmentation report as CSV."""
    csv_str = generate_segmentation_csv(dataset_id)
    filename = f"insightiq_customer_segments_{dataset_id}.csv"
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/insights-csv")
def export_insights_csv(
    dataset_id: str = "sample_superstore",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
):
    """Downloads business findings and strategic recommendations as CSV."""
    csv_str = generate_insights_csv(dataset_id, start_date, end_date, region, category, segment, product)
    filename = f"insightiq_business_insights_{dataset_id}.csv"
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/pdf")
def export_pdf_report(
    dataset_id: str = "sample_superstore",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
):
    """Generates and downloads professional PDF executive summary report."""
    try:
        pdf_bytes = generate_executive_pdf_report(
            dataset_id, start_date, end_date, region, category, segment, product
        )
        filename = f"InsightIQ_Executive_Report_{dataset_id}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")
