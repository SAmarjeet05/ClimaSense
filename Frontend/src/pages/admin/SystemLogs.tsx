import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ScrollText, Filter, Loader2 } from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { adminAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface SystemLog {
  id: number;
  action: string;
  user_id?: number;
  details: string;
  created_at: string;
  status?: 'success' | 'warning' | 'error';
}

const statusColors: Record<string, string> = {
  success: 'bg-accent/20 text-accent',
  warning: 'bg-warning/20 text-warning',
  error: 'bg-destructive/20 text-destructive',
};

const SystemLogs: React.FC = () => {
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');
  const { toast } = useToast();

  // Load logs on component mount
  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await adminAPI.getLogs(200);
      const logsWithStatus = (data.logs || []).map((log: SystemLog) => ({
        ...log,
        status: getStatusFromAction(log.action)
      }));
      setLogs(logsWithStatus);
    } catch (error) {
      console.error('Failed to load logs:', error);
      toast({
        title: 'Error',
        description: 'Failed to load system logs',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Determine status color based on action type
  const getStatusFromAction = (action: string): 'success' | 'warning' | 'error' => {
    if (action.includes('error') || action.includes('failed')) return 'error';
    if (action.includes('warning')) return 'warning';
    return 'success';
  };

  const filtered = filter === 'all' ? logs : logs.filter(l => l.status === filter);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">System Logs</h1>
          <p className="text-muted-foreground text-sm mt-1">Activity timeline and system events</p>
        </div>
        <div className="flex gap-2">
          {['all', 'success', 'warning', 'error'].map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all capitalize ${filter === f ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-muted/30 text-muted-foreground border border-border/20 hover:text-foreground'}`}>
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
            <span className="ml-2 text-muted-foreground">Loading logs...</span>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center text-muted-foreground">No logs available</div>
        ) : (
          filtered.map((log, i) => (
            <motion.div key={log.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
              <GlassCard className="p-4 flex items-start gap-4">
                <div className="flex-shrink-0 mt-1">
                  <div className={cn('w-2 h-2 rounded-full', log.status === 'success' ? 'bg-accent' : log.status === 'warning' ? 'bg-warning' : 'bg-destructive')} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-foreground font-medium text-sm">{log.action}</span>
                      <span className={cn('px-2 py-0.5 rounded-full text-[10px] uppercase font-bold', statusColors[log.status || 'success'])}>{log.status || 'success'}</span>
                    </div>
                    <span className="text-xs text-muted-foreground font-mono">
                      {new Date(log.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-muted-foreground text-xs mt-1">{log.details}</p>
                  {log.user_id && <p className="text-muted-foreground/60 text-[10px] mt-1">User ID: {log.user_id}</p>}
                </div>
              </GlassCard>
            </motion.div>
          ))
        )}
      </div>
    </motion.div>
  );
};

export default SystemLogs;
