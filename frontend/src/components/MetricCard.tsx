import React from 'react';
import { LucideIcon, ArrowUpRight, ArrowDownRight, Info } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  growthPct?: number | null;
  hasBaseline?: boolean;
  subtitle?: string;
  formulaNote?: string;
  iconColor?: string;
  bgColor?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon: Icon,
  growthPct,
  hasBaseline = false,
  subtitle,
  formulaNote,
  iconColor = 'text-blue-600',
  bgColor = 'bg-blue-50',
}) => {
  const isPositive = growthPct !== undefined && growthPct !== null && growthPct > 0;
  const isNegative = growthPct !== undefined && growthPct !== null && growthPct < 0;

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">{title}</span>
          <div className="text-2xl font-bold text-slate-900 mt-1 tracking-tight">{value}</div>
        </div>
        <div className={`p-2.5 rounded-xl ${bgColor} ${iconColor} transition-transform group-hover:scale-105`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3.5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        {hasBaseline && growthPct !== undefined && growthPct !== null ? (
          <div className="flex items-center gap-1.5">
            <span
              className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded-md font-semibold text-[11px] ${
                isPositive
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : isNegative
                  ? 'bg-rose-50 text-rose-700 border border-rose-200'
                  : 'bg-slate-100 text-slate-600'
              }`}
            >
              {isPositive ? (
                <ArrowUpRight className="w-3 h-3 text-emerald-600" />
              ) : isNegative ? (
                <ArrowDownRight className="w-3 h-3 text-rose-600" />
              ) : null}
              {growthPct > 0 ? `+${growthPct}%` : `${growthPct}%`}
            </span>
            <span className="text-slate-400 text-[11px]">vs prior period</span>
          </div>
        ) : (
          <span className="text-[11px] text-slate-400">
            {subtitle || 'Full dataset scope'}
          </span>
        )}

        {formulaNote && (
          <div className="relative group/tip cursor-help">
            <Info className="w-3.5 h-3.5 text-slate-400 hover:text-slate-600" />
            <div className="absolute right-0 bottom-full mb-1.5 hidden group-hover/tip:block w-48 p-2 bg-slate-900 text-white text-[10px] rounded-lg shadow-lg z-30 leading-snug">
              {formulaNote}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
