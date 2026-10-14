import React, { useState, useEffect } from 'react';
import {
  Lightbulb, TrendingUp, AlertTriangle, ShieldCheck, Target,
  Download, Filter, CheckCircle2, ArrowRight, Zap, RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { BusinessInsight, FilterParams } from '../types';
import { LoadingSpinner, ErrorAlert, EmptyState } from '../components/StatusStates';

interface InsightsPageProps {
  datasetId: string;
}

export const InsightsPage: React.FC<InsightsPageProps> = ({ datasetId }) => {
  const [insights, setInsights] = useState<BusinessInsight[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>('all');

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getInsights({ dataset_id: datasetId });
      setInsights(res.insights);
    } catch (err: any) {
      setError(err.message || 'Failed to generate business insights');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInsights();
  }, [datasetId]);

  const filteredInsights = typeFilter === 'all'
    ? insights
    : insights.filter((i) => i.type === typeFilter);

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'success':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'warning':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'critical':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'growth':
        return <TrendingUp className="w-4 h-4 text-emerald-600" />;
      case 'risk':
        return <AlertTriangle className="w-4 h-4 text-amber-600" />;
      case 'opportunity':
        return <Target className="w-4 h-4 text-blue-600" />;
      default:
        return <Zap className="w-4 h-4 text-purple-600" />;
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Automated Business & Analytical Insights
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Deterministic business findings derived from live margins, customer concentration, and transaction variance for <span className="font-semibold text-slate-700">{datasetId}</span>.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <a
            href={api.getInsightsCsvUrl({ dataset_id: datasetId })}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50 transition-colors"
            download
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Insights CSV</span>
          </a>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 bg-slate-100 rounded-xl max-w-md">
        {['all', 'growth', 'risk', 'opportunity', 'concentration'].map((t) => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
              typeFilter === t
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {loading && <LoadingSpinner message="Evaluating analytical rule engine against active transactions..." />}
      {error && <ErrorAlert title="Insights Notice" message={error} onRetry={loadInsights} />}

      {/* Insights Cards Grid */}
      {!loading && !error && (
        <div className="space-y-4">
          {filteredInsights.length > 0 ? (
            filteredInsights.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-slate-100">
                      {getTypeIcon(item.type)}
                    </div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                      {item.type} Analysis
                    </span>
                  </div>

                  <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${getSeverityBadge(item.severity)}`}>
                    {item.severity.toUpperCase()}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 mb-1">{item.headline}</h3>

                {/* Supporting Metric Pill */}
                <div className="inline-block mt-1 mb-3 px-2.5 py-1 rounded bg-slate-100 text-xs font-mono font-semibold text-slate-800">
                  Metric: {item.supporting_metric}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-3 border-t border-slate-100 text-xs">
                  <div>
                    <span className="font-semibold text-slate-700 block mb-0.5">Calculation Basis:</span>
                    <p className="text-slate-500 leading-relaxed">{item.calculation_basis}</p>
                  </div>

                  <div>
                    <span className="font-semibold text-slate-700 block mb-0.5">Business Interpretation:</span>
                    <p className="text-slate-600 leading-relaxed">{item.interpretation}</p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-blue-50/60 border border-blue-100">
                    <span className="font-bold text-blue-900 block mb-0.5 flex items-center gap-1">
                      <ArrowRight className="w-3 h-3 text-blue-600" /> Actionable Recommendation:
                    </span>
                    <p className="text-blue-800 leading-relaxed font-medium">{item.recommendation}</p>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <EmptyState
              title="No Insights for this Category"
              description="No automated business findings triggered for the selected filter threshold."
              actionText="View All Findings"
              onAction={() => setTypeFilter('all')}
            />
          )}
        </div>
      )}
    </div>
  );
};
