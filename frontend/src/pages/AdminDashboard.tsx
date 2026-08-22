import DisasterMap from '../components/DisasterMap';

export default function AdminDashboard() {
  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', backgroundColor: '#050505', color: '#e5e7eb', overflow: 'hidden' }}>
      
      {/* LEFT SIDEBAR: Statistical & Control Panel */}
      <aside style={{ 
        width: '380px', 
        backgroundColor: '#0a0a0a', 
        borderRight: '1px solid #1f2937',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px',
        zIndex: 10
      }}>
        <div style={{ marginBottom: '32px' }}>
          <p style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#60a5fa', marginBottom: '8px' }}>
            ● LIVE MONITORING
          </p>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>Kamrup District</h1>
          <p style={{ fontSize: '14px', color: '#9ca3af', marginTop: '4px' }}>Disaster Management Node</p>
        </div>

        {/* Mock Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '32px' }}>
          <div style={{ backgroundColor: '#171717', padding: '16px', borderRadius: '8px', border: '1px solid #262626' }}>
            <span style={{ display: 'block', fontSize: '12px', color: '#9ca3af' }}>Avg Soil Moisture</span>
            <span style={{ display: 'block', fontSize: '24px', fontWeight: 'bold', color: '#3b82f6', marginTop: '4px' }}>68%</span>
          </div>
          <div style={{ backgroundColor: '#171717', padding: '16px', borderRadius: '8px', border: '1px solid #262626' }}>
            <span style={{ display: 'block', fontSize: '12px', color: '#9ca3af' }}>24h Rainfall</span>
            <span style={{ display: 'block', fontSize: '24px', fontWeight: 'bold', color: '#3b82f6', marginTop: '4px' }}>142mm</span>
          </div>
        </div>

        {/* Active Alerts List */}
        <div>
          <h2 style={{ fontSize: '14px', fontWeight: '600', color: '#d1d5db', marginBottom: '16px', borderBottom: '1px solid #262626', paddingBottom: '8px' }}>
            Active AI Predictions
          </h2>
          <div style={{ backgroundColor: '#450a0a', borderLeft: '4px solid #ef4444', padding: '12px 16px', borderRadius: '4px' }}>
            <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#f87171' }}>HIGH RISK - H3: 88283082b9fffff</span>
            <p style={{ fontSize: '13px', color: '#fca5a5', marginTop: '4px', margin: 0 }}>Critical soil saturation detected near NH-27. Landslide probability: 92%.</p>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT: The GIS Map */}
      <main style={{ flex: 1, position: 'relative' }}>
        <DisasterMap />
      </main>

    </div>
  );
}