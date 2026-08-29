import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Import the newly translated UI components
import HomePage from './pages/HomePage';
import AuthPage from './pages/Auth/AuthPage';

// Import your existing dashboards
import DashboardPage from './pages/Dashboard/DashboardPage';
import AdminDashboard from './pages/AdminDashboard';

export default function App() {
  // Teammate's auth state (kept commented out until the backend auth is ready)
  // const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <BrowserRouter>
      <Routes>
        {/* Point the root and auth routes to our new components */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/signup" element={<AuthPage />} /> {/* AuthPage handles both via tabs */}

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