import { useState, useEffect } from 'react';

// Using your screenshot's exact mock data. 
// Note: We use timestamps (ms) so we can easily do math on them.
const MOCK_UPLOADS = [
  { id: '899b728e...', timestamp: new Date('2026-08-30T09:33:39').getTime(), status: 'Synced' },
  { id: 'fc992432...', timestamp: new Date('2026-08-28T16:18:33').getTime(), status: 'Synced' },
  { id: '241a811f...', timestamp: new Date('2026-08-26T10:16:23').getTime(), status: 'Synced' },
  { id: '7ea2e444...', timestamp: new Date('2026-08-23T09:59:22').getTime(), status: 'Synced' }
];

export default function RecentUploads() {
  const [uploads, setUploads] = useState(MOCK_UPLOADS);

  // Auto-Cleanup: Filter out items older than 24 hours
  useEffect(() => {
    const TWENTY_FOUR_HOURS_MS = 24 * 60 * 60 * 1000;
    const now = Date.now();
    
    const activeUploads = uploads.filter(
      (upload) => (now - upload.timestamp) < TWENTY_FOUR_HOURS_MS
    );
    
    // Only update state if items were actually removed to prevent infinite loops
    if (activeUploads.length !== uploads.length) {
      setUploads(activeUploads);
    }
  }, [uploads]);

  const clearHistory = () => setUploads([]);

  return (
    <div className="bg-[#171717] border border-[#262626] rounded-xl p-4 flex flex-col gap-4 mt-6">
      
      {/* Header with Clear Button */}
      <div className="flex justify-between items-center border-b border-[#262626] pb-3">
        <h3 className="text-white font-semibold flex items-center gap-2 text-sm">
          <span className="text-green-500">✓</span> Recent Uploads
        </h3>
        <button 
          onClick={clearHistory}
          className="text-xs text-gray-500 hover:text-red-400 transition-colors cursor-pointer"
        >
          Clear History
        </button>
      </div>

      {/* Uploads List */}
      <div className="flex flex-col gap-2 max-h-64 overflow-y-auto">
        {uploads.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-6">No recent uploads in the last 24 hours.</p>
        ) : (
          uploads.map((item, idx) => (
            <div key={idx} className="flex justify-between items-center bg-[#0a0a0a] p-3 rounded-lg border border-[#262626]">
              <div>
                <p className="text-xs text-gray-300">Incident ID: {item.id}</p>
                <p className="text-[10px] text-gray-500 mt-1">
                  {new Date(item.timestamp).toLocaleString()}
                </p>
              </div>
              <span className="text-[11px] text-green-500 bg-green-950/30 px-2 py-1 rounded border border-green-900 flex items-center gap-1">
                ✓ {item.status}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}