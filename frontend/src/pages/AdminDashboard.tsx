import { useState } from 'react';
import DisasterMap from '../components/DisasterMap'; 
import NotificationToggle from '../components/common/NotificationToggle';

// --- Helper Component for the Terrain Data Grid ---
const DataMetric = ({ label, value, subtext, alert }: { label: string, value: string, subtext: string, alert?: boolean }) => (
  <div className="flex flex-col gap-0.5">
    <span className="text-[10px] text-gray-500 uppercase font-semibold">{label}</span>
    <span className={`text-sm font-bold ${alert ? 'text-red-500' : 'text-gray-200'}`}>{value}</span>
    <span className="text-[10px] text-cyan-500/80">{subtext}</span>
  </div>
);

const TIMELINE_DATA = [
  { time: '00:00', rain: 15, quake: 5 },
  { time: '03:00', rain: 30, quake: 10 },
  { time: '06:00', rain: 85, quake: 15 },
  { time: '09:00', rain: 45, quake: 8 },
  { time: '12:00', rain: 95, quake: 60 }, // Peak disaster point
  { time: '15:00', rain: 60, quake: 25 },
  { time: '18:00', rain: 25, quake: 10 },
  { time: '21:00', rain: 10, quake: 5 },
];

export default function AdminDashboard() {
  // 1. Your Existing State Logic
  const [activeAlert, setActiveAlert] = useState<any>(null);
  const [mapData, setMapData] = useState<any>(null);
  const [mapMode, setMapMode] = useState<'monitoring' | 'planning'>('monitoring');
  
  // New UI State
  const [isEmergencyMode, setIsEmergencyMode] = useState(false);

  // Your existing simulation function
  const triggerLiveAlert = () => {
    setActiveAlert({
      h3Index: '88283082b9fffff',
      moisture: '94%',
      risk: '92%',
      message: 'Critical soil saturation detected near NH-27.'
    });
    setMapData({
      type: 'FeatureCollection' as const,
      features: [{
        type: 'Feature' as const,
        properties: { riskLevel: 'HIGH', score: 92, state: 'Critical', alert: 'Evacuate' },
        geometry: {
          type: 'Polygon' as const,
          coordinates: [[[91.7362, 26.2445], [91.8228, 26.1945], [91.8228, 26.0945], [91.7362, 26.0445], [91.6496, 26.0945], [91.6496, 26.1945], [91.7362, 26.2445]]]
        }
      }]
    });
  };

  return (
    <div className="h-screen w-screen bg-[#050505] text-white flex flex-col font-sans overflow-hidden">
      
      {/* TOP NAVIGATION BAR */}
      <header className="h-14 shrink-0 border-b border-[#1f2937] flex items-center justify-between px-6 bg-[#0a0a0a]">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <h1 className="text-lg font-bold tracking-widest uppercase text-gray-100">TerraSentry</h1>
        </div>
        
        <div className="flex items-center gap-4">
          <NotificationToggle />
          
          <button 
            onClick={() => setIsEmergencyMode(!isEmergencyMode)}
            className={`px-3 py-1.5 rounded text-xs font-bold border transition-colors ${
              isEmergencyMode 
                ? 'bg-red-900/50 border-red-500 text-red-400 animate-pulse' 
                : 'border-red-900/50 text-red-500 hover:bg-red-950/30'
            }`}
          >
            🚨 Emergency Mode
          </button>
          <button className="px-3 py-1.5 rounded text-xs font-medium border border-orange-700/50 text-orange-500 hover:bg-orange-950/30 transition-colors">
            Broadcast Alerts
          </button>
          <button className="px-3 py-1.5 rounded text-xs font-medium border border-cyan-800 text-cyan-400 hover:bg-cyan-950/30 transition-colors">
            Contact DMA
          </button>
          
          <div className="flex bg-[#111] p-1 rounded border border-[#1f2937] ml-2">
            <button
              onClick={() => setMapMode('monitoring')}
              className={`px-4 py-1 rounded text-xs font-medium transition-colors ${mapMode === 'monitoring' ? 'bg-cyan-600/20 text-cyan-400 border border-cyan-800' : 'text-gray-500 hover:text-gray-300'}`}
            >
              Analysis
            </button>
            <button
              onClick={() => setMapMode('planning')}
              className={`px-4 py-1 rounded text-xs font-medium transition-colors ${mapMode === 'planning' ? 'bg-cyan-600/20 text-cyan-400 border border-cyan-800' : 'text-gray-500 hover:text-gray-300'}`}
            >
              Planning
            </button>
          </div>
        </div>
      </header>

      {/* MAIN 3-COLUMN GRID */}
      <main className="flex-1 grid grid-cols-12 gap-3 p-3 min-h-0 bg-[#000000]">
        
        {/* ================= LEFT COLUMN: DATA PANELS ================= */}
        <aside className="col-span-3 flex flex-col gap-3 overflow-y-auto pr-1 custom-scrollbar">
          {!isEmergencyMode ? (
            <>
              {/* PANEL 1: Soil Composition */}
              <div className="bg-[#0a0a0a] border border-[#1f2937] rounded-lg p-4">
                <h3 className="text-cyan-500 text-[10px] font-bold mb-4 tracking-widest uppercase">Soil Composition</h3>
                <div className="flex items-center gap-6">
                  {/* CSS Conic Gradient Pie Chart */}
                  <div className="w-24 h-24 rounded-full" style={{ background: 'conic-gradient(#0891b2 0% 45%, #ea580c 45% 75%, #059669 75% 100%)' }} />
                  <div className="flex flex-col gap-2 text-xs">
                    <div className="flex items-center gap-2"><span className="w-2 h-2 bg-cyan-600 rounded-sm" /> Clay Loam</div>
                    <div className="flex items-center gap-2"><span className="w-2 h-2 bg-orange-600 rounded-sm" /> Weathered Silt</div>
                    <div className="flex items-center gap-2"><span className="w-2 h-2 bg-emerald-600 rounded-sm" /> Alpine Peat</div>
                  </div>
                </div>
              </div>
              
              {/* PANEL 2: Terrain & Indices */}
              <div className="bg-[#0a0a0a] border border-[#1f2937] rounded-lg p-4">
                <h3 className="text-cyan-500 text-[10px] font-bold mb-4 tracking-widest uppercase">Cell Terrain & Indices</h3>
                <div className="grid grid-cols-2 gap-y-4 gap-x-2">
                  <DataMetric label="Cell Solar Time" value="14:30" subtext="Daytime Phase" />
                  <DataMetric label="Thermal Temp" value="14.2°C" subtext="Diurnal Normal" />
                  <DataMetric label="Soil Type" value="Clay Loam" subtext="Highly Saturated" />
                  <DataMetric label="Lithology" value="Gneiss Schist" subtext="Weathered Bedrock" />
                  <DataMetric label="SPI (Precipitation)" value="+2.45" subtext="Extremely Wet" alert={true} />
                  <DataMetric label="TWI (Wetness Index)" value="12.8" subtext="High Accumulation" />
                  <DataMetric label="Elevation" value="3,240 m" subtext="High Alpine Ridge" />
                  <DataMetric label="Slope Gradient" value="34.2°" subtext="Critical Shear Zone" alert={true} />
                </div>
              </div>

              {/* PANEL 3: Emergency Nodes */}
              <div className="bg-[#0a0a0a] border border-[#1f2937] rounded-lg p-4 flex-1">
                <h3 className="text-cyan-500 text-[10px] font-bold mb-4 tracking-widest uppercase">Nearest Emergency Nodes</h3>
                <div className="flex flex-col gap-3">
                  {[
                    { name: 'Tawang Central Fire Station', dist: '223 m', color: 'text-cyan-400' },
                    { name: 'Khandro Drowa Tsangmu Hospital', dist: '326 m', color: 'text-emerald-400' },
                    { name: 'Alpine Disaster Rescue Outpost', dist: '869 m', color: 'text-orange-400' },
                    { name: 'Base Station Field Hospital', dist: '1.09 km', color: 'text-gray-400' },
                  ].map((node, i) => (
                    <div key={i} className="flex justify-between items-center text-xs border-b border-[#1f2937] pb-2 last:border-0">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] ${node.color}`}>⛑</span>
                        <span className="text-gray-300">{node.name}</span>
                      </div>
                      <span className="text-gray-500 font-mono">{node.dist}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-[#0a0a0a] border border-red-900/50 rounded-lg p-4 flex-1 flex flex-col">
               <h3 className="text-red-500 text-[10px] font-bold mb-4 tracking-widest uppercase flex items-center gap-2">
                 <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"/>
                 Evacuation Team Alpha (Active)
               </h3>
               <div className="flex-1 border border-red-900/30 rounded bg-[#050505] p-3 text-xs text-gray-400 font-mono flex flex-col justify-end">
                 <p className="text-red-400 mb-1">[14:32] COMMAND: Immediate evacuation NH-13.</p>
                 <p className="mb-1">[14:33] TEAM-1: Moving to designated nodes.</p>
                 <p className="animate-pulse text-white">[14:34] CIVILIAN SOS: Trapped at ridge sector...</p>
               </div>
            </div>
          )}
        </aside>

        {/* ================= CENTER COLUMN: MAP ================= */}
        <section className="col-span-6 flex flex-col gap-3">
          <div className="flex-1 bg-[#0a0a0a] border border-[#1f2937] rounded-lg overflow-hidden relative">
             <div className="absolute inset-0 w-full h-full">
                <DisasterMap riskData={mapData} mapMode={mapMode} />
             </div>
          </div>
          
          {/* ================= BOTTOM TIMELINE CHART ================= */}
          <div className="h-48 bg-[#0a0a0a] border border-[#1f2937] rounded-lg p-4 shrink-0 flex flex-col">
            
            {/* Header & Legend */}
            <div className="flex justify-between items-start mb-2 shrink-0">
              <h3 className="text-cyan-500 text-[10px] font-bold tracking-widest uppercase">
                Hydrological (Rainfall) & Seismic (Earthquake) Timeline
              </h3>
              <span className="text-[9px] text-gray-600 tracking-widest uppercase">Live Spatial Sync</span>
            </div>

            <div className="flex items-center justify-center gap-6 mb-4 shrink-0">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-cyan-500 rounded-sm"></div>
                <span className="text-[9px] text-gray-400 font-bold uppercase tracking-wider">Precipitation/Rainfall [mm]</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-pink-500 rounded-sm"></div>
                <span className="text-[9px] text-gray-400 font-bold uppercase tracking-wider">Earthquake / Seismic Magnitude</span>
              </div>
            </div>

            {/* CSS Flexbox Bar Chart */}
            <div className="flex-1 flex items-end justify-between gap-1 px-2 pb-1 border-b border-[#1f2937] relative">
              
              {/* Background Grid Lines */}
              <div className="absolute inset-0 flex flex-col justify-between pointer-events-none z-0">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="w-full border-t border-[#1f2937]/40 flex-1"></div>
                ))}
              </div>

              {/* Data Bars */}
              {TIMELINE_DATA.map((data, i) => (
                <div key={i} className="flex flex-col items-center gap-2 z-10 w-full group cursor-crosshair">
                  <div className="flex items-end justify-center gap-1 w-full h-24">
                    
                    {/* Rain Bar */}
                    <div 
                      className="w-full max-w-[14px] bg-cyan-500 rounded-t-[2px] transition-all duration-500 group-hover:bg-cyan-400" 
                      style={{ height: `${data.rain}%` }}
                      title={`Rainfall: ${data.rain}mm`}
                    />
                    
                    {/* Quake Bar */}
                    <div 
                      className="w-full max-w-[14px] bg-pink-500 rounded-t-[2px] transition-all duration-500 group-hover:bg-pink-400" 
                      style={{ height: `${data.quake}%` }}
                      title={`Magnitude: ${data.quake / 10}`}
                    />
                    
                  </div>
                  <span className="text-[9px] text-gray-500 font-mono group-hover:text-gray-300 transition-colors">{data.time}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ================= RIGHT COLUMN: KPIs & FEED ================= */}
        <aside className="col-span-3 flex flex-col gap-3 overflow-y-hidden pr-1">
          
          {/* 1. DISASTER SUMMARY KPIs */}
          <div className="flex flex-col gap-2 shrink-0">
            <h3 className="text-cyan-500 text-[10px] font-bold tracking-widest uppercase mb-1">Disaster Summary KPIs</h3>
            
            <div className="bg-[#0a0a0a] border border-[#1f2937] border-l-2 border-l-pink-500 rounded-lg p-3">
               <span className="block text-[10px] text-gray-400 font-bold uppercase tracking-wider mb-1">Confirmed Landslides</span>
               <span className="block text-2xl font-bold text-pink-500 leading-none">18</span>
            </div>
            
            <div className="bg-[#0a0a0a] border border-[#1f2937] border-l-2 border-l-orange-500 rounded-lg p-3">
               <span className="block text-[10px] text-gray-400 font-bold uppercase tracking-wider mb-1">Predictive Landslide Risks</span>
               <span className="block text-2xl font-bold text-orange-500 leading-none">0</span>
            </div>
            
            <div className="bg-[#0a0a0a] border border-[#1f2937] border-l-2 border-l-cyan-500 rounded-lg p-3">
               <span className="block text-[10px] text-gray-400 font-bold uppercase tracking-wider mb-1">Floods & Roadblocks</span>
               <span className="block text-2xl font-bold text-cyan-500 leading-none">0</span>
            </div>
          </div>

          {/* 2. SPATIAL MAP LEGEND */}
          <div className="bg-[#0a0a0a] border border-[#1f2937] rounded-lg p-4 shrink-0">
            <h3 className="text-cyan-500 text-[10px] font-bold mb-3 tracking-widest uppercase">Spatial Map Legend</h3>
            
            <div className="mb-4">
              <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider block mb-2">Incident Marker Icons</span>
              <div className="grid grid-cols-2 gap-2 text-[10px] text-gray-300">
                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded-full bg-pink-500 border border-pink-300" /> Confirmed Landslide</div>
                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded-full bg-orange-500 border border-orange-300" /> Highly Predictive</div>
                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded-full bg-cyan-500 border border-cyan-300" /> Flash Flood Zone</div>
                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded-full bg-yellow-500 border border-yellow-300" /> Road Blockage</div>
              </div>
            </div>

            <div>
              <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider block mb-2">H3 Polygon Risk Levels</span>
              <div className="grid grid-cols-2 gap-2 text-[10px] text-gray-300">
                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded bg-pink-900/50 border border-pink-500" /> Critical (&gt;80%)</div>
                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded bg-orange-900/50 border border-orange-500" /> High Risk (&gt;70%)</div>
                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded bg-yellow-900/50 border border-yellow-500" /> Warning (&gt;55%)</div>
                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded bg-cyan-900/50 border border-cyan-500" /> Info / Normal</div>
              </div>
            </div>
          </div>

          {/* 3. LIVE DISASTER RISK FEED */}
          <div className="bg-[#0a0a0a] border border-[#1f2937] rounded-lg p-3 flex-1 flex flex-col min-h-0">
            <h3 className="text-cyan-500 text-[10px] font-bold mb-3 tracking-widest uppercase flex items-center gap-2 shrink-0">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
              Live Disaster Risk Feed
            </h3>
            
            <div className="flex-1 overflow-y-auto custom-scrollbar flex flex-col gap-2 pr-1">
              
              {/* Simulation Button disguised as a feed tool */}
              <button 
                onClick={triggerLiveAlert}
                className="w-full bg-[#111] hover:bg-[#1a1a1a] text-[10px] text-gray-400 border border-[#1f2937] py-1.5 rounded transition-colors mb-1 uppercase tracking-wider font-bold"
              >
                + Inject Telemetry Alert
              </button>

              {/* Dynamic State Alert */}
              {activeAlert && (
                <div className="bg-[#111] border-l-2 border-pink-500 p-2.5 rounded flex flex-col gap-1.5">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold text-pink-500 uppercase">Critical Saturation</span>
                    <span className="text-[9px] text-gray-500 font-mono">Live</span>
                  </div>
                  <p className="text-[10px] text-gray-300 leading-tight">{activeAlert.message}</p>
                  <div className="flex gap-2 mt-1">
                    <span className="text-[9px] font-mono bg-black px-1.5 py-0.5 rounded text-gray-400 border border-[#1f2937]">H3: {activeAlert.h3Index}</span>
                    <span className="text-[9px] font-mono bg-pink-950/30 px-1.5 py-0.5 rounded text-pink-400 border border-pink-900/50">Risk: {activeAlert.risk}</span>
                  </div>
                </div>
              )}

              {/* Hardcoded Dummy Feed Item 1 */}
              <div className={`bg-[#111] border-l-2 border-orange-500 p-2.5 rounded flex flex-col gap-1.5 ${!activeAlert ? 'opacity-100' : 'opacity-60'}`}>
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-bold text-orange-500 uppercase">Highly Predictive Slip</span>
                  <span className="text-[9px] text-gray-500 font-mono">14:22</span>
                </div>
                <p className="text-[10px] text-gray-300 leading-tight">Steep slope detected with +2.45 SPI near Monastery Ridge.</p>
                <div className="flex gap-2 mt-1">
                  <span className="text-[9px] font-mono bg-black px-1.5 py-0.5 rounded text-gray-400 border border-[#1f2937]">Elev: 3,418m</span>
                  <span className="text-[9px] font-mono bg-orange-950/30 px-1.5 py-0.5 rounded text-orange-400 border border-orange-900/50">Risk: 74%</span>
                </div>
              </div>

              {/* Hardcoded Dummy Feed Item 2 */}
              <div className={`bg-[#111] border-l-2 border-cyan-500 p-2.5 rounded flex flex-col gap-1.5 ${!activeAlert ? 'opacity-100' : 'opacity-60'}`}>
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-bold text-cyan-500 uppercase">Flash Flood Overflow</span>
                  <span className="text-[9px] text-gray-500 font-mono">13:54</span>
                </div>
                <p className="text-[10px] text-gray-300 leading-tight">Disruption near Lumla bus stand. High water volume.</p>
                <div className="flex gap-2 mt-1">
                  <span className="text-[9px] font-mono bg-black px-1.5 py-0.5 rounded text-gray-400 border border-[#1f2937]">Area: Sector 4</span>
                  <span className="text-[9px] font-mono bg-cyan-950/30 px-1.5 py-0.5 rounded text-cyan-400 border border-cyan-900/50">Status: Advisory</span>
                </div>
              </div>

            </div>
          </div>
        </aside>

      </main>
    </div>
  );
}