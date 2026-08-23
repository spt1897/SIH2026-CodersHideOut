import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '../../lib/db'; // Adjust path if necessary
import { useState } from 'react';

export default function OfflineSyncWidget() {
  const [isSyncing, setIsSyncing] = useState(false);

  // Automatically listens to Dexie and updates when new items are queued
  const pendingItems = useLiveQuery(
    () => db.incidents.where('syncStatus').equals('QUEUED').toArray()
  );

  const handleManualSync = async () => {
    if (!pendingItems || pendingItems.length === 0) return;
    
    setIsSyncing(true);
    
    // Simulate a network delay for the mock sync
    setTimeout(async () => {
      try {
        // Here is where we will eventually loop through items and POST to backend
        // For now, we just update their status in Dexie to 'SYNCED'
        const itemIds = pendingItems.map(item => item.id);
        
        await db.incidents.where('id').anyOf(itemIds).modify({ syncStatus: 'SYNCED' });
        
        console.log(`Successfully synced ${itemIds.length} items!`);
      } catch (error) {
        console.error("Sync failed:", error);
      } finally {
        setIsSyncing(false);
      }
    }, 1500);
  };

  // If Dexie is loading or there are 0 queued items, render absolutely nothing.
  if (!pendingItems || pendingItems.length === 0) return null;

  return (
    <div className="mt-4 bg-[#0a0a0a] border border-[#262626] rounded-lg p-4 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-3">
        {/* Cloud Warning Icon */}
        <div className="bg-yellow-500/10 p-2 rounded-full border border-yellow-500/20">
          <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11v6m0 0l-3-3m3 3l3-3" />
          </svg>
        </div>
        
        <div>
          <h4 className="text-sm font-semibold text-gray-200">Offline Data Pending</h4>
          <p className="text-xs text-gray-400">
            {pendingItems.length} {pendingItems.length === 1 ? 'incident' : 'incidents'} waiting to be uploaded.
          </p>
        </div>
      </div>

      <button 
        onClick={handleManualSync}
        disabled={isSyncing}
        className="bg-[#171717] hover:bg-[#262626] border border-[#3f3f46] text-gray-200 text-xs font-medium py-2 px-4 rounded transition-colors disabled:opacity-50 flex items-center gap-2"
      >
        {isSyncing ? (
          <>
            <span className="w-3 h-3 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></span>
            Syncing...
          </>
        ) : (
          'Sync Now'
        )}
      </button>
    </div>
  );
}