import { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { latLngToCell } from 'h3-js';

import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
maplibregl.setWorkerUrl(maplibreWorkerUrl);

interface DisasterMapProps {
  riskData?: any;
}

// Re-adds custom layers whenever the base style is swapped
const addCustomLayers = (map: maplibregl.Map, data: any) => {
  if (!map.getSource('h3-cells')) {
    map.addSource('h3-cells', {
      type: 'geojson',
      data: data || { type: 'FeatureCollection', features: [] }
    });

    map.addLayer({
      id: 'h3-cells-layer',
      type: 'fill',
      source: 'h3-cells',
      paint: {
        'fill-color': [
          'step',
          ['get', 'score'],
          '#22c55e', 20,
          '#eab308', 45,
          '#f97316', 70,
          '#ef4444'
        ],
        'fill-opacity': 0.4
      }
    });
  }
};

export default function DisasterMap({ riskData }: DisasterMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [selectedCell, setSelectedCell] = useState<any>(null);
  const [currentTheme, setCurrentTheme] = useState<'dark' | 'light'>('dark');

  const styleUrl = currentTheme === 'dark'
    ? 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'
    : 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';

  // 1. Initialize Map
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    const mapInstance = new maplibregl.Map({
      container: mapContainer.current,
      style: styleUrl,
      center: [91.89, 25.57],
      zoom: 12
    });

    map.current = mapInstance;

    mapInstance.on('load', () => {
      addCustomLayers(mapInstance, riskData);

      mapInstance.on('click', (e) => {
        const features = mapInstance.queryRenderedFeatures(e.point, {
          layers: ['h3-cells-layer']
        });

        if (features && features.length > 0) {
          const clickedCell = features[0].properties;
          setSelectedCell({
            h3Index: clickedCell.h3Index,
            score: clickedCell.score,
            state: clickedCell.state,
            alert: clickedCell.alert
          });
        } else {
          const { lng, lat } = e.lngLat;
          const clickedH3Index = latLngToCell(lat, lng, 11);
          console.log("Clicked neutral zone. Target H3 ID:", clickedH3Index);
        }
      });

      mapInstance.on('mouseenter', 'h3-cells-layer', () => {
        mapInstance.getCanvas().style.cursor = 'pointer';
      });
      mapInstance.on('mouseleave', 'h3-cells-layer', () => {
        mapInstance.getCanvas().style.cursor = '';
      });
      mapInstance.addControl(
        new maplibregl.GeolocateControl({
          positionOptions: { enableHighAccuracy: true },
          trackUserLocation: true
        }),
        'top-right' // Position on the map canvas
      );
    });
  }, []);

  // 2. Handle Base Style Switching
  useEffect(() => {
    if (map.current) {
      map.current.setStyle(styleUrl);

      map.current.once('styledata', () => {
        addCustomLayers(map.current!, riskData);
      });
    }
  }, [styleUrl]);

  // 3. Handle Live Data Updates
  useEffect(() => {
    if (map.current && riskData) {
      const source = map.current.getSource('h3-cells') as maplibregl.GeoJSONSource;
      if (source) {
        source.setData(riskData);
      }
    }
  }, [riskData]);


  return (
    <div className="relative w-full h-[600px] rounded-lg overflow-hidden border border-[#262626]">
      <div ref={mapContainer} className="w-full h-full" />

      {/* Floating Theme Toggle (Always Accessible) */}
      <button
        onClick={() => setCurrentTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))}
        className="absolute bottom-6 left-6 bg-[#171717] text-white px-3 py-1.5 text-xs font-semibold rounded shadow-md border border-[#3f3f46] z-10 hover:bg-[#262626] transition-colors"
      >
        Switch to {currentTheme === 'dark' ? 'Light' : 'Dark'} Map
      </button>

      {/* Floating Cell Inspector */}
      {selectedCell && (
        <div className="absolute top-4 right-4 bg-[#171717] p-4 rounded-lg shadow-lg border border-[#262626] z-10 min-w-[200px]">
          <h3 className="text-sm font-bold text-white mb-2">Cell Information</h3>
          <p className="text-xs text-gray-400">ID: {selectedCell.h3Index}</p>
          <p className="text-xs text-gray-400">Status: {selectedCell.state}</p>
          <p className="text-xs text-gray-400">Threat Level: {selectedCell.alert}</p>
          <p className="text-xs text-gray-400">Priority Score: {selectedCell.score}</p>
          <button
            onClick={() => setSelectedCell(null)}
            className="mt-3 text-[10px] bg-blue-600 text-white px-2.5 py-1 rounded hover:bg-blue-700 transition-colors"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}