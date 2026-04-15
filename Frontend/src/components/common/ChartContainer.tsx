import React from 'react';
import { cn } from '@/lib/utils';

interface ChartContainerProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}

export const ChartContainer: React.FC<ChartContainerProps> = ({ title, subtitle, children, className }) => {
  return (
    <div className={cn('glass p-6', className)}>
      <div className="mb-4">
        <h3 className="text-foreground font-semibold text-lg">{title}</h3>
        {subtitle && <p className="text-muted-foreground text-sm mt-1">{subtitle}</p>}
      </div>
      <div className="w-full">{children}</div>
    </div>
  );
};
