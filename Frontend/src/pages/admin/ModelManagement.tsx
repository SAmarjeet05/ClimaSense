import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Cpu, Play, RefreshCw, Loader2 } from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { ChartContainer } from '@/components/common/ChartContainer';
import { adminAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface Model {
  id: number;
  name: string;
  version: string;
  algorithm: string;
  accuracy: number;
  r2_score: number;
  status: 'deployed' | 'training';
  last_trained: string;
  epochs: number;
  dataset: string;
  data_points: number;
  description: string;
}

const ModelManagement: React.FC = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Generate sample training history data
  const trainingHistory = Array.from({ length: 20 }, (_, i) => ({
    epoch: (i + 1) * 10,
    loss: 0.8 * Math.exp(-i * 0.15) + 0.05 + Math.random() * 0.02,
    val_loss: 0.85 * Math.exp(-i * 0.13) + 0.08 + Math.random() * 0.03,
  }));

  // Load models on component mount
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const data = await adminAPI.getModels();
      setModels(data.models || []);
    } catch (error) {
      console.error('Failed to load models:', error);
      toast({
        title: 'Error',
        description: 'Failed to load ML models',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Model Management</h1>
        <p className="text-muted-foreground text-sm mt-1">Train, deploy, and monitor ML models</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-6 h-6 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading models...</span>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {models.length === 0 ? (
              <div className="col-span-2 text-center text-muted-foreground">No models available</div>
            ) : (
              models.map(m => (
                <GlassCard key={m.id}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-primary" />
                      <div>
                        <h4 className="text-foreground font-medium text-sm">{m.name}</h4>
                        <p className="text-xs text-muted-foreground">{m.description}</p>
                      </div>
                    </div>
                    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${m.status === 'deployed' ? 'bg-accent/20 text-accent' : 'bg-warning/20 text-warning'}`}>
                      {m.status}
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
                    <div><span className="text-muted-foreground">Version:</span> <span className="text-foreground">{m.version}</span></div>
                    <div><span className="text-muted-foreground">Algorithm:</span> <span className="text-foreground">{m.algorithm}</span></div>
                    <div><span className="text-muted-foreground">Accuracy:</span> <span className="text-primary font-semibold">{m.accuracy}%</span></div>
                    <div><span className="text-muted-foreground">R² Score:</span> <span className="text-foreground">{m.r2_score}</span></div>
                    <div><span className="text-muted-foreground">Epochs:</span> <span className="text-foreground">{m.epochs}</span></div>
                    <div><span className="text-muted-foreground">Dataset:</span> <span className="text-foreground text-[11px]">{m.dataset}</span></div>
                  </div>
                  <p className="text-[10px] text-muted-foreground mt-3">
                    Last trained: {new Date(m.last_trained).toLocaleString()}
                  </p>
                  <p className="text-[10px] text-muted-foreground">
                    Data points: {m.data_points.toLocaleString()}
                  </p>
                  <div className="mt-3 flex gap-2">
                    <button className="flex items-center gap-1 px-3 py-1.5 bg-primary/20 text-primary border border-primary/30 rounded-lg text-xs hover:bg-primary/30 transition-colors">
                      <RefreshCw className="w-3 h-3" /> Retrain
                    </button>
                    <button className="flex items-center gap-1 px-3 py-1.5 bg-muted/30 text-foreground border border-border/20 rounded-lg text-xs hover:bg-muted/50 transition-colors">
                      <Play className="w-3 h-3" /> Test
                    </button>
                  </div>
                </GlassCard>
              ))
            )}
          </div>

          <ChartContainer title="Training Loss History" subtitle="Latest model training convergence">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trainingHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
                <XAxis dataKey="epoch" tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} tickLine={false} />
                <YAxis tick={{ fill: 'hsl(0,0%,55%)', fontSize: 11 }} tickLine={false} />
                <Tooltip />
                <Line type="monotone" dataKey="loss" stroke="hsl(190,100%,50%)" strokeWidth={2} dot={false} name="Train Loss" />
                <Line type="monotone" dataKey="val_loss" stroke="hsl(263,76%,66%)" strokeWidth={2} dot={false} name="Val Loss" />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        </>
      )}
    </motion.div>
  );
};

export default ModelManagement;
