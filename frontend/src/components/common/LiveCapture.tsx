import { useRef, useEffect } from 'react';
import { useMediaWebSocket } from '../../hooks/useMediaWebSocket';
import { useGeolocation } from '../../hooks/useGeolocation';

export default function LiveCapture() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const { startStreaming, stopStreaming, isStreaming, error } = useMediaWebSocket('/ws/ai-analysis');
  const { coordinates, geoError, isLocating, fetchLocation } = useGeolocation();

  const handleStart = async () => {
    try {
      fetchLocation(); 
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' }, 
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

  const handleTakeSnapshot = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => {
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
              syncStatus: 'QUEUED'
            };
            
            console.log('Incident Payload ready for queue:', payload);
            if (!coordinates) {
              console.warn("Snapshot captured without a GPS lock. Coordinates will be missing.");
            }
            // TODO: Await IndexedDB queue save here
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
        
        <canvas ref={canvasRef} className="hidden" />
        
        {isStreaming && (
          <div className="absolute top-3 right-3 flex items-center gap-2 bg-black/50 px-2 py-1 rounded text-xs text-white font-medium">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            LIVE
          </div>
        )}

        {isStreaming && (
          <div className="absolute bottom-3 left-3 bg-black/60 px-2 py-1 rounded text-xs font-medium backdrop-blur-sm">
            {isLocating && <span className="text-yellow-400">Acquiring GPS...</span>}
            {coordinates && <span className="text-green-400">✓ GPS Locked ({Math.round(coordinates.accuracy)}m)</span>}
            {geoError && <span className="text-red-400">GPS Error</span>}
          </div>
        )}
      </div>

      {error && <p className="text-red-400 text-sm mb-3">{error}</p>}
      {geoError && !isStreaming && <p className="text-red-400 text-sm mb-3">{geoError}</p>}

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