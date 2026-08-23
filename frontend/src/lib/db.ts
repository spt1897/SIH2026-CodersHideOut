import Dexie from 'dexie';
import type { Table } from 'dexie';

// Define the exact shape of the payload we built earlier
export interface IncidentPayload {
  id: string;
  timestamp: string;
  file: File;
  location: {
    lat: number;
    lng: number;
    accuracy: number;
  } | null;
  syncStatus: 'QUEUED' | 'SYNCED' | 'FAILED';
}

export class DisasterDatabase extends Dexie {
  incidents!: Table<IncidentPayload>;

  constructor() {
    super('DisasterAppDB');
    
    // Define the indexes (fields we might want to search or filter by)
    // We don't need to index the 'file' or 'location', just the metadata
    this.version(1).stores({
      incidents: 'id, syncStatus, timestamp' 
    });
  }
}

export const db = new DisasterDatabase();