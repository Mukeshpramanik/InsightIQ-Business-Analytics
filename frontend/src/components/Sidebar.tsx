import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, UploadCloud, BarChart3, TrendingUp,
  LineChart, Users, Lightbulb, Terminal, FileDown, Database,
  ChevronRight, Sparkles, Layers
} from 'lucide-react';

interface SidebarProps {
  currentDataset: string;
  isOpen: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentDataset, isOpen, onToggle }) => {
  const navItems = [
    { to: '/', label: 'Overview Dashboard', icon: LayoutDashboard },
    { to: '/import', label: 'Data Import & Quality', icon: UploadCloud },
    { to: '/eda', label: 'Exploratory EDA', icon: BarChart3 },
    { to: '/sales', label: 'Sales Analytics', icon: TrendingUp },
    { to: '/forecasting', label: 'Sales Forecasting', icon: LineChart },
    { to: '/segmentation', label: 'Customer Segmentation', icon: Users },
    { to: '/insights', label: 'Business Insights', icon: Lightbulb },
    { to: '/sql-lab', label: 'SQL Analytics Lab', icon: Terminal },
    { to: '/reports', label: 'Reports & Export', icon: FileDown },
    { to: '/datasets', label: 'Dataset Management', icon: Database },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/60 z-30 lg:hidden backdrop-blur-sm"
          onClick={onToggle}
        />
      )}

      <aside className={`
        fixed top-0 bottom-0 left-0 z-40 w-64 bg-slate-900 text-slate-200 border-r border-slate-800
        flex flex-col transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Brand header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800 bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-lg tracking-tight text-white">InsightIQ</span>
                <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">Pro</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-none">BI & Predictive Analytics</p>
            </div>
          </div>
        </div>

        {/* Dataset Pill */}
        <div className="px-4 py-3 border-b border-slate-800/60 bg-slate-950/20">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="flex items-center gap-1.5 font-medium">
              <Layers className="w-3.5 h-3.5 text-blue-400" /> Active Dataset
            </span>
            <span className="text-[10px] text-emerald-400 font-mono">Live</span>
          </div>
          <div className="text-xs font-semibold text-slate-200 truncate bg-slate-800/80 px-2.5 py-1.5 rounded-md border border-slate-700/60 flex items-center justify-between">
            <span className="truncate">{currentDataset}</span>
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          </div>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                onClick={() => {
                  if (window.innerWidth < 1024) onToggle();
                }}
                className={({ isActive }) => `
                  flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors
                  ${isActive 
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30 font-semibold' 
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}
                `}
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3.5 h-3.5 text-blue-200" />}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* User / Interview Portfolio Badge */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40">
          <div className="p-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50">
            <p className="text-[11px] font-semibold text-slate-200">Final-Year Capstone</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Enterprise BI & Data Science</p>
            <div className="mt-2 flex items-center gap-1.5 text-[10px] text-blue-400 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
              FastAPI + React 18 + Scikit
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
