import { useRef, useEffect } from 'react';
import { useMediaWebSocket } from '../../hooks/useMediaWebSocket';

export default function LiveCapture() {
    const videoRef = useRef<HTMLVideoElement>(null);

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


                {isStreaming && (
                    <div className="absolute top-3 right-3 flex items-center gap-2 bg-black/50 px-2 py-1 rounded text-xs text-white font-medium">
                        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                        LIVE
                    </div>
                )}
            </div>

            {error && <p className="text-red-400 text-sm mb-3">{error}</p>}

            <div className="flex justify-center gap-4">
                {!isStreaming ? (
                    <button
                        onClick={handleStart}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                        Start Camera & AI Analysis
                    </button>
                ) : (
                    <button
                        onClick={handleStop}
                        className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                        Stop Analysis
                    </button>
                )}
            </div>
        </div>
    );
}