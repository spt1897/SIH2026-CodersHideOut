import { useEffect, useState } from 'react';
import { offlineStorage } from '../services/db';
import { uploadService } from '../services/uploadService';

export function useOfflineSync() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    const handleOnline = async () => {
      setIsOnline(true);
      setIsSyncing(true);
      
      try {
        const pendingFiles = await offlineStorage.getPendingUploads();
        
        for (const item of pendingFiles) {
          // Convert Blob back to File if necessary for the upload service
          const fileToUpload = item.file instanceof File 
            ? item.file 
            : new File([item.file], item.fileName);
            
          // Upload using the chunked pipeline we built earlier
          await uploadService.uploadLargeFile(fileToUpload);
          
          // Delete from the local queue to save mobile storage
          await offlineStorage.deleteFromQueue(item.id);
          console.log(`Successfully synced ${item.fileName}`);
        }
      } catch (error) {
        console.error('Background sync failed:', error);
      } finally {
        setIsSyncing(false);
      }
    };

    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return { isOnline, isSyncing };
}