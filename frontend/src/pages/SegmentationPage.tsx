import React, { useState, useEffect } from 'react';
import {
  Users, Crown, HeartHandshake, AlertCircle, Download,
  Search, ChevronLeft, ChevronRight, Sparkles, Sliders, Info, ShieldCheck
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  CartesianGrid, PieChart, Pie, Cell, Legend
} from 'recharts';
import { api } from '../services/api';
import { SegmentationResponse } from '../types';
import { LoadingSpinner, ErrorAlert } from '../components/StatusStates';

const SEGMENT_COLORS: Record<string, string> = {
  'Champions': '#10b981',
  'Loyal Customers': '#3b82f6',
  'Potential Loyalists': '#06b6d4',
  'At-Risk Customers': '#f59e0b',
  'Promising & New': '#8b5cf6',
  'Hibernating & Inactive': '#64748b',
};

interface SegmentationPageProps {
  datasetId: string;
}

export const SegmentationPage: React.FC<SegmentationPageProps> = ({ datasetId }) => {
  const [data, setData] = useState<SegmentationResponse | null>(null);
  const [useKmeans, setUseKmeans] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [customerSearch, setCustomerSearch] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const pageSize = 10;

  const loadSegmentation = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getSegmentation(datasetId, useKmeans);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to calculate customer segmentation');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSegmentation();
  }, [datasetId, useKmeans]);

  if (loading && !data) {
    return <LoadingSpinner message="Calculating Recency, Frequency, Monetary quintiles and customer clusters..." />;
  }

  if (error && !data) {
    return <ErrorAlert title="Segmentation Error" message={error} onRetry={loadSegmentation} />;
  }

  if (!data) return null;

  const { total_customers_analyzed, reference_date, segments_summary, customers_sample, rules_documentation, kmeans_inertia } = data;

  const filteredCustomers = customers_sample.filter((c) => {
    const q = customerSearch.toLowerCase();
    return (
      c.customer_id.toLowerCase().includes(q) ||
      c.customer_name.toLowerCase().includes(q) ||
      c.rfm_segment.toLowerCase().includes(q)
    );
  });

  const totalPages = Math.ceil(filteredCustomers.length / pageSize) || 1;
  const paginatedCustomers = filteredCustomers.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Customer Segmentation & RFM Analytics</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Deterministic Recency, Frequency, Monetary (RFM) quintile classification and K-Means behavioral clustering for <span className="font-semibold text-slate-700">{datasetId}</span>.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 px-3 py-1.5 rounded-lg shadow-sm cursor-pointer hover:bg-slate-50">
            <input
              type="checkbox"
              checked={useKmeans}
              onChange={(e) => setUseKmeans(e.target.checked)}
              className="rounded text-blue-600 focus:ring-blue-500 h-3.5 w-3.5"
            />
            <span>Enable K-Means ML Clustering</span>
          </label>

          <a
            href={api.getSegmentationCsvUrl(datasetId)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50 transition-colors"
            download
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Segments CSV</span>
          </a>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Customers Analyzed</span>
          <p className="text-xl font-bold text-slate-900 mt-0.5">{total_customers_analyzed.toLocaleString()}</p>
          <span className="text-[10px] text-slate-400">Unique accounts</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
          <span className="text-xs font-medium text-slate-500">Benchmark Reference Date</span>
          <p className="text-xl font-bold text-blue-600 mt-0.5 font-mono">{reference_date}</p>
          <span className="text-[10px] text-slate-400">Dataset Max Date + 1 Day</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
          <span className="text-xs font-medium text-slate-500">RFM Quintile Buckets</span>
          <p className="text-xl font-bold text-slate-900 mt-0.5">5 × 5 × 5 Grid</p>
          <span className="text-[10px] text-slate-400">Deterministic scoring (1-5)</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
          <span className="text-xs font-medium text-slate-500">K-Means Cluster Inertia</span>
          <p className="text-xl font-bold text-emerald-600 mt-0.5 font-mono">
            {kmeans_inertia != null ? kmeans_inertia.toLocaleString() : 'Disabled'}
          </p>
          <span className="text-[10px] text-slate-400">Log-standardized feature space</span>
        </div>
      </div>

      {/* Visualizations: Segment Revenue Share & Customer Headcount */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Contribution by Segment */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Revenue Contribution by Customer Segment</h3>
              <p className="text-xs text-slate-500">Cumulative sales dollar volume per behavioral group</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={segments_summary} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="segment_name" stroke="#94a3b8" fontSize={10} angle={-15} textAnchor="end" />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Total Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                />
                <Bar dataKey="total_revenue" radius={[4, 4, 0, 0]}>
                  {segments_summary.map((entry) => (
                    <Cell key={entry.segment_name} fill={SEGMENT_COLORS[entry.segment_name] || '#3b82f6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Customer Headcount Share (Donut) */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-1">Customer Distribution</h3>
            <p className="text-xs text-slate-500 mb-4">Share of total active accounts</p>

            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={segments_summary}
                    dataKey="customer_count"
                    nameKey="segment_name"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={68}
                    paddingAngle={3}
                  >
                    {segments_summary.map((entry) => (
                      <Cell key={entry.segment_name} fill={SEGMENT_COLORS[entry.segment_name] || '#3b82f6'} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: any) => [`${val} customers`, 'Headcount']}
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-100 text-xs">
            {segments_summary.map((s) => (
              <div key={s.segment_name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: SEGMENT_COLORS[s.segment_name] || '#3b82f6' }}
                  />
                  <span className="font-medium text-slate-700">{s.segment_name}</span>
                </div>
                <span className="font-semibold text-slate-900">{s.customer_percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Segment Strategic Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {segments_summary.map((seg) => (
          <div key={seg.segment_name} className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span
                  className="px-2.5 py-0.5 rounded-full text-xs font-bold text-white"
                  style={{ backgroundColor: SEGMENT_COLORS[seg.segment_name] || '#3b82f6' }}
                >
                  {seg.segment_name}
                </span>
                <span className="text-xs font-semibold text-slate-900">${seg.total_revenue.toLocaleString()}</span>
              </div>

              <p className="text-xs text-slate-600 mt-2 leading-relaxed">{seg.description}</p>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                Recommended Strategy:
              </span>
              <p className="text-xs font-medium text-slate-800 leading-snug">{seg.recommended_strategy}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Individual Customer RFM Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Customer RFM Scores & Classification</h3>
            <p className="text-xs text-slate-500">Recency in days, total order frequency, and cumulative spend</p>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search customer name or segment..."
              value={customerSearch}
              onChange={(e) => {
                setCustomerSearch(e.target.value);
                setPage(1);
              }}
              className="text-xs bg-slate-50 border border-slate-300 rounded-lg pl-8 pr-3 py-1.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700 w-full sm:w-64"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-y border-slate-200 text-slate-500 uppercase text-[10px] tracking-wider">
                <th className="py-2.5 px-3 font-semibold">Customer ID</th>
                <th className="py-2.5 px-3 font-semibold">Customer Name</th>
                <th className="py-2.5 px-3 font-semibold text-right">Recency (Days)</th>
                <th className="py-2.5 px-3 font-semibold text-center">Frequency</th>
                <th className="py-2.5 px-3 font-semibold text-right">Monetary Spend</th>
                <th className="py-2.5 px-3 font-semibold text-center">R-F-M Score</th>
                <th className="py-2.5 px-3 font-semibold">Assigned Segment</th>
                {useKmeans && <th className="py-2.5 px-3 font-semibold text-center">ML Cluster</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
              {paginatedCustomers.map((c) => (
                <tr key={c.customer_id} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3 font-bold text-slate-800">{c.customer_id}</td>
                  <td className="py-2.5 px-3 font-sans font-medium text-slate-800">{c.customer_name}</td>
                  <td className="py-2.5 px-3 text-right text-slate-600">{c.recency_days}d ago</td>
                  <td className="py-2.5 px-3 text-center text-slate-700">{c.frequency_orders} orders</td>
                  <td className="py-2.5 px-3 text-right font-bold text-slate-900">${c.monetary_spend.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold text-[10px]">
                      {c.r_score}-{c.f_score}-{c.m_score}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-sans">
                    <span
                      className="px-2 py-0.5 rounded text-[10px] font-bold text-white inline-block"
                      style={{ backgroundColor: SEGMENT_COLORS[c.rfm_segment] || '#3b82f6' }}
                    >
                      {c.rfm_segment}
                    </span>
                  </td>
                  {useKmeans && (
                    <td className="py-2.5 px-3 text-center font-sans">
                      <span className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 text-[10px] font-bold">
                        Cluster #{c.cluster_id ?? 0}
                      </span>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between pt-3 mt-2 border-t border-slate-100 text-xs text-slate-500">
          <div>
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, filteredCustomers.length)} of {filteredCustomers.length} customers
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 font-medium text-slate-700">{page} / {totalPages}</span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
