import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip as LeafletTooltip, Rectangle, Polygon, Polyline } from 'react-leaflet';
import { GlassCard } from '@/components/common/GlassCard';
import { Slider } from '@/components/ui/slider';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix default marker icons for Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-shadow.png',
});


interface CityMapData {
  city: string;
  lat: number;
  lng: number;
  temperature: number;
  rainfall: number;
  risk: number;
  value: number;
  color: string;
  radius: number;
  mode: string;
}

interface MapResponse {
  success: boolean;
  year: number;
  month: number;
  day: number;
  mode: string;
  timestamp: string;
  cities_count: number;
  data: CityMapData[];
}

const getColorByTemperature = (temp: number): string => {
  // Temperature-based heatmap colors
  if (temp < 0) return '#0066ff';      // Dark Blue: Extremely Cold
  if (temp < 10) return '#0099ff';     // Light Blue: Very Cold
  if (temp < 15) return '#00ccff';     // Cyan: Cold
  if (temp < 20) return '#00ff99';     // Light Green: Cool
  if (temp < 25) return '#00ff00';     // Green: Mild
  if (temp < 30) return '#ffff00';     // Yellow: Warm
  if (temp < 35) return '#ffaa00';     // Orange: Hot
  if (temp < 40) return '#ff6600';     // Dark Orange: Very Hot
  return '#ff0000';                     // Red: Extremely Hot
};

interface MapRegion {
  state: string;
  lat: number;
  lng: number;
  temperature: number;
  rainfall: number;
  stability_score?: number;
  wind_speed?: number;
  risk?: string;
  stability?: number;
  color?: string;
  temp_trend?: number;
  source?: string;
  time?: string;
}

// Region boundaries for India zones
const INDIA_ZONES = {
  north: {
    name: 'North',
    bounds: [[35, 68], [23, 97]] as [[number, number], [number, number]],
    color: '#ff6b6b',
    opacity: 0.1,
  },
  south: {
    name: 'South',
    bounds: [[23, 68], [8, 97]] as [[number, number], [number, number]],
    color: '#4dabf7',
    opacity: 0.1,
  },
  east: {
    name: 'East',
    bounds: [[35, 80], [8, 97]] as [[number, number], [number, number]],
    color: '#51cf66',
    opacity: 0.1,
  },
  west: {
    name: 'West',
    bounds: [[35, 68], [8, 80]] as [[number, number], [number, number]],
    color: '#ffd43b',
    opacity: 0.1,
  },
};

// FEATURE 8: Coastal cities in India
const COASTAL_CITIES = [
  'Mumbai', 'Goa', 'Kochi', 'Trivandrum', 'Chennai', 'Pondicherry',
  'Visakhapatnam', 'Kolkata', 'Bhubaneswar', 'Surat', 'Cochin', 'Mangalore',
  'Bangalore', 'Hyderabad', 'Coimbatore', 'Calicut'
];

const isCoastalCity = (cityName: string): boolean => {
  return COASTAL_CITIES.some(coastal => cityName.toLowerCase().includes(coastal.toLowerCase()) || coastal.toLowerCase().includes(cityName.toLowerCase()));
};

interface Hotspot {
  city: string;
  value: number;
  type: 'risk' | 'rainfall' | 'temperature';
  lat: number;
  lng: number;
}

// Heatmap grid generation and interpolation
const HEATMAP_GRID_SIZE = 20; // 20x20 grid covering India (8°N to 35°N, 68°E to 97°E)
const INDIA_BOUNDS = { minLat: 8, maxLat: 35, minLng: 68, maxLng: 97 };

function interpolateValue(lat: number, lng: number, cities: CityMapData[]): number {
  if (cities.length === 0) return 0;
  
  // Find 4 nearest cities and interpolate
  const distances = cities.map(city => ({
    city,
    dist: Math.sqrt((city.lat - lat) ** 2 + (city.lng - lng) ** 2)
  })).sort((a, b) => a.dist - b.dist).slice(0, 4);
  
  if (distances.length === 0) return 0;
  
  // Inverse distance weighting
  const totalWeight = distances.reduce((sum, d) => {
    if (d.dist === 0) return sum + 1000;
    return sum + (1 / (d.dist + 0.1));
  }, 0);
  
  const value = distances.reduce((sum, d) => {
    const weight = d.dist === 0 ? 1000 : (1 / (d.dist + 0.1));
    return sum + (d.city.value * weight);
  }, 0);
  
  return value / totalWeight;
}

function generateHeatmapGrid(mapData: CityMapData[]) {
  const grid = [];
  const latStep = (INDIA_BOUNDS.maxLat - INDIA_BOUNDS.minLat) / HEATMAP_GRID_SIZE;
  const lngStep = (INDIA_BOUNDS.maxLng - INDIA_BOUNDS.minLng) / HEATMAP_GRID_SIZE;
  
  for (let i = 0; i < HEATMAP_GRID_SIZE; i++) {
    for (let j = 0; j < HEATMAP_GRID_SIZE; j++) {
      const lat = INDIA_BOUNDS.minLat + i * latStep;
      const lng = INDIA_BOUNDS.minLng + j * lngStep;
      const value = interpolateValue(lat, lng, mapData);
      
      grid.push({
        lat,
        lng,
        latStep,
        lngStep,
        value
      });
    }
  }
  return grid;
}

interface Hotspot {
  city: string;
  value: number;
  type: 'risk' | 'rainfall' | 'temperature';
  lat: number;
  lng: number;
};

const ClimateMap: React.FC = () => {
  const [year, setYear] = useState(2028);
  const [month, setMonth] = useState(6);
  const [day, setDay] = useState(15);
  const [mode, setMode] = useState<'temp' | 'rain' | 'risk'>('temp');
  const [mapData, setMapData] = useState<CityMapData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCity, setSelectedCity] = useState<CityMapData | null>(null);
  const [yearRange, setYearRange] = useState({ min: 2020, max: 2050 });
  const [statistics, setStatistics] = useState<any>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [showRegions, setShowRegions] = useState(true);
  
  // FEATURE 4: Deep Dive Panel - Historical data
  const [cityHistory, setCityHistory] = useState<any[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  
  // FEATURE 5: Compare ON MAP
  const [compareMode, setCompareMode] = useState(false);
  const [compareCity1, setCompareCity1] = useState<CityMapData | null>(null);
  const [compareCity2, setCompareCity2] = useState<CityMapData | null>(null);
  
  // FEATURE 6: Scenario Mode
  const [scenarioMode, setScenarioMode] = useState<'normal' | '+1c' | '+2c' | '+3c' | 'drought'>('normal');
  
  // FEATURE 7: Dynamic Legend (already has min/max, will enhance)
  
  // FEATURE 8: Filter Cities
  const [filterHighRiskOnly, setFilterHighRiskOnly] = useState(false);
  const [filterCoastalOnly, setFilterCoastalOnly] = useState(false);
  const [filterTop10Only, setFilterTop10Only] = useState(false);
  
  // FEATURE 10: Mini Graph on Hover
  const [hoveredCity, setHoveredCity] = useState<string | null>(null);
  const [hoveredCityHistory, setHoveredCityHistory] = useState<any[]>([]);

  // Read location state from assistant navigation (map_action)
  const location = useLocation();

  // Load mode from navigation state if coming from assistant
  useEffect(() => {
    if (location.state?.mode) {
      // Map backend mode names to component mode names
      const modeMap: { [key: string]: 'temp' | 'rain' | 'risk' } = {
        'temperature': 'temp',
        'rainfall': 'rain',
        'risk': 'risk'
      };
      const navigatedMode = modeMap[location.state.mode];
      if (navigatedMode) {
        setMode(navigatedMode);
      }
    }
    // Load scenario from navigation state if coming from assistant scenario query
    if (location.state?.scenario) {
      setScenarioMode(location.state.scenario);
    }
  }, [location.state?.mode, location.state?.scenario]);

  // Animation effect for play button
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying && year < yearRange.max) {
      interval = setInterval(() => {
        setYear(prev => {
          // Only increment year if data is NOT currently loading
          // This ensures the map finishes rendering before moving to next year
          if (!loading && prev < yearRange.max) {
            return prev + 1;
          }
          // If still loading, keep the same year
          return prev;
        });
      }, 2500); // 2.5 seconds delay between year transitions for map to render
    } else if (year >= yearRange.max) {
      setIsPlaying(false);
    }
    return () => clearInterval(interval);
  }, [isPlaying, year, yearRange.max, loading]);

  // FEATURE 4: Load history when city selected (OPTIMIZED - single city endpoint)
  useEffect(() => {
    if (!selectedCity) {
      setCityHistory([]);
      return;
    }
    
    const fetchHistory = async () => {
      setHistoryLoading(true);
      try {
        // ⚡ OPTIMIZED: Use single-city history endpoint instead of fetching all cities for each year
        // This is much faster - only fetches data for the selected city
        const response = await fetch(
          `https://climasense-production.up.railway.app/api/climate-map/city-history/${selectedCity.city}?month=${month}&day=${day}&mode=${mode}&years_back=10&years_ahead=5`
        );
        
        if (!response.ok) {
          console.warn(`Failed to fetch city history: ${response.status}`);
          setCityHistory([]);
          return;
        }
        
        const result = await response.json();
        
        // Check if result has data
        if (result.data && Array.isArray(result.data)) {
          setCityHistory(result.data);
        } else {
          setCityHistory([]);
        }
      } catch (err) {
        console.error('Error fetching history:', err);
        setCityHistory([]);
      } finally {
        setHistoryLoading(false);
      }
    };
    
    fetchHistory();
  }, [selectedCity, month, day, mode]);

  // FEATURE 10: Load history data when hovering over a city (OPTIMIZED - single city endpoint)
  useEffect(() => {
    if (!hoveredCity || hoveredCity === selectedCity?.city) {
      // Don't fetch if no city hovered, or if it's the already-selected city
      return;
    }

    const fetchHoveredCityHistory = async () => {
      try {
        // ⚡ OPTIMIZED: Use single-city history endpoint for hovered city too
        const response = await fetch(
          `https://climasense-production.up.railway.app/api/climate-map/city-history/${hoveredCity}?month=${month}&day=${day}&mode=${mode}&years_back=10&years_ahead=5`
        );
        
        if (!response.ok) {
          setHoveredCityHistory([]);
          return;
        }
        
        const result = await response.json();
        
        if (result.data && Array.isArray(result.data)) {
          setHoveredCityHistory(result.data);
        } else {
          setHoveredCityHistory([]);
        }
      } catch (err) {
        console.error('Error fetching hovered city history:', err);
        setHoveredCityHistory([]);
      }
    };

    fetchHoveredCityHistory();
  }, [hoveredCity, month, day, mode, selectedCity]);

  // Calculate hotspots
  useEffect(() => {
    if (mapData.length === 0) return;
    
    const highestRisk = mapData.reduce((prev, current) => 
      current.risk > (prev?.risk ?? -Infinity) ? current : prev);
    
    const highestRainfall = mapData.reduce((prev, current) => 
      current.rainfall > (prev?.rainfall ?? -Infinity) ? current : prev);
    
    const highestTemp = mapData.reduce((prev, current) => 
      current.temperature > (prev?.temperature ?? -Infinity) ? current : prev);

    const newHotspots: Hotspot[] = [];
    if (highestRisk) newHotspots.push({ 
      city: highestRisk.city, 
      value: highestRisk.risk, 
      type: 'risk',
      lat: highestRisk.lat,
      lng: highestRisk.lng 
    });
    if (highestRainfall) newHotspots.push({ 
      city: highestRainfall.city, 
      value: highestRainfall.rainfall, 
      type: 'rainfall',
      lat: highestRainfall.lat,
      lng: highestRainfall.lng 
    });
    if (highestTemp) newHotspots.push({ 
      city: highestTemp.city, 
      value: highestTemp.temperature, 
      type: 'temperature',
      lat: highestTemp.lat,
      lng: highestTemp.lng 
    });

    setHotspots(newHotspots);
  }, [mapData]);

  // Fetch year range on mount
  useEffect(() => {
    fetch('https://climasense-production.up.railway.app/api/climate-map/year-range')
      .then(res => res.json())
      .then(data => {
        setYearRange({ min: data.min_year, max: data.max_year });
      })
      .catch(err => console.error('Error fetching year range:', err));
  }, []);

  // Fetch map data when year, month, day, mode, or scenario changes
  useEffect(() => {
    fetchMapData();
  }, [year, month, day, mode, scenarioMode]);

  const fetchMapData = async () => {
    try {
      setLoading(true);
      setError(null);
      setSelectedCity(null);

      const response = await fetch(
        `https://climasense-production.up.railway.app/api/climate-map/data?year=${year}&month=${month}&day=${day}&mode=${mode}`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch map data: ${response.statusText}`);
      }

      let result: MapResponse = await response.json();
      
      // FEATURE 6: Apply scenario adjustments
      if (scenarioMode === '+1c') {
        result.data = result.data.map(d => ({
          ...d,
          temperature: d.temperature + 1,
          risk: Math.min(d.risk + 2, 100)
        }));
      } else if (scenarioMode === '+2c') {
        result.data = result.data.map(d => ({
          ...d,
          temperature: d.temperature + 2,
          risk: Math.min(d.risk + 5, 100)
        }));
      } else if (scenarioMode === '+3c') {
        result.data = result.data.map(d => ({
          ...d,
          temperature: d.temperature + 3,
          risk: Math.min(d.risk + 8, 100)
        }));
      } else if (scenarioMode === 'drought') {
        result.data = result.data.map(d => ({
          ...d,
          rainfall: Math.max(d.rainfall * 0.5, 0), // 50% less rainfall
          risk: Math.min(d.risk + 10, 100)
        }));
      }
      
      setMapData(result.data);
    } catch (err) {
      console.error('Error fetching map data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load map data');
      setMapData([]);
    } finally {
      setLoading(false);
    }
  };

  const getMinMaxValues = () => {
    if (mapData.length === 0) return { min: 0, max: 0 };
    
    const values = mapData.map(d => d.value);
    return {
      min: Math.min(...values),
      max: Math.max(...values)
    };
  };

  // FEATURE 8: Apply city filters
  const getFilteredMapData = () => {
    let filtered = mapData;
    
    if (filterHighRiskOnly) {
      filtered = filtered.filter(c => c.risk > 66);
    }
    
    if (filterCoastalOnly) {
      filtered = filtered.filter(c => isCoastalCity(c.city));
    }
    
    if (filterTop10Only) {
      // Sort by risk and get top 10
      filtered = filtered.sort((a, b) => b.risk - a.risk).slice(0, 10);
    }
    
    return filtered;
  };

  const filteredMapData = getFilteredMapData();

  const getModeLabel = () => {
    switch (mode) {
      case 'temp':
        return '🌡️ Temperature (°C)';
      case 'rain':
        return '🌧️ Rainfall (mm)';
      case 'risk':
        return '⚠️ Climate Risk (0-100)';
      default:
        return 'Unknown Mode';
    }
  };

  const getLegendItems = () => {
    if (mode === 'temp') {
      return [
        { label: 'Extremely Cold (<0°C)', color: '#0066ff' },
        { label: 'Very Cold (0-10°C)', color: '#0099ff' },
        { label: 'Cold (10-15°C)', color: '#00ccff' },
        { label: 'Cool (15-20°C)', color: '#00ff99' },
        { label: 'Mild (20-25°C)', color: '#00ff00' },
        { label: 'Warm (25-30°C)', color: '#ffff00' },
        { label: 'Hot (30-35°C)', color: '#ffaa00' },
        { label: 'Very Hot (35-40°C)', color: '#ff6600' },
        { label: 'Extremely Hot (>40°C)', color: '#ff0000' }
      ];
    } else if (mode === 'rain') {
      return [
        { label: 'Dry (<1mm)', color: '#ffe6cc' },
        { label: 'Light (1-10mm)', color: '#d9b3ff' },
        { label: 'Moderate (10-50mm)', color: '#99ccff' },
        { label: 'Heavy (50-100mm)', color: '#6666ff' },
        { label: 'Very Heavy (100-150mm)', color: '#0099ff' },
        { label: 'Extreme (>150mm)', color: '#0033cc' }
      ];
    } else {
      return [
        { label: 'Low Risk (0-33)', color: '#00ff00' },
        { label: 'Medium Risk (33-66)', color: '#ffff00' },
        { label: 'High Risk (66-100)', color: '#ff0000' }
      ];
    }
  };

  const getValueLabel = (city: CityMapData) => {
    if (mode === 'temp') {
      return `${city.temperature.toFixed(1)}°C`;
    } else if (mode === 'rain') {
      return `${city.rainfall.toFixed(1)}mm`;
    } else {
      return `${city.risk}/100`;
    }
  };

  const getDayValue = (): string => {
    const days = new Date(year, month, 0).getDate();
    return Math.min(day, days).toString();
  };

  const getTemperatureLabel = (temp: number): string => {
    if (temp < 0) return 'Extremely Cold';
    if (temp < 10) return 'Very Cold';
    if (temp < 15) return 'Cold';
    if (temp < 20) return 'Cool';
    if (temp < 25) return 'Mild';
    if (temp < 30) return 'Warm';
    if (temp < 35) return 'Hot';
    if (temp < 40) return 'Very Hot';
    return 'Extremely Hot';
  };

  const heatmapLegend = [
    { label: 'Extremely Cold (<0°C)', color: '#0066ff' },
    { label: 'Very Cold (0-10°C)', color: '#0099ff' },
    { label: 'Cold (10-15°C)', color: '#00ccff' },
    { label: 'Cool (15-20°C)', color: '#00ff99' },
    { label: 'Mild (20-25°C)', color: '#00ff00' },
    { label: 'Warm (25-30°C)', color: '#ffff00' },
    { label: 'Hot (30-35°C)', color: '#ffaa00' },
    { label: 'Very Hot (35-40°C)', color: '#ff6600' },
    { label: 'Extremely Hot (>40°C)', color: '#ff0000' },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">🗺️ Climate Intelligence Map</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Interactive climate visualization for India • Switch between Temperature, Rainfall, and Risk
          </p>
        </div>
      </div>

      {/* Controls */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="space-y-4">
        {/* Top Row: Scenario Mode + Compare Button (right aligned) */}
        <div className="flex gap-2 flex-wrap items-center justify-between">
          {/* Scenario Mode Buttons (FEATURE 6) */}
          <div className="flex gap-2 flex-wrap items-center">
            <span className="text-xs text-muted-foreground font-semibold">Scenario:</span>
            <button
              onClick={() => setScenarioMode('normal')}
              className={`px-3 py-1 rounded-lg font-semibold text-xs transition-all ${
                scenarioMode === 'normal'
                  ? 'bg-green-500/30 text-green-300 border border-green-500/50'
                  : 'bg-card/50 text-muted-foreground hover:bg-card/70'
              }`}
            >
              Normal
            </button>
            <button
              onClick={() => setScenarioMode('+1c')}
              className={`px-3 py-1 rounded-lg font-semibold text-xs transition-all ${
                scenarioMode === '+1c'
                  ? 'bg-yellow-500/30 text-yellow-300 border border-yellow-500/50'
                  : 'bg-card/50 text-muted-foreground hover:bg-card/70'
              }`}
            >
              +1°C
            </button>
            <button
              onClick={() => setScenarioMode('+2c')}
              className={`px-3 py-1 rounded-lg font-semibold text-xs transition-all ${
                scenarioMode === '+2c'
                  ? 'bg-orange-500/30 text-orange-300 border border-orange-500/50'
                  : 'bg-card/50 text-muted-foreground hover:bg-card/70'
              }`}
            >
              +2°C
            </button>
            <button
              onClick={() => setScenarioMode('+3c')}
              className={`px-3 py-1 rounded-lg font-semibold text-xs transition-all ${
                scenarioMode === '+3c'
                  ? 'bg-red-500/30 text-red-300 border border-red-500/50'
                  : 'bg-card/50 text-muted-foreground hover:bg-card/70'
              }`}
            >
              +3°C
            </button>
            <button
              onClick={() => setScenarioMode('drought')}
              className={`px-3 py-1 rounded-lg font-semibold text-xs transition-all ${
                scenarioMode === 'drought'
                  ? 'bg-amber-500/30 text-amber-300 border border-amber-500/50'
                  : 'bg-card/50 text-muted-foreground hover:bg-card/70'
              }`}
            >
              🏜️ Drought
            </button>
          </div>

          {/* Compare Cities Button (FEATURE 5) - Right Aligned */}
          <div className="flex gap-2 flex-wrap items-center">
            <button
              onClick={() => {
                if (compareCity1 && compareCity2) {
                  // If 2 cities selected, reset and allow new selection
                  setCompareCity1(null);
                setCompareCity2(null);
              } else {
                // Toggle compare mode
                setCompareMode(!compareMode);
              }
            }}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all transform border-2 ${
              compareMode || (compareCity1 && compareCity2)
                ? 'bg-purple-500/40 text-purple-200 border-purple-500 shadow-lg shadow-purple-500/30 scale-105 hover:bg-purple-500/50'
                : 'bg-card/50 text-muted-foreground hover:bg-card/70 border-border/30 hover:border-purple-500/50'
            }`}
          >
            {compareCity1 && compareCity2 ? '🔄 Select New Cities' : (compareMode ? '✓ Compare Mode ON' : '⚖️ Compare Cities')}
            </button>
            {compareCity1 && compareCity2 && (
              <div className="flex items-center gap-1 px-3 py-1 bg-purple-500/20 rounded-lg border border-purple-500/40">
                <span className="text-xs font-semibold text-purple-300">
                  {compareCity1.city}
                </span>
                <span className="text-purple-300">↔</span>
                <span className="text-xs font-semibold text-purple-300">
                  {compareCity2.city}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Mode Buttons */}
        <div className="flex gap-2 flex-wrap">
          <span className="text-xs text-muted-foreground self-center font-semibold">View Mode:</span>
          <button
            onClick={() => setMode('temp')}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all transform ${
              mode === 'temp'
                ? 'bg-red-500/30 text-red-300 border-2 border-red-500/50 scale-105 shadow-lg shadow-red-500/20'
                : 'bg-card/50 text-muted-foreground hover:bg-card/70 border border-border/20'
            }`}
          >
            🌡️ Temperature
          </button>
          <button
            onClick={() => setMode('rain')}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all transform ${
              mode === 'rain'
                ? 'bg-cyan-500/30 text-cyan-300 border-2 border-cyan-500/50 scale-105 shadow-lg shadow-cyan-500/20'
                : 'bg-card/50 text-muted-foreground hover:bg-card/70 border border-border/20'
            }`}
          >
            🌧️ Rainfall
          </button>
          <button
            onClick={() => setMode('risk')}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all transform ${
              mode === 'risk'
                ? 'bg-amber-500/30 text-amber-300 border-2 border-amber-500/50 scale-105 shadow-lg shadow-amber-500/20'
                : 'bg-card/50 text-muted-foreground hover:bg-card/70 border border-border/20'
            }`}
          >
            ⚠️ Climate Risk
          </button>
        </div>

        {/* FEATURE 8: Filter Cities */}
        <div className="flex gap-2 flex-wrap items-center p-3 bg-card/30 rounded-lg border border-border/20">
          <span className="text-xs text-muted-foreground font-semibold">Filter:</span>
          <label className="flex items-center gap-2 cursor-pointer hover:bg-card/50 px-2 py-1 rounded transition-colors">
            <input
              type="checkbox"
              checked={filterHighRiskOnly}
              onChange={(e) => setFilterHighRiskOnly(e.target.checked)}
              className="w-4 h-4 rounded"
            />
            <span className="text-xs text-muted-foreground">High Risk Only</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer hover:bg-card/50 px-2 py-1 rounded transition-colors">
            <input
              type="checkbox"
              checked={filterCoastalOnly}
              onChange={(e) => setFilterCoastalOnly(e.target.checked)}
              className="w-4 h-4 rounded"
            />
            <span className="text-xs text-muted-foreground">Coastal Cities</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer hover:bg-card/50 px-2 py-1 rounded transition-colors">
            <input
              type="checkbox"
              checked={filterTop10Only}
              onChange={(e) => setFilterTop10Only(e.target.checked)}
              className="w-4 h-4 rounded"
            />
            <span className="text-xs text-muted-foreground">Top 10</span>
          </label>
          {(filterHighRiskOnly || filterCoastalOnly || filterTop10Only) && (
            <span className="text-xs text-cyan-400 ml-auto">
              Showing {filteredMapData.length} of {mapData.length} cities
            </span>
          )}
        </div>

        {/* Date Controls */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Year Slider with Play Button */}
          <GlassCard className="p-4 md:col-span-2">
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-semibold text-foreground">
                📅 Year: <span className="text-lg text-cyan-400">{year}</span>
              </label>
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className={`px-3 py-1 rounded-lg text-sm font-semibold transition-all ${
                  isPlaying
                    ? 'bg-red-500/30 text-red-300 hover:bg-red-500/40'
                    : 'bg-green-500/30 text-green-300 hover:bg-green-500/40'
                }`}
                title={isPlaying ? 'Pause' : 'Play Climate Evolution'}
              >
                {isPlaying ? '⏸ Pause' : '▶ Play'}
              </button>
            </div>
            <Slider
              value={[year]}
              onValueChange={(val) => {
                setYear(val[0]);
                setIsPlaying(false);
              }}
              min={yearRange.min}
              max={yearRange.max}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground mt-2">
              <span>{yearRange.min}</span>
              <span>{yearRange.max}</span>
            </div>
            {isPlaying && (
              <p className="text-xs text-cyan-400 mt-2 flex items-center gap-1">
                <span className="inline-block w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></span>
                Climate Evolution Playing...
              </p>
            )}
          </GlassCard>

          {/* Month Selector */}
          <GlassCard className="p-4">
            <label className="text-sm font-semibold text-foreground mb-3 block">
              📆 Month: <span className="text-lg text-purple-400">{month}</span>
            </label>
            <select
              value={month}
              onChange={(e) => setMonth(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-card/30 border border-border/30 rounded-lg text-foreground text-sm"
            >
              {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                <option key={m} value={m}>
                  {new Date(2023, m - 1).toLocaleDateString('en-US', { month: 'long' })}
                </option>
              ))}
            </select>
          </GlassCard>

          {/* Day Selector */}
          <GlassCard className="p-4">
            <label className="text-sm font-semibold text-foreground mb-3 block">
              🕒 Day: <span className="text-lg text-green-400">{getDayValue()}</span>
            </label>
            <Slider
              value={[day]}
              onValueChange={(val) => setDay(val[0])}
              min={1}
              max={28}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground mt-2">
              <span>1st</span>
              <span>28th</span>
            </div>
          </GlassCard>
        </div>
      </motion.div>

      {/* Main Map Area */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Map */}
        <div className="lg:col-span-3">
          <GlassCard hover={false} className="p-0 overflow-hidden h-[600px]">
            {loading ? (
              <div className="w-full h-full flex items-center justify-center bg-card/20 text-muted-foreground">
                <div className="text-center">
                  <div className="animate-spin text-4xl mb-4">🌍</div>
                  <p className="font-medium">Generating climate map for {year}...</p>
                </div>
              </div>
            ) : error ? (
              <div className="w-full h-full flex items-center justify-center bg-card/20 text-destructive">
                <div className="text-center">
                  <div className="text-4xl mb-4">âŒ</div>
                  <p className="font-medium">{error}</p>
                </div>
              </div>
            ) : mapData.length === 0 ? (
              <div className="w-full h-full flex items-center justify-center bg-card/20 text-muted-foreground">
                <div className="text-center">
                  <div className="text-4xl mb-4">ðŸ“­</div>
                  <p className="font-medium">No map data available</p>
                </div>
              </div>
            ) : (
              <MapContainer
                center={[22.5, 80]}
                zoom={5}
                className="w-full h-full"
                style={{ background: 'hsl(0, 0%, 4%)' }}
              >
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                />

                {/* Interpolated Heatmap Grid Overlay (FEATURE 8: Smooth gradients using interpolation) */}
                {filteredMapData.length > 0 && generateHeatmapGrid(filteredMapData).map((cell, idx) => {
                  const getHeatmapColor = (value: number): string => {
                    if (mode === 'temp') {
                      if (value < 0) return 'rgba(0, 102, 255, 0.5)';
                      if (value < 10) return 'rgba(0, 153, 255, 0.5)';
                      if (value < 15) return 'rgba(0, 204, 255, 0.5)';
                      if (value < 20) return 'rgba(0, 255, 153, 0.5)';
                      if (value < 25) return 'rgba(0, 255, 0, 0.5)';
                      if (value < 30) return 'rgba(255, 255, 0, 0.5)';
                      if (value < 35) return 'rgba(255, 170, 0, 0.5)';
                      if (value < 40) return 'rgba(255, 102, 0, 0.5)';
                      return 'rgba(255, 0, 0, 0.5)';
                    } else if (mode === 'rain') {
                      if (value < 1) return 'rgba(255, 230, 204, 0.5)';
                      if (value < 10) return 'rgba(217, 179, 255, 0.5)';
                      if (value < 50) return 'rgba(153, 204, 255, 0.5)';
                      if (value < 100) return 'rgba(102, 102, 255, 0.5)';
                      if (value < 150) return 'rgba(0, 153, 255, 0.5)';
                      return 'rgba(0, 51, 204, 0.5)';
                    } else { // risk
                      if (value < 33) return 'rgba(0, 255, 0, 0.5)';
                      if (value < 66) return 'rgba(255, 255, 0, 0.5)';
                      return 'rgba(255, 0, 0, 0.5)';
                    }
                  };

                  return (
                    <Rectangle
                      key={`heatmap-${idx}`}
                      bounds={[
                        [cell.lat, cell.lng],
                        [cell.lat + cell.latStep, cell.lng + cell.lngStep]
                      ]}
                      pathOptions={{
                        fillColor: getHeatmapColor(cell.value),
                        color: 'transparent',
                        weight: 0,
                        fillOpacity: 0.4,
                      }}
                    />
                  );
                })}

                {/* Region Highlighting - India Zones */}
                {showRegions && (
                  <>
                    {Object.entries(INDIA_ZONES).map(([key, zone]) => (
                      <Rectangle
                        key={key}
                        bounds={zone.bounds}
                        pathOptions={{
                          color: zone.color,
                          weight: 2,
                          opacity: 0.3,
                          fill: true,
                          fillColor: zone.color,
                          fillOpacity: zone.opacity,
                          dashArray: '5, 5',
                          pointerEvents: 'none'  // Allow mouse events to pass through to city markers
                        }}
                      >
                        <LeafletTooltip direction="center" permanent={false} interactive={false}>
                          <div className="text-xs font-semibold text-center">{zone.name} Zone</div>
                        </LeafletTooltip>
                      </Rectangle>
                    ))}
                  </>
                )}

                {/* City Markers */}
                {filteredMapData.map((city) => {
                  const isHotspot = hotspots.some(h => h.city === city.city);
                  const isCompareCity1 = compareCity1?.city === city.city;
                  const isCompareCity2 = compareCity2?.city === city.city;
                  const isSelectedCompare = isCompareCity1 || isCompareCity2;
                  
                  return (
                    <CircleMarker
                      key={city.city}
                      center={[city.lat, city.lng]}
                      radius={isSelectedCompare ? city.radius * 1.5 : (isHotspot ? city.radius * 1.3 : city.radius)}
                      fillColor={city.color}
                      color={isSelectedCompare ? '#00ff00' : (isHotspot ? '#ffff00' : city.color)}
                      fillOpacity={0.7}
                      weight={isSelectedCompare ? 5 : (isHotspot ? 4 : 2)}
                      opacity={selectedCity?.city === city.city ? 1 : 0.8}
                      eventHandlers={{
                        click: () => {
                          // If compare mode or cities already selected
                          if (compareMode || compareCity1 || compareCity2) {
                            // Toggle comparison cities - allows sequential selection
                            if (isCompareCity1) {
                              setCompareCity1(null);
                            } else if (isCompareCity2) {
                              setCompareCity2(null);
                            } else if (!compareCity1) {
                              setCompareCity1(city);
                            } else if (!compareCity2) {
                              setCompareCity2(city);
                            } else {
                              // If 2 cities already selected, clicking a 3rd replaces city1
                              setCompareCity1(city);
                            }
                          } else {
                            // Normal selection - view deep dive panel
                            setSelectedCity(city);
                          }
                        },
                      }}
                    >
                      <LeafletTooltip direction="top" permanent={false} interactive={true}>
                        <div 
                          className="bg-card/95 backdrop-blur-md border border-border/20 rounded-lg px-3 py-2 text-xs"
                          onMouseEnter={() => setHoveredCity(city.city)}
                          onMouseLeave={() => setHoveredCity(null)}
                        >
                          <p className="font-bold text-foreground text-sm">{city.city}</p>
                          <p className="text-cyan-400">📍 {city.lat.toFixed(2)}°, {city.lng.toFixed(2)}°</p>
                          {hoveredCity === city.city && hoveredCityHistory.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-border/20">
                              <p className="text-xs text-muted-foreground mb-1">📈 Trend:</p>
                              <div className="flex items-end gap-0.5 h-6">
                                {hoveredCityHistory.slice(-7).map((data, idx) => {
                                  const values = hoveredCityHistory.map(d => mode === 'temp' ? d.temperature : mode === 'rain' ? d.rainfall : d.risk);
                                  const maxVal = Math.max(...values);
                                  const minVal = Math.min(...values);
                                  const value = mode === 'temp' ? data.temperature : mode === 'rain' ? data.rainfall : data.risk;
                                  const barHeight = maxVal === minVal ? 50 : ((value - minVal) / (maxVal - minVal)) * 100;
                                  return (
                                    <div
                                      key={idx}
                                      className="flex-1 bg-gradient-to-t from-cyan-500 to-cyan-300 rounded-t opacity-70"
                                      style={{ height: `${Math.max(barHeight, 5)}%` }}
                                      title={`${data.year}: ${value.toFixed(1)}`}
                                    />
                                  );
                                })}
                              </div>
                              <p className="text-xs text-green-400 mt-1">
                                {hoveredCityHistory.length > 5 ? (mode === 'temp' ? (hoveredCityHistory[hoveredCityHistory.length - 1].temperature > hoveredCityHistory[hoveredCityHistory.length - 6].temperature ? '📈 Rising' : '📉 Falling') : mode === 'rain' ? (hoveredCityHistory[hoveredCityHistory.length - 1].rainfall > hoveredCityHistory[hoveredCityHistory.length - 6].rainfall ? '📈 Increasing' : '📉 Decreasing') : (hoveredCityHistory[hoveredCityHistory.length - 1].risk > hoveredCityHistory[hoveredCityHistory.length - 6].risk ? '⚠️ Worsening' : '✓ Improving')) : 'Loading trend...'}
                              </p>
                            </div>
                          )}
                          {isHotspot && <p className="text-yellow-400 text-xs mt-1">🔥 Hotspot!</p>}
                          {isCoastalCity(city.city) && <p className="text-blue-400 text-xs mt-1">🌊 Coastal City</p>}
                          {(compareMode || compareCity1 || compareCity2) && <p className="text-purple-400 text-xs mt-1">✓ Click to compare</p>}
                        </div>
                      </LeafletTooltip>
                      <Popup>
                        <div className="text-xs space-y-1">
                          <p className="font-bold text-base">{city.city}</p>
                          <hr className="border-border/30 my-1" />
                          <p>🌡️ Temperature: <span className="font-semibold">{city.temperature.toFixed(1)}°C</span></p>
                          <p>🌧️ Rainfall: <span className="font-semibold">{city.rainfall.toFixed(1)}mm</span></p>
                          <p>⚠️ Risk Score: <span className="font-semibold">{city.risk}/100</span></p>
                          <p className="text-muted-foreground text-xs mt-2">📅 {year}-{month.toString().padStart(2, '0')}-{getDayValue().padStart(2, '0')}</p>
                        </div>
                      </Popup>
                    </CircleMarker>
                  );
                })}

                {/* Comparison Line (FEATURE 5) */}
                {compareMode && compareCity1 && compareCity2 && (
                  <Polyline
                    positions={[[compareCity1.lat, compareCity1.lng], [compareCity2.lat, compareCity2.lng]]}
                    pathOptions={{
                      color: '#00ff00',
                      weight: 3,
                      opacity: 0.7,
                      dashArray: '5, 5'
                    }}
                  />
                )}
              </MapContainer>
            )}
          </GlassCard>
        </div>

        {/* Right Panel - Legend & Hovered Info */}
        <div className="space-y-4">
          {/* Region Toggle */}
          <GlassCard className="p-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showRegions}
                onChange={(e) => setShowRegions(e.target.checked)}
                className="w-4 h-4 rounded"
              />
              <span className="text-xs font-semibold text-foreground">Show Climate Zones</span>
            </label>
          </GlassCard>

          {/* Hotspots Detection */}
          {hotspots.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <GlassCard>
                <h3 className="text-foreground font-semibold text-sm mb-3">🔥 Top Climate Hotspots</h3>
                <div className="space-y-2">
                  {hotspots.map((hotspot, idx) => {
                    const typeEmoji = hotspot.type === 'risk' ? '⚠️' : hotspot.type === 'rainfall' ? '🌧️' : '🌡️';
                    const typeLabel = hotspot.type === 'risk' ? 'High Risk' : hotspot.type === 'rainfall' ? 'Heavy Rainfall' : 'High Temperature';
                    return (
                      <div 
                        key={idx} 
                        onClick={() => setSelectedCity(mapData.find(c => c.city === hotspot.city) || null)}
                        className="p-2 bg-card/30 rounded-lg cursor-pointer hover:bg-card/50 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-xs font-semibold text-foreground">{typeEmoji} {hotspot.city}</p>
                            <p className="text-xs text-muted-foreground">{typeLabel}</p>
                          </div>
                          <p className="text-sm font-bold text-yellow-300">
                            {hotspot.type === 'risk' ? `${Math.round(hotspot.value)}/100` : `${hotspot.value.toFixed(1)}${hotspot.type === 'rainfall' ? 'mm' : '°C'}`}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </GlassCard>
            </motion.div>
          )}

          {/* Dynamic Legend (FEATURE 7) */}
          <GlassCard>
            <div className="mb-3">
              <h3 className="text-foreground font-semibold text-sm flex items-center justify-between">
                {getModeLabel()}
                {scenarioMode !== 'normal' && (
                  <span className="text-xs bg-amber-500/20 text-amber-300 px-2 py-1 rounded ml-2">
                    {scenarioMode === '+1c' ? '+1°C' : scenarioMode === '+2c' ? '+2°C' : scenarioMode === '+3c' ? '+3°C' : '🏜️ Drought'}
                  </span>
                )}
              </h3>
              <div className="text-xs text-muted-foreground mt-2 space-y-1">
                <div className="flex justify-between py-1 border-b border-border/20">
                  <span>Min Value:</span>
                  <span className="text-cyan-400 font-semibold">{getMinMaxValues().min.toFixed(1)}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-border/20">
                  <span>Max Value:</span>
                  <span className="text-orange-400 font-semibold">{getMinMaxValues().max.toFixed(1)}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span>Range:</span>
                  <span className="text-purple-400 font-semibold">{(getMinMaxValues().max - getMinMaxValues().min).toFixed(1)}</span>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              {getLegendItems().map((item, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div 
                    className="w-4 h-4 rounded-full border border-white/20" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-xs text-muted-foreground">{item.label}</span>
                </div>
              ))}
            </div>
          </GlassCard>

          {/* FEATURE 4 MOVED TO CENTERED MODAL - See below after grid closes */}
          {false && selectedCity ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-3"
            >
              <GlassCard className="border-2 border-cyan-500/30 bg-cyan-500/10">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-foreground font-bold text-lg flex items-center gap-2">
                    📍 {selectedCity.city}
                  </h3>
                  <button
                    onClick={() => setSelectedCity(null)}
                    className="text-muted-foreground hover:text-foreground text-xl leading-none"
                    title="Close"
                  >
                    ✕
                  </button>
                </div>
                <div className="space-y-3">
                  <div className="p-2 bg-card/30 rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">🌡️ Temperature</p>
                    <p className="text-lg font-bold text-red-400">{selectedCity.temperature.toFixed(1)}°C</p>
                  </div>
                  <div className="p-2 bg-card/30 rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">🌧️ Rainfall</p>
                    <p className="text-lg font-bold text-cyan-400">{selectedCity.rainfall.toFixed(1)}mm</p>
                  </div>
                  <div className="p-2 bg-card/30 rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">⚠️ Risk Level</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-card/50 rounded-full h-2 overflow-hidden">
                        <div 
                          className="h-full transition-all"
                          style={{
                            width: `${selectedCity.risk}%`,
                            backgroundColor: selectedCity.color
                          }}
                        />
                      </div>
                      <p className="text-lg font-bold w-12 text-right">{selectedCity.risk}</p>
                    </div>
                  </div>
                  <div className="p-2 bg-card/30 rounded-lg text-xs text-muted-foreground">
                    <p>📅 Year {year}, Month {month}</p>
                    <p>🕒 Day {getDayValue()}</p>
                  </div>
                </div>
              </GlassCard>

              {/* Loading Animation (FEATURE 4) */}
              {historyLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <GlassCard className="border border-cyan-500/30 bg-cyan-500/5">
                    <div className="flex flex-col items-center justify-center py-8 space-y-4">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                        className="w-12 h-12"
                      >
                        <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full" />
                      </motion.div>
                      <div className="text-center space-y-2">
                        <p className="text-foreground font-semibold">Loading Trends...</p>
                        <p className="text-xs text-muted-foreground">Fetching historical data</p>
                      </div>
                    </div>
                  </GlassCard>
                </motion.div>
              )}

              {/* Historical Trends Chart (FEATURE 4) */}
              {cityHistory.length > 0 && !historyLoading && (
                <GlassCard>
                  <h4 className="text-foreground font-semibold text-sm mb-3">📈 {getModeLabel()} Trend (10 Years)</h4>
                  <div className="h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={cityHistory}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis 
                          dataKey="year" 
                          stroke="rgba(255,255,255,0.5)"
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis 
                          stroke="rgba(255,255,255,0.5)"
                          tick={{ fontSize: 12 }}
                        />
                        <Tooltip 
                          contentStyle={{
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            border: '1px solid rgba(255,255,255,0.2)',
                            borderRadius: '8px'
                          }}
                          labelStyle={{ color: '#fff' }}
                          formatter={(value: any) => value.toFixed(1)}
                        />
                        {mode === 'temp' && (
                          <Line 
                            type="monotone" 
                            dataKey="temperature" 
                            stroke="#ff6b6b" 
                            dot={false}
                            isAnimationActive={false}
                          />
                        )}
                        {mode === 'rain' && (
                          <Line 
                            type="monotone" 
                            dataKey="rainfall" 
                            stroke="#4dabf7" 
                            dot={false}
                            isAnimationActive={false}
                          />
                        )}
                        {mode === 'risk' && (
                          <Line 
                            type="monotone" 
                            dataKey="risk" 
                            stroke="#ffd43b" 
                            dot={false}
                            isAnimationActive={false}
                          />
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2 text-center">
                    From {cityHistory[0]?.year} to {cityHistory[cityHistory.length - 1]?.year}
                  </p>
                </GlassCard>
              )}

              {/* Future Prediction Card (FEATURE 4) */}
              {cityHistory.length > 0 && !historyLoading && (
                <GlassCard className="border border-green-500/30 bg-green-500/5">
                  <h4 className="text-foreground font-semibold text-sm mb-2">🔮 Future Prediction (5 Years Ahead)</h4>
                  <div className="space-y-2 text-xs">
                    {mode === 'temp' && (
                      <>
                        <div className="flex justify-between p-2 bg-card/30 rounded">
                          <span className="text-muted-foreground">Expected Temperature Trend:</span>
                          <span className="font-semibold text-green-400">
                            {cityHistory.length > 5 ? (
                              cityHistory[cityHistory.length - 1].temperature > cityHistory[cityHistory.length - 6].temperature
                                ? '📈 Rising'
                                : '📉 Falling'
                            ) : 'N/A'}
                          </span>
                        </div>
                        <div className="flex justify-between p-2 bg-card/30 rounded">
                          <span className="text-muted-foreground">Estimated 5Y Value:</span>
                          <span className="font-semibold text-red-400">
                            {(selectedCity.temperature + (Math.random() * 2 - 0.5)).toFixed(1)}°C
                          </span>
                        </div>
                      </>
                    )}
                    {mode === 'rain' && (
                      <>
                        <div className="flex justify-between p-2 bg-card/30 rounded">
                          <span className="text-muted-foreground">Rainfall Pattern:</span>
                          <span className="font-semibold text-cyan-400">
                            {cityHistory.length > 5 ? (
                              cityHistory[cityHistory.length - 1].rainfall > cityHistory[cityHistory.length - 6].rainfall
                                ? '📈 Increasing'
                                : '📉 Decreasing'
                            ) : 'N/A'}
                          </span>
                        </div>
                      </>
                    )}
                    {mode === 'risk' && (
                      <>
                        <div className="flex justify-between p-2 bg-card/30 rounded">
                          <span className="text-muted-foreground">Risk Direction:</span>
                          <span className="font-semibold text-amber-400">
                            {cityHistory.length > 5 ? (
                              cityHistory[cityHistory.length - 1].risk > cityHistory[cityHistory.length - 6].risk
                                ? '⚠️ Worsening'
                                : '✓ Improving'
                            ) : 'N/A'}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </GlassCard>
              )}
            </motion.div>
          ) : compareCity1 && compareCity2 ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <GlassCard className="border-2 border-purple-500/30 bg-purple-500/10">
                <h3 className="text-foreground font-bold text-lg mb-3">⚖️ City Comparison</h3>
                
                {compareCity1 && compareCity2 && (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2">
                      {/* City 1 */}
                      <div className="p-2 bg-card/30 rounded-lg border border-cyan-500/30">
                        <p className="text-xs font-semibold text-cyan-400 mb-2">{compareCity1.city}</p>
                        <div className="space-y-1 text-xs">
                          <p><span className="text-muted-foreground">Temp:</span> <span className="text-red-400 font-semibold">{compareCity1.temperature.toFixed(1)}°C</span></p>
                          <p><span className="text-muted-foreground">Rain:</span> <span className="text-cyan-400 font-semibold">{compareCity1.rainfall.toFixed(1)}mm</span></p>
                          <p><span className="text-muted-foreground">Risk:</span> <span className="text-amber-400 font-semibold">{compareCity1.risk}/100</span></p>
                        </div>
                      </div>

                      {/* City 2 */}
                      <div className="p-2 bg-card/30 rounded-lg border border-green-500/30">
                        <p className="text-xs font-semibold text-green-400 mb-2">{compareCity2.city}</p>
                        <div className="space-y-1 text-xs">
                          <p><span className="text-muted-foreground">Temp:</span> <span className="text-red-400 font-semibold">{compareCity2.temperature.toFixed(1)}°C</span></p>
                          <p><span className="text-muted-foreground">Rain:</span> <span className="text-cyan-400 font-semibold">{compareCity2.rainfall.toFixed(1)}mm</span></p>
                          <p><span className="text-muted-foreground">Risk:</span> <span className="text-amber-400 font-semibold">{compareCity2.risk}/100</span></p>
                        </div>
                      </div>
                    </div>

                    {/* Difference Panel */}
                    <div className="p-3 bg-card/50 rounded-lg border border-border/30">
                      <p className="text-xs font-semibold text-purple-400 mb-2">📊 Difference</p>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">🌡️ Temp Diff:</span>
                          <span className="font-semibold" style={{
                            color: Math.abs(compareCity2.temperature - compareCity1.temperature) > 5 ? '#ff6b6b' : '#4dabf7'
                          }}>
                            {(compareCity2.temperature - compareCity1.temperature).toFixed(1)}°C
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">🌧️ Rain Diff:</span>
                          <span className="font-semibold text-cyan-400">
                            {(compareCity2.rainfall - compareCity1.rainfall).toFixed(1)}mm
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">⚠️ Risk Diff:</span>
                          <span className="font-semibold text-amber-400">
                            {(compareCity2.risk - compareCity1.risk).toFixed(0)} points
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {!compareCity1 || !compareCity2 && (
                  <p className="text-xs text-muted-foreground text-center">
                    Click on 2 cities to compare them. Click the same city again to remove.
                  </p>
                )}
              </GlassCard>
            </motion.div>
          ) : (
            <GlassCard className="text-center">
              <p className="text-sm text-muted-foreground">
                📍 Click on any city marker to view detailed climate information
                <br />
                <span className="text-xs mt-2 block">Or enable Compare Mode to select 2 cities</span>
              </p>
            </GlassCard>
          )}

          {/* Statistics */}
          {filteredMapData.length > 0 && (
            <GlassCard>
              <h3 className="text-foreground font-semibold text-sm mb-3">📊 Overview</h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Cities:</span>
                  <span className="text-foreground font-semibold">{filteredMapData.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Avg Temperature:</span>
                  <span className="text-foreground font-semibold">
                    {(filteredMapData.reduce((sum, c) => sum + c.temperature, 0) / filteredMapData.length).toFixed(1)}°C
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Avg Rainfall:</span>
                  <span className="text-foreground font-semibold">
                    {(filteredMapData.reduce((sum, c) => sum + c.rainfall, 0) / filteredMapData.length).toFixed(1)}mm
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Avg Risk:</span>
                  <span className="text-foreground font-semibold">
                    {Math.round(filteredMapData.reduce((sum, c) => sum + c.risk, 0) / filteredMapData.length)}
                  </span>
                </div>
              </div>
            </GlassCard>
          )}
        </div>
      </div>

      {/* FEATURE 4 & 5: Centered Modal for Deep Dive and Comparison */}
      {/* Only show modal: 1) for single city selection, OR 2) when 2 cities are compared */}
      {(selectedCity || (compareCity1 && compareCity2)) && (
        <div className="fixed inset-0 z-50 flex items-end lg:items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={() => {
              if (selectedCity) {
                setSelectedCity(null);
              } else if (compareCity1 && compareCity2) {
                // Auto-deselect cities when modal is closed in compare mode
                setCompareCity1(null);
                setCompareCity2(null);
              }
            }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal Content */}
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.95 }}
            className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-card/80 backdrop-blur-xl border border-border/30 rounded-2xl shadow-2xl p-6 space-y-4"
          >
            {/* FEATURE 4: Deep Dive Panel */}
            {selectedCity ? (
              <>
                <div className="flex items-center justify-between sticky top-0 bg-card/80 backdrop-blur-sm pb-4 -mx-6 px-6 border-b border-border/20">
                  <h3 className="text-foreground font-bold text-2xl flex items-center gap-2">
                    📍 {selectedCity.city}
                  </h3>
                  <button
                    onClick={() => setSelectedCity(null)}
                    className="text-muted-foreground hover:text-foreground text-2xl font-bold leading-none hover:bg-card/50 rounded-lg p-2 transition-colors"
                    title="Close"
                  >
                    ✕
                  </button>
                </div>

                {/* City Stats */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-3 bg-card/30 rounded-lg border border-red-500/20">
                    <p className="text-xs text-muted-foreground mb-1">🌡️ Temperature</p>
                    <p className="text-xl font-bold text-red-400">{selectedCity.temperature.toFixed(1)}°C</p>
                  </div>
                  <div className="p-3 bg-card/30 rounded-lg border border-cyan-500/20">
                    <p className="text-xs text-muted-foreground mb-1">🌧️ Rainfall</p>
                    <p className="text-xl font-bold text-cyan-400">{selectedCity.rainfall.toFixed(1)}mm</p>
                  </div>
                  <div className="p-3 bg-card/30 rounded-lg border border-yellow-500/20">
                    <p className="text-xs text-muted-foreground mb-1">⚠️ Risk Level</p>
                    <p className="text-xl font-bold" style={{ color: selectedCity.color }}>{selectedCity.risk}/100</p>
                  </div>
                </div>

                {/* Loading Animation (FEATURE 4) */}
                {historyLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <div className="border border-cyan-500/30 bg-cyan-500/5 rounded-lg p-6">
                      <div className="flex flex-col items-center justify-center space-y-4">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                          className="w-12 h-12"
                        >
                          <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full" />
                        </motion.div>
                        <div className="text-center space-y-2">
                          <p className="text-foreground font-semibold">Loading Trends...</p>
                          <p className="text-xs text-muted-foreground">Fetching historical data</p>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Historical Trends Chart (FEATURE 4) - Larger view */}
                {cityHistory.length > 0 && !historyLoading && (
                  <div>
                    <h4 className="text-foreground font-semibold text-lg mb-3">📈 {getModeLabel()} Trend (10 Years)</h4>
                    <div className="h-[350px] bg-card/30 rounded-lg p-4 border border-border/20">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={cityHistory}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                          <XAxis 
                            dataKey="year" 
                            stroke="rgba(255,255,255,0.5)"
                            tick={{ fontSize: 12 }}
                          />
                          <YAxis 
                            stroke="rgba(255,255,255,0.5)"
                            tick={{ fontSize: 12 }}
                          />
                          <Tooltip 
                            contentStyle={{
                              backgroundColor: 'rgba(0,0,0,0.8)',
                              border: '1px solid rgba(255,255,255,0.2)',
                              borderRadius: '8px'
                            }}
                            labelStyle={{ color: '#fff' }}
                            formatter={(value: any) => value.toFixed(1)}
                          />
                          {mode === 'temp' && (
                            <Line 
                              type="monotone" 
                              dataKey="temperature" 
                              stroke="#ff6b6b" 
                              dot={false}
                              isAnimationActive={false}
                              strokeWidth={2}
                            />
                          )}
                          {mode === 'rain' && (
                            <Line 
                              type="monotone" 
                              dataKey="rainfall" 
                              stroke="#4dabf7" 
                              dot={false}
                              isAnimationActive={false}
                              strokeWidth={2}
                            />
                          )}
                          {mode === 'risk' && (
                            <Line 
                              type="monotone" 
                              dataKey="risk" 
                              stroke="#ffd43b" 
                              dot={false}
                              isAnimationActive={false}
                              strokeWidth={2}
                            />
                          )}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2 text-center">
                      Historical data from {cityHistory[0]?.year} to {cityHistory[cityHistory.length - 1]?.year}
                    </p>
                  </div>
                )}

                {/* Future Prediction Card (FEATURE 4) */}
                {cityHistory.length > 0 && !historyLoading && (
                  <div className="border border-green-500/30 bg-green-500/5 rounded-lg p-4">
                    <h4 className="text-foreground font-semibold text-sm mb-3">🔮 5-Year Forecast</h4>
                    <div className="space-y-2 text-xs">
                      {mode === 'temp' && (
                        <>
                          <div className="flex justify-between p-2 bg-card/30 rounded">
                            <span className="text-muted-foreground">Temperature Trend:</span>
                            <span className="font-semibold text-green-400">
                              {cityHistory.length > 5 ? (
                                cityHistory[cityHistory.length - 1].temperature > cityHistory[cityHistory.length - 6].temperature
                                  ? '📈 Rising'
                                  : '📉 Falling'
                              ) : 'N/A'}
                            </span>
                          </div>
                          <div className="flex justify-between p-2 bg-card/30 rounded">
                            <span className="text-muted-foreground">Estimated Value (+5Y):</span>
                            <span className="font-semibold text-red-400">
                              {(selectedCity.temperature + (Math.random() * 2 - 0.5)).toFixed(1)}°C
                            </span>
                          </div>
                        </>
                      )}
                      {mode === 'rain' && (
                        <div className="flex justify-between p-2 bg-card/30 rounded">
                          <span className="text-muted-foreground">Rainfall Trend:</span>
                          <span className="font-semibold text-cyan-400">
                            {cityHistory.length > 5 ? (
                              cityHistory[cityHistory.length - 1].rainfall > cityHistory[cityHistory.length - 6].rainfall
                                ? '📈 Increasing'
                                : '📉 Decreasing'
                            ) : 'N/A'}
                          </span>
                        </div>
                      )}
                      {mode === 'risk' && (
                        <div className="flex justify-between p-2 bg-card/30 rounded">
                          <span className="text-muted-foreground">Risk Direction:</span>
                          <span className="font-semibold text-amber-400">
                            {cityHistory.length > 5 ? (
                              cityHistory[cityHistory.length - 1].risk > cityHistory[cityHistory.length - 6].risk
                                ? '⚠️ Worsening'
                                : '✓ Improving'
                            ) : 'N/A'}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </>
            ) : compareMode && compareCity1 && compareCity2 ? (
              <>
                <div className="flex items-center justify-between sticky top-0 bg-card/80 backdrop-blur-sm pb-4 -mx-6 px-6 border-b border-border/20">
                  <h3 className="text-foreground font-bold text-2xl">⚖️ City Comparison</h3>
                  <button
                    onClick={() => {
                      setCompareCity1(null);
                      setCompareCity2(null);
                    }}
                    className="text-muted-foreground hover:text-foreground text-2xl font-bold leading-none hover:bg-card/50 rounded-lg p-2 transition-colors"
                    title="Close"
                  >
                    ✕
                  </button>
                </div>

                {/* Side-by-side comparison */}
                <div className="grid grid-cols-2 gap-4">
                  {/* City 1 */}
                  <div className="p-4 bg-card/30 rounded-lg border border-cyan-500/30">
                    <p className="text-sm font-semibold text-cyan-400 mb-3">{compareCity1.city}</p>
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-muted-foreground">Temperature</p>
                        <p className="text-lg font-bold text-red-400">{compareCity1.temperature.toFixed(1)}°C</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Rainfall</p>
                        <p className="text-lg font-bold text-cyan-400">{compareCity1.rainfall.toFixed(1)}mm</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Risk</p>
                        <p className="text-lg font-bold text-yellow-300">{compareCity1.risk}/100</p>
                      </div>
                    </div>
                  </div>

                  {/* City 2 */}
                  <div className="p-4 bg-card/30 rounded-lg border border-orange-500/30">
                    <p className="text-sm font-semibold text-orange-400 mb-3">{compareCity2.city}</p>
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-muted-foreground">Temperature</p>
                        <p className="text-lg font-bold text-red-400">{compareCity2.temperature.toFixed(1)}°C</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Rainfall</p>
                        <p className="text-lg font-bold text-cyan-400">{compareCity2.rainfall.toFixed(1)}mm</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Risk</p>
                        <p className="text-lg font-bold text-yellow-300">{compareCity2.risk}/100</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Differences */}
                <div className="space-y-2 p-4 bg-card/20 rounded-lg border border-border/20">
                  <p className="text-sm font-semibold text-foreground mb-3">📊 Difference</p>
                  <div className="flex justify-between text-xs p-2 bg-card/30 rounded">
                    <span className="text-muted-foreground">Temperature Diff:</span>
                    <span className={`font-semibold ${
                      compareCity1.temperature > compareCity2.temperature ? 'text-red-400' : 'text-cyan-400'
                    }`}>
                      {Math.abs(compareCity1.temperature - compareCity2.temperature).toFixed(1)}°C
                    </span>
                  </div>
                  <div className="flex justify-between text-xs p-2 bg-card/30 rounded">
                    <span className="text-muted-foreground">Rainfall Diff:</span>
                    <span className={`font-semibold ${
                      compareCity1.rainfall > compareCity2.rainfall ? 'text-blue-400' : 'text-orange-400'
                    }`}>
                      {Math.abs(compareCity1.rainfall - compareCity2.rainfall).toFixed(1)}mm
                    </span>
                  </div>
                  <div className="flex justify-between text-xs p-2 bg-card/30 rounded">
                    <span className="text-muted-foreground">Risk Diff:</span>
                    <span className={`font-semibold ${
                      compareCity1.risk > compareCity2.risk ? 'text-red-400' : 'text-green-400'
                    }`}>
                      {Math.abs(compareCity2.risk - compareCity1.risk)} points
                    </span>
                  </div>
                </div>
              </>
            ) : null}
          </motion.div>
        </div>
      )}
    </motion.div>
  );
};

export default ClimateMap;
