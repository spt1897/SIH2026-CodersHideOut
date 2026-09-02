import { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { latLngToCell } from 'h3-js';

import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
maplibregl.setWorkerUrl(maplibreWorkerUrl);

// Update interface to accept mapMode from the parent dashboard
interface DisasterMapProps {
  riskData?: any;
  mapMode: 'monitoring' | 'planning';
}

// Dark Mode (Constant Monitoring)
const MONITORING_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

// Satellite Mode (Hybrid: Imagery + Roads + Labels)
const PLANNING_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    // 1. The base satellite imagery
    'esri-satellite': {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
      ],
      tileSize: 256,
      attribution: 'Tiles &copy; Esri'
    },
    // 2. The transparent road network overlay
    'esri-roads': {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}'
      ],
      tileSize: 256
    },
    // 3. The transparent city/street labels overlay
    'esri-labels': {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'
      ],
      tileSize: 256
    }
  },
  layers: [
    {
      id: 'satellite-base',
      type: 'raster',
      source: 'esri-satellite',
      minzoom: 0,
      maxzoom: 22
    },
    {
      id: 'roads-overlay',
      type: 'raster',
      source: 'esri-roads',
      minzoom: 0,
      maxzoom: 22
    },
    {
      id: 'labels-overlay',
      type: 'raster',
      source: 'esri-labels',
      minzoom: 0,
      maxzoom: 22
    }
  ]
};

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
          '#22c55e', 20, // Green for low risk
          '#eab308', 45, // Yellow
          '#f97316', 70, // Orange
          '#ef4444'      // Red for critical
        ],
        'fill-opacity': 0.6 // Slightly higher opacity for visibility over satellite
      }
    });
  }
};

export default function DisasterMap({ riskData, mapMode }: DisasterMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [selectedCell, setSelectedCell] = useState<any>(null);

  // 1. Initialize Map
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    const initialStyle = mapMode === 'monitoring' ? MONITORING_STYLE : PLANNING_STYLE;

    const mapInstance = new maplibregl.Map({
      container: mapContainer.current,
      style: initialStyle,
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
            h3Index: clickedCell.h3Index || 'N/A',
            score: clickedCell.score || 0,
            state: clickedCell.state || 'Unknown',
            alert: clickedCell.alert || 'None'
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
        'top-right'
      );
    });
  }, []); // Only runs on mount

  // 2. Handle Base Style Switching (Monitoring vs Planning)
  useEffect(() => {
    if (!map.current) return;

    const targetStyle = mapMode === 'monitoring' ? MONITORING_STYLE : PLANNING_STYLE;
    
    // Update the base map tiles
    map.current.setStyle(targetStyle);

    // Re-inject H3 layers when the new style finishes loading
    map.current.once('styledata', () => {
      addCustomLayers(map.current!, riskData);
    });
  }, [mapMode]);

  // 3. Handle Live Data Updates
  useEffect(() => {
    if (map.current && riskData) {
      const source = map.current.getSource('h3-cells') as maplibregl.GeoJSONSource;
      if (source) {
        source.setData(riskData);
      } else if (map.current.isStyleLoaded()) {
        // Fallback if data arrives before source is added during style switch
        addCustomLayers(map.current, riskData);
      }
    }
  }, [riskData]);

  return (
    <div className="relative w-full h-full md:rounded-lg overflow-hidden md:border border-[#262626]">
      <div ref={mapContainer} className="w-full h-full" />

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