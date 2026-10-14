import React from 'react';
import {
  FileDown, FileText, Table, Users, Lightbulb,
  LineChart, CheckCircle2, ShieldCheck, Download
} from 'lucide-react';
import { api } from '../services/api';

interface ReportsPageProps {
  datasetId: string;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ datasetId }) => {
  const exportCards = [
    {
      title: 'Executive PDF Summary Report',
      description: 'Formal executive briefing document containing headline KPIs, category breakdowns, customer segments, and strategic findings generated via ReportLab.',
      format: 'PDF Document',
      badge: 'Certified',
      badgeColor: 'bg-blue-100 text-blue-800',
      icon: FileText,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
      downloadUrl: api.getPdfReportUrl({ dataset_id: datasetId }),
      filename: `InsightIQ_Executive_Report_${datasetId}.pdf`,
      isPdf: true,
    },
    {
      title: 'Filtered Transaction Dataset',
      description: 'Granular order records matching the active filter configuration with line-item quantities, discounts, revenues, and net profits.',
      format: 'CSV Spreadsheet',
      badge: 'Sanitized',
      badgeColor: 'bg-emerald-100 text-emerald-800',
      icon: Table,
      iconColor: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      downloadUrl: api.getFilteredCsvUrl({ dataset_id: datasetId }),
      filename: `insightiq_export_${datasetId}.csv`,
    },
    {
      title: 'Customer Segmentation (RFM)',
      description: 'Full customer master with Recency (days), Frequency, Monetary spend, 1-5 quintile scores, segment classifications, and cluster assignments.',
      format: 'CSV Spreadsheet',
      badge: 'Deterministic',
      badgeColor: 'bg-purple-100 text-purple-800',
      icon: Users,
      iconColor: 'text-purple-600',
      bgColor: 'bg-purple-50',
      downloadUrl: api.getSegmentationCsvUrl(datasetId),
      filename: `insightiq_customer_segments_${datasetId}.csv`,
    },
    {
      title: 'Business Insights & Recommendations',
      description: 'Rule-based analytical findings, supporting numbers, mathematical calculations, interpretations, and practical management recommendations.',
      format: 'CSV Spreadsheet',
      badge: 'Audited',
      badgeColor: 'bg-amber-100 text-amber-800',
      icon: Lightbulb,
      iconColor: 'text-amber-600',
      bgColor: 'bg-amber-50',
      downloadUrl: api.getInsightsCsvUrl({ dataset_id: datasetId }),
      filename: `insightiq_business_insights_${datasetId}.csv`,
    },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Reports & Export Center</h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Generate audit-ready CSV extracts and high-resolution executive PDF reports for <span className="font-semibold text-slate-700">{datasetId}</span>.
        </p>
      </div>

      {/* Security & Integrity Callout */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
        <div className="text-xs text-slate-600">
          <span className="font-bold text-slate-900">Security & Integrity Assurance: </span>
          All exported tabular CSV files are systematically sanitized against Spreadsheet Formula Injection attacks (preventing malicious Excel execution). Metrics exported reflect real-time calculations from the active database.
        </div>
      </div>

      {/* Export Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {exportCards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2.5 rounded-xl ${card.bgColor} ${card.iconColor}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${card.badgeColor}`}>
                    {card.badge}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-slate-900">{card.title}</h3>
                <span className="text-[11px] font-mono font-medium text-slate-400 block mt-0.5">
                  Format: {card.format}
                </span>

                <p className="text-xs text-slate-600 mt-2.5 leading-relaxed">{card.description}</p>
              </div>

              <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-400 font-mono">Dataset: {datasetId}</span>
                <a
                  href={card.downloadUrl}
                  download={card.filename}
                  target={card.isPdf ? '_blank' : undefined}
                  rel={card.isPdf ? 'noopener noreferrer' : undefined}
                  className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg shadow-sm transition-all ${
                    card.isPdf
                      ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-500/20'
                      : 'bg-slate-900 hover:bg-slate-800 text-white shadow-slate-900/10'
                  }`}
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download {card.isPdf ? 'PDF Report' : 'CSV'}</span>
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
