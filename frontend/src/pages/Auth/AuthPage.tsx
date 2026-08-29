import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from '../LandingPage';
import AuthPage from '../Auth/AuthPage'; // Update this import!
import DashboardPage from '../Dashboard/DashboardPage';
import AdminDashboard from '../AdminDashboard';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        
        {/* Unified Auth Route */}
        <Route path="/auth" element={<AuthPage />} />

        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/admindashboard" element={<AdminDashboard/>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}