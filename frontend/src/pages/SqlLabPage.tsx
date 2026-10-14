import React, { useState, useEffect } from 'react';
import {
  Terminal, Play, RotateCcw, AlertTriangle, CheckCircle2,
  Clock, Database, ShieldAlert, Sparkles, ChevronLeft, ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { SQLQueryResponse, SampleQuery } from '../types';
import { LoadingSpinner, ErrorAlert } from '../components/StatusStates';

export const SqlLabPage: React.FC = () => {
  const [samples, setSamples] = useState<SampleQuery[]>([]);
  const [queryText, setQueryText] = useState<string>('');
  const [executing, setExecuting] = useState<boolean>(false);
  const [result, setResult] = useState<SQLQueryResponse | null>(null);
  const [selectedSample, setSelectedSample] = useState<SampleQuery | null>(null);

  // Pagination for results
  const [page, setPage] = useState<number>(1);
  const pageSize = 15;

  const loadSamples = async () => {
    try {
      const qList = await api.getSqlSamples();
      setSamples(qList);
      if (qList.length > 0) {
        setSelectedSample(qList[0]);
        setQueryText(qList[0].query);
      }
    } catch (err: any) {
      console.error('Failed to load SQL samples:', err);
    }
  };

  useEffect(() => {
    loadSamples();
  }, []);

  const handleRunQuery = async () => {
    if (!queryText.trim()) return;

    try {
      setExecuting(true);
      setPage(1);
      const res = await api.executeSql(queryText);
      setResult(res);
    } catch (err: any) {
      setResult({
        success: false,
        columns: [],
        rows: [],
        row_count: 0,
        execution_time_ms: 0,
        error_message: err.message || 'Execution failed',
        query_executed: queryText,
      });
    } finally {
      setExecuting(false);
    }
  };

  const handleSelectSample = (sample: SampleQuery) => {
    setSelectedSample(sample);
    setQueryText(sample.query);
    setResult(null);
  };

  const handleResetToCurrentSample = () => {
    if (selectedSample) {
      setQueryText(selectedSample.query);
      setResult(null);
    }
  };

  const rows = result?.rows || [];
  const totalPages = Math.ceil(rows.length / pageSize) || 1;
  const paginatedRows = rows.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Interactive SQL Analytics Lab</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Execute safe, read-only SQL queries against SQLite database tables. Ideal for demonstrating SQL mastery in analytics interviews.
          </p>
        </div>

        {/* Security Sandbox Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-semibold">
          <ShieldAlert className="w-4 h-4 text-emerald-600" />
          <span>AST Validator: Read-Only Enforced</span>
        </div>
      </div>

      {/* Query Catalog Selector */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">
          Curated Business Analyst SQL Questions:
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {samples.map((s) => (
            <button
              key={s.id}
              onClick={() => handleSelectSample(s)}
              className={`p-2.5 rounded-lg text-left transition-all border text-xs ${
                selectedSample?.id === s.id
                  ? 'bg-blue-50/80 border-blue-500 text-blue-950 font-medium shadow-sm'
                  : 'bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-700'
              }`}
            >
              <div className="font-semibold truncate">{s.title}</div>
              <div className="text-[10px] text-slate-500 mt-0.5">{s.category}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Editor & Execution Panel */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              {selectedSample ? selectedSample.title : 'Custom SQL Query'}
            </h3>
            {selectedSample && (
              <p className="text-xs text-slate-500 mt-0.5">{selectedSample.description}</p>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleResetToCurrentSample}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Query</span>
            </button>

            <button
              onClick={handleRunQuery}
              disabled={executing || !queryText.trim()}
              className="flex items-center gap-2 px-5 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm shadow-blue-500/20 transition-all disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{executing ? 'Executing Query...' : 'Execute SQL'}</span>
            </button>
          </div>
        </div>

        {/* Textarea Editor */}
        <div className="relative rounded-lg overflow-hidden border border-slate-800 bg-slate-950 font-mono text-xs">
          <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5 text-blue-400" /> SQLite Dialect
            </span>
            <span className="text-[10px] text-slate-500">Allowed Tables: sales_data, datasets, cleaning_history</span>
          </div>

          <textarea
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            rows={8}
            className="w-full bg-slate-950 text-emerald-400 p-4 focus:outline-none resize-y leading-relaxed font-mono"
            placeholder="SELECT region, SUM(revenue) FROM sales_data GROUP BY region;"
          />
        </div>
      </div>

      {/* Query Execution Feedback */}
      {result && (
        <div className="space-y-4">
          {result.success ? (
            <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 text-xs">
                <div className="flex items-center gap-2 text-emerald-700 font-semibold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Query Executed Successfully</span>
                </div>

                <div className="flex items-center gap-4 text-slate-500 font-mono text-[11px]">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" /> {result.execution_time_ms} ms
                  </span>
                  <span>{result.row_count} rows returned</span>
                </div>
              </div>

              {/* Result Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="bg-slate-50 border-y border-slate-200 text-slate-600 font-semibold uppercase text-[10px] tracking-wider">
                      {result.columns.map((col) => (
                        <th key={col} className="py-2.5 px-3 font-mono">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                    {paginatedRows.length > 0 ? (
                      paginatedRows.map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-50">
                          {result.columns.map((col) => (
                            <td key={col} className="py-2.5 px-3 text-slate-800">
                              {row[col] !== null ? String(row[col]) : <span className="text-slate-400 italic">NULL</span>}
                            </td>
                          ))}
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={result.columns.length} className="py-6 text-center text-slate-400">
                          Query returned 0 rows.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Table Pagination */}
              {rows.length > pageSize && (
                <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs text-slate-500">
                  <div>
                    Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, rows.length)} of {rows.length} rows
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
              )}
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800">
              <div className="flex items-start gap-2.5">
                <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-rose-900 text-sm">Query Rejected by AST Security Engine</h4>
                  <p className="mt-1 font-mono text-[11px] leading-relaxed text-rose-700">{result.error_message}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
