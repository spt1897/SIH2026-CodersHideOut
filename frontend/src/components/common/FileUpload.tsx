import { useState, useRef } from 'react';
import { uploadService } from '../../services/uploadService';

export default function FileUpload() {
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setProgress(0);
    setStatusMessage(`Uploading ${file.name}...`);

    try {
      await uploadService.uploadLargeFile(file, (percent) => {
        setProgress(percent);
      });
      setStatusMessage('Upload complete!');
      
      // Clear the input so they can upload another file if needed
      if (fileInputRef.current) fileInputRef.current.value = '';
      
    } catch (error) {
      console.error(error);
      setStatusMessage('Upload failed. Please check your connection.');
    } finally {
      setIsUploading(false);
      setTimeout(() => setStatusMessage(null), 5000); // Clear success message after 5s
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-md w-full shadow-lg">
      <h2 className="text-white font-semibold mb-4">Upload Media for Analysis</h2>
      
      <div className="border-2 border-dashed border-slate-700 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileChange} 
          disabled={isUploading}
          className="hidden" 
          id="file-upload"
        />
        <label 
          htmlFor="file-upload" 
          className="cursor-pointer flex flex-col items-center"
        >
          <svg className="w-10 h-10 text-slate-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span className="text-slate-300 font-medium hover:text-blue-400 transition-colors">
            Click to browse files
          </span>
          <span className="text-slate-500 text-sm mt-1">Supports large video and image files</span>
        </label>
      </div>

      {/* Progress Bar UI */}
      {isUploading && (
        <div className="mt-6">
          <div className="flex justify-between text-sm mb-2 text-slate-300">
            <span>{statusMessage}</span>
            <span className="font-medium text-blue-400">{progress}%</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden border border-slate-700">
            <div 
              className="bg-blue-600 h-full rounded-full transition-all duration-300 ease-out" 
              style={{ width: `${progress}%` }} 
            />
          </div>
        </div>
      )}

      {/* Success/Error Message */}
      {statusMessage && !isUploading && (
        <p className={`mt-4 text-sm font-medium ${statusMessage.includes('complete') ? 'text-green-400' : 'text-red-400'}`}>
          {statusMessage}
        </p>
      )}
    </div>
  );
}