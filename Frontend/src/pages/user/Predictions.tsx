import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, MapPin, Calendar, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { GlassCard } from '@/components/common/GlassCard';
import { ChartContainer } from '@/components/common/ChartContainer';
import { climateAPI } from '@/services/api';

const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];

// Available cities with coordinates for predictions (39 cities from NASA dataset)
// Coordinates extracted directly from nasa_india_40cities.csv for accuracy
const availableCities = [
  { name: 'Agartala', lat: 23.83, lon: 91.28 },
  { name: 'Agra', lat: 27.18, lon: 78.01 },
  { name: 'Ahmedabad', lat: 23.02, lon: 72.57 },
  { name: 'Bangalore', lat: 12.97, lon: 77.59 },
  { name: 'Bhopal', lat: 23.25, lon: 77.41 },
  { name: 'Bhubaneswar', lat: 20.3, lon: 85.82 },
  { name: 'Chandigarh', lat: 30.73, lon: 76.78 },
  { name: 'Chennai', lat: 13.08, lon: 80.27 },
  { name: 'Coimbatore', lat: 11.01, lon: 76.96 },
  { name: 'Dehradun', lat: 30.32, lon: 78.03 },
  { name: 'Delhi', lat: 28.6, lon: 77.2 },
  { name: 'Ghaziabad', lat: 28.67, lon: 77.45 },
  { name: 'Greater Noida', lat: 28.47, lon: 77.5 },
  { name: 'Guwahati', lat: 26.14, lon: 91.73 },
  { name: 'Hyderabad', lat: 17.38, lon: 78.48 },
  { name: 'Imphal', lat: 24.81, lon: 93.94 },
  { name: 'Indore', lat: 22.72, lon: 75.86 },
  { name: 'Jaipur', lat: 26.91, lon: 75.78 },
  { name: 'Jodhpur', lat: 26.24, lon: 73.02 },
  { name: 'Kanpur', lat: 26.44, lon: 80.33 },
  { name: 'Kochi', lat: 9.93, lon: 76.26 },
  { name: 'Kolkata', lat: 22.57, lon: 88.36 },
  { name: 'Lucknow', lat: 26.85, lon: 80.95 },
  { name: 'Meerut', lat: 28.98, lon: 77.7 },
  { name: 'Mumbai', lat: 19.07, lon: 72.87 },
  { name: 'Mysore', lat: 12.3, lon: 76.65 },
  { name: 'Noida', lat: 28.53, lon: 77.39 },
  { name: 'Patna', lat: 25.59, lon: 85.13 },
  { name: 'Prayagraj', lat: 25.45, lon: 81.84 },
  { name: 'Pune', lat: 18.52, lon: 73.85 },
  { name: 'Raipur', lat: 21.25, lon: 81.63 },
  { name: 'Ranchi', lat: 23.34, lon: 85.31 },
  { name: 'Shillong', lat: 25.57, lon: 91.88 },
  { name: 'Srinagar', lat: 34.08, lon: 74.79 },
  { name: 'Surat', lat: 21.17, lon: 72.83 },
  { name: 'Trivandrum', lat: 8.52, lon: 76.93 },
  { name: 'Udaipur', lat: 24.58, lon: 73.68 },
  { name: 'Varanasi', lat: 25.32, lon: 82.97 },
  { name: 'Visakhapatnam', lat: 17.68, lon: 83.22 }
];

interface ForecastPoint {
  year: number;
  temperature: number;
  rainfall: number;
  type: 'historical' | 'predicted';
  confidence?: number;
}

const Predictions: React.FC = () => {
  const [year, setYear] = useState(2026);
  const [month, setMonth] = useState(6);
  const [selectedCity, setSelectedCity] = useState(availableCities[24]); // Mumbai by default
  const day = 15; // Fixed day (month-level predictions ignore day)
  const [predicted, setPredicted] = useState<{ temperature_celsius?: number; rainfall_mm?: number; temperature?: number; rainfall?: number } | null>(null);
  const [forecasts, setForecasts] = useState<ForecastPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [forecastLoading, setForecastLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forecastError, setForecastError] = useState<string | null>(null);

  // Load forecast data on mount and when city or month changes
  useEffect(() => {
    loadForecastData();
  }, [selectedCity, month]);

  const loadForecastData = async () => {
    try {
      setForecastLoading(true);
      setForecastError(null);
      
      const data = await climateAPI.getForecast(selectedCity.name, 10, month);
      
      if (data?.historical && data?.predicted) {
        // Combine historical and predicted data
        const combined = [
          ...data.historical.map((h: any) => ({
            year: h.year,
            temperature: h.temperature,
            rainfall: h.rainfall,
            type: 'historical'
          })),
          ...data.predicted.map((p: any) => ({
            year: p.year,
            temperature: p.temperature,
            rainfall: p.rainfall,
            type: 'predicted',
            confidence: p.confidence
          }))
        ];
        
        setForecasts(combined);
        console.log('✓ Forecast data loaded for', selectedCity.name, 'month', month, ':', combined.length, 'data points');
      }
    } catch (err) {
      console.error('Error loading forecast:', err);
      setForecastError('Failed to load forecast data');
    } finally {
      setForecastLoading(false);
    }
  };

  const handlePredict = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Call predict with new schema: year, month, day, city, latitude, longitude
      const data = await climateAPI.predict(
        year,
        month,
        day,
        selectedCity.name,
        selectedCity.lat,
        selectedCity.lon
      );
      
      if (data) {
        setPredicted({
          temperature_celsius: data.temperature_celsius,
          rainfall_mm: data.rainfall_mm
        });
        console.log('✓ Prediction generated for', selectedCity.name, ':', data);
      }
    } catch (err: any) {
      console.error('Error making prediction:', err);
      // Extract error message from response
      const errorMsg = err.response?.data?.detail || 'Failed to generate prediction. Please try again.';
      setError(errorMsg);
      setPredicted(null);
    } finally {
      setLoading(false);
    }
  };

  // Transform forecast data for chart with prediction indicator line
  const chartData = forecasts.map(f => ({
    ...f,
    tempDisplay: f.temperature,
    isHistorical: f.type === 'historical'
  }));

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Climate Predictions</h1>
        <p className="text-muted-foreground text-sm mt-1">AI-powered climate forecasting for Indian regions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <GlassCard className="lg:col-span-1 space-y-5">
          <h3 className="text-foreground font-semibold flex items-center gap-2"><Brain className="w-4 h-4 text-primary" /> Prediction Input</h3>
          
          {error && (
            <div className="flex items-center gap-2 text-xs text-warning bg-warning/10 p-2 rounded border border-warning/20">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label className="text-xs text-muted-foreground block mb-1.5">Year</label>
              <input 
                type="number" 
                value={year} 
                onChange={e => setYear(+e.target.value)} 
                min={2025} 
                max={2050}
                disabled={loading}
                className="w-full bg-muted/30 border border-border/20 rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary/50 disabled:opacity-50" 
              />
              <p className="text-[10px] text-muted-foreground mt-1">Range: 2025-2050</p>
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1.5">Month</label>
              <select 
                value={month} 
                onChange={e => setMonth(+e.target.value)}
                disabled={loading}
                className="w-full bg-muted/30 border border-border/20 rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary/50 disabled:opacity-50">
                {months.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
              </select>
            </div>

            <div>
              <label className="text-xs text-muted-foreground block mb-1.5">City</label>
              <select 
                value={selectedCity.name} 
                onChange={e => {
                  const city = availableCities.find(c => c.name === e.target.value);
                  if (city) setSelectedCity(city);
                }}
                disabled={loading}
                className="w-full bg-muted/30 border border-border/20 rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary/50 disabled:opacity-50">
                {availableCities.map((c, i) => (
                  <option key={i} value={c.name}>{c.name}</option>
                ))}
              </select>
              <p className="text-[10px] text-muted-foreground mt-1">{selectedCity.lat.toFixed(2)}°N, {selectedCity.lon.toFixed(2)}°E</p>
            </div>
            <button 
              onClick={handlePredict}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-primary to-secondary text-primary-foreground rounded-lg font-medium text-sm hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? 'Generating...' : 'Generate Prediction'}
            </button>
            <p className="text-[10px] text-muted-foreground">
              📊 Forecast data: {forecasts.length} data points loaded
            </p>
          </div>
        </GlassCard>

        {/* Results */}
        <div className="lg:col-span-2 space-y-4">
          {predicted ? (
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <GlassCard glowColor="primary">
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Predicted Temperature</p>
                <p className="text-4xl font-bold text-primary mt-2">{(predicted.temperature_celsius || 0).toFixed(1)}°C</p>
                <p className="text-xs text-muted-foreground mt-2">{selectedCity.name} · {months[month - 1]} {year}</p>
              </GlassCard>
              <GlassCard glowColor="secondary">
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Predicted Rainfall</p>
                <p className="text-4xl font-bold text-secondary mt-2">{(predicted.rainfall_mm || 0).toFixed(1)}mm</p>
                <p className="text-xs text-muted-foreground mt-2">{selectedCity.name} · {months[month - 1]} {year}</p>
              </GlassCard>
            </motion.div>
          ) : (
            <GlassCard className="flex items-center justify-center py-16 text-center">
              <div>
                <Brain className="w-12 h-12 text-muted-foreground/30 mx-auto" />
                <p className="text-muted-foreground mt-3 text-sm">Configure parameters and generate a prediction</p>
              </div>
            </GlassCard>
          )}

          <ChartContainer title="Historical + Forecast" subtitle={`Temperature projection for ${selectedCity.name}`}>
            {forecastLoading ? (
              <div className="h-80 flex items-center justify-center">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  <p className="text-muted-foreground mt-2 text-sm">Loading forecast...</p>
                </div>
              </div>
            ) : forecastError ? (
              <div className="h-80 flex items-center justify-center">
                <div className="text-center text-warning text-sm">{forecastError}</div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="hsl(190,100%,50%)" stopOpacity={0.2} />
                      <stop offset="100%" stopColor="hsl(190,100%,50%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
                  <XAxis 
                    dataKey="year" 
                    tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} 
                    tickLine={false}
                    interval={Math.floor(chartData.length / 8) || 0}
                  />
                  <YAxis tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} tickLine={false} domain={['auto', 'auto']} />
                  <Tooltip 
                    content={({ active, payload }: any) => {
                      if (!active || !payload) return null;
                      return (
                        <div className="glass p-3 text-xs">
                          <p className="text-foreground font-medium mb-1">{payload[0]?.payload.year}</p>
                          <p className="text-primary">{payload[0]?.value?.toFixed(1)}°C</p>
                          <p className="text-muted-foreground text-[10px]">{payload[0]?.payload.type === 'predicted' ? 'Predicted' : 'Historical'}</p>
                        </div>
                      );
                    }} 
                  />
                  <Area type="monotone" dataKey="temperature" stroke="hsl(190,100%,50%)" fill="url(#forecastGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </ChartContainer>
        </div>
      </div>
    </motion.div>
  );
};

export default Predictions;
