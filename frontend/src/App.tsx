import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from './components/Toast';
import { Layout } from './components/Layout';
import ClassifierPage from './pages/ClassifierPage';
import EnumEditorPage from './pages/EnumEditorPage';
import PositionsPage from './pages/PositionsPage';
import PositionCardPage from './pages/PositionCardPage';
import ParametersPage from './pages/ParametersPage';
import UnitsPage from './pages/UnitsPage';

const qc = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/classifier" replace />} />
            <Route element={<Layout />}>
              <Route path="/classifier"    element={<ClassifierPage />} />
              <Route path="/enums"         element={<EnumEditorPage />} />
              <Route path="/positions"     element={<PositionsPage />} />
              <Route path="/positions/:id" element={<PositionCardPage />} />
              <Route path="/parameters"    element={<ParametersPage />} />
              <Route path="/units"         element={<UnitsPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}
