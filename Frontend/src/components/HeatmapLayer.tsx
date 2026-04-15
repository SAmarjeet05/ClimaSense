import React, { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';
import './HeatmapLayer.css';

interface HeatmapData {
  lat: number;
  lng: number;
  temperature: number;
  rainfall?: number;
  state?: string;
  humidity?: number;
}

interface HeatmapLayerProps {
  data: HeatmapData[];
  mode?: 'temperature' | 'rainfall' | 'risk';
}

/**
 * Calculate risk score: combines temperature and rainfall
 * Risk = 0.6 * normalized_temp + 0.4 * normalized_rain
 */
function calculateRiskScore(
  temperature: number,
  rainfall: number | undefined,
  minTemp: number,
  maxTemp: number,
  minRain: number,
  maxRain: number
): number {
  const tempRange = maxTemp - minTemp || 1;
  const rainRange = maxRain - minRain || 1;

  const tempNorm = (temperature - minTemp) / tempRange;
  const rainNorm = rainfall ? Math.min(1, (rainfall - minRain) / rainRange) : 0;

  return 0.6 * tempNorm + 0.4 * rainNorm;
}

/**
 * Production-grade heatmap layer with multiple modes and interactions
 */
const HeatmapLayer: React.FC<HeatmapLayerProps> = ({ data, mode = 'temperature' }) => {
  const map = useMap();
  const heatLayerRef = useRef<any>(null);
  const markersRef = useRef<L.FeatureGroup>(new L.FeatureGroup());

  useEffect(() => {
    if (!data || data.length === 0) return;

    // Remove existing layers
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
    }
    if (markersRef.current) {
      map.removeLayer(markersRef.current);
    }

    // Calculate ranges for normalization
    const temps = data.map(d => d.temperature);
    const minTemp = Math.min(...temps);
    const maxTemp = Math.max(...temps);

    const rains = data
      .map(d => d.rainfall || 0)
      .filter(r => r > 0);
    const minRain = Math.min(...rains);
    const maxRain = Math.max(...rains);

    // Prepare data based on mode
    let heatData: Array<[number, number, number]>;

    if (mode === 'temperature') {
      heatData = data.map(d => {
        const normalized = (d.temperature - minTemp) / (maxTemp - minTemp || 1);
        return [d.lat, d.lng, normalized];
      });
    } else if (mode === 'rainfall') {
      heatData = data.map(d => {
        const rainfall = d.rainfall || 0;
        const normalized = rainfall > 0 ? (rainfall - minRain) / (maxRain - minRain || 1) : 0;
        return [d.lat, d.lng, normalized];
      });
    } else {
      // Risk mode: combine both
      heatData = data.map(d => {
        const risk = calculateRiskScore(
          d.temperature,
          d.rainfall,
          minTemp,
          maxTemp,
          minRain,
          maxRain
        );
        return [d.lat, d.lng, Math.min(1, risk)];
      });
    }

    // Create heatmap with proper gradient
    const gradient =
      mode === 'temperature'
        ? {
            0.0: '#0066ff', // cold blue
            0.25: '#00ccff', // cool cyan
            0.5: '#00ff00', // moderate green
            0.7: '#ffff00', // warm yellow
            0.9: '#ff9900', // hot orange
            1.0: '#ff0000', // extreme red
          }
        : mode === 'rainfall'
          ? {
              0.0: '#fff5e6', // very light
              0.2: '#ccccff', // light blue
              0.4: '#6666ff', // blue
              0.6: '#0099ff', // cyan
              0.8: '#00ff00', // green
              1.0: '#0066cc', // dark blue (heavy rain)
            }
          : {
              0.0: '#00ff00', // safe green
              0.33: '#ffff00', // warning yellow
              0.66: '#ff9900', // danger orange
              1.0: '#ff0000', // critical red
            };

    // Create heat layer with optimized settings
    const heatLayer = (L as any).heatLayer(heatData, {
      radius: 30,
      blur: 25,
      maxZoom: 10,
      gradient: gradient,
      minOpacity: 0.3,
      max: 1.0,
    });

    heatLayer.addTo(map);
    heatLayerRef.current = heatLayer;

    // Create tooltip markers (invisible but interactive)
    const featureGroup = new L.FeatureGroup();

    data.forEach((point, index) => {
      const marker = L.circleMarker([point.lat, point.lng], {
        radius: 0,
        opacity: 0,
        fillOpacity: 0,
      });

      // Build tooltip text based on mode
      let tooltipText = `<b>${point.state || `Location ${index + 1}`}</b><br/>`;

      if (mode === 'temperature') {
        tooltipText += `🌡️ Temperature: ${point.temperature.toFixed(1)}°C<br/>`;
      } else if (mode === 'rainfall') {
        tooltipText += `🌧️ Rainfall: ${(point.rainfall || 0).toFixed(1)}mm<br/>`;
      } else {
        const risk = calculateRiskScore(
          point.temperature,
          point.rainfall,
          minTemp,
          maxTemp,
          minRain,
          maxRain
        );
        const riskLevel =
          risk < 0.33 ? '🟢 Low' : risk < 0.66 ? '🟡 Medium' : '🔴 High';
        tooltipText += `⚠️ Risk Score: ${(risk * 100).toFixed(0)}% ${riskLevel}<br/>`;
        tooltipText += `🌡️ Temp: ${point.temperature.toFixed(1)}°C<br/>`;
        tooltipText += `🌧️ Rain: ${(point.rainfall || 0).toFixed(1)}mm`;
      }

      marker
        .bindTooltip(tooltipText, {
          permanent: false,
          direction: 'top',
          offset: [0, -10],
          className: 'heatmap-tooltip',
        })
        .addTo(featureGroup);
    });

    featureGroup.addTo(map);
    markersRef.current = featureGroup;

    // Animate map to center
    if (data.length > 0) {
      setTimeout(() => {
        map.flyTo([20.5, 78.9], 5, { duration: 1 });
      }, 300);
    }

    return () => {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
      }
      if (markersRef.current) {
        map.removeLayer(markersRef.current);
      }
    };
  }, [data, mode, map]);

  return null;
};

export default HeatmapLayer;
