import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, TrendingUp, Cloud, Zap } from 'lucide-react';
import clsx from 'clsx';

interface InsightItem {
  text: string;
  icon?: string;
}

interface InsightsProps {
  insights: string[];
  loading?: boolean;
}

const Insights: React.FC<InsightsProps> = ({ insights, loading = false }) => {
  // Extract emoji and clean text
  const getInsightData = (text: string) => {
    const emojiMatch = text.match(/^[\p{Emoji}\s]+/u);
    const emoji = emojiMatch ? emojiMatch[0].trim() : '→';
    const cleanText = text.replace(/^[\p{Emoji}\s]+/u, '').trim();
    return { emoji, text: cleanText };
  };

  // Determine color based on insight type
  const getInsightColor = (text: string) => {
    // Red theme: warnings, errors, high risk
    if (text.includes('🔥') || text.includes('⚠️') || text.includes('🌡️') || text.includes('danger') || text.includes('high risk') || text.includes('alert')) {
      return { container: 'border-l-red-500 bg-red-50 dark:bg-red-900/30', icon: 'bg-red-200 dark:bg-red-900/50' };
    }
    // Blue theme: water, rainfall, precipitation, humidity
    if (text.includes('🌧️') || text.includes('🌊') || text.includes('💧') || text.includes('rain') || text.includes('water') || text.includes('humidity')) {
      return { container: 'border-l-blue-500 bg-blue-50 dark:bg-blue-900/30', icon: 'bg-blue-200 dark:bg-blue-900/50' };
    }
    // Yellow theme: alerts, trends, statistics, data
    if (text.includes('📈') || text.includes('📊') || text.includes('📉') || text.includes('📢') || text.includes('❄️') || text.includes('trend') || text.includes('data') || text.includes('stability')) {
      return { container: 'border-l-yellow-500 bg-yellow-50 dark:bg-yellow-900/30', icon: 'bg-yellow-200 dark:bg-yellow-900/50' };
    }
    // Green theme: positive, stable, good conditions
    if (text.includes('✓') || text.includes('📍') || text.includes('regions') || text.includes('variation') || text.includes('stable') || text.includes('normal')) {
      return { container: 'border-l-green-500 bg-green-50 dark:bg-green-900/30', icon: 'bg-green-200 dark:bg-green-900/50' };
    }
    // Pink theme: locations, regional data
    if (text.includes('🌍') || text.includes('🌏') || text.includes('🌎') || text.includes('regional') || text.includes('location')) {
      return { container: 'border-l-pink-500 bg-pink-50 dark:bg-pink-900/30', icon: 'bg-pink-200 dark:bg-pink-900/50' };
    }
    return { container: 'border-l-gray-500 bg-gray-50 dark:bg-gray-900/20', icon: 'bg-gray-200 dark:bg-gray-900/50' };
  };

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, x: -20 },
    show: { opacity: 1, x: 0, transition: { type: 'spring', stiffness: 100 } }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-0">
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-3"
      >
        {insights.map((insight, idx) => {
          const { emoji, text } = getInsightData(insight);
          const colors = getInsightColor(insight);
          return (
            <motion.div key={idx} variants={item}>
              <div
                className={clsx(
                  'border-l-4 p-4 rounded-lg transition-all duration-300',
                  'hover:shadow-md hover:translate-x-1',
                  colors.container
                )}
              >
                <div className="flex gap-3 items-start">
                  {/* Icon with background */}
                  <span className={clsx(
                    'text-xl flex-shrink-0 mt-0.5 w-8 h-8 flex items-center justify-center rounded',
                    colors.icon
                  )}>
                    {emoji}
                  </span>

                  {/* Text */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm leading-relaxed break-words text-gray-800 dark:text-gray-100">
                      {text}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {insights.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <p className="text-sm">No insights available</p>
        </div>
      )}
    </div>
  );
};

export default Insights;
