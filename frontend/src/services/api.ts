import {
  DashboardData, FilterParams, DataQualityReport, CleaningResult,
  EDAResponse, ForecastResponse, SegmentationResponse, BusinessInsight,
  SQLQueryResponse, SampleQuery, DatasetInfo
} from '../types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || '/api';

export const api = {
  // System & Health
  async getHealth(): Promise<{ status: string; database_records: number }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to fetch API health');
    return res.json();
  },

  async getDatasets(): Promise<DatasetInfo[]> {
    const res = await fetch(`${API_BASE}/datasets`);
    if (!res.ok) throw new Error('Failed to fetch datasets');
    return res.json();
  },

  async resetSampleDataset(): Promise<{ message: string; dataset_id: string }> {
    const res = await fetch(`${API_BASE}/datasets/reset-sample`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset sample data');
    return res.json();
  },

  async deleteDataset(datasetId: string): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}`, { method: 'DELETE' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to delete dataset' }));
      throw new Error(err.detail || 'Failed to delete dataset');
    }
    return res.json();
  },

  // Upload & Cleaning
  async previewCsvUpload(file: File): Promise<DataQualityReport> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/upload/preview`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to preview CSV' }));
      throw new Error(err.detail || 'Failed to preview CSV');
    }
    return res.json();
  },

  async cleanAndSaveUpload(params: {
    temp_file_token: string;
    dataset_name: string;
    remove_duplicates: boolean;
    impute_missing_numeric: string;
    impute_missing_categorical: string;
    trim_strings: boolean;
    normalize_dates: boolean;
    column_mappings: Record<string, string>;
  }): Promise<CleaningResult> {
    const formData = new FormData();
    formData.append('temp_file_token', params.temp_file_token);
    formData.append('dataset_name', params.dataset_name);
    formData.append('remove_duplicates', String(params.remove_duplicates));
    formData.append('impute_missing_numeric', params.impute_missing_numeric);
    formData.append('impute_missing_categorical', params.impute_missing_categorical);
    formData.append('trim_strings', String(params.trim_strings));
    formData.append('normalize_dates', String(params.normalize_dates));
    formData.append('column_mappings_json', JSON.stringify(params.column_mappings));

    const res = await fetch(`${API_BASE}/upload/clean`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to clean dataset' }));
      throw new Error(err.detail || 'Failed to clean dataset');
    }
    return res.json();
  },

  // Dashboard & KPIs
  async getDashboard(filters: FilterParams): Promise<DashboardData> {
    const params = new URLSearchParams();
    if (filters.dataset_id) params.append('dataset_id', filters.dataset_id);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.region && filters.region !== 'All') params.append('region', filters.region);
    if (filters.category && filters.category !== 'All') params.append('category', filters.category);
    if (filters.segment && filters.segment !== 'All') params.append('segment', filters.segment);
    if (filters.product && filters.product !== 'All') params.append('product', filters.product);

    const res = await fetch(`${API_BASE}/analytics/dashboard?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch dashboard metrics');
    return res.json();
  },

  // Filter Options
  async getFilterOptions(datasetId: string): Promise<{
    regions: string[];
    categories: string[];
    segments: string[];
    min_date: string[];
    max_date: string[];
  }> {
    const res = await fetch(`${API_BASE}/analytics/filter-options?dataset_id=${datasetId}`);
    if (!res.ok) throw new Error('Failed to fetch filter options');
    return res.json();
  },

  // Exploratory Data Analysis
  async getEda(datasetId: string): Promise<EDAResponse> {
    const res = await fetch(`${API_BASE}/analytics/eda?dataset_id=${datasetId}`);
    if (!res.ok) throw new Error('Failed to fetch EDA analysis');
    return res.json();
  },

  // Sales Analytics Deep Dive
  async getSalesPerformance(filters: FilterParams): Promise<any> {
    const params = new URLSearchParams();
    if (filters.dataset_id) params.append('dataset_id', filters.dataset_id);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.region && filters.region !== 'All') params.append('region', filters.region);
    if (filters.category && filters.category !== 'All') params.append('category', filters.category);
    if (filters.segment && filters.segment !== 'All') params.append('segment', filters.segment);

    const res = await fetch(`${API_BASE}/analytics/sales?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch sales performance analytics');
    return res.json();
  },

  // Predictive Forecasting
  async runForecast(req: {
    dataset_id: string;
    target_metric: string;
    granularity: string;
    horizon: number;
    model_type: string;
  }): Promise<ForecastResponse> {
    const res = await fetch(`${API_BASE}/analytics/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error('Failed to generate forecast');
    return res.json();
  },

  // Customer Segmentation
  async getSegmentation(datasetId: string, useKmeans: boolean = true): Promise<SegmentationResponse> {
    const res = await fetch(`${API_BASE}/analytics/segmentation?dataset_id=${datasetId}&use_kmeans=${useKmeans}`);
    if (!res.ok) throw new Error('Failed to fetch customer segmentation');
    return res.json();
  },

  // Business Insights
  async getInsights(filters: FilterParams): Promise<{ insights: BusinessInsight[]; total_insights: number }> {
    const params = new URLSearchParams();
    if (filters.dataset_id) params.append('dataset_id', filters.dataset_id);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.region && filters.region !== 'All') params.append('region', filters.region);
    if (filters.category && filters.category !== 'All') params.append('category', filters.category);

    const res = await fetch(`${API_BASE}/analytics/insights?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch business insights');
    return res.json();
  },

  // SQL Lab
  async getSqlSamples(): Promise<SampleQuery[]> {
    const res = await fetch(`${API_BASE}/sql-lab/samples`);
    if (!res.ok) throw new Error('Failed to fetch SQL sample queries');
    return res.json();
  },

  async executeSql(query: string): Promise<SQLQueryResponse> {
    const res = await fetch(`${API_BASE}/sql-lab/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) throw new Error('Failed to execute SQL query');
    return res.json();
  },

  // Export URLs
  getFilteredCsvUrl(filters: FilterParams): string {
    const params = new URLSearchParams();
    if (filters.dataset_id) params.append('dataset_id', filters.dataset_id);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.region && filters.region !== 'All') params.append('region', filters.region);
    if (filters.category && filters.category !== 'All') params.append('category', filters.category);
    return `${API_BASE}/export/csv?${params.toString()}`;
  },

  getSegmentationCsvUrl(datasetId: string): string {
    return `${API_BASE}/export/segmentation-csv?dataset_id=${datasetId}`;
  },

  getInsightsCsvUrl(filters: FilterParams): string {
    const params = new URLSearchParams();
    if (filters.dataset_id) params.append('dataset_id', filters.dataset_id);
    return `${API_BASE}/export/insights-csv?${params.toString()}`;
  },

  getPdfReportUrl(filters: FilterParams): string {
    const params = new URLSearchParams();
    if (filters.dataset_id) params.append('dataset_id', filters.dataset_id);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.region && filters.region !== 'All') params.append('region', filters.region);
    if (filters.category && filters.category !== 'All') params.append('category', filters.category);
    return `${API_BASE}/export/pdf?${params.toString()}`;
  }
};
