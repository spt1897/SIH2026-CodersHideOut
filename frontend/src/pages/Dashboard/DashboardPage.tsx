import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../store/useAuthStore';
import LiveCapture from '../../components/common/LiveCapture';
import FileUpload from '../../components/common/FileUpload'; // Import the new component
import OfflineSyncWidget from '../../components/common/OfflineWidgetSync';
import SyncHistoryLog from '../../components/common/SyncHistoryLog';

export default function DashboardPage() {
  const { t } = useTranslation();
  const logout = useAuthStore((state) => state.logout);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 flex flex-col items-center p-6">
      
      <nav className="w-full max-w-5xl flex justify-between items-center border-b border-slate-800 pb-4 mb-8">
        <h1 className="text-2xl font-bold text-white">{t('navbar.title', 'Dashboard')}</h1>
        <button 
          onClick={logout}
          className="text-sm bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded transition-colors"
        >
          Logout
        </button>
      </nav>

      {/* Grid Layout for the Media Tools */}
      <main className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Side: Live Analysis */}
        <div className="flex flex-col items-center">
          <h2 className="text-xl font-bold text-slate-200 mb-4 w-full max-w-md">Live AI Analysis</h2>
          <LiveCapture />
        </div>

        {/* Right Side: Static File Upload */}
        <div className="flex flex-col items-center">
          <h2 className="text-xl font-bold text-slate-200 mb-4 w-full max-w-md">Batch Processing</h2>
          <FileUpload />
        </div>

        <OfflineSyncWidget />
        <SyncHistoryLog />

      </main>

    </div>
  );
}