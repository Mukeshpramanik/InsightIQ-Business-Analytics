import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { api } from './services/api';
import { DatasetInfo } from './types';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { OverviewDashboard } from './pages/OverviewDashboard';
import { DataImportPage } from './pages/DataImportPage';
import { EdaPage } from './pages/EdaPage';
import { SalesAnalyticsPage } from './pages/SalesAnalyticsPage';
import { ForecastingPage } from './pages/ForecastingPage';
import { SegmentationPage } from './pages/SegmentationPage';
import { InsightsPage } from './pages/InsightsPage';
import { SqlLabPage } from './pages/SqlLabPage';
import { ReportsPage } from './pages/ReportsPage';
import { DatasetsPage } from './pages/DatasetsPage';

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
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
