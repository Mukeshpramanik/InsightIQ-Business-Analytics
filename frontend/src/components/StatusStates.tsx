import React from 'react';
import { AlertCircle, RefreshCw, FolderSearch, CheckCircle2 } from 'lucide-react';

export const LoadingSpinner: React.FC<{ message?: string }> = ({
  message = 'Calculating analytics and loading visualizations...',
}) => (
  <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
    <div className="w-12 h-12 rounded-full border-4 border-blue-200 border-t-blue-600 animate-spin mb-4 shadow-sm" />
    <p className="text-sm font-medium text-slate-700">{message}</p>
    <p className="text-xs text-slate-400 mt-1">Processing active transactional dataset</p>
  </div>
);

export const ErrorAlert: React.FC<{
  title?: string;
  message: string;
  onRetry?: () => void;
}> = ({ title = 'Failed to load data', message, onRetry }) => (
  <div className="rounded-xl bg-rose-50 border border-rose-200 p-4 mb-6 shadow-sm">
    <div className="flex items-start gap-3">
      <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-rose-900">{title}</h4>
        <p className="text-xs text-rose-700 mt-1 leading-relaxed">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-rose-800 bg-rose-100 hover:bg-rose-200 px-3 py-1.5 rounded-md transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry Action</span>
          </button>
        )}
      </div>
    </div>
  </div>
);

export const EmptyState: React.FC<{
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
}> = ({ title, description, actionText, onAction }) => (
  <div className="flex flex-col items-center justify-center py-16 px-4 text-center bg-white rounded-xl border border-dashed border-slate-300 my-4">
    <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mb-3">
      <FolderSearch className="w-6 h-6 text-slate-400" />
    </div>
    <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
    <p className="text-xs text-slate-500 max-w-sm mt-1 leading-normal">{description}</p>
    {actionText && onAction && (
      <button
        onClick={onAction}
        className="mt-4 px-3.5 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md transition-colors"
      >
        {actionText}
      </button>
    )}
  </div>
);
