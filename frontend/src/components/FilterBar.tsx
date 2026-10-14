import React from 'react';
import { Filter, RotateCcw, Calendar, MapPin, Tag, UserCheck } from 'lucide-react';
import { FilterParams } from '../types';

interface FilterBarProps {
  filters: FilterParams;
  options: {
    regions: string[];
    categories: string[];
    segments: string[];
    min_date: string[];
    max_date: string[];
  };
  onChange: (updated: Partial<FilterParams>) => void;
  onReset: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  options,
  onChange,
  onReset,
}) => {
  const isFiltered = !!(
    filters.start_date ||
    filters.end_date ||
    (filters.region && filters.region !== 'All') ||
    (filters.category && filters.category !== 'All') ||
    (filters.segment && filters.segment !== 'All')
  );

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-3.5 shadow-sm mb-6">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-2.5 border-b border-slate-100">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
          <Filter className="w-4 h-4 text-blue-600" />
          <span>Interactive Analytical Filters</span>
          {isFiltered && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-700">
              Active
            </span>
          )}
        </div>

        <button
          onClick={onReset}
          disabled={!isFiltered}
          className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-md transition-colors ${
            isFiltered
              ? 'text-rose-600 bg-rose-50 hover:bg-rose-100 border border-rose-200 cursor-pointer'
              : 'text-slate-400 bg-slate-50 border border-slate-200 cursor-not-allowed opacity-60'
          }`}
          title="Reset all filters to full dataset scope"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset Filters</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 pt-3">
        {/* Start Date */}
        <div>
          <label className="block text-[11px] font-medium text-slate-500 mb-1 flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-400" /> Start Date
          </label>
          <input
            type="date"
            value={filters.start_date || ''}
            onChange={(e) => onChange({ start_date: e.target.value || undefined })}
            className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
          />
        </div>

        {/* End Date */}
        <div>
          <label className="block text-[11px] font-medium text-slate-500 mb-1 flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-400" /> End Date
          </label>
          <input
            type="date"
            value={filters.end_date || ''}
            onChange={(e) => onChange({ end_date: e.target.value || undefined })}
            className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
          />
        </div>

        {/* Region */}
        <div>
          <label className="block text-[11px] font-medium text-slate-500 mb-1 flex items-center gap-1">
            <MapPin className="w-3 h-3 text-slate-400" /> Region
          </label>
          <select
            value={filters.region || 'All'}
            onChange={(e) => onChange({ region: e.target.value })}
            className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700 cursor-pointer"
          >
            {(options.regions || ['All']).map((r) => (
              <option key={r} value={r}>
                {r === 'All' ? 'All Regions' : r}
              </option>
            ))}
          </select>
        </div>

        {/* Category */}
        <div>
          <label className="block text-[11px] font-medium text-slate-500 mb-1 flex items-center gap-1">
            <Tag className="w-3 h-3 text-slate-400" /> Category
          </label>
          <select
            value={filters.category || 'All'}
            onChange={(e) => onChange({ category: e.target.value })}
            className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700 cursor-pointer"
          >
            {(options.categories || ['All']).map((c) => (
              <option key={c} value={c}>
                {c === 'All' ? 'All Categories' : c}
              </option>
            ))}
          </select>
        </div>

        {/* Customer Segment */}
        <div>
          <label className="block text-[11px] font-medium text-slate-500 mb-1 flex items-center gap-1">
            <UserCheck className="w-3 h-3 text-slate-400" /> Customer Segment
          </label>
          <select
            value={filters.segment || 'All'}
            onChange={(e) => onChange({ segment: e.target.value })}
            className="w-full text-xs bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700 cursor-pointer"
          >
            {(options.segments || ['All']).map((s) => (
              <option key={s} value={s}>
                {s === 'All' ? 'All Segments' : s}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};
