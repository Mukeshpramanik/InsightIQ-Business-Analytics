import React, { useState, useEffect } from 'react';
import {
  BarChart3, Activity, Table, Grid, HelpCircle, Info,
  TrendingUp, PieChart as PieIcon, ArrowRight
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  CartesianGrid, ScatterChart, Scatter, ZAxis, Cell
} from 'recharts';
import { api } from '../services/api';
import { EDAResponse } from '../types';
import { LoadingSpinner, ErrorAlert } from '../components/StatusStates';

interface EdaPageProps {
  datasetId: string;
}

export const EdaPage: React.FC<EdaPageProps> = ({ datasetId }) => {
  const [data, setData] = useState<EDAResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedHistColumn, setSelectedHistColumn] = useState<string>('revenue');
  const [selectedCategoryCol, setSelectedCategoryCol] = useState<string>('category');

  const loadEda = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getEda(datasetId);
      setData(res);
      const histKeys = Object.keys(res.distributions);
      if (histKeys.length > 0 && !histKeys.includes(selectedHistColumn)) {
        setSelectedHistColumn(histKeys[0]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load EDA analysis');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEda();
  }, [datasetId]);

  if (loading && !data) {
    return <LoadingSpinner message="Computing descriptive statistics, IQR outliers, and correlations..." />;
  }

  if (error && !data) {
    return <ErrorAlert title="EDA Analysis Error" message={error} onRetry={loadEda} />;
  }

  if (!data) return null;

  const {
    row_count, column_count, descriptive_statistics,
    distributions, box_plots, category_frequencies,
    correlation_matrix, scatter_data, explanations
  } = data;

  const activeHistogramBins = distributions[selectedHistColumn] || [];
  const activeBoxPlot = box_plots[selectedHistColumn];
  const activeCatFreq = category_frequencies[selectedCategoryCol] || [];
  const corrCols = Object.keys(correlation_matrix);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
          Exploratory Data Analysis (EDA) Workspace
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Detailed distributional metrics, Pearson correlations, Tukey's IQR outlier analysis, and frequency distributions for <span className="font-semibold text-slate-700">{datasetId}</span>.
        </p>
      </div>

      {/* Dataset Dimensions Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Total Observations</span>
          <p className="text-xl font-bold text-slate-900 mt-0.5">{row_count.toLocaleString()} rows</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Schema Features</span>
          <p className="text-xl font-bold text-slate-900 mt-0.5">{column_count} columns</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Numeric Measures</span>
          <p className="text-xl font-bold text-blue-600 mt-0.5">{descriptive_statistics.length} variables</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Categorical Dimensions</span>
          <p className="text-xl font-bold text-emerald-600 mt-0.5">{Object.keys(category_frequencies).length} dimensions</p>
        </div>
      </div>

      {/* Descriptive Statistics Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Parametric & Non-Parametric Summary Statistics</h3>
            <p className="text-xs text-slate-500">Central tendency, dispersion, percentiles, and skewness coefficients</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-y border-slate-200 text-slate-500 uppercase text-[10px] tracking-wider">
                <th className="py-2.5 px-3 font-semibold">Measure</th>
                <th className="py-2.5 px-3 font-semibold text-right">Count</th>
                <th className="py-2.5 px-3 font-semibold text-right">Mean</th>
                <th className="py-2.5 px-3 font-semibold text-right">Std Dev</th>
                <th className="py-2.5 px-3 font-semibold text-right">Min</th>
                <th className="py-2.5 px-3 font-semibold text-right">25% (Q1)</th>
                <th className="py-2.5 px-3 font-semibold text-right">Median</th>
                <th className="py-2.5 px-3 font-semibold text-right">75% (Q3)</th>
                <th className="py-2.5 px-3 font-semibold text-right">Max</th>
                <th className="py-2.5 px-3 font-semibold text-right">Skewness</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {descriptive_statistics.map((s) => (
                <tr key={s.column} className="hover:bg-slate-50 font-mono text-[11px]">
                  <td className="py-2.5 px-3 font-sans font-semibold text-slate-800">{s.column}</td>
                  <td className="py-2.5 px-3 text-right text-slate-600">{s.count}</td>
                  <td className="py-2.5 px-3 text-right text-slate-900 font-medium">{s.mean.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right text-slate-600">{s.std.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right text-slate-600">{s.min.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right text-slate-600">{s.p25.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right text-blue-700 font-bold">{s.median.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right text-slate-600">{s.p75.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right text-slate-900 font-medium">{s.max.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                      Math.abs(s.skewness) > 1 ? 'bg-amber-100 text-amber-800 font-bold' : 'text-slate-600'
                    }`}>
                      {s.skewness > 0 ? `+${s.skewness}` : s.skewness}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Numeric Distributions & Box Plot Outlier Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Distribution Histogram */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Empirical Frequency Distribution</h3>
              <p className="text-xs text-slate-500">10-bin histogram displaying frequency density</p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 font-medium">Variable:</span>
              <select
                value={selectedHistColumn}
                onChange={(e) => setSelectedHistColumn(e.target.value)}
                className="text-xs font-semibold bg-slate-50 border border-slate-300 rounded px-2.5 py-1 text-slate-800 cursor-pointer"
              >
                {Object.keys(distributions).map((k) => (
                  <option key={k} value={k}>{k}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={activeHistogramBins} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="bin_label" stroke="#94a3b8" fontSize={10} angle={-25} textAnchor="end" />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip
                  formatter={(val: any) => [`${val} records`, 'Frequency Count']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} name="Frequency" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {explanations?.distributions && (
            <div className="mt-3 p-3 rounded-lg bg-blue-50/70 border border-blue-100 flex items-start gap-2 text-xs text-blue-900">
              <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
              <p>{explanations.distributions}</p>
            </div>
          )}
        </div>

        {/* Box Plot & Tukey Outliers Breakdown */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-1">Tukey's IQR Outlier Analysis</h3>
            <p className="text-xs text-slate-500 mb-4">Five-number summary & statistical anomaly check</p>

            {activeBoxPlot ? (
              <div className="space-y-2.5 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Minimum:</span>
                  <span className="font-mono font-semibold text-slate-800">{activeBoxPlot.min_val}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Q1 (25th Percentile):</span>
                  <span className="font-mono font-semibold text-slate-800">{activeBoxPlot.q1}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Median (50th):</span>
                  <span className="font-mono font-bold text-blue-600">{activeBoxPlot.median}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Q3 (75th Percentile):</span>
                  <span className="font-mono font-semibold text-slate-800">{activeBoxPlot.q3}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Maximum:</span>
                  <span className="font-mono font-semibold text-slate-800">{activeBoxPlot.max_val}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Interquartile Range (IQR):</span>
                  <span className="font-mono font-bold text-slate-900">{activeBoxPlot.iqr}</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-500">Outliers Beyond Fences:</span>
                  <span className="font-mono font-bold text-amber-600">{activeBoxPlot.outlier_count}</span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400">Select a variable to view box plot statistics.</p>
            )}
          </div>

          <div className="mt-4 p-3 rounded-lg bg-slate-50 border border-slate-200 text-[11px] text-slate-600 leading-relaxed">
            <span className="font-semibold text-slate-800">Analytical Distinction: </span>
            Tukey's IQR outliers flagged in upper fences represent high-value bulk purchases rather than corrupt data entries.
          </div>
        </div>
      </div>

      {/* Correlation Matrix & Bivariate Scatter Plot */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pearson Correlation Heatmap */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Pearson Correlation Matrix</h3>
              <p className="text-xs text-slate-500">Linear co-movement coefficients between numeric variables (-1 to +1)</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-sans">
                  <th className="p-2 text-left">Measure</th>
                  {corrCols.map((c) => (
                    <th key={c} className="p-2 truncate max-w-[80px]" title={c}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {corrCols.map((rowCol) => (
                  <tr key={rowCol}>
                    <td className="p-2 text-left font-sans font-medium text-slate-800">{rowCol}</td>
                    {corrCols.map((colCol) => {
                      const val = correlation_matrix[rowCol]?.[colCol] ?? 0;
                      // Heatmap color logic
                      let bg = 'bg-slate-50 text-slate-600';
                      if (val >= 0.7) bg = 'bg-blue-600 text-white font-bold';
                      else if (val >= 0.4) bg = 'bg-blue-200 text-blue-900 font-semibold';
                      else if (val > 0) bg = 'bg-blue-50 text-blue-800';
                      else if (val <= -0.4) bg = 'bg-rose-200 text-rose-900 font-semibold';
                      else if (val < 0) bg = 'bg-rose-50 text-rose-800';

                      return (
                        <td key={colCol} className="p-2">
                          <span className={`inline-block w-12 py-1 rounded text-[11px] ${bg}`}>
                            {val.toFixed(2)}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Bivariate Scatter Plot: Revenue vs Profit */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Bivariate Dispersion: Revenue vs Profit</h3>
              <p className="text-xs text-slate-500">Linear relationship and margin dispersion across individual sales</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" dataKey="x" name="Revenue" stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `$${v}`} />
                <YAxis type="number" dataKey="y" name="Profit" stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `$${v}`} />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ payload }) => {
                    if (!payload || payload.length === 0) return null;
                    const d = payload[0].payload;
                    return (
                      <div className="p-2.5 bg-slate-900 text-white text-xs rounded-lg shadow-lg">
                        <p className="font-bold text-blue-300">{d.product}</p>
                        <p className="text-slate-400 text-[11px]">{d.category}</p>
                        <div className="mt-1 pt-1 border-t border-slate-800 flex justify-between gap-4">
                          <span>Revenue: ${d.x}</span>
                          <span className={d.y >= 0 ? 'text-emerald-400' : 'text-rose-400'}>Profit: ${d.y}</span>
                        </div>
                      </div>
                    );
                  }}
                />
                <Scatter name="Transactions" data={scatter_data} fill="#2563eb" opacity={0.65} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
