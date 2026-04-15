import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { ChartContainer } from '@/components/common/ChartContainer';
import { climateAPI, intelligenceAPI } from '@/services/api';
import { mockTrendsData } from '@/services/api';

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload) return null;
  return (
    <div className="glass p-3 text-xs">
      <p className="text-foreground font-medium mb-1">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} style={{ color: p.color }}>{p.name}: {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}</p>
      ))}
    </div>
  );
};

const Trends: React.FC = () => {
  const [view, setView] = useState<'india' | 'state'>('india');
  const [trendsData, setTrendsData] = useState(mockTrendsData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rawData, setRawData] = useState<any>(null);
  const [co2Data, setCO2Data] = useState<any>(null);

  useEffect(() => {
    fetchTrendsData();
  }, []);

  // When view changes, re-aggregate the data
  useEffect(() => {
    if (rawData) {
      aggregateDataByView(rawData, view);
    }
  }, [view, rawData]);

  const aggregateDataByView = (data: any, currentView: 'india' | 'state') => {
    if (currentView === 'india') {
      // Aggregate to India-wide yearly averages
      aggregateToIndiaWide(data);
    } else {
      // Show regional/state-level data with region breakdown
      aggregateToStateLevel(data);
    }
  };

  const aggregateToIndiaWide = (data: any) => {
    const yearlyAverages: { [key: number]: { year: number; temperature: number; rainfall: number; co2?: number; count: number } } = {};
    
    if (Array.isArray(data.years)) {
      data.years.forEach((year: number, idx: number) => {
        if (!yearlyAverages[year]) {
          yearlyAverages[year] = { year, temperature: 0, rainfall: 0, count: 0 };
        }
        
        if (typeof data.temperatures?.[idx] === 'number') {
          yearlyAverages[year].temperature += data.temperatures[idx];
        }
        if (typeof data.rainfall?.[idx] === 'number') {
          yearlyAverages[year].rainfall += data.rainfall[idx];
        }
        
        yearlyAverages[year].count++;
      });
      
      // Add CO2 data if available
      if (co2Data?.data && Array.isArray(co2Data.data)) {
        co2Data.data.forEach((co2point: any) => {
          if (yearlyAverages[co2point.year]) {
            yearlyAverages[co2point.year].co2 = co2point.co2_emissions_mtco2;
          }
        });
      }
      
      // Calculate averages
      const aggregatedData = Object.values(yearlyAverages)
        .map(data => ({
          year: data.year,
          temperature: Math.round((data.temperature / data.count) * 10) / 10,
          rainfall: Math.round((data.rainfall / data.count) * 10) / 10,
          co2: data.co2 || undefined
        }))
        .sort((a, b) => a.year - b.year);
      
      setTrendsData(aggregatedData as any);
      console.log('✓ India-wide trends aggregated:', aggregatedData.length, 'years (1901-2025)');
    }
  };

  const aggregateToStateLevel = (data: any) => {
    const stateYearlyData: { [key: string]: { [key: number]: { temps: number[]; rainfalls: number[] } } } = {};
    
    if (Array.isArray(data.years) && Array.isArray(data.regions)) {
      data.years.forEach((year: number, idx: number) => {
        const region = data.regions?.[idx] || 'Unknown';
        
        if (!stateYearlyData[region]) {
          stateYearlyData[region] = {};
        }
        if (!stateYearlyData[region][year]) {
          stateYearlyData[region][year] = { temps: [], rainfalls: [] };
        }
        
        if (typeof data.temperatures?.[idx] === 'number') {
          stateYearlyData[region][year].temps.push(data.temperatures[idx]);
        }
        if (typeof data.rainfall?.[idx] === 'number') {
          stateYearlyData[region][year].rainfalls.push(data.rainfall[idx]);
        }
      });
      
      // Take first region's data or average of all regions
      const firstRegion = Object.keys(stateYearlyData)[0];
      if (firstRegion && stateYearlyData[firstRegion]) {
        const aggregatedData = Object.entries(stateYearlyData[firstRegion])
          .map(([year, data]) => ({
            year: parseInt(year),
            temperature: data.temps.length > 0 
              ? Math.round((data.temps.reduce((a, b) => a + b, 0) / data.temps.length) * 10) / 10
              : 0,
            rainfall: data.rainfalls.length > 0 
              ? Math.round((data.rainfalls.reduce((a, b) => a + b, 0) / data.rainfalls.length) * 10) / 10
              : 0
          }))
          .sort((a, b) => a.year - b.year);
        
        setTrendsData(aggregatedData as any);
        console.log('✓ State-level trends aggregated:', Object.keys(stateYearlyData).length, 'regions');
      }
    }
  };

  const fetchTrendsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch unified trends (1901-2025) and CO2 in parallel
      const [trendsRes, co2Res] = await Promise.all([
        climateAPI.getUnifiedTrends(),
        intelligenceAPI.getCO2()
      ]);

      if (trendsRes?.data) {
        setRawData(trendsRes.data);
        console.log('✓ Unified trends fetched:', trendsRes.data.years?.length || 0, 'years (1901-2025)');
      }

      if (co2Res?.data) {
        setCO2Data(co2Res);
        console.log('✓ CO2 data fetched:', co2Res.data.length, 'years');
      }

      // Aggregate for current view (india-wide by default)
      if (trendsRes?.data) {
        aggregateToIndiaWide(trendsRes.data);
      }
    } catch (err) {
      console.error('Error fetching trends:', err);
      setError('Failed to load trends. Showing cached data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Trends Analysis</h1>
          <p className="text-muted-foreground text-sm mt-1">Historical climate patterns across India</p>
          {error && (
            <div className="mt-2 flex items-center gap-2 text-xs text-warning bg-warning/10 p-2 rounded border border-warning/20">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
          {/* Debug info */}
          {rawData && (
            <div className="mt-2 text-xs text-muted-foreground">
              📊 {rawData.years?.length || 0} data points loaded
              {view === 'india' ? ' (India-wide aggregated)' : ' (State-level)'}
            </div>
          )}
        </div>
        <div className="flex gap-2">
          {['india', 'state'].map(v => (
            <button
              key={v}
              onClick={() => setView(v as any)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${view === v ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-muted/30 text-muted-foreground border border-border/20 hover:text-foreground'}`}
            >
              {v === 'india' ? 'India-wide' : 'State-level'}
            </button>
          ))}
        </div>
      </div>

      {loading && trendsData === mockTrendsData ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <p className="text-muted-foreground mt-4">Loading trends data...</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartContainer title="Temperature vs Year" subtitle="Annual average temperature trend (°C)">
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={trendsData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
                  <XAxis 
                    dataKey="year" 
                    tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} 
                    tickLine={false}
                    interval={Math.floor(trendsData.length / 8) || 0}
                  />
                  <YAxis tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} tickLine={false} domain={['auto', 'auto']} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="temperature" stroke="hsl(190,100%,50%)" strokeWidth={2} dot={false} name="Temperature" />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="Rainfall vs Year" subtitle="Annual precipitation (mm)">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={trendsData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
                  <XAxis 
                    dataKey="year" 
                    tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} 
                    tickLine={false}
                    interval={Math.floor(trendsData.length / 8) || 0}
                  />
                  <YAxis tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="rainfall" fill="hsl(263,76%,66%)" radius={[4, 4, 0, 0]} name="Rainfall" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </div>

          {/* CO2 Chart - only show if CO2 data available */}
          {co2Data?.data && (
            <ChartContainer title="CO₂ Emissions Over Time" subtitle="Megatons CO₂ per year (MtCO₂)">
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={co2Data.data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
                  <XAxis 
                    dataKey="year" 
                    tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} 
                    tickLine={false}
                  />
                  <YAxis tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line 
                    type="monotone" 
                    dataKey="co2_emissions_mtco2" 
                    stroke="hsl(151,100%,50%)" 
                    strokeWidth={2} 
                    dot={false} 
                    name="CO₂ Emissions" 
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          )}
        </>
      )}
    </motion.div>
  );
};

export default Trends;
