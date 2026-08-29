import { useState } from 'react';
import DisasterMap from '../components/DisasterMap'; // Verify this path matches your directory
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
          properties: { riskLevel: 'HIGH', score: 92, state: 'Critical', alert: 'Evacuate' }, // Added properties to match your map's step colors
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
    // Responsive outer container: Column on mobile, Row on desktop
    <div className="flex flex-col md:flex-row h-screen w-full bg-[#050505] text-gray-200 overflow-hidden">
      
      {/* LEFT SIDEBAR -> BOTTOM PANEL ON MOBILE */}
      <aside className="w-full md:w-[380px] h-[45vh] md:h-full overflow-y-auto bg-[#0a0a0a] border-t md:border-t-0 md:border-r border-gray-800 p-6 flex flex-col z-10 shrink-0 order-2 md:order-1">
        
        <div className="flex justify-between items-center mb-8 shrink-0">
          <div>
            <p className="text-xs uppercase tracking-widest text-blue-400 mb-2">
              ● LIVE MONITORING
            </p>
            <h1 className="text-2xl font-bold m-0 text-white">Kamrup District</h1>
          </div>
          
          {/* SIMULATION BUTTON */}
          <button 
            onClick={triggerLiveAlert}
            className="bg-gray-800 text-white border border-gray-700 py-2 px-3 rounded-md text-xs cursor-pointer hover:bg-gray-700 transition-colors"
          >
            Simulate Alert
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-8 shrink-0">
          <div className="bg-[#171717] p-4 rounded-lg border border-[#262626]">
            <span className="block text-xs text-gray-400">Avg Soil Moisture</span>
            <span className={`block text-2xl font-bold mt-1 ${activeAlert ? 'text-red-500' : 'text-blue-500'}`}>
              {activeAlert ? activeAlert.moisture : '68%'}
            </span>
          </div>
          <div className="bg-[#171717] p-4 rounded-lg border border-[#262626]">
            <span className="block text-xs text-gray-400">24h Rainfall</span>
            <span className="block text-2xl font-bold text-blue-500 mt-1">142mm</span>
          </div>
        </div>

        {/* Dynamic Alerts List */}
        <div className="mb-8 shrink-0">
          <h2 className="text-sm font-semibold text-gray-300 mb-4 border-b border-[#262626] pb-2">
            Active AI Predictions
          </h2>
          
          {activeAlert ? (
            <div className="bg-[#450a0a] border-l-4 border-red-500 p-3 rounded shadow-md animate-pulse">
              <span className="text-xs font-bold text-red-400">HIGH RISK - H3: {activeAlert.h3Index}</span>
              <p className="text-[13px] text-red-300 mt-1 m-0">{activeAlert.message} Landslide probability: {activeAlert.risk}.</p>
            </div>
          ) : (
            <p className="text-[13px] text-gray-500">Waiting for telemetry data...</p>
          )}
        </div>

        {/* Firebase Notification Widget */}
        <div className="mt-auto pt-4 shrink-0">
          <NotificationToggle />
        </div>
        
      </aside>

      {/* MAIN CONTENT -> TOP PANEL ON MOBILE */}
      <main className="flex-1 w-full h-[55vh] md:h-full relative order-1 md:order-2">
        <DisasterMap riskData={mapData} />
      </main>

    </div>
  );
}