import { useState } from 'react';
import Map, { Source, Layer } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

const mockHexagonData = {
  type: 'FeatureCollection' as const,
  features: [
    {
      type: 'Feature' as const,
      properties: {
        riskLevel: 'HIGH',
        moisture: '87%',
      },
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

export default function DisasterMap() {
  const [viewState, setViewState] = useState({
    longitude: 91.7362,
    latitude: 26.1445,
    zoom: 9,
    pitch: 45,
    bearing: 0
  });

  // Replaced OSM with CartoDB Dark Matter
  const mapStyle = {
    version: 8 as const,
    sources: {
      'carto-dark': {
        type: 'raster' as const,
        tiles: [
          'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        ],
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

  return (
    <div style={{ width: '100%', height: '100%', overflow: 'hidden' }}>
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapStyle={mapStyle}
        interactive={true}
      >
        <Source id="risk-data" type="geojson" data={mockHexagonData}>
          <Layer {...riskLayerStyle} />
        </Source>
      </Map>
    </div>
  );
}