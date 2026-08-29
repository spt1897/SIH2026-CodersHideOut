import { useState } from 'react';
import DisasterMap from '../components/DisasterMap';
import NotificationToggle from '../components/common/NotificationToggle';

export default function AdminDashboard() {
  const [activeAlert, setActiveAlert] = useState<any>(null);
  const [mapData, setMapData] = useState<any>(null);

  // The Mock WebSocket Trigger
  const triggerLiveAlert = () => {
    // 1. Update the Sidebar
    setActiveAlert({
      h3Index: '88283082b9fffff',
      moisture: '94%',
      risk: '92%',
      message: 'Critical soil saturation detected near NH-27.'
    });

    // 2. Update the Map (Draw the Hexagon)
    setMapData({
      type: 'FeatureCollection' as const,
      features: [
        {
          type: 'Feature' as const,
          properties: { riskLevel: 'HIGH' },
          geometry: {
            type: 'Polygon' as const,
            coordinates: [
              [
                [91.7362, 26.2445],
                [91.8228, 26.1945],
                [91.8228, 26.0945],
                [91.7362, 26.0445],
                [91.6496, 26.0945],
                [91.6496, 26.1945],
                [91.7362, 26.2445]
              ]
            ]
          }
        }
      ]
    });
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', backgroundColor: '#050505', color: '#e5e7eb', overflow: 'hidden' }}>
      
      {/* LEFT SIDEBAR */}
      <aside style={{ width: '380px', backgroundColor: '#0a0a0a', borderRight: '1px solid #1f2937', display: 'flex', flexDirection: 'column', padding: '24px', zIndex: 10 }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <div>
            <p style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#60a5fa', marginBottom: '8px' }}>
              ● LIVE MONITORING
            </p>
            <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>Kamrup District</h1>
          </div>
          
          {/* SIMULATION BUTTON */}
          <button 
            onClick={triggerLiveAlert}
            style={{ backgroundColor: '#1f2937', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '6px', fontSize: '12px', cursor: 'pointer' }}
          >
            Simulate Alert
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '32px' }}>
          <div style={{ backgroundColor: '#171717', padding: '16px', borderRadius: '8px', border: '1px solid #262626' }}>
            <span style={{ display: 'block', fontSize: '12px', color: '#9ca3af' }}>Avg Soil Moisture</span>
            <span style={{ display: 'block', fontSize: '24px', fontWeight: 'bold', color: activeAlert ? '#ef4444' : '#3b82f6', marginTop: '4px' }}>
              {activeAlert ? activeAlert.moisture : '68%'}
            </span>
          </div>
          <div style={{ backgroundColor: '#171717', padding: '16px', borderRadius: '8px', border: '1px solid #262626' }}>
            <span style={{ display: 'block', fontSize: '12px', color: '#9ca3af' }}>24h Rainfall</span>
            <span style={{ display: 'block', fontSize: '24px', fontWeight: 'bold', color: '#3b82f6', marginTop: '4px' }}>142mm</span>
          </div>
        </div>

        {/* Dynamic Alerts List */}
        <div>
          <h2 style={{ fontSize: '14px', fontWeight: '600', color: '#d1d5db', marginBottom: '16px', borderBottom: '1px solid #262626', paddingBottom: '8px' }}>
            Active AI Predictions
          </h2>
          
          {activeAlert ? (
            <div style={{ backgroundColor: '#450a0a', borderLeft: '4px solid #ef4444', padding: '12px 16px', borderRadius: '4px', animation: 'pulse 2s infinite' }}>
              <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#f87171' }}>HIGH RISK - H3: {activeAlert.h3Index}</span>
              <p style={{ fontSize: '13px', color: '#fca5a5', marginTop: '4px', margin: 0 }}>{activeAlert.message} Landslide probability: {activeAlert.risk}.</p>
            </div>
          ) : (
            <p style={{ fontSize: '13px', color: '#6b7280' }}>Waiting for telemetry data...</p>
          )}
        </div>

        {/* Firebase Notification Widget */}
        <NotificationToggle />
        
      </aside>

      {/* MAIN CONTENT */}
      <main style={{ flex: 1, position: 'relative' }}>
        <DisasterMap riskData={mapData} />
      </main>

    </div>
  );
}