import { openDB, type DBSchema } from 'idb';

// Define the exact shape of our offline database
interface AppDB extends DBSchema {
  offlineMedia: {
    key: string;
    value: {
      id: string;
      file: File | Blob;
      fileName: string;
      capturedAt: number;
      syncStatus: 'pending' | 'uploaded';
    };
    indexes: { 'by-status': string }; 
  };
}

// Initialize the database connection
const dbPromise = openDB<AppDB>('coders-hideout-db', 1, {
  upgrade(db) {
    const store = db.createObjectStore('offlineMedia', { keyPath: 'id' });
    store.createIndex('by-status', 'syncStatus');
  },
});

export const offlineStorage = {
  saveMedia: async (file: File | Blob, fileName: string) => {
    const db = await dbPromise;
    const id = `media_${Date.now()}`;
    
    await db.put('offlineMedia', {
      id,
      file,
      fileName,
      capturedAt: Date.now(),
      syncStatus: 'pending',
    });
    
    return id;
  },

  getPendingUploads: async () => {
    const db = await dbPromise;
    return db.getAllFromIndex('offlineMedia', 'by-status', 'pending');
  },

  // Using the pure queue deletion approach to save device space
  deleteFromQueue: async (id: string) => {
    const db = await dbPromise;
    await db.delete('offlineMedia', id);
  }
};