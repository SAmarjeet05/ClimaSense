import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, Zap } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line
} from 'recharts';
import RiskCard from '@/components/common/RiskCard';
import Insights from '@/components/common/Insights';
import ClimateHeatmap from '@/components/common/ClimateHeatmap';
import { ChartContainer } from '@/components/common/ChartContainer';
import { GlassCard } from '@/components/common/GlassCard';
import { climateAPI, intelligenceAPI } from '@/services/api';
import { mockTrendsData } from '@/services/api';

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload) return null;
  return (
    <div className="glass p-3 text-xs">
      <p className="text-foreground font-medium mb-1">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}
        </p>
      ))}
    </div>
  );
};

interface RiskData {
  city: string;
  risk_score: number;
  risk_level: string;
  temperature: number;
  rainfall: number;
}

const Dashboard: React.FC = () => {
  const [riskData, setRiskData] = useState<RiskData[]>([]);
  const [insights, setInsights] = useState<string[]>([]);
  const [trendsData, setTrendsData] = useState(mockTrendsData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    fetchDashboardData();
    
    // Set up auto-refresh every 30 minutes to match backend scheduler
    const refreshIntervalId = setInterval(() => {
      console.log('🔄 Auto-refreshing dashboard real-time insights (every 30 min)...');
      fetchDashboardData();
    }, 30 * 60 * 1000); // 30 minutes
    
    return () => clearInterval(refreshIntervalId);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get auth token
      const token = localStorage.getItem('climaai_token');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Fetch risk data
      let riskData = null;
      try {
        const riskRes = await fetch('https://climasense-production.up.railway.app/api/dashboard/risk', { headers });
        console.log('Risk response status:', riskRes.status);
        if (riskRes.ok) {
          riskData = await riskRes.json();
          console.log('✓ Risk data:', riskData);
        } else {
          const text = await riskRes.text();
          console.error('Risk error response:', text.substring(0, 200));
        }
      } catch (err) {
        console.error('Risk fetch error:', err);
      }

      // Fetch REAL-TIME insights from the new endpoint
      let insightsData = null;
      try {
        console.log('Fetching real-time insights from /api/realtime/generate-insights...');
        const insightsRes = await fetch('https://climasense-production.up.railway.app/api/realtime/generate-insights', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          mode: 'cors'
        });
        console.log('Real-time insights response status:', insightsRes.status);
        if (insightsRes.ok) {
          insightsData = await insightsRes.json();
          console.log('✓ Real-time insights data:', insightsData);
        } else {
          const text = await insightsRes.text();
          console.error('Real-time insights error response:', text.substring(0, 200));
          throw new Error('Failed to fetch real-time insights');
        }
      } catch (err) {
        console.error('Real-time insights fetch error:', err);
        console.log('Falling back to static insights...');
      }

      // Fetch trends
      let trendsData = null;
      try {
        const trendsRes = await climateAPI.getUnifiedTrends();
        if (trendsRes?.data) {
          trendsData = trendsRes.data;
          console.log('✓ Trends loaded');
        }
      } catch (err) {
        console.error('Trends fetch error:', err);
      }

      // Update state
      if (riskData?.data) {
        setRiskData(riskData.data);
      } else {
        setRiskData([
          { city: "Delhi", risk_score: 78, risk_level: "High", temperature: 38.5, rainfall: 22.5 },
          { city: "Mumbai", risk_score: 65, risk_level: "Medium", temperature: 32.1, rainfall: 68.0 },
          { city: "Bangalore", risk_score: 48, risk_level: "Medium", temperature: 28.3, rainfall: 45.0 },
          { city: "Agartala", risk_score: 32, risk_level: "Low", temperature: 29.8, rainfall: 92.0 }
        ]);
      }

      // Use real-time insights if available, otherwise use fallback
      if (insightsData?.data && Array.isArray(insightsData.data)) {
        setInsights(insightsData.data);
        setLastUpdated(new Date().toLocaleTimeString());
        console.log('✓ Real-time insights set:', insightsData.data.length, 'insights');
      } else {
        console.warn('No real-time insights available, using fallback...');
        setInsights([
          "🔥 Rapid warming detected: +1.2°C increase over historical baseline. Urgent climate action needed.",
          "🌧️ Rainfall variability increasing: 18.5% change. Monsoon patterns becoming more unpredictable.",
          "⚠️ Northern India showing elevated risk factors. Delhi and nearby regions need climate adaptation strategies.",
          "🌊 Coastal regions (Mumbai, Chennai) experiencing increased monsoon intensity. Enhanced preparedness recommended.",
          "✓ Agartala maintains relatively stable climate patterns. Lower immediate risk compared to other regions.",
          "📢 Implement early warning systems and community engagement in high-risk zones to build climate resilience."
        ]);
      }

      if (trendsData?.years) {
        const aggregatedData = trendsData.years.map((year: number, idx: number) => ({
          year: year,
          temperature: trendsData.temperatures?.[idx] || 0,
          rainfall: trendsData.rainfall?.[idx] || 0
        }));
        setTrendsData(aggregatedData);
      }

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load some data.');
    } finally {
      setLoading(false);
    }
  };

  // Get recent data for trends chart
  const recentTrends = trendsData?.slice(-20) || [];

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Header */}
      <motion.div variants={item}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
              🌍 ClimaSense Dashboard
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              Real-time climate risk assessment and intelligence {lastUpdated && <span className="text-xs ml-2">(Updated: {lastUpdated})</span>}
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={fetchDashboardData}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors text-sm font-medium disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : '🔄 Refresh'}
          </motion.button>
        </div>

        {error && (
          <div className="mt-3 flex items-center gap-2 text-xs text-warning bg-warning/10 p-2 rounded border border-warning/20">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}
      </motion.div>

      {loading && riskData.length === 0 ? (
        <motion.div variants={item} className="text-center py-16">
          <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
          <p className="text-muted-foreground mt-4">Loading climate dashboard...</p>
        </motion.div>
      ) : (
        <>
          {/* 🔥 RISK CARDS - TOP ROW */}
          <motion.div variants={item}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {riskData.map((city, idx) => (
                <motion.div
                  key={city.city}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <RiskCard
                    city={city.city}
                    riskScore={city.risk_score}
                    riskLevel={city.risk_level}
                    temperature={city.temperature}
                    rainfall={city.rainfall}
                  />
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* 🗺️ HEATMAP + 📊 TRENDS - MIDDLE ROW */}
          <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Heatmap Section */}
            <ChartContainer
              title="🗺️ Climate Heatmap"
              subtitle="Regional risk visualization - hover for details"
            >
              <ClimateHeatmap riskData={riskData} />
            </ChartContainer>

            {/* Trends Chart */}
            <ChartContainer
              title="📊 Temperature Trends"
              subtitle="Last 20 years - showing warming pattern"
            >
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={recentTrends}>
                  <defs>
                    <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="hsl(0, 100%, 50%)" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="hsl(0, 100%, 50%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 15%)" />
                  <XAxis
                    dataKey="year"
                    tick={{ fill: 'hsl(0, 0%, 55%)', fontSize: 11 }}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: 'hsl(0, 0%, 55%)', fontSize: 11 }}
                    tickLine={false}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="temperature"
                    stroke="hsl(0, 100%, 50%)"
                    strokeWidth={3}
                    dot={false}
                    name="Temperature (°C)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          </motion.div>

          {/* ⚠️ INSIGHTS - BOTTOM ROW */}
          <motion.div variants={item}>
            <GlassCard>
              <div className="p-6">
                <h3 className="text-lg font-bold text-foreground flex items-center gap-2 mb-4">
                  💡 AI Climate Insights
                </h3>
                <Insights insights={insights} loading={loading} />
              </div>
            </GlassCard>
          </motion.div>

          {/* Quick Stats Footer */}
          <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <GlassCard className="p-4">
              <p className="text-xs text-muted-foreground">Highest Risk</p>
              <p className="text-xl font-bold text-foreground mt-1">
                {riskData.length > 0
                  ? riskData.reduce((a, b) =>
                    a.risk_score > b.risk_score ? a : b
                  ).city
                  : 'N/A'}
              </p>
            </GlassCard>

            <GlassCard className="p-4">
              <p className="text-xs text-muted-foreground">Data Points</p>
              <p className="text-xl font-bold text-foreground mt-1">
                {trendsData?.length || 0} years
              </p>
            </GlassCard>

            <GlassCard className="p-4">
              <p className="text-xs text-muted-foreground">Last Updated</p>
              <p className="text-xl font-bold text-foreground mt-1">
                {new Date().toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric'
                })}
              </p>
            </GlassCard>
          </motion.div>
        </>
      )}
    </motion.div>
  );
};

export default Dashboard;
