import { useRef,useState, useEffect } from 'react';
import { useMediaWebSocket } from '../../hooks/useMediaWebSocket';
import { useGeolocation } from '../../hooks/useGeolocation';
import { db } from '../../lib/db';

export default function LiveCapture() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isMockStreaming, setIsMockStreaming] = useState(false);
  
  const { startStreaming, stopStreaming, error } = useMediaWebSocket('/ws/ai-analysis');
  const { coordinates, geoError, isLocating, fetchLocation } = useGeolocation();

  const handleStart = async () => {
    try {
      fetchLocation(); 
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' }, 
        audio: false // audio off for testing
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      // FAKE THE STREAM INSTEAD OF CALLING THE BACKEND
      setIsMockStreaming(true); 
      // startStreaming(stream, 'video/webm;codecs=vp8,opus', 1000); 
    } catch (err) {
      console.error("Hardware access denied:", err);
    }
  };

  const handleStop = () => {
    setIsMockStreaming(false);
    // stopStreaming();
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  const handleTakeSnapshot = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(async (blob) => { // <-- Make sure to add 'async' here
          if (blob) {
            const file = new File([blob], `snapshot_${Date.now()}.jpg`, { type: 'image/jpeg' });
            
            const payload = {
              id: crypto.randomUUID(),
              timestamp: new Date().toISOString(),
              file: file,
              location: coordinates ? {
                lat: coordinates.lat,
                lng: coordinates.lng,
                accuracy: coordinates.accuracy
              } : null,
              syncStatus: 'QUEUED' as const // Ensure TypeScript knows this is the exact string
            };
            
            try {
              // The magic line: Saves the file and GPS data to the local hard drive
              await db.incidents.add(payload);
              console.log('Successfully saved to IndexedDB queue:', payload.id);
              alert("Incident saved offline! Will sync when connection is restored.");
            } catch (err) {
              console.error("Failed to save offline:", err);
            }
          }
        }, 'image/jpeg', 0.95);
      }
    }
  };

  useEffect(() => {
    return () => {
      if (isMockStreaming) handleStop();
    };
  }, [isMockStreaming]);

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
        
        <canvas ref={canvasRef} className="hidden" />
        
        {isMockStreaming && (
          <div className="absolute top-3 right-3 flex items-center gap-2 bg-black/50 px-2 py-1 rounded text-xs text-white font-medium">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            LIVE
          </div>
        )}

        {isMockStreaming && (
          <div className="absolute bottom-3 left-3 bg-black/60 px-2 py-1 rounded text-xs font-medium backdrop-blur-sm">
            {isLocating && <span className="text-yellow-400">Acquiring GPS...</span>}
            {coordinates && <span className="text-green-400">✓ GPS Locked ({Math.round(coordinates.accuracy)}m)</span>}
            {geoError && <span className="text-red-400">GPS Error</span>}
          </div>
        )}
      </div>

      {error && <p className="text-red-400 text-sm mb-3">{error}</p>}
      {geoError && !isMockStreaming && <p className="text-red-400 text-sm mb-3">{geoError}</p>}

      <div className="flex flex-col gap-3">
        {!isMockStreaming ? (
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
              Capture Geo-Tagged Snapshot
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