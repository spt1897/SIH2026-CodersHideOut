import { useRef, useState, useCallback } from 'react';
import { useAuthStore } from '../store/useAuthStore';

export function useMediaWebSocket(wsEndpoint: string) {
    const wsRef = useRef<WebSocket | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const connectWebSocket = useCallback(() => {
        // Note: Standard WebBrowser WebSockets cannot send custom HTTP headers.
        // We pass the JWT token in the URL query string so the backend gateway can authenticate it.
        const token = useAuthStore.getState().accessToken;
        const wsUrl = `${import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8080'}${wsEndpoint}?token=${token}`;

        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => console.log(`WebSocket Connected: ${wsEndpoint}`);

        wsRef.current.onclose = () => {
            console.log('WebSocket Disconnected');
            setIsStreaming(false);
        };

        wsRef.current.onerror = (e) => {
            console.error('WebSocket Error', e);
            setError('Connection lost. Please try again.');
        };
    }, [wsEndpoint]);


    const startStreaming = async (stream: MediaStream, mimeType: string, timesliceMs = 1000) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            connectWebSocket();
        }

        try {

            const recorder = new MediaRecorder(stream, { mimeType });
            mediaRecorderRef.current = recorder;


            recorder.ondataavailable = (event) => {
                if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {

                    wsRef.current.send(event.data);
                }
            };

            recorder.start(timesliceMs);
            setIsStreaming(true);
            setError(null);
        } catch (err) {
            setError('Failed to start media recorder. Check device permissions.');
            console.error(err);
        }
    };

    const stopStreaming = useCallback(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
        }

        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {

            wsRef.current.send(JSON.stringify({ type: 'END_OF_STREAM' }));
            wsRef.current.close();
        }

        setIsStreaming(false);
    }, []);

    return {
        connectWebSocket,
        startStreaming,
        stopStreaming,
        isStreaming,
        error
    };
}