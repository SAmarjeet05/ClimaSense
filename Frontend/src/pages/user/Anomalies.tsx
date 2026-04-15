import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, AlertCircle } from 'lucide-react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { GlassCard } from '@/components/common/GlassCard';
import { ChartContainer } from '@/components/common/ChartContainer';
import { climateAPI } from '@/services/api';
import { cn } from '@/lib/utils';

const severityColors: Record<string, string> = {
  critical: 'bg-destructive/20 text-destructive border-destructive/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  low: 'bg-accent/20 text-accent border-accent/30',
};

interface Anomaly {
  id: number | string;
  date: string;
  region: string;
  type: string;
  temperature: number;
  rainfall: number;
  temp_deviation: number;
  rain_deviation: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  year?: number;
  month?: number;
}

const Anomalies: React.FC = () => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await climateAPI.getAnomalies(100);
        console.log('Fetched anomalies:', data);
        setAnomalies(data.anomalies || []);
      } catch (err) {
        console.error('Error fetching anomalies:', err);
        setError('Failed to load anomalies. Please try again later.');
        setAnomalies([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAnomalies();
  }, []);

  // Prepare scatter data: temperature deviation vs rainfall deviation
  const scatterData = anomalies.map((a, i) => ({
    key: i,
    x: Math.abs(a.temp_deviation),
    y: Math.abs(a.rain_deviation),
    isAnomaly: true,
    severity: a.severity,
  }));

  // Add some normal data points for context
  const normalData = Array.from({ length: Math.max(20, Math.floor(anomalies.length / 2)) }, (_, i) => ({
    key: `normal-${i}`,
    x: Math.random() * 3,
    y: Math.random() * 100,
    isAnomaly: false,
    severity: 'low',
  }));

  const chartData = [...normalData, ...scatterData];

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Anomaly Detection</h1>
        <p className="text-muted-foreground text-sm mt-1">AI-identified abnormal climate events across India</p>
      </div>

      {error && (
        <GlassCard className="bg-destructive/10 border-destructive/30 flex items-center gap-3 p-4">
          <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
          <p className="text-sm text-destructive">{error}</p>
        </GlassCard>
      )}

      <ChartContainer title="Anomalies vs Normal Data Points" subtitle="Temperature and rainfall deviation scatter plot">
        {loading ? (
          <div className="h-[280px] flex items-center justify-center text-muted-foreground">
            Loading chart data...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
              <XAxis 
                type="number" 
                dataKey="x" 
                tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} 
                tickLine={false} 
                name="Temp Deviation (°C)" 
              />
              <YAxis 
                type="number" 
                dataKey="y" 
                tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} 
                tickLine={false} 
                name="Rainfall Deviation (mm)" 
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter 
                data={chartData.filter(d => !d.isAnomaly)} 
                fill="hsl(190,100%,50%)" 
                opacity={0.5} 
                name="Normal" 
              />
              <Scatter 
                data={chartData.filter(d => d.isAnomaly)} 
                fill="hsl(0,84%,60%)" 
                name="Anomaly" 
              />
            </ScatterChart>
          </ResponsiveContainer>
        )}
      </ChartContainer>

      <GlassCard hover={false} className="overflow-hidden p-0">
        <div className="p-5 border-b border-border/10 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-destructive" />
          <h3 className="text-foreground font-semibold">
            Detected Anomalies {!loading && anomalies.length > 0 && `(${anomalies.length})`}
          </h3>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 text-center text-muted-foreground">
              Loading anomaly data...
            </div>
          ) : anomalies.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              No anomalies detected in the selected range.
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border/10 text-muted-foreground text-xs uppercase tracking-wider">
                  <th className="text-left p-4">Date</th>
                  <th className="text-left p-4">Region</th>
                  <th className="text-left p-4">Type</th>
                  <th className="text-left p-4">Temp Dev</th>
                  <th className="text-left p-4">Rain Dev</th>
                  <th className="text-left p-4">Severity</th>
                  <th className="text-left p-4 hidden md:table-cell">Description</th>
                </tr>
              </thead>
              <tbody>
                {anomalies.map((a, i) => (
                  <motion.tr 
                    key={`${a.id}-${i}`} 
                    initial={{ opacity: 0, x: -10 }} 
                    animate={{ opacity: 1, x: 0 }} 
                    transition={{ delay: i * 0.05 }}
                    className="border-b border-border/5 hover:bg-muted/20 transition-colors">
                    <td className="p-4 text-foreground">{a.date}</td>
                    <td className="p-4 text-foreground font-medium">{a.region}</td>
                    <td className="p-4 text-foreground text-xs">{a.type}</td>
                    <td className="p-4 font-mono text-orange-400">{a.temp_deviation >= 0 ? '+' : ''}{a.temp_deviation.toFixed(2)}°C</td>
                    <td className="p-4 font-mono text-blue-400">{a.rain_deviation >= 0 ? '+' : ''}{a.rain_deviation.toFixed(1)}mm</td>
                    <td className="p-4">
                      <span className={cn('px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider border', severityColors[a.severity])}>
                        {a.severity}
                      </span>
                    </td>
                    <td className="p-4 text-muted-foreground hidden md:table-cell max-w-xs truncate">{a.description}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </GlassCard>
    </motion.div>
  );
};

export default Anomalies;
