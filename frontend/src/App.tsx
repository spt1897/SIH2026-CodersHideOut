import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import your new Landing Page
import LandingPage from './pages/LandingPage';

// Import your existing pages (adjust these paths if yours are named differently)
import LoginPage from './pages/Auth/LoginPage';
import SignupPage from './pages/Auth/SignupPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import AdminDashboard from './pages/AdminDashboard';

export default function App() {
  return (
    <Router>
      <Routes>
        {/* The new default home screen */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Your existing authentication and app routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/admindashboard" element={<AdminDashboard/>} />
      </Routes>
    </Router>
  );
}