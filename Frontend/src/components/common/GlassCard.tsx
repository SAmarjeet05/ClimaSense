import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: 'primary' | 'secondary' | 'accent' | 'none';
  hover?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className, glowColor = 'none', hover = true }) => {
  return (
    <motion.div
      whileHover={hover ? { y: -2, scale: 1.005 } : undefined}
      transition={{ duration: 0.2 }}
      className={cn(
        'glass p-6 transition-all duration-300',
        hover && 'hover:border-primary/20',
        glowColor === 'primary' && 'hover:shadow-[0_0_30px_hsl(190_100%_50%/0.1)]',
        glowColor === 'secondary' && 'hover:shadow-[0_0_30px_hsl(263_76%_66%/0.1)]',
        glowColor === 'accent' && 'hover:shadow-[0_0_30px_hsl(151_100%_50%/0.1)]',
        className
      )}
    >
      {children}
    </motion.div>
  );
};
