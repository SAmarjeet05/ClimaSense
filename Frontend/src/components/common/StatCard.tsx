import React from 'react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  label: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon: React.ReactNode;
  color: 'primary' | 'secondary' | 'accent' | 'warning';
}

const colorMap = {
  primary: 'from-primary/20 to-primary/5 border-primary/20 text-primary',
  secondary: 'from-secondary/20 to-secondary/5 border-secondary/20 text-secondary',
  accent: 'from-accent/20 to-accent/5 border-accent/20 text-accent',
  warning: 'from-warning/20 to-warning/5 border-warning/20 text-warning',
};

export const StatCard: React.FC<StatCardProps> = ({ label, value, change, trend, icon, color }) => {
  return (
    <div className={cn('glass p-5 bg-gradient-to-br transition-all duration-300 hover:scale-[1.02]', colorMap[color])}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-muted-foreground text-xs uppercase tracking-wider font-medium">{label}</p>
          <p className="text-2xl font-bold text-foreground mt-2">{value}</p>
          {change && (
            <p className={cn('text-xs mt-1 font-medium', trend === 'up' ? 'text-destructive' : trend === 'down' ? 'text-accent' : 'text-muted-foreground')}>
              {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {change}
            </p>
          )}
        </div>
        <div className={cn('p-2.5 rounded-lg bg-card/50', `text-${color === 'warning' ? 'warning' : color}`)}>
          {icon}
        </div>
      </div>
    </div>
  );
};
