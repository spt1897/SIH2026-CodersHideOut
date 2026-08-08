import { useTranslation } from 'react-i18next';
import './App.css'

export default function App() {
  const { t, i18n } = useTranslation();

  return (
    <div className="min-h-screen bg-black text-gray-300 flex flex-col items-center justify-center p-4">
      <nav className="w-full max-w-4xl flex justify-between items-center border-b border-gray-800 pb-4 mb-8">
        <h1 className="text-2xl font-bold text-white">{t('navbar.title')}</h1>
        
        <select 
          onChange={(e) => i18n.changeLanguage(e.target.value)}
          defaultValue={i18n.language}
          className="bg-gray-900 border border-gray-700 text-white px-3 py-1 rounded"
        >
          <option value="en">English</option>
          <option value="hi">हिंदी</option>
          <option value="kn">ಕನ್ನಡ (DB Fetch Test)</option>
        </select>
      </nav>

      <main className="text-center space-y-4">
        <p className="text-lg">{t('dashboard.welcome')}</p>
        <button className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded transition-colors">
          {t('dashboard.uploadPrompt')}
        </button>
      </main>
    </div>
  );
}