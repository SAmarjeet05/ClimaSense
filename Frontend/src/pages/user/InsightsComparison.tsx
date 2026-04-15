import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Lightbulb, TrendingUp, TrendingDown, ArrowRight, AlertCircle, 
  Zap, BarChart3, Award, ArrowUpRight, ArrowDownLeft, Droplet, Thermometer, Shield
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { GlassCard } from '@/components/common/GlassCard';
import { cn } from '@/lib/utils';
import { loggerService } from '@/services/logger';

const container = { hidden: {}, show: { transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

interface CityData {
  name: string;
  stability_score: number;
  risk_level: string;
  avg_temperature: number;
  avg_rainfall: number;
  temp_variation: number;
  rain_variation: number;
  historical_data?: any;
}

interface ComparisonData {
  city1: CityData;
  city2: CityData;
  winner: {
    most_stable_city: string;
    score_difference: number;
    temp_difference: number;
    rain_difference: number;
    ai_comparison?: string;
  };
  overall_assessment?: string;
}

const InsightsComparison: React.FC = () => {
  // ============================================================
  // STATE MANAGEMENT
  // ============================================================
  
  // Available cities
  const [allCities, setAllCities] = useState<string[]>([]);
  const [citiesLoading, setCitiesLoading] = useState(true);
  
  // City Comparison
  const [city1, setCity1] = useState('');
  const [city2, setCity2] = useState('');
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [overallAssessment, setOverallAssessment] = useState<string>('');
  
  // Trends Analysis
  const [trendsData, setTrendsData] = useState<any[]>([]);
  const [currentTrendCity, setCurrentTrendCity] = useState('Delhi');
  
  // Anomaly Detection
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [anomalyCity, setAnomalyCity] = useState('');
  const [anomaliesLoading, setAnomaliesLoading] = useState(false);
  
  // AI Insights
  const [aiInsights, setAiInsights] = useState<string[]>([]);
  const [aiAnalysis, setAiAnalysis] = useState<string>('');
  const [aiLoading, setAiLoading] = useState(false);
  
  // Mode Toggle
  const [mode, setMode] = useState<'temperature' | 'rainfall' | 'risk'>('temperature');
  
  // ============================================================
  // FETCH FUNCTIONS
  // ============================================================
  
  const fetchAllCities = async () => {
    try {
      setCitiesLoading(true);
      const res = await fetch('https://climasense-production.up.railway.app/api/comparison/cities', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors'
      });
      
      if (!res.ok) throw new Error('Failed to fetch cities');
      
      const data = await res.json();
      setAllCities(data.cities || []);
      
    } catch (err) {
      console.error('Error fetching cities:', err);
      // Fallback to default cities if API fails
      setAllCities([
        'Agartala', 'Agra', 'Ahmedabad', 'Bangalore', 'Bhopal', 'Bhubaneswar',
        'Chandigarh', 'Chennai', 'Coimbatore', 'Dehradun', 'Delhi', 'Ghaziabad',
        'Greater Noida', 'Guwahati', 'Hyderabad', 'Imphal', 'Indore', 'Jaipur',
        'Jodhpur', 'Kanpur', 'Kochi', 'Kolkata', 'Lucknow', 'Meerut', 'Mumbai',
        'Mysore', 'Noida', 'Patna', 'Prayagraj', 'Pune', 'Raipur', 'Ranchi',
        'Shillong', 'Srinagar', 'Surat', 'Trivandrum', 'Udaipur', 'Varanasi',
        'Visakhapatnam'
      ]);
    } finally {
      setCitiesLoading(false);
    }
  };
  
  const fetchComparison = async () => {
    try {
      setComparisonLoading(true);
      // Pass mode parameter to API
      const res = await fetch(`https://climasense-production.up.railway.app/api/compare-cities?city1=${city1}&city2=${city2}&mode=${mode}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors'
      });
      
      if (!res.ok) throw new Error('Failed to fetch comparison');
      
      const data = await res.json();
      setComparisonData(data.comparison);
      
      // Extract overall assessment from top-level response (mode-specific)
      setOverallAssessment(data.overall_assessment || '');
      
      // Extract AI comparison from winner section
      const comparison = data.comparison?.winner?.ai_comparison || '';
      setAiAnalysis(comparison);
      
      // Generate trends data from comparison
      const historicalData = data.comparison.city1.historical_data?.temperatures || [];
      const years = Array.from({ length: historicalData.length }, (_, i) => 2025 - historicalData.length + i);
      
      const trendChartData = historicalData.map((temp: number, idx: number) => ({
        year: years[idx],
        [city1]: parseFloat(temp.toFixed(1)),
        [city2]: data.comparison.city2.historical_data?.temperatures[idx] 
          ? parseFloat(data.comparison.city2.historical_data.temperatures[idx].toFixed(1))
          : temp
      }));
      
      setTrendsData(trendChartData);
      
    } catch (err) {
      console.error('Error fetching comparison:', err);
      alert('Failed to compare cities. Make sure backend is running.');
    } finally {
      setComparisonLoading(false);
    }
  };
  
  const fetchAnomalies = async (targetCity: string) => {
    try {
      setAnomaliesLoading(true);
      const res = await fetch(`https://climasense-production.up.railway.app/api/detect-anomalies-city?city=${targetCity}&limit=10`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors'
      });
      
      if (!res.ok) throw new Error('Failed to fetch anomalies');
      
      const data = await res.json();
      // Include Ollama explanations if available
      const enrichedAnomalies = data.anomalies || [];
      setAnomalies(enrichedAnomalies);
      
    } catch (err) {
      console.error('Error fetching anomalies:', err);
      setAnomalies([]);
    } finally {
      setAnomaliesLoading(false);
    }
  };
  
  const fetchAIInsights = async () => {
    try {
      setAiLoading(true);
      const res = await fetch('https://climasense-production.up.railway.app/api/realtime/generate-insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors'
      });
      
      if (!res.ok) throw new Error('Failed to fetch AI insights');
      
      const data = await res.json();
      const insightsList = data.data || [];
      
      // Format insights
      const formatted = insightsList.slice(0, 4).map((insight: string) => {
        // Remove emoji and clean text
        return insight.replace(/^[🌡️🌧️⚠️✅📍💧🔥📊]+\s*/, '');
      });
      
      setAiInsights(formatted);
      
    } catch (err) {
      console.error('Error fetching AI insights:', err);
      setAiInsights([
        'Analyzing climate patterns across compared cities',
        'Temperature stability shows interesting variations',
        'Rainfall distribution differs significantly between regions',
        'Risk patterns indicate distinct climate challenges'
      ]);
    } finally {
      setAiLoading(false);
    }
  };
  
  // ============================================================
  // EFFECTS
  // ============================================================
  
  const location = useLocation();
  
  useEffect(() => {
    // Initial load: fetch all cities
    fetchAllCities();
    // Fetch anomalies for default city only if we have one
    if (anomalyCity) {
      fetchAnomalies(anomalyCity);
    }
  }, []);

  // Read cities from location state (when navigating from assistant)
  useEffect(() => {
    if (location.state?.cities && Array.isArray(location.state.cities) && location.state.cities.length >= 2) {
      const [c1, c2] = location.state.cities;
      setCity1(c1);
      setCity2(c2);
    }
  }, [location.state?.cities]);
  
  useEffect(() => {
    if (city1 && city2) {
      fetchComparison();
    }
  }, [city1, city2, mode]);
  
  useEffect(() => {
    if (anomalyCity) {
      fetchAnomalies(anomalyCity);
    }
  }, [anomalyCity]);

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6 pb-10">
      {/* Header */}
      <motion.div variants={item}>
        <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
          <Zap className="w-8 h-8 text-primary" />
          ⚔️ Insights & Comparison
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          Advanced climate analysis with city-to-city comparison, anomaly detection, and AI insights
        </p>
      </motion.div>

      {/* Mode Toggle */}
      <motion.div variants={item}>
        <GlassCard className="inline-flex gap-2 p-1 bg-muted">
          {(['temperature', 'rainfall', 'risk'] as const).map((m) => (
            <button
              key={m}
              onClick={() => {
                setMode(m);
                loggerService.logModeChanged(m);
              }}
              className={cn(
                'px-4 py-2 rounded-lg font-medium text-sm transition-all',
                mode === m 
                  ? 'bg-primary text-primary-foreground shadow-lg' 
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              {m === 'temperature' && '🌡️ Temperature'}
              {m === 'rainfall' && '🌧️ Rainfall'}
              {m === 'risk' && '⚠️ Risk'}
            </button>
          ))}
        </GlassCard>
      </motion.div>

      {/* 1. CITY COMPARISON */}
      <motion.div variants={item}>
        <GlassCard>
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">🆚 City Comparison</h2>
          </div>
          
          {/* City Selectors */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">City 1</label>
              <select 
                value={city1} 
                onChange={(e) => {
                  setCity1(e.target.value);
                  if (e.target.value) {
                    loggerService.logCitySelected(e.target.value);
                  }
                }}
                className="w-full px-3 py-2 bg-muted border border-border rounded-lg text-sm"
              >
                <option value="">-- Select City --</option>
                {allCities.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">City 2</label>
              <select 
                value={city2} 
                onChange={(e) => {
                  setCity2(e.target.value);
                  if (e.target.value) {
                    loggerService.logCitySelected(e.target.value);
                  }
                }}
                className="w-full px-3 py-2 bg-muted border border-border rounded-lg text-sm"
              >
                <option value="">-- Select City --</option>
                {allCities.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>

          {/* Comparison Cards */}
          {comparisonLoading ? (
            <div className="text-center py-8 text-muted-foreground">Loading comparison...</div>
          ) : comparisonData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* City 1 Card */}
              <div className="bg-gradient-to-br from-primary/10 to-transparent p-4 rounded-lg border border-primary/20">
                <h3 className="font-bold text-lg mb-3">{comparisonData.city1.name}</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Stability Score</span>
                    <span className="font-bold text-primary">{comparisonData.city1.stability_score.toFixed(1)}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Avg Temperature</span>
                    <span className="font-bold">{comparisonData.city1.avg_temperature}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Avg Rainfall</span>
                    <span className="font-bold">{comparisonData.city1.avg_rainfall}mm</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Risk Level</span>
                    <span className={cn(
                      'font-bold px-2 py-1 rounded text-xs',
                      comparisonData.city1.risk_level === 'low' && 'bg-accent/20 text-accent',
                      comparisonData.city1.risk_level === 'medium' && 'bg-warning/20 text-warning',
                      comparisonData.city1.risk_level === 'high' && 'bg-destructive/20 text-destructive'
                    )}>
                      {comparisonData.city1.risk_level}
                    </span>
                  </div>
                </div>
              </div>

              {/* City 2 Card */}
              <div className="bg-gradient-to-br from-secondary/10 to-transparent p-4 rounded-lg border border-secondary/20">
                <h3 className="font-bold text-lg mb-3">{comparisonData.city2.name}</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Stability Score</span>
                    <span className="font-bold text-secondary">{comparisonData.city2.stability_score.toFixed(1)}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Avg Temperature</span>
                    <span className="font-bold">{comparisonData.city2.avg_temperature}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Avg Rainfall</span>
                    <span className="font-bold">{comparisonData.city2.avg_rainfall}mm</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Risk Level</span>
                    <span className={cn(
                      'font-bold px-2 py-1 rounded text-xs',
                      comparisonData.city2.risk_level === 'low' && 'bg-accent/20 text-accent',
                      comparisonData.city2.risk_level === 'medium' && 'bg-warning/20 text-warning',
                      comparisonData.city2.risk_level === 'high' && 'bg-destructive/20 text-destructive'
                    )}>
                      {comparisonData.city2.risk_level}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : null}

          {/* Winner */}
          {comparisonData && (
            <div className="space-y-3">
              <div className="p-3 bg-accent/10 border border-accent/30 rounded-lg">
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4 text-accent" />
                  <span className="text-sm">
                    <strong>🏆 Winner:</strong> {' '}
                    {comparisonData.winner.most_stable_city === 'Equal' 
                      ? 'Cities have equal climate stability'
                      : `${comparisonData.winner.most_stable_city} has more stable climate (+${comparisonData.winner.score_difference} points)`
                    }
                  </span>
                </div>
              </div>
              
              {/* Ollama AI Comparison */}
              {aiAnalysis && (
                <div className="p-3 bg-primary/10 border border-primary/30 rounded-lg">
                  <div className="flex items-start gap-2">
                    <Lightbulb className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-xs font-medium text-primary mb-1">💡 AI Comparison (via Ollama)</p>
                      <p className="text-sm text-muted-foreground">{aiAnalysis}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </GlassCard>
      </motion.div>

      {/* 2. TRENDS ANALYSIS */}
      <motion.div variants={item}>
        <GlassCard>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">📊 Trends Analysis (10-Year)</h2>
          </div>

          {trendsData.length > 0 ? (
            <div className="w-full h-80 -mx-4 -mb-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendsData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="year" stroke="rgba(255,255,255,0.5)" />
                  <YAxis stroke="rgba(255,255,255,0.5)" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(0,0,0,0.8)', 
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey={city1} stroke="#3b82f6" strokeWidth={2} />
                  <Line type="monotone" dataKey={city2} stroke="#ec4899" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">No trend data available</div>
          )}
        </GlassCard>
      </motion.div>

      {/* 3. ANOMALY DETECTION */}
      <motion.div variants={item}>
        <GlassCard>
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-warning" />
            <h2 className="text-xl font-bold">⚠️ Anomaly Detection</h2>
          </div>

          <div className="mb-4">
            <label className="text-sm font-medium text-muted-foreground mb-2 block">Select City to Analyze</label>
            <select 
              value={anomalyCity} 
              onChange={(e) => setAnomalyCity(e.target.value)}
              className="w-full px-3 py-2 bg-muted border border-border rounded-lg text-sm"
            >
              <option value="">-- Select City --</option>
              {allCities.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          {anomaliesLoading ? (
            <div className="text-center py-8 text-muted-foreground">Detecting anomalies...</div>
          ) : anomalies.length > 0 ? (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {anomalies.map((anomaly, idx) => (
                <div key={idx} className={cn(
                  'p-3 rounded-lg border',
                  anomaly.severity === 'high' 
                    ? 'bg-destructive/20 border-destructive/30' 
                    : 'bg-warning/20 border-warning/30'
                )}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        {anomaly.type === 'temperature' ? (
                          <Thermometer className="w-4 h-4" />
                        ) : (
                          <Droplet className="w-4 h-4" />
                        )}
                        <span className="font-medium text-sm">{anomaly.description}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{anomaly.year} • {anomaly.value}{anomaly.type === 'temperature' ? '°C' : 'mm'}</p>
                      {/* Ollama Explanation */}
                      {anomaly.explanation && (
                        <p className="text-xs text-muted-foreground mt-2 italic">💡 {anomaly.explanation}</p>
                      )}
                    </div>
                    <span className={cn(
                      'px-2.5 py-1 rounded text-xs font-bold flex-shrink-0',
                      anomaly.severity === 'high' ? 'bg-destructive/20 text-destructive' : 'bg-warning/20 text-warning'
                    )}>
                      {anomaly.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
              No anomalies detected for {anomalyCity}
            </div>
          )}
        </GlassCard>
      </motion.div>

      {/* 4. AI INSIGHTS */}
      <motion.div variants={item}>
        <GlassCard>
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">🧠 AI Insights</h2>
          </div>

          {aiLoading ? (
            <div className="text-center py-8 text-muted-foreground">Generating insights...</div>
          ) : (
            <div className="space-y-3">
              {aiInsights.map((insight, idx) => (
                <div key={idx} className="flex gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-lg">
                      {idx === 0 ? '💡' : idx === 1 ? '🌡️' : idx === 2 ? '🌧️' : '📊'}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">{insight}</p>
                </div>
              ))}
            </div>
          )}
        </GlassCard>
      </motion.div>

      {/* 5. COMPARISON SUMMARY */}
      <motion.div variants={item}>
        <GlassCard>
          <div className="flex items-center gap-2 mb-4">
            <Award className="w-5 h-5 text-accent" />
            <h2 className="text-xl font-bold">🔥 Comparison Summary</h2>
          </div>

          {comparisonData ? (
            <div className="space-y-4">
              {/* Winner Section */}
              <div className="p-4 bg-gradient-to-r from-accent/20 to-accent/10 border border-accent/30 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wide">🏆 Climate Winner</p>
                    <p className="text-2xl font-bold text-accent mt-1">
                      {comparisonData.winner.most_stable_city === 'Equal' 
                        ? 'Tie' 
                        : comparisonData.winner.most_stable_city
                      }
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">Stability Advantage</p>
                    <p className="text-2xl font-bold">{comparisonData.winner.score_difference}%</p>
                  </div>
                </div>
              </div>

              {/* Strengths & Weaknesses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-sm text-primary mb-2">
                    {comparisonData.city1.name}'s Profile
                  </h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li className="flex items-center gap-2">
                      {comparisonData.city1.avg_temperature < comparisonData.city2.avg_temperature ? (
                        <ArrowDownLeft className="w-4 h-4 text-accent" />
                      ) : (
                        <ArrowUpRight className="w-4 h-4 text-destructive" />
                      )}
                      Cooler avg temperature
                    </li>
                    <li className="flex items-center gap-2">
                      {comparisonData.city1.temp_variation < comparisonData.city2.temp_variation ? (
                        <ArrowDownLeft className="w-4 h-4 text-accent" />
                      ) : (
                        <ArrowUpRight className="w-4 h-4 text-destructive" />
                      )}
                      {comparisonData.city1.temp_variation < comparisonData.city2.temp_variation ? 'More' : 'Less'} stable temperatures
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-sm text-secondary mb-2">
                    {comparisonData.city2.name}'s Profile
                  </h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li className="flex items-center gap-2">
                      {comparisonData.city2.avg_rainfall > comparisonData.city1.avg_rainfall ? (
                        <ArrowUpRight className="w-4 h-4 text-primary" />
                      ) : (
                        <ArrowDownLeft className="w-4 h-4 text-destructive" />
                      )}
                      More rainfall
                    </li>
                    <li className="flex items-center gap-2">
                      {comparisonData.city2.rain_variation < comparisonData.city1.rain_variation ? (
                        <ArrowDownLeft className="w-4 h-4 text-accent" />
                      ) : (
                        <ArrowUpRight className="w-4 h-4 text-destructive" />
                      )}
                      {comparisonData.city2.rain_variation < comparisonData.city1.rain_variation ? 'More' : 'Less'} consistent rainfall
                    </li>
                  </ul>
                </div>
              </div>

              {/* Overall Assessment - Mode Specific */}
              <div className="p-4 bg-gradient-to-br from-primary/15 to-accent/15 border border-primary/30 rounded-lg">
                <div className="flex items-start gap-2">
                  <Lightbulb className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <div className="w-full">
                    <p className="text-xs font-medium text-primary uppercase tracking-wide mb-2">
                      📋 {mode === 'temperature' ? '🌡️ Temperature' : mode === 'rainfall' ? '🌧️ Rainfall' : '⚠️ Risk'} Assessment
                    </p>
                    <p className="text-sm leading-relaxed text-muted-foreground">
                      {overallAssessment || 'Loading assessment...'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">No comparison data available</div>
          )}
        </GlassCard>
      </motion.div>

      {/* 6. MODE INDICATOR */}
      <motion.div variants={item}>
        <GlassCard className="bg-gradient-to-r from-muted/50 to-muted/30">
          <div className="flex items-center gap-3">
            {mode === 'temperature' && <Thermometer className="w-5 h-5 text-primary" />}
            {mode === 'rainfall' && <Droplet className="w-5 h-5 text-blue-400" />}
            {mode === 'risk' && <Shield className="w-5 h-5 text-destructive" />}
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wide">Analysis Mode</p>
              <p className="text-sm font-medium">
                {mode === 'temperature' && '🌡️ Temperature Analysis'}
                {mode === 'rainfall' && '🌧️ Rainfall Analysis'}
                {mode === 'risk' && '⚠️ Risk Assessment'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {mode === 'temperature' && 'Analyzing temperature trends and variations across cities'}
                {mode === 'rainfall' && 'Analyzing rainfall patterns and precipitation variations'}
                {mode === 'risk' && 'Analyzing climate risk levels and stability scores'}
              </p>
            </div>
          </div>
        </GlassCard>
      </motion.div>
    </motion.div>
  );
};

export default InsightsComparison;
