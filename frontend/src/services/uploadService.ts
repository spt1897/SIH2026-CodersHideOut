import { apiClient } from './apiClient';

export const uploadService = {

  uploadFile: async (file: File, additionalData?: Record<string, string>) => {
    const formData = new FormData();
    
    
    formData.append('file', file);
    
    // Append any extra form fields if needed (e.g., description, category)
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    
    const response = await apiClient.post('/api/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data', 
      },
    });

    return response.data;
  },
};