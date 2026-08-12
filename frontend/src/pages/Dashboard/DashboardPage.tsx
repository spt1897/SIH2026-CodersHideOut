import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../store/useAuthStore';
import LiveCapture from '../../components/common/LiveCapture';

export default function DashboardPage() {
  const { t } = useTranslation();
  const logout = useAuthStore((state) => state.logout);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 flex flex-col items-center p-6">
      
      {/* Temporary Navbar for testing */}
      <nav className="w-full max-w-4xl flex justify-between items-center border-b border-slate-800 pb-4 mb-8">
        <h1 className="text-2xl font-bold text-white">{t('navbar.title', 'Dashboard')}</h1>
        <button 
          onClick={logout}
          className="text-sm bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded transition-colors"
        >
          Logout
        </button>
      </nav>

      {/* The Live Capture Engine */}
      <main className="w-full flex justify-center">
        <LiveCapture />
      </main>

    </div>
  );
}