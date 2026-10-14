export interface FilterParams {
  dataset_id: string;
  start_date?: string;
  end_date?: string;
  region?: string;
  category?: string;
  segment?: string;
  product?: string;
}

export interface KPISummary {
  total_revenue: number;
  total_profit: number;
  total_orders: number;
  average_order_value: number;
  total_customers: number;
  profit_margin_pct: number;
  prev_revenue?: number | null;
  prev_profit?: number | null;
  revenue_growth_pct?: number | null;
  profit_growth_pct?: number | null;
  has_comparison_baseline: boolean;
  date_range: {
    start?: string;
    end?: string;
  };
}

export interface CategoryBreakdown {
  category: string;
  revenue: number;
  profit: number;
  orders: number;
  profit_margin: number;
  share_pct: number;
}

export interface RegionBreakdown {
  region: string;
  revenue: number;
  profit: number;
  orders: number;
  customers: number;
  profit_margin: number;
}

export interface TrendPoint {
  period: string;
  revenue: number;
  profit: number;
  orders: number;
  mom_growth_pct?: number | null;
}

export interface ProductPerformance {
  product_name: string;
  category: string;
  revenue: number;
  profit: number;
  quantity: number;
  profit_margin: number;
}

export interface OrderRecord {
  id: number;
  order_id: string;
  order_date: string;
  customer_name?: string;
  segment?: string;
  region?: string;
  category?: string;
  product_name?: string;
  quantity: number;
  unit_price: number;
  discount: number;
  revenue: number;
  profit: number;
}

export interface DashboardData {
  kpis: KPISummary;
  category_sales: CategoryBreakdown[];
  regional_sales: RegionBreakdown[];
  trend_data: TrendPoint[];
  top_products: ProductPerformance[];
  bottom_products: ProductPerformance[];
  recent_orders: OrderRecord[];
  active_filters: FilterParams;
  filter_options: {
    regions: string[];
    categories: string[];
    segments: string[];
    min_date: string[];
    max_date: string[];
  };
}

export interface ColumnProfile {
  name: string;
  inferred_type: string;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  sample_values: any[];
}

export interface DataQualityReport {
  dataset_name: string;
  quality_score: number;
  quality_grade: string;
  total_rows: number;
  total_columns: number;
  duplicate_rows: number;
  duplicate_percentage: number;
  missing_cells: number;
  missing_percentage: number;
  columns_profile: ColumnProfile[];
  suggested_mappings: Record<string, string>;
  preview_data: Record<string, any>[];
  score_breakdown: Record<string, number>;
  temp_file_token?: string;
}

export interface CleaningResult {
  dataset_id: string;
  dataset_name: string;
  rows_before: number;
  rows_after: number;
  duplicates_removed: number;
  nulls_handled: number;
  outliers_flagged: number;
  quality_score_before: number;
  quality_score_after: number;
  quality_grade_before: string;
  quality_grade_after: string;
  cleaned_at: string;
}

export interface DescriptiveStats {
  column: string;
  count: number;
  mean: number;
  std: number;
  min: number;
  p25: number;
  median: number;
  p75: number;
  max: number;
  skewness: number;
}

export interface HistogramBin {
  bin_start: number;
  bin_end: number;
  bin_label: string;
  count: number;
}

export interface BoxPlotData {
  column: string;
  min_val: number;
  q1: number;
  median: number;
  q3: number;
  max_val: number;
  iqr: number;
  outlier_count: number;
  outliers_sample: number[];
}

export interface EDAResponse {
  row_count: number;
  column_count: number;
  schema_info: Array<{
    column: string;
    dtype: string;
    non_null_count: number;
    null_count: number;
  }>;
  descriptive_statistics: DescriptiveStats[];
  distributions: Record<string, HistogramBin[]>;
  box_plots: Record<string, BoxPlotData>;
  category_frequencies: Record<string, Array<{ name: string; count: number; percentage: number }>>;
  correlation_matrix: Record<string, Record<string, number>>;
  scatter_data: Array<{ x: number; y: number; category: string; product: string }>;
  explanations: Record<string, string>;
}

export interface ForecastPoint {
  date: string;
  actual?: number | null;
  predicted?: number | null;
  lower_bound?: number | null;
  upper_bound?: number | null;
}

export interface ForecastMetrics {
  mae?: number | null;
  rmse?: number | null;
  mape?: number | null;
  r2_score?: number | null;
  test_size_points: number;
  zero_actuals_count: number;
  historical_points_total: number;
}

export interface ForecastResponse {
  historical_points: ForecastPoint[];
  forecast_points: ForecastPoint[];
  metrics: ForecastMetrics;
  model_info: Record<string, any>;
  limitations: string;
  methodology_explanation: string;
}

export interface CustomerSegment {
  segment_name: string;
  customer_count: number;
  customer_percentage: number;
  total_revenue: number;
  revenue_percentage: number;
  avg_recency_days: number;
  avg_frequency: number;
  avg_monetary: number;
  description: string;
  recommended_strategy: string;
}

export interface CustomerDetail {
  customer_id: string;
  customer_name: string;
  recency_days: number;
  frequency_orders: number;
  monetary_spend: number;
  r_score: number;
  f_score: number;
  m_score: number;
  rfm_segment: string;
  cluster_id?: number | null;
}

export interface SegmentationResponse {
  method: string;
  total_customers_analyzed: number;
  reference_date: string;
  segments_summary: CustomerSegment[];
  customers_sample: CustomerDetail[];
  rules_documentation: Record<string, string>;
  kmeans_inertia?: number | null;
}

export interface BusinessInsight {
  id: string;
  type: 'growth' | 'risk' | 'opportunity' | 'concentration' | 'quality';
  severity: 'info' | 'warning' | 'success' | 'critical';
  headline: string;
  supporting_metric: string;
  calculation_basis: string;
  interpretation: string;
  recommendation: string;
}

export interface SQLQueryResponse {
  success: boolean;
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  execution_time_ms: number;
  error_message?: string | null;
  query_executed: string;
}

export interface SampleQuery {
  id: string;
  title: string;
  description: string;
  category: string;
  query: string;
}

export interface DatasetInfo {
  id: string;
  name: string;
  description?: string;
  row_count: number;
  column_count: number;
  is_sample: boolean;
  created_at: string;
}
