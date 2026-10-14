import React, { useState, useEffect } from 'react';
import {
  DollarSign, TrendingUp, ShoppingBag, Users, Percent, CreditCard,
  ArrowUpRight, AlertTriangle, Lightbulb, Search, ChevronLeft, ChevronRight,
  Download, Eye
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip,
  CartesianGrid, BarChart, Bar, Legend, PieChart, Pie, Cell
} from 'recharts';
import { api } from '../services/api';
import { DashboardData, FilterParams } from '../types';
import { MetricCard } from '../components/MetricCard';
import { FilterBar } from '../components/FilterBar';
import { LoadingSpinner, ErrorAlert } from '../components/StatusStates';

const CATEGORY_COLORS = ['#2563eb', '#0d9488', '#f59e0b', '#8b5cf6'];
const REGION_COLORS = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#6366f1'];

interface OverviewDashboardProps {
  datasetId: string;
}

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({ datasetId }) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [filters, setFilters] = useState<FilterParams>({
    dataset_id: datasetId,
    region: 'All',
    category: 'All',
    segment: 'All',
  });

  const [orderSearch, setOrderSearch] = useState<string>('');
  const [orderPage, setOrderPage] = useState<number>(1);
  const ordersPerPage = 8;

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getDashboard({ ...filters, dataset_id: datasetId });
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load executive dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setFilters((prev) => ({ ...prev, dataset_id: datasetId }));
  }, [datasetId]);

  useEffect(() => {
    loadDashboard();
  }, [filters, datasetId]);

  const handleFilterChange = (updated: Partial<FilterParams>) => {
    setFilters((prev) => ({ ...prev, ...updated }));
    setOrderPage(1);
  };

  const handleResetFilters = () => {
    setFilters({
      dataset_id: datasetId,
      region: 'All',
      category: 'All',
      segment: 'All',
      start_date: undefined,
      end_date: undefined,
    });
    setOrderSearch('');
    setOrderPage(1);
  };

  if (loading && !data) {
    return <LoadingSpinner message="Calculating dashboard financial metrics and aggregations..." />;
  }

  if (error && !data) {
    return <ErrorAlert title="Dashboard Error" message={error} onRetry={loadDashboard} />;
  }

  if (!data) return null;

  const { kpis, category_sales, regional_sales, trend_data, top_products, bottom_products, recent_orders, filter_options } = data;

  // Filter recent orders by search
  const filteredOrders = recent_orders.filter((ord) => {
    const q = orderSearch.toLowerCase();
    return (
      ord.order_id.toLowerCase().includes(q) ||
      (ord.customer_name && ord.customer_name.toLowerCase().includes(q)) ||
      (ord.product_name && ord.product_name.toLowerCase().includes(q)) ||
      (ord.category && ord.category.toLowerCase().includes(q))
    );
  });

  const totalPages = Math.ceil(filteredOrders.length / ordersPerPage) || 1;
  const paginatedOrders = filteredOrders.slice((orderPage - 1) * ordersPerPage, orderPage * ordersPerPage);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Executive BI Dashboard</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Certified financial performance, unit economics, and transactional KPIs for <span className="font-semibold text-slate-700">{datasetId}</span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={api.getFilteredCsvUrl(filters)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50 transition-colors"
            download
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export View CSV</span>
          </a>
        </div>
      </div>

      {/* Global Interactive Filters */}
      <FilterBar
        filters={filters}
        options={filter_options}
        onChange={handleFilterChange}
        onReset={handleResetFilters}
      />

      {/* 6 Executive KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCard
          title="Total Revenue"
          value={`$${kpis.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon={DollarSign}
          growthPct={kpis.revenue_growth_pct}
          hasBaseline={kpis.has_comparison_baseline}
          subtitle="Gross sales turnover"
          formulaNote="Sum of all net line item sales: quantity * price * (1 - discount)"
          iconColor="text-blue-600"
          bgColor="bg-blue-50"
        />

        <MetricCard
          title="Total Profit"
          value={`$${kpis.total_profit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon={TrendingUp}
          growthPct={kpis.profit_growth_pct}
          hasBaseline={kpis.has_comparison_baseline}
          subtitle="Net operating earnings"
          formulaNote="Revenue - Cost of Goods Sold - Freight/Shipping"
          iconColor="text-emerald-600"
          bgColor="bg-emerald-50"
        />

        <MetricCard
          title="Profit Margin"
          value={`${kpis.profit_margin_pct.toFixed(2)}%`}
          icon={Percent}
          subtitle="Return on sales"
          formulaNote="Total Profit / Total Revenue * 100"
          iconColor="text-indigo-600"
          bgColor="bg-indigo-50"
        />

        <MetricCard
          title="Total Orders"
          value={kpis.total_orders.toLocaleString()}
          icon={ShoppingBag}
          subtitle="Distinct orders"
          formulaNote="Count of distinct completed order identifiers"
          iconColor="text-amber-600"
          bgColor="bg-amber-50"
        />

        <MetricCard
          title="Average Order Value"
          value={`$${kpis.average_order_value.toFixed(2)}`}
          icon={CreditCard}
          subtitle="AOV per basket"
          formulaNote="Total Revenue / Total Distinct Orders"
          iconColor="text-cyan-600"
          bgColor="bg-cyan-50"
        />

        <MetricCard
          title="Customers"
          value={kpis.total_customers.toLocaleString()}
          icon={Users}
          subtitle="Unique buyers"
          formulaNote="Count of unique customer identifiers in active scope"
          iconColor="text-purple-600"
          bgColor="bg-purple-50"
        />
      </div>

      {/* Primary Visualizations Row: Trend & Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue & Profit Trends (2 Columns) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Revenue & Profit Trajectory</h3>
              <p className="text-xs text-slate-500">Monthly chronological sales volume and operating margins</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 font-medium text-slate-600">
                <span className="w-3 h-3 rounded-sm bg-blue-600 inline-block"></span> Revenue
              </span>
              <span className="flex items-center gap-1.5 font-medium text-slate-600">
                <span className="w-3 h-3 rounded-sm bg-emerald-500 inline-block"></span> Profit
              </span>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend_data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="colorProf" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="period" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, '']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#2563eb" strokeWidth={2.5} fillOpacity={1} fill="url(#colorRev)" name="Revenue" />
                <Area type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorProf)" name="Profit" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sales by Category (1 Column) */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Sales by Category</h3>
                <p className="text-xs text-slate-500">Revenue contribution & category margin</p>
              </div>
            </div>

            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={category_sales}
                    dataKey="revenue"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={68}
                    paddingAngle={4}
                  >
                    {category_sales.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={CATEGORY_COLORS[idx % CATEGORY_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Revenue']}
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100">
            {category_sales.map((c, idx) => (
              <div key={c.category} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: CATEGORY_COLORS[idx % CATEGORY_COLORS.length] }}
                  />
                  <span className="font-medium text-slate-700">{c.category}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-slate-500">{c.share_pct}% share</span>
                  <span className="font-semibold text-slate-900">${(c.revenue / 1000).toFixed(1)}k</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Secondary Visualizations: Regional Distribution & Top Products */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Regional Performance Bar Chart */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Regional Performance</h3>
              <p className="text-xs text-slate-500">Sales volume and net profit across territories</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={regional_sales} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="region" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, '']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Revenue" />
                <Bar dataKey="profit" fill="#10b981" radius={[4, 4, 0, 0]} name="Profit" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Performing Products */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Top Performing Products</h3>
                <p className="text-xs text-slate-500">Ranked by gross sales volume and profit margin</p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500">
                    <th className="pb-2 font-medium">Product</th>
                    <th className="pb-2 font-medium">Category</th>
                    <th className="pb-2 font-medium text-right">Revenue</th>
                    <th className="pb-2 font-medium text-right">Profit Margin</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {top_products.slice(0, 5).map((p, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="py-2.5 font-medium text-slate-800 truncate max-w-[180px]" title={p.product_name}>
                        {p.product_name}
                      </td>
                      <td className="py-2.5 text-slate-500">{p.category}</td>
                      <td className="py-2.5 text-right font-semibold text-slate-900">${p.revenue.toLocaleString()}</td>
                      <td className="py-2.5 text-right">
                        <span className={`inline-flex px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                          p.profit_margin >= 25 ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {p.profit_margin.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Margin Drag Warning */}
          {bottom_products.length > 0 && bottom_products[0].profit_margin < 10 && (
            <div className="mt-3 p-2.5 rounded-lg bg-amber-50 border border-amber-200 flex items-start gap-2 text-xs text-amber-800">
              <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold">Margin Drag Alert:</span> '{bottom_products[0].product_name}' yields only {bottom_products[0].profit_margin}% margin. Inspect in Sales Analytics.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Transactional Records Table with Search and Pagination */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Recent Transaction Records</h3>
            <p className="text-xs text-slate-500">Live order lines with line-item discounts and net profit</p>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search order ID, product, or customer..."
              value={orderSearch}
              onChange={(e) => {
                setOrderSearch(e.target.value);
                setOrderPage(1);
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
                <th className="py-2.5 px-3 font-semibold">Region</th>
                <th className="py-2.5 px-3 font-semibold">Product</th>
                <th className="py-2.5 px-3 font-semibold text-center">Qty</th>
                <th className="py-2.5 px-3 font-semibold text-right">Discount</th>
                <th className="py-2.5 px-3 font-semibold text-right">Revenue</th>
                <th className="py-2.5 px-3 font-semibold text-right">Profit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedOrders.length > 0 ? (
                paginatedOrders.map((ord) => (
                  <tr key={ord.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-mono text-blue-600 font-medium">{ord.order_id}</td>
                    <td className="py-2.5 px-3 text-slate-600">{ord.order_date}</td>
                    <td className="py-2.5 px-3 text-slate-800 font-medium">{ord.customer_name || 'N/A'}</td>
                    <td className="py-2.5 px-3 text-slate-600">{ord.region || 'National'}</td>
                    <td className="py-2.5 px-3 text-slate-700 max-w-[200px] truncate" title={ord.product_name}>
                      {ord.product_name}
                    </td>
                    <td className="py-2.5 px-3 text-center text-slate-700">{ord.quantity}</td>
                    <td className="py-2.5 px-3 text-right text-slate-600">{(ord.discount * 100).toFixed(0)}%</td>
                    <td className="py-2.5 px-3 text-right font-semibold text-slate-900">${ord.revenue.toFixed(2)}</td>
                    <td className={`py-2.5 px-3 text-right font-semibold ${ord.profit >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      ${ord.profit.toFixed(2)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-400">
                    No order records match the active filter criteria or search query.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="flex items-center justify-between pt-3 mt-2 border-t border-slate-100 text-xs text-slate-500">
          <div>
            Showing {(orderPage - 1) * ordersPerPage + 1} to {Math.min(orderPage * ordersPerPage, filteredOrders.length)} of {filteredOrders.length} orders
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setOrderPage((p) => Math.max(1, p - 1))}
              disabled={orderPage === 1}
              className="p-1 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 font-medium text-slate-700">
              {orderPage} / {totalPages}
            </span>
            <button
              onClick={() => setOrderPage((p) => Math.min(totalPages, p + 1))}
              disabled={orderPage === totalPages}
              className="p-1 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
