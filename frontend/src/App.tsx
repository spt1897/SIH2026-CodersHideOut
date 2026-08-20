import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/Auth/LoginPage';
import DashboardPage from './pages/Dashboard/DashboardPage';

// Keep your mock components for the others for now
const LandingPage = () => <div className="text-white p-8">Landing Page</div>;

export default function App() {
  // const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />


        <Route path="/login" element={<LoginPage />} />

        {/* <Route
          path="/dashboard"
          element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" replace />}
        /> */}
        <Route
          path="/dashboard"
          element={<DashboardPage />}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}