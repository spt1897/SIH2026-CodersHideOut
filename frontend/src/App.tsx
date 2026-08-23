import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Import all your actual pages (Overriding your teammate's mock components)
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/Auth/LoginPage';
import SignupPage from './pages/Auth/SignupPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import AdminDashboard from './pages/AdminDashboard';

export default function App() {
  // Teammate's auth state (kept commented out until the backend auth is ready)
  // const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Teammate's protected route logic (ready for later) */}
        {/* <Route
          path="/dashboard"
          element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" replace />}
        /> */}
        <Route path="/dashboard" element={<DashboardPage />} />
        
        {/* Your newly created GIS Admin Dashboard */}
        <Route path="/admindashboard" element={<AdminDashboard/>} />

        {/* Teammate's catch-all route for 404s */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}