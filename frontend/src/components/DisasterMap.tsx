import { useState } from 'react';
import Map, { Source, Layer } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

// 1. MOVED OUTSIDE: This prevents the map from reloading the basemap on every state change.
const mapStyle = {
  version: 8 as const,
  sources: {
    'carto-dark': {
      type: 'raster' as const,
      tiles: ['https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'],
      tileSize: 256,
      attribution: '&copy; CARTO',
    },
  },
  layers: [
    {
      id: 'dark-tiles',
      type: 'raster' as const,
      source: 'carto-dark',
      minzoom: 0,
      maxzoom: 19,
    },
  ],
};

const riskLayerStyle = {
  id: 'risk-heat-layer',
  type: 'fill' as const,
  paint: {
    'fill-color': '#ef4444', 
    'fill-opacity': 0.4,
    'fill-outline-color': '#7f1d1d' 
  }
};

// 2. EMPTY STATE: Keeps the layer alive in the background when there's no active alert.
const emptyFeatureCollection = {
  type: 'FeatureCollection' as const,
  features: []
};

export default function DisasterMap({ riskData }: { riskData: any }) {
  const [viewState, setViewState] = useState({
    longitude: 91.7362,
    latitude: 26.1445,
    zoom: 9,
    pitch: 45,
    bearing: 0
  });

  // Use the live data, or default to the invisible empty collection
  const geojsonData = riskData || emptyFeatureCollection;

  return (
    <div style={{ width: '100%', height: '100%', overflow: 'hidden' }}>
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapStyle={mapStyle}
        interactive={true}
      >
        {/* The Source is now permanently mounted, safely updating when geojsonData changes */}
        <Source id="risk-data" type="geojson" data={geojsonData}>
          <Layer {...riskLayerStyle} />
        </Source>
      </Map>
    </div>
  );
}