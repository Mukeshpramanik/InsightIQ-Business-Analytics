import React from 'react';
import { Menu, RefreshCw, FileText, Activity, Database, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

interface NavbarProps {
  onToggleSidebar: () => void;
  datasetId: string;
  datasets: Array<{ id: string; name: string }>;
  onSelectDataset: (id: string) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onToggleSidebar,
  datasetId,
  datasets,
  onSelectDataset,
  onRefresh,
  isRefreshing,
}) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-20 flex items-center justify-between px-4 sm:px-6 shadow-sm">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 lg:hidden focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-slate-400 hidden sm:inline" />
          <span className="text-xs font-medium text-slate-500 hidden sm:inline">Active Dataset:</span>
          <select
            value={datasetId}
            onChange={(e) => onSelectDataset(e.target.value)}
            className="text-xs font-semibold text-slate-800 bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 hover:border-slate-400 transition-colors cursor-pointer max-w-[220px] sm:max-w-[320px] md:max-w-[400px] truncate"
          >
            {datasets.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {/* Live System Indicator */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          <span>Engine Online</span>
        </div>

        {/* Quick Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors disabled:opacity-50"
          title="Refresh calculations and metrics"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-blue-600' : ''}`} />
          <span className="hidden sm:inline">Refresh Data</span>
        </button>

        {/* PDF Quick Export Shortcut */}
        <a
          href={api.getPdfReportUrl({ dataset_id: datasetId })}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors shadow-sm shadow-blue-500/20"
          title="Download certified executive PDF report"
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Executive PDF</span>
        </a>
      </div>
    </header>
  );
};
