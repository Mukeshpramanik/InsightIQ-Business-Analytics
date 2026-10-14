"""
Pydantic Request and Response Schemas for InsightIQ REST API.
Enforces strict type safety and schema validation across all endpoints.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- Common / Filter Models ---
class FilterParams(BaseModel):
    dataset_id: str = "sample_superstore"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    region: Optional[str] = None
    category: Optional[str] = None
    segment: Optional[str] = None
    product: Optional[str] = None

# --- Overview Dashboard Models ---
class KPISummary(BaseModel):
    total_revenue: float
    total_profit: float
    total_orders: int
    average_order_value: float
    total_customers: int
    profit_margin_pct: float
    prev_revenue: Optional[float] = None
    prev_profit: Optional[float] = None
    revenue_growth_pct: Optional[float] = None
    profit_growth_pct: Optional[float] = None
    has_comparison_baseline: bool = False
    date_range: Dict[str, Optional[str]]

class CategoryBreakdown(BaseModel):
    category: str
    revenue: float
    profit: float
    orders: int
    profit_margin: float
    share_pct: float

class RegionBreakdown(BaseModel):
    region: str
    revenue: float
    profit: float
    orders: int
    customers: int
    profit_margin: float

class TrendPoint(BaseModel):
    period: str
    revenue: float
    profit: float
    orders: int

class ProductPerformance(BaseModel):
    product_name: str
    category: str
    revenue: float
    profit: float
    quantity: int
    profit_margin: float

class OrderRecord(BaseModel):
    id: int
    order_id: str
    order_date: str
    customer_name: Optional[str]
    segment: Optional[str]
    region: Optional[str]
    category: Optional[str]
    product_name: Optional[str]
    quantity: int
    unit_price: float
    discount: float
    revenue: float
    profit: float

class DashboardData(BaseModel):
    kpis: KPISummary
    category_sales: List[CategoryBreakdown]
    regional_sales: List[RegionBreakdown]
    trend_data: List[TrendPoint]
    top_products: List[ProductPerformance]
    bottom_products: List[ProductPerformance]
    recent_orders: List[OrderRecord]
    active_filters: Dict[str, Any]
    filter_options: Dict[str, List[str]]

# --- Data Import & Quality Models ---
class ColumnProfile(BaseModel):
    name: str
    inferred_type: str
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: List[Any]

class DataQualityReport(BaseModel):
    dataset_name: str
    quality_score: float
    quality_grade: str
    total_rows: int
    total_columns: int
    duplicate_rows: int
    duplicate_percentage: float
    missing_cells: int
    missing_percentage: float
    columns_profile: List[ColumnProfile]
    suggested_mappings: Dict[str, str]
    preview_data: List[Dict[str, Any]]
    score_breakdown: Dict[str, float]

class CleaningRequest(BaseModel):
    dataset_id: Optional[str] = None
    dataset_name: str = "Uploaded Dataset"
    remove_duplicates: bool = True
    impute_missing_numeric: str = "median"  # drop, median, mean, zero
    impute_missing_categorical: str = "Unknown"  # drop, Unknown, mode
    trim_strings: bool = True
    normalize_dates: bool = True
    column_mappings: Dict[str, str] = Field(default_factory=dict)

class CleaningResult(BaseModel):
    dataset_id: str
    dataset_name: str
    rows_before: int
    rows_after: int
    duplicates_removed: int
    nulls_handled: int
    outliers_flagged: int
    quality_score_before: float
    quality_score_after: float
    quality_grade_before: str
    quality_grade_after: str
    cleaned_at: str

# --- EDA Models ---
class DescriptiveStats(BaseModel):
    column: str
    count: int
    mean: float
    std: float
    min: float
    p25: float
    median: float
    p75: float
    max: float
    skewness: float

class HistogramBin(BaseModel):
    bin_start: float
    bin_end: float
    bin_label: str
    count: int

class BoxPlotData(BaseModel):
    column: str
    min_val: float
    q1: float
    median: float
    q3: float
    max_val: float
    iqr: float
    outlier_count: int
    outliers_sample: List[float]

class SchemaInfoColumn(BaseModel):
    column: str
    dtype: str
    non_null_count: int
    null_count: int

class ScatterDataPoint(BaseModel):
    x: float
    y: float
    category: str
    product: str

class EDAResponse(BaseModel):
    row_count: int
    column_count: int
    schema_info: List[SchemaInfoColumn]
    descriptive_statistics: List[DescriptiveStats]
    distributions: Dict[str, List[HistogramBin]]
    box_plots: Dict[str, BoxPlotData]
    category_frequencies: Dict[str, List[Dict[str, Any]]]
    correlation_matrix: Dict[str, Dict[str, float]]
    scatter_data: List[ScatterDataPoint]
    explanations: Dict[str, str]

# --- Forecasting Models ---
class ForecastRequest(BaseModel):
    dataset_id: str = "sample_superstore"
    target_metric: str = "revenue"  # revenue or orders
    granularity: str = "D"  # D (daily) or M (monthly)
    horizon: int = 30  # periods ahead
    model_type: str = "ridge"  # baseline or ridge

class ForecastPoint(BaseModel):
    date: str
    actual: Optional[float] = None
    predicted: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class ForecastMetrics(BaseModel):
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    r2_score: Optional[float] = None
    test_size_points: int = 0
    zero_actuals_count: int = 0
    historical_points_total: int = 0

class ForecastResponse(BaseModel):
    historical_points: List[ForecastPoint]
    forecast_points: List[ForecastPoint]
    metrics: ForecastMetrics
    model_info: Dict[str, Any]
    limitations: str
    methodology_explanation: str

# --- Customer Segmentation Models ---
class CustomerSegment(BaseModel):
    segment_name: str
    customer_count: int
    customer_percentage: float
    total_revenue: float
    revenue_percentage: float
    avg_recency_days: float
    avg_frequency: float
    avg_monetary: float
    description: str
    recommended_strategy: str

class CustomerDetail(BaseModel):
    customer_id: str
    customer_name: str
    recency_days: int
    frequency_orders: int
    monetary_spend: float
    r_score: int
    f_score: int
    m_score: int
    rfm_segment: str
    cluster_id: Optional[int] = None

class SegmentationResponse(BaseModel):
    method: str
    total_customers_analyzed: int
    reference_date: str
    segments_summary: List[CustomerSegment]
    customers_sample: List[CustomerDetail]
    rules_documentation: Dict[str, str]
    kmeans_inertia: Optional[float] = None

# --- Business Insights Models ---
class BusinessInsight(BaseModel):
    id: str
    type: str  # growth, risk, opportunity, concentration, quality
    severity: str  # info, warning, success, critical
    headline: str
    supporting_metric: str
    calculation_basis: str
    interpretation: str
    recommendation: str

class InsightsResponse(BaseModel):
    insights: List[BusinessInsight]
    total_insights: int
    generated_at: str
    dataset_analyzed: str

# --- SQL Lab Models ---
class SQLQueryRequest(BaseModel):
    query: str

class SQLQueryResponse(BaseModel):
    success: bool
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float
    error_message: Optional[str] = None
    query_executed: str

class SampleQuery(BaseModel):
    id: str
    title: str
    description: str
    category: str
    query: str

# --- Dataset Management Models ---
class DatasetInfo(BaseModel):
    id: str
    name: str
    description: Optional[str]
    row_count: int
    column_count: int
    is_sample: bool
    created_at: str
