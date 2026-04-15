import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, TrendingUp, Droplets, Thermometer } from 'lucide-react';
import clsx from 'clsx';

interface RiskCardProps {
  city: string;
  riskScore: number;
  riskLevel: string;
  temperature: number;
  rainfall: number;
}

const RiskCard: React.FC<RiskCardProps> = ({
  city,
  riskScore,
  riskLevel,
  temperature,
  rainfall
}) => {
  // Determine card color based on risk level
  const getCardColor = () => {
    if (riskScore > 70) return 'from-red-500 to-red-600';
    if (riskScore > 40) return 'from-yellow-500 to-yellow-600';
    return 'from-green-500 to-green-600';
  };

  // Determine risk level text color
  const getRiskTextColor = () => {
    if (riskScore > 70) return 'text-red-100';
    if (riskScore > 40) return 'text-yellow-100';
    return 'text-green-100';
  };

  // Get icon based on risk level
  const getRiskIcon = () => {
    if (riskScore > 70) return <AlertCircle className="w-5 h-5" />;
    if (riskScore > 40) return <TrendingUp className="w-5 h-5" />;
    return <AlertCircle className="w-5 h-5" />;
  };

  return (
    <motion.div
      whileHover={{ 
        scale: 1.05,
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
      }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className={clsx(
        'relative overflow-hidden rounded-xl p-6 text-white',
        'cursor-pointer transition-all duration-300',
        'shadow-lg hover:shadow-2xl',
        'backdrop-blur-sm border border-white border-opacity-20'
      )}
      style={{
        background: `linear-gradient(135deg, ${
          riskScore > 70
            ? 'rgb(239, 68, 68), rgb(220, 38, 38)'
            : riskScore > 40
            ? 'rgb(234, 179, 8), rgb(202, 138, 4)'
            : 'rgb(34, 197, 94), rgb(22, 163, 74)'
        })`
      }}
    >
      {/* Background glow effect */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          background: 'radial-gradient(circle at top-right, white, transparent)'
        }}
      />

      {/* Content */}
      <div className="relative z-10 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-bold">{city}</h3>
            <p className="text-xs opacity-90 mt-1">Climate Risk Assessment</p>
          </div>
          <div className="opacity-80">
            {getRiskIcon()}
          </div>
        </div>

        {/* Risk Score */}
        <div className="space-y-1">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{riskScore}</span>
            <span className="text-sm opacity-90">/100</span>
          </div>
          <div className="text-sm font-semibold opacity-95">
            {riskLevel} Risk
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-3 pt-2 border-t border-white border-opacity-20">
          <div className="flex items-center gap-2">
            <Thermometer className="w-4 h-4 opacity-75" />
            <div>
              <p className="text-xs opacity-75">Temperature</p>
              <p className="text-sm font-semibold">{temperature}°C</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Droplets className="w-4 h-4 opacity-75" />
            <div>
              <p className="text-xs opacity-75">Rainfall</p>
              <p className="text-sm font-semibold">{rainfall}mm</p>
            </div>
          </div>
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-2 pt-2">
          <div
            className={clsx(
              'w-2 h-2 rounded-full animate-pulse',
              riskScore > 70
                ? 'bg-red-300'
                : riskScore > 40
                ? 'bg-yellow-300'
                : 'bg-green-300'
            )}
          />
          <span className="text-xs opacity-85">
            {riskScore > 70
              ? 'Monitor closely'
              : riskScore > 40
              ? 'Observe trends'
              : 'Stable conditions'}
          </span>
        </div>
      </div>

      {/* Subtle background pattern */}
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage:
            'repeating-linear-gradient(45deg, transparent, transparent 10px, white 10px, white 20px)'
        }}
      />
    </motion.div>
  );
};

export default RiskCard;
