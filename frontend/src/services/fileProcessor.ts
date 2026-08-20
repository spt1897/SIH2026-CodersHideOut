export const fileProcessor = {
  /**
   * Reads a file and returns it as an ArrayBuffer for binary processing/chunking.
   */
  toArrayBuffer: (file: File | Blob): Promise<ArrayBuffer> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as ArrayBuffer);
      reader.onerror = () => reject(new Error('Failed to read file as ArrayBuffer'));
      reader.readAsArrayBuffer(file);
    });
  },

  /**
   * Reads a file and returns it as a Base64 string for immediate frontend UI preview.
   */
  toBase64: (file: File | Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = () => reject(new Error('Failed to read file as Base64'));
      reader.readAsDataURL(file);
    });
  }
};