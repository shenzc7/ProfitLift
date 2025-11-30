import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';
import { Recommendations } from './pages/Recommendations';
import { Validation } from './pages/Validation';
import { PerformanceTracker, StoreComparison } from './pages/ComingSoon';
import { SettingsPage } from './pages/Settings';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {/* Core Pages */}
        <Route index element={<Dashboard />} />
        <Route path="upload" element={<Upload />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="validation" element={<Validation />} />
        
        {/* Phase 2 Placeholders */}
        <Route path="performance" element={<PerformanceTracker />} />
        <Route path="stores" element={<StoreComparison />} />
        
        {/* Settings */}
        <Route path="settings" element={<SettingsPage />} />
        
        {/* Legacy redirects (in case old bookmarks exist) */}
        <Route path="rules" element={<Navigate to="/recommendations" replace />} />
        <Route path="bundles" element={<Navigate to="/recommendations" replace />} />
        <Route path="what-if" element={<Navigate to="/validation" replace />} />
        
        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
