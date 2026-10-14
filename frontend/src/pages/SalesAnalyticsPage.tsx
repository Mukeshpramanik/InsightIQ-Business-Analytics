import React, { useState, useEffect } from 'react';
import {
  TrendingUp, ArrowUpRight, ArrowDownRight, AlertTriangle,
  Download, Search, ChevronLeft, ChevronRight, Filter, DollarSign
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, Legend
} from 'recharts';
import { api } from '../services/api';
import { FilterParams } from '../types';
import { FilterBar } from '../components/FilterBar';
import { LoadingSpinner, ErrorAlert } from '../components/StatusStates';

interface SalesAnalyticsPageProps {
  datasetId: string;
}

export const SalesAnalyticsPage: React.FC<SalesAnalyticsPageProps> = ({ datasetId }) => {
  const [data, setData] = useState<any>(null);
  const [filterOptions, setFilterOptions] = useState<any>({ regions: ['All'], categories: ['All'], segments: ['All'] });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [filters, setFilters] = useState<FilterParams>({
    dataset_id: datasetId,
    region: 'All',
    category: 'All',
    segment: 'All',
  });

  const [tableSearch, setTableSearch] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const pageSize = 10;

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [salesRes, fOptions] = await Promise.all([
        api.getSalesPerformance({ ...filters, dataset_id: datasetId }),
        api.getFilterOptions(datasetId),
      ]);
      setData(salesRes);
      setFilterOptions(fOptions);
    } catch (err: any) {
      setError(err.message || 'Failed to load sales analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setFilters((prev) => ({ ...prev, dataset_id: datasetId }));
  }, [datasetId]);

  useEffect(() => {
    loadData();
  }, [filters, datasetId]);

  if (loading && !data) {
    return <LoadingSpinner message="Evaluating sales trends, product margins, and growth velocities..." />;
  }

  if (error && !data) {
    return <ErrorAlert title="Sales Analytics Error" message={error} onRetry={loadData} />;
  }

  if (!data) return null;

  const { kpis, monthly_trends, top_products, bottom_products, order_records } = data;

  // Filter order records
  const filteredRecords = (order_records || []).filter((r: any) => {
    const q = tableSearch.toLowerCase();
    return (
      r.order_id?.toLowerCase().includes(q) ||
      r.customer_name?.toLowerCase().includes(q) ||
      r.product_name?.toLowerCase().includes(q) ||
      r.category?.toLowerCase().includes(q)
    );
  });

  const totalPages = Math.ceil(filteredRecords.length / pageSize) || 1;
  const paginatedRecords = filteredRecords.slice((page - 1) * pageSize, page * pageSize);

  // High Revenue / Low Margin Risk Detection
  const marginDragProduct = bottom_products?.find((p: any) => p.profit_margin < 12.0 && p.revenue > 10000);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Sales Performance Analytics</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Growth velocities, Month-over-Month (MoM) trajectories, product margin contribution, and transaction drill-down.
          </p>
        </div>

        <a
          href={api.getFilteredCsvUrl(filters)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50 transition-colors"
          download
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Sales CSV</span>
        </a>
      </div>

      {/* Filter Bar */}
      <FilterBar
        filters={filters}
        options={filterOptions}
        onChange={(upd) => {
          setFilters((prev) => ({ ...prev, ...upd }));
          setPage(1);
        }}
        onReset={() => {
          setFilters({ dataset_id: datasetId, region: 'All', category: 'All', segment: 'All' });
          setTableSearch('');
          setPage(1);
        }}
      />

      {/* Margin Drag Highlight Alert */}
      {marginDragProduct && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3 shadow-sm">
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-xs font-bold text-amber-900">
              High-Revenue Margin Drag Identified: {marginDragProduct.product_name}
            </h4>
            <p className="text-xs text-amber-800 mt-0.5">
              Generates substantial revenue (${marginDragProduct.revenue.toLocaleString()}) but delivers an anemic net margin of only {marginDragProduct.profit_margin.toFixed(1)}%. Consider renegotiating supplier terms or curtailing discounts.
            </p>
          </div>
        </div>
      )}

      {/* MoM Growth Chart & Trajectory */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Month-over-Month (MoM) Growth Dynamic</h3>
              <p className="text-xs text-slate-500">Chronological percentage changes in gross monthly turnover</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthly_trends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="period" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `${val}%`}
                />
                <Tooltip
                  formatter={(val: any) => [`${val}%`, 'MoM Growth']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                />
                <Bar
                  dataKey="mom_growth_pct"
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                  name="MoM Growth %"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Product Ranking: Top & Bottom */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-1">Bottom Products by Net Profit</h3>
            <p className="text-xs text-slate-500 mb-3">Lowest operating margins requiring pricing review</p>

            <div className="space-y-3">
              {(bottom_products || []).slice(0, 5).map((p: any, idx: number) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between text-xs">
                  <div className="truncate max-w-[170px]">
                    <p className="font-semibold text-slate-800 truncate" title={p.product_name}>{p.product_name}</p>
                    <p className="text-[10px] text-slate-400">{p.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-slate-900">${p.revenue.toLocaleString()}</p>
                    <span className="text-[10px] font-bold text-rose-600">{p.profit_margin.toFixed(1)}% margin</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Underlying Transaction Records Drilldown Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Detailed Transaction Drill-Down</h3>
            <p className="text-xs text-slate-500">Inspect line-item unit economics, quantities, and net margins</p>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search orders, customers, products..."
              value={tableSearch}
              onChange={(e) => {
                setTableSearch(e.target.value);
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
                <th className="py-2.5 px-3 font-semibold">Order ID</th>
                <th className="py-2.5 px-3 font-semibold">Date</th>
                <th className="py-2.5 px-3 font-semibold">Customer</th>
                <th className="py-2.5 px-3 font-semibold">Product</th>
                <th className="py-2.5 px-3 font-semibold text-center">Qty</th>
                <th className="py-2.5 px-3 font-semibold text-right">Unit Price</th>
                <th className="py-2.5 px-3 font-semibold text-right">Discount</th>
                <th className="py-2.5 px-3 font-semibold text-right">Revenue</th>
                <th className="py-2.5 px-3 font-semibold text-right">Profit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedRecords.length > 0 ? (
                paginatedRecords.map((r: any) => (
                  <tr key={r.id} className="hover:bg-slate-50/80">
                    <td className="py-2.5 px-3 font-mono font-medium text-blue-600">{r.order_id}</td>
                    <td className="py-2.5 px-3 text-slate-600">{r.order_date}</td>
                    <td className="py-2.5 px-3 text-slate-800 font-medium">{r.customer_name || 'Customer'}</td>
                    <td className="py-2.5 px-3 text-slate-700 max-w-[200px] truncate" title={r.product_name}>{r.product_name}</td>
                    <td className="py-2.5 px-3 text-center text-slate-700">{r.quantity}</td>
                    <td className="py-2.5 px-3 text-right text-slate-700">${r.unit_price.toFixed(2)}</td>
                    <td className="py-2.5 px-3 text-right text-slate-600">{(r.discount * 100).toFixed(0)}%</td>
                    <td className="py-2.5 px-3 text-right font-semibold text-slate-900">${r.revenue.toFixed(2)}</td>
                    <td className={`py-2.5 px-3 text-right font-semibold ${r.profit >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      ${r.profit.toFixed(2)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-400">
                    No orders match your search criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between pt-3 mt-2 border-t border-slate-100 text-xs text-slate-500">
          <div>
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, filteredRecords.length)} of {filteredRecords.length} records
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
