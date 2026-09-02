import { useState, useRef, useEffect } from 'react';

export default function LiveFieldCapture() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);

  const startCamera = async (mode: 'environment' | 'user') => {
    stopCamera();
    setFacingMode(mode);
    setVideoUrl(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { exact: mode } },
        audio: true,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (err) {
      if (mode === 'environment') startCameraFallback();
    }
  };

  const startCameraFallback = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (err) {
      console.error("Camera failed:", err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      setIsCameraActive(false);
    }
  };

  const startRecording = () => {
    if (!videoRef.current || !videoRef.current.srcObject) return;
    
    chunksRef.current = [];
    const stream = videoRef.current.srcObject as MediaStream;
    const mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/mp4' });
      const url = URL.createObjectURL(blob);
      setVideoUrl(url);
      
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
          (err) => console.warn("GPS failed:", err),
          { enableHighAccuracy: true }
        );
      }
    };

    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      stopCamera();
    }
  };
  const handleUpload = async () => {
    if (!chunksRef.current.length) return;
    setIsUploading(true);
    
    try {
      const blob = new Blob(chunksRef.current, { type: 'video/mp4' });
      const formData = new FormData();
      
      // 1. Append the video blob
      formData.append('file', blob, `incident_${Date.now()}.mp4`);
      
      // 2. Append the location metadata if you have GPS lock
      if (location) {
        formData.append('latitude', location.lat.toString());
        formData.append('longitude', location.lng.toString());
      }

      // 3. Send to your teammate's backend
      const UPLOAD_ENDPOINT = 'http://localhost:8000/api/upload'; // Make sure this matches his FastAPI route

      const response = await fetch(UPLOAD_ENDPOINT, {
        method: 'POST',
        body: formData,
        // The browser automatically sets the correct multipart/form-data headers
      });

      if (!response.ok) throw new Error(`Server responded with status ${response.status}`);

      alert(`Upload Successful!\nLocation: ${location?.lat}, ${location?.lng}`);
      
      // Reset UI for the next capture
      setVideoUrl(null);
      setLocation(null);
      startCamera(facingMode);
    } catch (error) {
      console.error("Backend upload error:", error);
      alert("Upload failed. Verify backend server is running.");
    } finally {
      setIsUploading(false);
    }
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  return (
    <div className="w-full bg-[#171717] border border-[#262626] rounded-xl p-4 flex flex-col gap-4">
      
      {/* Video Container */}
      <div className="relative bg-black rounded-lg aspect-video overflow-hidden border border-[#3f3f46]">
        
        {/* State A: Camera Offline */}
        {!isCameraActive && !videoUrl && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-gray-500 text-sm font-medium tracking-wide">Camera Offline</span>
          </div>
        )}

        {/* State B: Live Camera Feed */}
        <video 
          ref={videoRef} 
          autoPlay 
          muted 
          playsInline 
          className={`absolute inset-0 w-full h-full object-cover ${(isCameraActive && !videoUrl) ? 'block' : 'hidden'}`}
        />
        
        {/* State C: Recorded Video Playback */}
        {videoUrl && (
          <video src={videoUrl} controls className="absolute inset-0 w-full h-full object-contain bg-black" />
        )}

        {/* Recording Indicator */}
        {isRecording && (
          <div className="absolute top-4 right-4 flex items-center gap-2 z-10">
            <span className="animate-pulse w-3 h-3 bg-red-500 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.8)]"></span>
            <span className="text-red-500 text-xs font-bold bg-black/60 px-2 py-1 rounded">REC</span>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-3">
        {/* Coordinate Display */}
        {location && (
          <div className="bg-blue-950/30 border border-blue-900/50 rounded py-1.5 flex justify-center items-center gap-2">
            <span className="text-xs text-blue-400">📍 Captured at: {location.lat.toFixed(4)}, {location.lng.toFixed(4)}</span>
          </div>
        )}

        {/* Button Controls */}
        <div className="flex gap-2">
          
          {/* Action: Activate */}
          {!isCameraActive && !videoUrl && (
            <button 
              onClick={() => startCamera('environment')}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Activate Camera
            </button>
          )}
          
          {/* Action: Record / Stop / Flip */}
          {isCameraActive && !videoUrl && (
            <>
              <button 
                onClick={() => startCamera(facingMode === 'environment' ? 'user' : 'environment')}
                disabled={isRecording}
                className="px-4 bg-[#262626] hover:bg-[#3f3f46] text-white py-2 rounded-lg text-sm disabled:opacity-30 transition-colors"
                title="Flip Camera"
              >
                🔄
              </button>
              
              {isRecording ? (
                <button 
                  onClick={stopRecording}
                  className="flex-1 bg-red-600 hover:bg-red-500 text-white py-2 rounded-lg text-sm font-bold transition-colors flex justify-center items-center gap-2"
                >
                  ⏹ Stop Recording
                </button>
              ) : (
                <button 
                  onClick={startRecording}
                  className="flex-1 bg-green-600 hover:bg-green-500 text-white py-2 rounded-lg text-sm font-bold transition-colors flex justify-center items-center gap-2"
                >
                  ⏺ Start Recording
                </button>
              )}
            </>
          )}

          {/* Action: Discard or Upload */}
          {videoUrl && (
            <>
              <button 
                onClick={() => { setVideoUrl(null); setLocation(null); startCamera(facingMode); }}
                disabled={isUploading}
                className="flex-1 bg-[#262626] hover:bg-[#3f3f46] text-white py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
              >
                Discard & Retake
              </button>
              <button 
                onClick={handleUpload}
                disabled={isUploading}
                className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 flex justify-center items-center"
              >
                {isUploading ? 'Uploading...' : 'Upload Video'}
              </button>
            </>
          )}  
        </div>
      </div>
    </div>
  );
}