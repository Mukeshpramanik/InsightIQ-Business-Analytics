import React, { useState, useEffect } from 'react';
import {
  LineChart as LineChartIcon, Play, Download, AlertCircle, Info,
  TrendingUp, Activity, CheckCircle2, ShieldAlert
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, Legend
} from 'recharts';
import { api } from '../services/api';
import { ForecastResponse } from '../types';
import { LoadingSpinner, ErrorAlert } from '../components/StatusStates';

interface ForecastingPageProps {
  datasetId: string;
}

export const ForecastingPage: React.FC<ForecastingPageProps> = ({ datasetId }) => {
  const [targetMetric, setTargetMetric] = useState<string>('revenue');
  const [granularity, setGranularity] = useState<string>('M'); // 'D' or 'M'
  const [horizon, setHorizon] = useState<number>(6);
  const [modelType, setModelType] = useState<string>('ridge');

  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const runForecast = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.runForecast({
        dataset_id: datasetId,
        target_metric: targetMetric,
        granularity: granularity,
        horizon: horizon,
        model_type: modelType,
      });
      setForecastData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate predictive forecast');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runForecast();
  }, [datasetId]);

  // Combine historical and forecast for seamless visualization
  const combinedChartData = forecastData
    ? [
        ...forecastData.historical_points.map((p) => ({
          date: p.date,
          actual: p.actual,
          predicted: null,
          lower_bound: null,
          upper_bound: null,
        })),
        ...forecastData.forecast_points.map((p) => ({
          date: p.date,
          actual: null,
          predicted: p.predicted,
          lower_bound: p.lower_bound,
          upper_bound: p.upper_bound,
        })),
      ]
    : [];

  const handleDownloadCsv = () => {
    if (!forecastData) return;
    const rows = [
      ['Date', 'Predicted Value', 'Lower 95% Bound', 'Upper 95% Bound'],
      ...forecastData.forecast_points.map((p) => [p.date, p.predicted, p.lower_bound, p.upper_bound]),
    ];
    const csvContent = 'data:text/csv;charset=utf-8,' + rows.map((e) => e.join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `forecast_${targetMetric}_${datasetId}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Predictive Analytics & Sales Forecasting
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Machine learning projections with strict time-ordered out-of-sample evaluation and 95% confidence intervals.
          </p>
        </div>

        {forecastData && (
          <button
            onClick={handleDownloadCsv}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Forecast CSV</span>
          </button>
        )}
      </div>

      {/* Model Controls Bar */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 items-end text-xs">
          <div>
            <label className="block font-medium text-slate-600 mb-1">Target Metric:</label>
            <select
              value={targetMetric}
              onChange={(e) => setTargetMetric(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-slate-800 cursor-pointer"
            >
              <option value="revenue">Gross Sales Revenue ($)</option>
              <option value="orders">Distinct Order Volume</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-slate-600 mb-1">Time Granularity:</label>
            <select
              value={granularity}
              onChange={(e) => {
                const g = e.target.value;
                setGranularity(g);
                setHorizon(g === 'D' ? 30 : 6);
              }}
              className="w-full bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-slate-800 cursor-pointer"
            >
              <option value="M">Monthly ('MS')</option>
              <option value="D">Daily ('D')</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-slate-600 mb-1">Forecast Horizon:</label>
            <select
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-slate-800 cursor-pointer"
            >
              {granularity === 'M' ? (
                <>
                  <option value={3}>3 Months Ahead</option>
                  <option value={6}>6 Months Ahead</option>
                  <option value={12}>12 Months Ahead</option>
                </>
              ) : (
                <>
                  <option value={7}>7 Days Ahead</option>
                  <option value={14}>14 Days Ahead</option>
                  <option value={30}>30 Days Ahead</option>
                  <option value={60}>60 Days Ahead</option>
                </>
              )}
            </select>
          </div>

          <div>
            <label className="block font-medium text-slate-600 mb-1">Forecasting Model:</label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-slate-800 cursor-pointer"
            >
              <option value="ridge">Scikit-Learn Ridge (Autoregressive)</option>
              <option value="baseline">Exponential Smoothing (EWMA)</option>
            </select>
          </div>

          <div>
            <button
              onClick={runForecast}
              disabled={loading}
              className="w-full flex items-center justify-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-md shadow-sm transition-colors disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Run Model</span>
            </button>
          </div>
        </div>
      </div>

      {loading && <LoadingSpinner message="Fitting autoregressive features and computing out-of-sample error metrics..." />}
      {error && <ErrorAlert title="Forecast Notice" message={error} onRetry={runForecast} />}

      {forecastData && (
        <div className="space-y-6">
          {/* Out-of-Sample Performance Validation Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
              <span className="text-xs font-medium text-slate-500">Mean Absolute Error (MAE)</span>
              <p className="text-xl font-bold text-slate-900 mt-1 font-mono">
                {forecastData.metrics.mae !== null ? `$${forecastData.metrics.mae?.toLocaleString()}` : 'N/A'}
              </p>
              <span className="text-[10px] text-slate-400">Average magnitude of error</span>
            </div>

            <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
              <span className="text-xs font-medium text-slate-500">Root Mean Squared Error (RMSE)</span>
              <p className="text-xl font-bold text-slate-900 mt-1 font-mono">
                {forecastData.metrics.rmse !== null ? `$${forecastData.metrics.rmse?.toLocaleString()}` : 'N/A'}
              </p>
              <span className="text-[10px] text-slate-400">Penalizes large deviations</span>
            </div>

            <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
              <span className="text-xs font-medium text-slate-500">Safe MAPE %</span>
              <p className="text-xl font-bold text-blue-600 mt-1 font-mono">
                {forecastData.metrics.mape !== null ? `${forecastData.metrics.mape}%` : 'N/A'}
              </p>
              <span className="text-[10px] text-slate-400">Zero-actual handled safely</span>
            </div>

            <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
              <span className="text-xs font-medium text-slate-500">Out-of-Sample Test Size</span>
              <p className="text-xl font-bold text-slate-900 mt-1 font-mono">
                {forecastData.metrics.test_size_points} periods
              </p>
              <span className="text-[10px] text-slate-400">20% chronological split</span>
            </div>
          </div>

          {/* Forecasting Chart with Confidence Interval Band */}
          <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Historical Trajectory vs Forward Projection ({forecastData.model_info.name})
                </h3>
                <p className="text-xs text-slate-500">
                  Solid blue indicates actual historical data; dashed amber line indicates predicted forward values with 95% confidence interval shaded.
                </p>
              </div>

              <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-0.5 bg-blue-600 inline-block"></span> Actual
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-0.5 bg-amber-500 inline-block border-t border-dashed"></span> Projected
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 bg-amber-100 rounded inline-block"></span> 95% Band
                </span>
              </div>
            </div>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={combinedChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="forecastBand" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.05} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                    tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                    formatter={(val: any, name: any) => [
                      val !== null ? `$${Number(val).toLocaleString()}` : 'N/A',
                      name === 'actual' ? 'Historical Actual' : name === 'predicted' ? 'Model Predicted' : name,
                    ]}
                  />
                  {/* Upper and lower bound shaded band */}
                  <Area type="monotone" dataKey="upper_bound" stroke="transparent" fill="url(#forecastBand)" />
                  <Area type="monotone" dataKey="lower_bound" stroke="transparent" fill="#ffffff" />
                  {/* Historical actual line */}
                  <Line type="monotone" dataKey="actual" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 3 }} name="actual" />
                  {/* Predicted line */}
                  <Line type="monotone" dataKey="predicted" stroke="#f59e0b" strokeWidth={2.5} strokeDasharray="5 5" dot={{ r: 4 }} name="predicted" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Model Methodology and Limitations Callout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200/80 text-xs">
              <div className="flex items-center gap-2 font-bold text-blue-900 mb-1">
                <CheckCircle2 className="w-4 h-4 text-blue-600" />
                <span>Zero Data Leakage Guarantee</span>
              </div>
              <p className="text-blue-800 leading-relaxed">{forecastData.methodology_explanation}</p>
            </div>

            <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200/80 text-xs">
              <div className="flex items-center gap-2 font-bold text-amber-900 mb-1">
                <ShieldAlert className="w-4 h-4 text-amber-600" />
                <span>Model Scope & Limitations</span>
              </div>
              <p className="text-amber-800 leading-relaxed">{forecastData.limitations}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
