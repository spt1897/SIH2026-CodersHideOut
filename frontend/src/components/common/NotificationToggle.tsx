import { useState, useEffect } from 'react';
import { messaging, getToken, onMessage } from '../../lib/firebase';

export default function NotificationToggle() {
  const [deviceToken, setDeviceToken] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = onMessage(messaging, (payload: any) => {
      console.log('Message received in foreground: ', payload);
      alert(`🚨 ${payload.notification?.title}\n${payload.notification?.body}`);
    });

    return () => unsubscribe(); 
  }, []);

  const enableAlerts = async () => {
    try {
      const permission = await Notification.requestPermission();
      
      if (permission === 'granted') {
        const sw = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
        
        const token = await getToken(messaging, {
          // Replaced with the exact key from Saptarshi's backend
          vapidKey: 'BEXNVp8EAf12YBLnBkSI4Ao8JOCVzC8IinIiN3vVpJTbajbafkJEndJsDXJodaOn1AMElayNRM2QHVJKOMr5ghg', 
          serviceWorkerRegistration: sw
        });

        setDeviceToken(token);
        console.log("Your FCM Token is:", token);
      } else {
        alert("Permission denied. We cannot send you critical landslide alerts.");
      }
    } catch (error) {
      console.error("Error setting up notifications:", error);
    }
  };

  return (
    <button 
      onClick={enableAlerts}
      disabled={!!deviceToken}
      className={`px-3 py-1.5 rounded text-xs font-bold border transition-colors flex items-center gap-2 ${
        deviceToken 
          ? 'bg-green-950/20 border-green-900/50 text-green-500 cursor-default' 
          : 'border-blue-900/50 text-blue-400 hover:bg-blue-950/30'
      }`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${
        deviceToken ? 'bg-green-500 animate-pulse' : 'bg-blue-500'
      }`} />
      
      {deviceToken ? 'Alerts Active' : 'Enable Alerts'}
    </button>
  );
}