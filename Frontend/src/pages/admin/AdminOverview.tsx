import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Database, Cpu, Users, Activity, AlertCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { StatCard } from '@/components/common/StatCard';
import { ChartContainer } from '@/components/common/ChartContainer';
import { GlassCard } from '@/components/common/GlassCard';
import { adminAPI } from '@/services/api';

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

interface AdminStats {
  totalDataPoints: number;
  totalUsers: number;
  activeUsers: number;
  modelsDeployed: number;
  systemUptime: number;
  lastModelTraining: string;
  dataUpdates: Array<{ month: string; uploads: number; processed: number }>;
  modelStatus: Array<{ name: string; status: string; accuracy: string }>;
}

const AdminOverview: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOverviewData();
  }, []);

  const fetchOverviewData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminAPI.getOverview();
      console.log('Admin overview data:', data);
      setStats(data);
    } catch (err) {
      console.error('Error fetching admin overview:', err);
      setError('Failed to load admin overview data.');
      setStats(null);
    } finally {
      setLoading(false);
    }
  };
  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <h1 className="text-2xl font-bold text-foreground">Admin Overview</h1>
        <p className="text-muted-foreground text-sm mt-1">System health and performance metrics</p>
        {error && (
          <div className="mt-2 flex items-center gap-2 text-xs text-warning bg-warning/10 p-2 rounded border border-warning/20">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}
      </motion.div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">
          Loading system overview...
        </div>
      ) : !stats ? (
        <div className="text-center py-12 text-destructive">
          No overview data available
        </div>
      ) : (
        <>
          <motion.div variants={item} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Data Points" value={stats.totalDataPoints.toLocaleString()} icon={<Database className="w-5 h-5" />} color="primary" />
            <StatCard label="Models Deployed" value={String(stats.modelsDeployed)} icon={<Cpu className="w-5 h-5" />} color="secondary" />
            <StatCard label="Active Users" value={String(stats.activeUsers)} icon={<Users className="w-5 h-5" />} color="accent" />
            <StatCard label="System Uptime" value={`${stats.systemUptime}%`} icon={<Activity className="w-5 h-5" />} color="warning" />
          </motion.div>

          <motion.div variants={item}>
            <ChartContainer title="Data Upload Trends" subtitle="Monthly dataset uploads and processing">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.dataUpdates}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
                  <XAxis dataKey="month" tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} tickLine={false} />
                  <YAxis tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} tickLine={false} />
                  <Tooltip />
                  <Bar dataKey="uploads" fill="hsl(190,100%,50%)" radius={[4, 4, 0, 0]} name="Uploads" />
                  <Bar dataKey="processed" fill="hsl(263,76%,66%)" radius={[4, 4, 0, 0]} name="Processed" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </motion.div>

          <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {stats.modelStatus.map(model => (
              <GlassCard key={model.name}>
                <div className="flex items-center justify-between mb-2">
                  <Cpu className="w-4 h-4 text-primary" />
                  <span className={`text-[10px] uppercase font-bold ${
                    model.status === 'Active' ? 'text-accent' : 'text-warning'
                  }`}>{model.status}</span>
                </div>
                <h4 className="text-foreground font-medium text-sm">{model.name}</h4>
                <p className="text-muted-foreground text-xs mt-1">Accuracy: <span className="text-foreground">{model.accuracy}</span></p>
              </GlassCard>
            ))}
          </motion.div>
        </>
      )}
    </motion.div>
  );
};

export default AdminOverview;
