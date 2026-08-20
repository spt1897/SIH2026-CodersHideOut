import { useRef, useEffect } from 'react';
import { useMediaWebSocket } from '../../hooks/useMediaWebSocket';

export default function LiveCapture() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null); // NEW: Hidden canvas reference
  
  const { startStreaming, stopStreaming, isStreaming, error } = useMediaWebSocket('/ws/ai-analysis');

  const handleStart = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' }, 
        audio: true 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      startStreaming(stream, 'video/webm;codecs=vp8,opus', 1000);
    } catch (err) {
      console.error("Hardware access denied:", err);
      alert("Please allow camera and microphone access to proceed.");
    }
  };

  const handleStop = () => {
    stopStreaming();
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  // --- NEW: Snapshot Logic ---
  const handleTakeSnapshot = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      // Match canvas dimensions to the actual video resolution
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Draw the exact current frame onto the hidden canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Extract the frame as a high-quality JPEG Blob
        canvas.toBlob((blob) => {
          if (blob) {
            // Convert Blob to a standard File object
            const file = new File([blob], `snapshot_${Date.now()}.jpg`, { type: 'image/jpeg' });
            
            console.log('Snapshot captured successfully:', file);
            // TODO: In Step 2, we will route this 'file' to your new Flexible File Handler or IndexedDB!
          }
        }, 'image/jpeg', 0.95);
      }
    }
  };

  useEffect(() => {
    return () => {
      if (isStreaming) handleStop();
    };
  }, [isStreaming]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 max-w-md w-full shadow-lg">
      <div className="relative aspect-video bg-black rounded-lg overflow-hidden mb-4 border border-slate-700">
        <video 
          ref={videoRef} 
          autoPlay 
          muted 
          playsInline 
          className="w-full h-full object-cover"
        />
        
        {/* Hidden canvas for image processing */}
        <canvas ref={canvasRef} className="hidden" />
        
        {isStreaming && (
          <div className="absolute top-3 right-3 flex items-center gap-2 bg-black/50 px-2 py-1 rounded text-xs text-white font-medium">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            LIVE
          </div>
        )}
      </div>

      {error && <p className="text-red-400 text-sm mb-3">{error}</p>}

      <div className="flex flex-col gap-3">
        {!isStreaming ? (
          <button 
            onClick={handleStart}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            Start Camera & AI Analysis
          </button>
        ) : (
          <>
            <button 
              onClick={handleTakeSnapshot}
              className="w-full bg-slate-800 border border-slate-600 hover:bg-slate-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex justify-center items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Capture Snapshot
            </button>
            <button 
              onClick={handleStop}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
            >
              Stop Analysis
            </button>
          </>
        )}
      </div>
    </div>
  );
}