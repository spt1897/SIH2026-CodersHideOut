import { apiClient } from './apiClient';

// Set chunk size (e.g., 5MB = 5 * 1024 * 1024 bytes)
const CHUNK_SIZE = 5 * 1024 * 1024; 

export const uploadService = {
  
  uploadLargeFile: async (file: File, onProgress?: (progress: number) => void) => {
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    
    // Loop through and send chunks sequentially
    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
      
      // Calculate start and end bytes for the slice
      const start = chunkIndex * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, file.size);
      
      // Slice the file into a binary blob
      const chunk = file.slice(start, end);

      // Build the FormData exactly as requested
      const formData = new FormData();
      
      // The actual binary chunk
      formData.append('file_chunk', chunk, file.name); 
      
      // Backend requirements
      formData.append('chunk_index', chunkIndex.toString());
      formData.append('content_type', file.type || 'application/octet-stream');
      formData.append('file_size', file.size.toString());
      
      // Extra metadata that helps the backend assemble it
      formData.append('file_name', file.name);
      formData.append('total_chunks', totalChunks.toString()); 

      try {
        // Await the POST request so it only sends the next chunk if this one succeeds
        await apiClient.post('/api/media/upload-chunk', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        // Optional: Calculate and fire the progress percentage
        if (onProgress) {
          const percentCompleted = Math.round(((chunkIndex + 1) / totalChunks) * 100);
          onProgress(percentCompleted);
        }
        
      } catch (error) {
        console.error(`Failed to upload chunk ${chunkIndex}`, error);
        throw new Error(`Upload aborted at chunk ${chunkIndex}`);
      }
    }

    return { success: true, message: 'All chunks uploaded successfully!' };
  },
};