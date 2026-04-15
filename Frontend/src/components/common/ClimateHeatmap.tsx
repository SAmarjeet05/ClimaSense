import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';

interface CityData {
  city: string;
  temperature: number;
  rainfall: number;
  risk_score: number;
  risk_level: string;
  latitude: number;
  longitude: number;
  year?: number;
}

interface ClimateHeatmapProps {
  riskData?: CityData[];
}

// India map center
const INDIA_CENTER: [number, number] = [20.5937, 78.9629];

export const ClimateHeatmap: React.FC<ClimateHeatmapProps> = ({ riskData: initialData }) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const heatLayer = useRef<any>(null);
  const markersGroup = useRef<L.FeatureGroup | null>(null);

  const [selectedMetric, setSelectedMetric] = useState<'risk' | 'temp' | 'rain'>('risk');
  const [year, setYear] = useState(2026);
  const [riskData, setRiskData] = useState<CityData[]>(initialData || []);
  const [loading, setLoading] = useState(false);
  const [citiesCount, setCitiesCount] = useState(0);

  // Fetch heatmap data for a specific year
  const fetchHeatmapData = async (selectedYear: number) => {
    try {
      setLoading(true);
      // Use direct backend URL to bypass proxy issues
      const url = `https://climasense-production.up.railway.app/api/dashboard/heatmap-data?year=${selectedYear}`;
      console.log(`Fetching heatmap data for year ${selectedYear}`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const response = await fetch(url, { 
        signal: controller.signal,
        mode: 'cors'  // Enable CORS
      });
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.data && Array.isArray(result.data) && result.data.length > 0) {
        setRiskData(result.data);
        setCitiesCount(result.count || result.data.length);
        console.log(`✓ Loaded ${result.data.length} cities for year ${selectedYear}`);
      } else {
        console.warn('No data in response');
        throw new Error('No city data received');
      }
    } catch (error: any) {
      console.error('Error fetching heatmap data:', error?.message || error);
      // Fallback: use initial data if available
      if (initialData && initialData.length > 0) {
        setRiskData(initialData);
        setCitiesCount(initialData.length);
        console.log(`Fallback: Using ${initialData.length} cities from initial data`);
      }
    } finally {
      setLoading(false);
    }
  };

  // Fetch data when component mounts or year changes
  useEffect(() => {
    if (riskData.length === 0 || riskData.length < 10) {
      // Only fetch if we don't have data or have very few cities
      fetchHeatmapData(year);
    }
  }, []);

  // Refetch when year changes
  useEffect(() => {
    fetchHeatmapData(year);
  }, [year]);

  // Initialize and update map
  useEffect(() => {
    if (!mapContainer.current || !riskData || riskData.length === 0) return;

    // Ensure container has proper dimensions
    if (mapContainer.current) {
      const rect = mapContainer.current.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) {
        console.warn('Map container has zero dimensions, waiting...');
        return;
      }
    }

    // Initialize map
    if (!map.current) {
      try {
        map.current = L.map(mapContainer.current).setView(INDIA_CENTER, 5);

        // Add dark CartoDB tiles
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
          attribution: '© CartoDB',
          subdomains: 'abcd',
          maxZoom: 20,
        }).addTo(map.current);

        // Initialize markers group
        markersGroup.current = L.featureGroup().addTo(map.current);
        
        // Invalidate size when map loads
        map.current.on('load', () => {
          map.current?.invalidateSize();
        });
      } catch (error) {
        console.error('Error initializing map:', error);
        return;
      }
    }

    // Clear previous heat layer and markers
    if (heatLayer.current && map.current) {
      try {
        map.current.removeLayer(heatLayer.current);
      } catch (e) {
        console.warn('Error removing previous heat layer:', e);
      }
      heatLayer.current = null;
    }
    if (markersGroup.current) {
      markersGroup.current.clearLayers();
    }

    // Get metric values for heatmap
    const getMetricValue = (city: CityData): number => {
      if (selectedMetric === 'risk') {
        return city.risk_score / 100;
      } else if (selectedMetric === 'temp') {
        // Normalize: 15°C = 0.2, 35°C = 1.0
        return Math.max(0.2, Math.min(1, (city.temperature - 10) / 30));
      } else {
        // Normalize: 0mm = 0.2, 150mm = 1.0
        return Math.max(0.2, Math.min(1, city.rainfall / 150));
      }
    };

    const getColor = (value: number): string => {
      if (selectedMetric === 'temp') {
        // Blue to Red for temperature
        if (value < 0.3) return '#0066ff'; // Blue - cold
        if (value < 0.5) return '#00ff00'; // Green - cool
        if (value < 0.7) return '#ffff00'; // Yellow - warm
        if (value < 0.85) return '#ff8800'; // Orange - hot
        return '#ff0000'; // Red - very hot
      } else if (selectedMetric === 'rain') {
        // Blue scale for rainfall
        if (value < 0.3) return '#ffffcc'; // Light - dry
        if (value < 0.5) return '#99ccff'; // Light blue - some rain
        if (value < 0.7) return '#3366ff'; // Blue - more rain
        if (value < 0.85) return '#0033ff'; // Deep blue - heavy
        return '#000099'; // Very deep blue - very heavy
      } else {
        // Risk: Green to Red
        if (value < 0.3) return '#00ff00'; // Green - low
        if (value < 0.5) return '#ffff00'; // Yellow - medium
        if (value < 0.7) return '#ff8800'; // Orange - high
        if (value < 0.85) return '#ff0000'; // Red - critical
        return '#8b0000'; // Dark red - extreme
      }
    };

    // Create heat data points - validate coordinates
    const heatData: Array<[number, number, number]> = [];
    riskData.forEach((city) => {
      if (
        city.latitude != null &&
        city.longitude != null &&
        typeof city.latitude === 'number' &&
        typeof city.longitude === 'number' &&
        !isNaN(city.latitude) &&
        !isNaN(city.longitude)
      ) {
        const value = getMetricValue(city);
        heatData.push([city.latitude, city.longitude, value]);
      }
    });

    console.log(`✓ Heat layer data: ${heatData.length} valid points from ${riskData.length} cities`);

    // Add heat layer with gradient
    const gradient: Record<number, string> = {};
    for (let i = 0; i <= 1; i += 0.1) {
      gradient[i] = getColor(i);
    }

    if (map.current && heatData.length > 0) {
      try {
        // Ensure map is ready before adding heat layer
        if (!map.current._container) {
          console.warn('Map container not ready, skipping heat layer');
          return;
        }

        // Small delay to ensure map is fully initialized
        setTimeout(() => {
          if (map.current && heatData.length > 0) {
            try {
              // Ensure container still has dimensions
              const rect = map.current._container.getBoundingClientRect();
              if (rect.width > 0 && rect.height > 0) {
                heatLayer.current = (L as any).heatLayer(heatData, {
                  radius: 60,
                  blur: 30,
                  maxZoom: 18,
                  gradient: gradient,
                  minOpacity: 0.3
                }).addTo(map.current);
                
                // Trigger map resize
                map.current.invalidateSize();
              }
            } catch (error) {
              console.error('Error creating heat layer:', error);
            }
          }
        }, 100);
      } catch (error) {
        console.error('Error in heat layer setup:', error);
      }
    } else if (!heatData.length) {
      console.warn('No valid heat data points to display');
    }

    // Add city markers as overlay
    riskData.forEach((city) => {
      if (
        !city.latitude ||
        !city.longitude ||
        isNaN(city.latitude) ||
        isNaN(city.longitude)
      ) {
        return;
      }

      const value = getMetricValue(city);
      const markerColor = getColor(value);

      // Create circle marker
      const circle = L.circleMarker([city.latitude, city.longitude], {
        radius: 8,
        fillColor: markerColor,
        color: '#fff',
        weight: 2,
        opacity: 0.8,
        fillOpacity: 0.9
      });

      // Create tooltip HTML based on selected metric
      let tooltipHTML = `
        <div style="font-weight: bold; margin-bottom: 4px;">${city.city}</div>
      `;
      
      if (selectedMetric === 'risk') {
        // Show all three metrics when Risk is selected
        tooltipHTML += `
          <div>🔥 Risk: ${city.risk_score}/100 (${city.risk_level})</div>
          <div>🌡️ Temp: ${city.temperature.toFixed(1)}°C</div>
          <div>🌧️ Rain: ${city.rainfall.toFixed(1)}mm</div>
        `;
      } else if (selectedMetric === 'temp') {
        // Show only temperature when Temp is selected
        tooltipHTML += `<div>🌡️ Temperature: ${city.temperature.toFixed(1)}°C</div>`;
      } else if (selectedMetric === 'rain') {
        // Show only rainfall when Rain is selected
        tooltipHTML += `<div>🌧️ Rainfall: ${city.rainfall.toFixed(1)}mm</div>`;
      }
      
      tooltipHTML += `<div style="font-size: 0.8em; margin-top: 4px; color: #999;">Year: ${city.year || year}</div>`;

      circle.bindTooltip(tooltipHTML, {
        permanent: false,
        direction: 'top',
        className: 'climate-tooltip',
        offset: [0, -10]
      });

      circle.on('mouseover', function() {
        this.setRadius(12);
        this.setStyle({ weight: 3, fillOpacity: 1 });
      });

      circle.on('mouseout', function() {
        this.setRadius(8);
        this.setStyle({ weight: 2, fillOpacity: 0.9 });
      });

      if (markersGroup.current) {
        markersGroup.current.addLayer(circle);
      }
    });

  }, [riskData, selectedMetric, year]);

  const getGradientBar = (): JSX.Element => {
    if (selectedMetric === 'temp') {
      return (
        <div className="flex items-center h-8 rounded overflow-hidden border border-gray-400/30">
          <div className="flex-1 h-full" style={{ background: 'linear-gradient(90deg, #0066ff, #00ff00, #ffff00, #ff8800, #ff0000)' }} />
          <div className="px-2 py-1 text-xs text-gray-300 ml-2">
            <span className="text-xs">15°C</span>
            <span className="mx-2">→</span>
            <span className="text-xs">35°C</span>
          </div>
        </div>
      );
    } else if (selectedMetric === 'rain') {
      return (
        <div className="flex items-center h-8 rounded overflow-hidden border border-gray-400/30">
          <div className="flex-1 h-full" style={{ background: 'linear-gradient(90deg, #ffffcc, #99ccff, #3366ff, #0033ff, #000099)' }} />
          <div className="px-2 py-1 text-xs text-gray-300 ml-2">
            <span className="text-xs">0mm</span>
            <span className="mx-2">→</span>
            <span className="text-xs">150mm</span>
          </div>
        </div>
      );
    }
    return (
      <div className="flex items-center h-8 rounded overflow-hidden border border-gray-400/30">
        <div className="flex-1 h-full" style={{ background: 'linear-gradient(90deg, #00ff00, #ffff00, #ff8800, #ff0000, #8b0000)' }} />
        <div className="px-2 py-1 text-xs text-gray-300 ml-2">
          <span className="text-xs">Low</span>
          <span className="mx-2">→</span>
          <span className="text-xs">Critical</span>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="space-y-3">
        {/* Metric Selector */}
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedMetric('risk')}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              selectedMetric === 'risk'
                ? 'bg-red-500/30 text-red-300 border border-red-500'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            🔥 Risk
          </button>
          <button
            onClick={() => setSelectedMetric('temp')}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              selectedMetric === 'temp'
                ? 'bg-orange-500/30 text-orange-300 border border-orange-500'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            🌡️ Temp
          </button>
          <button
            onClick={() => setSelectedMetric('rain')}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              selectedMetric === 'rain'
                ? 'bg-blue-500/30 text-blue-300 border border-blue-500'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            🌧️ Rain
          </button>
          {/* City counter */}
          <div className="flex-1 text-right text-xs text-gray-400">
            {loading ? '⏳ Loading cities...' : `${citiesCount || riskData.length} cities`}
          </div>
        </div>

        {/* Year Slider */}
        <div className="flex items-center gap-3">
          <label className="text-xs text-gray-300 font-semibold">Year:</label>
          <input
            type="range"
            min="2007"
            max="2026"
            value={year}
            onChange={(e) => setYear(parseInt(e.target.value))}
            className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
          <span className="text-xs text-gray-300 font-mono w-12">{year}</span>
        </div>

        {/* Gradient Legend */}
        {getGradientBar()}
      </div>

      {/* Map Container */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="relative rounded-lg overflow-hidden border border-gray-700 h-96 shadow-2xl"
        ref={mapContainer}
        style={{
          filter: 'drop-shadow(0 0 20px rgba(0, 255, 0, 0.1))',
          minHeight: '400px',
          width: '100%',
          position: 'relative'
        }}
      />

      {/* Info Text */}
      <p className="text-xs text-gray-400 text-center">
        💡 Hover over city markers for details • Move slider to change year and see historical climate patterns
      </p>
    </div>
  );
};

export default ClimateHeatmap;
