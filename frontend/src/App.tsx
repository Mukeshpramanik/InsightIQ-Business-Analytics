import React, { useState, useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { api } from './services/api';
import { DatasetInfo } from './types';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { LoadingSpinner } from './components/StatusStates';
import { ErrorBoundary } from './components/ErrorBoundary';

// Lazy-loaded page components for route-level code splitting
const OverviewDashboard = lazy(() => import('./pages/OverviewDashboard').then((m) => ({ default: m.OverviewDashboard })));
const DataImportPage = lazy(() => import('./pages/DataImportPage').then((m) => ({ default: m.DataImportPage })));
const EdaPage = lazy(() => import('./pages/EdaPage').then((m) => ({ default: m.EdaPage })));
const SalesAnalyticsPage = lazy(() => import('./pages/SalesAnalyticsPage').then((m) => ({ default: m.SalesAnalyticsPage })));
const ForecastingPage = lazy(() => import('./pages/ForecastingPage').then((m) => ({ default: m.ForecastingPage })));
const SegmentationPage = lazy(() => import('./pages/SegmentationPage').then((m) => ({ default: m.SegmentationPage })));
const InsightsPage = lazy(() => import('./pages/InsightsPage').then((m) => ({ default: m.InsightsPage })));
const SqlLabPage = lazy(() => import('./pages/SqlLabPage').then((m) => ({ default: m.SqlLabPage })));
const ReportsPage = lazy(() => import('./pages/ReportsPage').then((m) => ({ default: m.ReportsPage })));
const DatasetsPage = lazy(() => import('./pages/DatasetsPage').then((m) => ({ default: m.DatasetsPage })));

export const App: React.FC = () => {
  const [currentDatasetId, setCurrentDatasetId] = useState<string>('sample_superstore');
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [refreshKey, setRefreshKey] = useState<number>(0);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchDatasets = async () => {
    try {
      const list = await api.getDatasets();
      setDatasets(list);
      if (list.length > 0 && !list.find((d) => d.id === currentDatasetId)) {
        setCurrentDatasetId(list[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch dataset list:', err);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, [refreshKey]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshKey((k) => k + 1);
    setTimeout(() => setIsRefreshing(false), 600);
  };

  const handleDatasetImported = async (newDatasetId: string) => {
    await fetchDatasets();
    setCurrentDatasetId(newDatasetId);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 flex flex-col antialiased font-sans text-slate-800">
        {/* Responsive Sidebar */}
        <Sidebar
          currentDataset={currentDatasetId}
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen((prev) => !prev)}
        />

        {/* Main Content Area */}
        <div className="lg:pl-64 flex flex-col flex-1 min-w-0">
          <Navbar
            onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
            datasetId={currentDatasetId}
            datasets={datasets}
            onSelectDataset={(id) => setCurrentDatasetId(id)}
            onRefresh={handleRefresh}
            isRefreshing={isRefreshing}
          />

          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            <ErrorBoundary fallbackTitle="Application Error">
              <Suspense fallback={<LoadingSpinner message="Loading application module..." />}>
                <Routes>
                  <Route path="/" element={<OverviewDashboard key={`${currentDatasetId}-${refreshKey}`} datasetId={currentDatasetId} />} />
                  <Route path="/import" element={<DataImportPage onDatasetImported={handleDatasetImported} />} />
                  <Route path="/eda" element={<EdaPage key={`${currentDatasetId}-${refreshKey}`} datasetId={currentDatasetId} />} />
                  <Route path="/sales" element={<SalesAnalyticsPage key={`${currentDatasetId}-${refreshKey}`} datasetId={currentDatasetId} />} />
                  <Route path="/forecasting" element={<ForecastingPage key={`${currentDatasetId}-${refreshKey}`} datasetId={currentDatasetId} />} />
                  <Route path="/segmentation" element={<SegmentationPage key={`${currentDatasetId}-${refreshKey}`} datasetId={currentDatasetId} />} />
                  <Route path="/insights" element={<InsightsPage key={`${currentDatasetId}-${refreshKey}`} datasetId={currentDatasetId} />} />
                  <Route path="/sql-lab" element={<SqlLabPage />} />
                  <Route path="/reports" element={<ReportsPage datasetId={currentDatasetId} />} />
                  <Route path="/datasets" element={<DatasetsPage currentDatasetId={currentDatasetId} onSelectDataset={(id) => setCurrentDatasetId(id)} />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Suspense>
            </ErrorBoundary>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
