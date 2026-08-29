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
    <div style={{ backgroundColor: '#171717', border: '1px solid #262626', padding: '16px', borderRadius: '8px', marginTop: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h4 style={{ fontSize: '14px', fontWeight: 'bold', color: '#e5e7eb', margin: 0 }}>System Alerts</h4>
          <p style={{ fontSize: '12px', color: '#9ca3af', margin: '4px 0 0 0' }}>Enable push notifications.</p>
        </div>
        <button 
          onClick={enableAlerts}
          style={{ backgroundColor: '#2563eb', color: 'white', fontSize: '12px', fontWeight: '500', padding: '8px 16px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Enable Alerts
        </button>
      </div>
      
      {deviceToken && (
        <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#0a0a0a', borderRadius: '4px', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
          <p style={{ fontSize: '10px', color: '#4ade80', fontFamily: 'monospace', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            Token: {deviceToken}
          </p>
        </div>
      )}
    </div>
  );
}