import React, { useState, useEffect } from 'react';
import {
  Database, RefreshCw, Trash2, CheckCircle2, AlertTriangle,
  UploadCloud, FileText, ArrowRight, Layers
} from 'lucide-react';
import { api } from '../services/api';
import { DatasetInfo } from '../types';
import { LoadingSpinner, ErrorAlert } from '../components/StatusStates';

interface DatasetsPageProps {
  currentDatasetId: string;
  onSelectDataset: (id: string) => void;
}

const getDomainBadge = (id: string, isSample: boolean) => {
  switch (id) {
    case 'sample_superstore':
      return { label: 'Retail & Wholesale', style: 'bg-blue-50 text-blue-700 border-blue-200' };
    case 'sales_revenue_analytics':
      return { label: 'B2B Enterprise', style: 'bg-purple-50 text-purple-700 border-purple-200' };
    case 'customer_analytics':
      return { label: 'Customer Loyalty', style: 'bg-teal-50 text-teal-700 border-teal-200' };
    case 'ecommerce_analytics':
      return { label: 'D2C E-Commerce', style: 'bg-amber-50 text-amber-700 border-amber-200' };
    case 'hr_analytics':
      return { label: 'Workforce & HR', style: 'bg-rose-50 text-rose-700 border-rose-200' };
    default:
      return isSample
        ? { label: 'Benchmark', style: 'bg-slate-100 text-slate-700 border-slate-200' }
        : { label: 'User Upload', style: 'bg-emerald-50 text-emerald-700 border-emerald-200' };
  }
};

export const DatasetsPage: React.FC<DatasetsPageProps> = ({
  currentDatasetId,
  onSelectDataset,
}) => {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actionNotice, setActionNotice] = useState<string | null>(null);
  const [resetting, setResetting] = useState<boolean>(false);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await api.getDatasets();
      setDatasets(list);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch registered datasets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  const handleResetSample = async () => {
    if (!window.confirm('Resetting benchmark datasets will re-seed all 5 pristine domain datasets (16,000+ total records: Retail, B2B, Customer, E-Commerce, and HR). Proceed?')) {
      return;
    }
    try {
      setResetting(true);
      const res = await api.resetSampleDataset();
      setActionNotice(res.message);
      onSelectDataset(res.dataset_id);
      await loadDatasets();
    } catch (err: any) {
      setError('Failed to reset sample dataset: ' + err.message);
    } finally {
      setResetting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm(`Are you sure you want to delete dataset '${id}' and its transactions? This action cannot be undone.`)) {
      return;
    }
    try {
      const res = await api.deleteDataset(id);
      setActionNotice(res.message);
      if (currentDatasetId === id) {
        onSelectDataset('sample_superstore');
      }
      await loadDatasets();
    } catch (err: any) {
      setError(err.message || 'Failed to delete dataset');
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Dataset Management</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Switch active datasets, inspect relational metadata, or restore pristine benchmark sample data.
          </p>
        </div>

        <button
          onClick={handleResetSample}
          disabled={resetting}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${resetting ? 'animate-spin text-blue-600' : ''}`} />
          <span>Restore Pristine Sample Data</span>
        </button>
      </div>

      {actionNotice && (
        <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{actionNotice}</span>
          </div>
          <button onClick={() => setActionNotice(null)} className="text-emerald-700 font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {error && <ErrorAlert title="Dataset Error" message={error} onRetry={loadDatasets} />}
      {loading && <LoadingSpinner message="Querying dataset catalog and relational table schemas..." />}

      {/* Datasets Grid */}
      {!loading && (
        <div className="space-y-4">
          {datasets.map((d) => {
            const isActive = d.id === currentDatasetId;
            return (
              <div
                key={d.id}
                className={`bg-white rounded-xl border p-5 shadow-sm transition-all flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 ${
                  isActive ? 'border-blue-500 ring-2 ring-blue-500/20' : 'border-slate-200/80 hover:border-slate-300'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-sm font-bold text-slate-900">{d.name}</h3>
                    {(() => {
                      const badge = getDomainBadge(d.id, d.is_sample);
                      return (
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-semibold border ${badge.style}`}>
                          {badge.label}
                        </span>
                      );
                    })()}
                    {d.is_sample && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                        Benchmark
                      </span>
                    )}
                    {isActive && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">
                        Active Scope
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-500 max-w-xl leading-relaxed">{d.description || 'No description provided.'}</p>

                  <div className="flex items-center gap-4 text-[11px] text-slate-400 font-mono pt-1">
                    <span>ID: {d.id}</span>
                    <span>• {d.row_count.toLocaleString()} records</span>
                    <span>• {d.column_count} fields</span>
                    <span>• Created: {d.created_at}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2.5 self-end sm:self-center">
                  {!isActive ? (
                    <button
                      onClick={() => onSelectDataset(d.id)}
                      className="px-3.5 py-1.5 text-xs font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors"
                    >
                      Set as Active
                    </button>
                  ) : (
                    <span className="px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 rounded-lg flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Active
                    </span>
                  )}

                  {!d.is_sample && (
                    <button
                      onClick={() => handleDelete(d.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                      title="Delete dataset"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
