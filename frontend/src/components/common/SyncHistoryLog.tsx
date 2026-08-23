import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '../../lib/db';

export default function SyncHistoryLog() {
  // Fetch synced items and sort them by timestamp (newest first)
  const syncedItems = useLiveQuery(
    () => db.incidents
      .where('syncStatus')
      .equals('SYNCED')
      .reverse()
      .sortBy('timestamp')
  );

  // If there's no history, render nothing
  if (!syncedItems || syncedItems.length === 0) return null;

  // Keep the UI clean by only showing the 5 most recent uploads
  const recentItems = syncedItems.slice(0, 5);

  return (
    <div className="mt-4 bg-[#0a0a0a] border border-[#262626] rounded-lg p-4 shadow-lg">
      <h4 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
        <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Recent Uploads
      </h4>
      
      <ul className="space-y-2">
        {recentItems.map((item) => (
          <li key={item.id} className="flex justify-between items-center text-xs p-2 bg-[#171717] rounded border border-[#262626]">
            <div className="flex flex-col">
              <span className="text-gray-300 font-mono text-[10px]">
                Incident ID: {item.id.split('-')[0]}...
              </span>
              <span className="text-gray-500">
                {new Date(item.timestamp).toLocaleString()}
              </span>
            </div>
            <span className="text-green-400/80 font-medium px-2 py-1 bg-green-500/10 rounded">
              ✓ Synced
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}