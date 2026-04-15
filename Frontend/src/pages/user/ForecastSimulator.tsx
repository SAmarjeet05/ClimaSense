import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { AlertCircle, Zap } from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { ChartContainer } from '@/components/common/ChartContainer';

const INDIAN_CITIES = [
  'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',
  'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow',
  'Agartala', 'Srinagar', 'Itanagar', 'Imphal', 'Thiruvananthapuram'
];

const SCENARIOS = [
  { name: 'Heatwave 🔥', temp: 3, rain: -30, desc: 'Extreme heat with reduced rainfall' },
  { name: 'Drought 🌵', temp: 2, rain: -50, desc: 'Water stress scenario' },
  { name: 'Flood 🌧️', temp: -1, rain: 50, desc: 'Heavy precipitation event' },
];

interface Prediction {
  temperature_celsius: number;
  rainfall_mm: number;
  confidence: number;
}

interface SimulationResult {
  baseline_temperature: number;
  baseline_rainfall: number;
  baseline_risk: number;
  simulated_temperature: number;
  simulated_rainfall: number;
  simulated_risk: number;
  temperature_change: number;
  rainfall_change: number;
  risk_change: number;
  insight: string;
}

const container = { hidden: {}, show: { transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function ForecastSimulator() {
  // Input controls
  const [city, setCity] = useState('Mumbai');
  const [year, setYear] = useState(2028);
  const [month, setMonth] = useState(6);
  const [day, setDay] = useState(15);

  // Simulation controls
  const [tempDelta, setTempDelta] = useState(0);
  const [rainDelta, setRainDelta] = useState(0);

  // Results
  const [baseline, setBaseline] = useState<Prediction | null>(null);
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate initial prediction
  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('climaai_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('https://climasense-production.up.railway.app/api/predict', {
        method: 'POST',
        headers,
        body: JSON.stringify({ city, year, month, day })
      });
      if (!res.ok) {
        const errText = await res.text();
        console.error('Prediction HTTP error:', res.status, errText);
        throw new Error(`HTTP ${res.status}: Failed to generate prediction`);
      }
      const data = await res.json();
      console.log('✓ Prediction succeeded:', data);
      setBaseline(data);
      // Auto-run simulation when we get baseline
      await runSimulation(data);
    } catch (err) {
      setError((err as Error).message);
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Run simulation with current deltas
  const runSimulation = async (baselineData?: Prediction) => {
    if (!baseline && !baselineData) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('climaai_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('https://climasense-production.up.railway.app/api/simulate', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          city,
          year,
          month,
          day,
          temp_delta: tempDelta,
          rain_delta: rainDelta
        })
      });
      if (!res.ok) {
        const errText = await res.text();
        console.error('Simulation HTTP error:', res.status, errText);
        throw new Error(`HTTP ${res.status}: Failed to run simulation`);
      }
      const data = await res.json();
      console.log('✓ Simulation succeeded:', data);
      setSimulation(data);
    } catch (err) {
      setError((err as Error).message);
      console.error('Simulation error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Update sliders (triggers simulation)
  const handleTempChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    setTempDelta(value);
  };

  const handleRainChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    setRainDelta(value);
  };

  // Apply scenario
  const applyScenario = (tempD: number, rainD: number) => {
    setTempDelta(tempD);
    setRainDelta(rainD);
    setTimeout(() => runSimulation(), 100);
  };

  // Graph data
  const graphData = [
    {
      name: 'Baseline',
      temperature: baseline?.temperature_celsius || 0,
      rainfall: baseline?.rainfall_mm || 0,
      risk: simulation?.baseline_risk || 0
    },
    {
      name: 'Simulated',
      temperature: simulation?.simulated_temperature || 0,
      rainfall: simulation?.simulated_rainfall || 0,
      risk: simulation?.simulated_risk || 0
    }
  ];

  // Risk color
  const getRiskColor = (risk: number): string => {
    if (risk > 70) return 'text-red-500';
    if (risk > 50) return 'text-yellow-500';
    return 'text-green-500';
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Header */}
      <motion.div variants={item}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-foreground flex items-center gap-3">
              🔮 Forecast & Climate Simulator
            </h1>
            <p className="text-muted-foreground mt-2">
              Predict future climate + simulate what-if scenarios. See impacts instantly.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Main 2-Column Layout: Input (Left) + Output (Right) */}
      <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT SIDE - INPUT PANEL */}
        <GlassCard className="lg:col-span-1 p-6 h-fit">
          <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
            🎯 Prediction Input
          </h2>

          {/* City Selector */}
          <div className="space-y-3 mb-4">
            <label className="block text-sm font-medium text-foreground">City</label>
            <select
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {INDIAN_CITIES.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Year */}
          <div className="space-y-3 mb-4">
            <label className="block text-sm font-medium text-foreground">
              Year: <span className="text-primary text-lg font-bold">{year}</span>
            </label>
            <input
              type="range"
              min="2020"
              max="2050"
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Month */}
          <div className="space-y-3 mb-4">
            <label className="block text-sm font-medium text-foreground">
              Month: <span className="text-primary text-lg font-bold">{month}</span>
            </label>
            <input
              type="range"
              min="1"
              max="12"
              value={month}
              onChange={(e) => setMonth(parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Day */}
          <div className="space-y-3 mb-6">
            <label className="block text-sm font-medium text-foreground">
              Day: <span className="text-primary text-lg font-bold">{day}</span>
            </label>
            <input
              type="range"
              min="1"
              max="28"
              value={day}
              onChange={(e) => setDay(parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Generate Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleGenerate}
            disabled={loading}
            className="w-full px-6 py-3 rounded-lg bg-gradient-to-r from-primary to-blue-600 text-white font-bold disabled:opacity-50 transition-all"
          >
            {loading ? '🔄 Generating...' : '⚡ Generate Prediction'}
          </motion.button>

          {error && (
            <div className="mt-4 p-3 rounded-lg bg-red-900/30 border border-red-500 text-red-300 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
        </GlassCard>

        {/* RIGHT SIDE - OUTPUT PANEL */}
        {baseline && simulation && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="lg:col-span-2 space-y-4">
            {/* Baseline Result */}
            <GlassCard className="p-6 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20">
              <h3 className="text-lg font-bold text-blue-300 mb-4 flex items-center gap-2">
                📊 Baseline Prediction
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Temperature</p>
                  <p className="text-3xl font-bold text-blue-400">{baseline.temperature_celsius.toFixed(1)}°C</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Rainfall</p>
                  <p className="text-3xl font-bold text-cyan-400">{baseline.rainfall_mm.toFixed(1)}mm</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Risk Score</p>
                  <p className={`text-3xl font-bold ${getRiskColor(simulation.baseline_risk)}`}>
                    {simulation.baseline_risk}/100
                  </p>
                </div>
              </div>
            </GlassCard>

            {/* Simulated Result */}
            <GlassCard className="p-6 bg-gradient-to-br from-red-500/10 to-orange-500/10 border border-red-500/20">
              <h3 className="text-lg font-bold text-red-300 mb-4 flex items-center gap-2">
                🎬 Simulated Result
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Temperature</p>
                  <div className="flex items-center gap-2">
                    <p className="text-3xl font-bold text-red-400">{simulation.simulated_temperature.toFixed(1)}°C</p>
                    <p className={`text-xl ${simulation.temperature_change > 0 ? 'text-red-400' : 'text-blue-400'}`}>
                      {simulation.temperature_change > 0 ? '+' : ''}{simulation.temperature_change.toFixed(1)}°C
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Rainfall</p>
                  <div className="flex items-center gap-2">
                    <p className="text-3xl font-bold text-cyan-400">{simulation.simulated_rainfall.toFixed(1)}mm</p>
                    <p className={`text-xl ${simulation.rainfall_change > 0 ? 'text-cyan-400' : 'text-orange-400'}`}>
                      {simulation.rainfall_change > 0 ? '+' : ''}{simulation.rainfall_change.toFixed(0)}%
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Risk Score</p>
                  <div className="flex items-center gap-2">
                    <p className={`text-3xl font-bold ${getRiskColor(simulation.simulated_risk)}`}>
                      {simulation.simulated_risk}/100
                    </p>
                    <p className={`text-xl font-bold ${simulation.risk_change > 0 ? 'text-red-400' : 'text-green-400'}`}>
                      {simulation.risk_change > 0 ? '+' : ''}{simulation.risk_change}
                    </p>
                  </div>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </motion.div>

      {/* WHAT-IF SIMULATOR CONTROLS */}
      {baseline && (
        <motion.div variants={item}>
          <GlassCard className="p-6">
            <h2 className="text-xl font-bold text-foreground mb-6 flex items-center gap-2">
              🎛️ What-If Simulator
            </h2>

            {/* Sliders */}
            <div className="space-y-6 mb-8">
              {/* Temperature Slider */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="font-medium text-foreground flex items-center gap-2">
                    🌡️ Temperature Change
                  </label>
                  <span className={`text-lg font-bold ${tempDelta > 0 ? 'text-red-400' : tempDelta < 0 ? 'text-blue-400' : 'text-gray-400'}`}>
                    {tempDelta > 0 ? '+' : ''}{tempDelta.toFixed(1)}°C
                  </span>
                </div>
                <input
                  type="range"
                  min="-10"
                  max="10"
                  step="0.1"
                  value={tempDelta}
                  onChange={handleTempChange}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>-10°C (cooling)</span>
                  <span>0°C (baseline)</span>
                  <span>+10°C (heating)</span>
                </div>
              </div>

              {/* Rainfall Slider */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="font-medium text-foreground flex items-center gap-2">
                    💧 Rainfall Change
                  </label>
                  <span className={`text-lg font-bold ${rainDelta > 0 ? 'text-cyan-400' : rainDelta < 0 ? 'text-orange-400' : 'text-gray-400'}`}>
                    {rainDelta > 0 ? '+' : ''}{rainDelta.toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="-100"
                  max="100"
                  step="1"
                  value={rainDelta}
                  onChange={handleRainChange}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>-100% (drought)</span>
                  <span>0% (baseline)</span>
                  <span>+100% (flood)</span>
                </div>
              </div>
            </div>

            {/* Scenario Buttons */}
            <div className="mb-6">
              <p className="text-sm font-medium text-foreground mb-3">Quick Scenarios:</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {SCENARIOS.map((scenario) => (
                  <motion.button
                    key={scenario.name}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => applyScenario(scenario.temp, scenario.rain)}
                    className="p-4 rounded-lg border border-yellow-500/30 bg-yellow-900/20 hover:bg-yellow-900/40 text-yellow-300 transition-all text-sm font-medium"
                  >
                    <div className="font-bold mb-1">{scenario.name}</div>
                    <div className="text-xs text-yellow-400/80">{scenario.desc}</div>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Update Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => runSimulation()}
              disabled={loading}
              className="w-full px-6 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold disabled:opacity-50 transition-all"
            >
              {loading ? '🔄 Updating...' : '⚡ Run Simulation'}
            </motion.button>
          </GlassCard>
        </motion.div>
      )}

      {/* INSIGHTS PANEL */}
      {simulation && (
        <motion.div variants={item}>
          <GlassCard className="p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
            <h2 className="text-xl font-bold text-purple-300 mb-4 flex items-center gap-2">
              💡 AI Climate Insights
            </h2>
            <p className="text-base text-foreground leading-relaxed">{simulation.insight}</p>
          </GlassCard>
        </motion.div>
      )}

      {/* COMPARISON GRAPH */}
      {baseline && simulation && (
        <motion.div variants={item}>
          <ChartContainer title="📈 Baseline vs Simulated" subtitle="Visual comparison of climate metrics">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={graphData}>
                <defs>
                  <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00f" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#00f" stopOpacity={0.1} />
                  </linearGradient>
                  <linearGradient id="colorRain" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ff" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#0ff" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 15%)" />
                <XAxis dataKey="name" tick={{ fill: 'hsl(0, 0%, 55%)', fontSize: 12 }} />
                <YAxis tick={{ fill: 'hsl(0, 0%, 55%)', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: 'hsl(0, 0%, 10%)', border: '1px solid hsl(0, 0%, 30%)' }}
                  labelStyle={{ color: 'hsl(0, 0%, 90%)' }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="temperature"
                  stroke="#00f"
                  fill="url(#colorTemp)"
                  name="Temperature (°C)"
                />
                <Area
                  type="monotone"
                  dataKey="rainfall"
                  stroke="#0ff"
                  fill="url(#colorRain)"
                  name="Rainfall (mm)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>
        </motion.div>
      )}

      {/* Info Box */}
      {!baseline && (
        <motion.div variants={item}>
          <GlassCard className="p-6 bg-blue-900/20 border border-blue-500/30">
            <div className="flex items-start gap-3">
              <Zap className="w-5 h-5 text-blue-400 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-bold text-blue-300 mb-2">How to use this simulator:</h3>
                <ul className="text-sm text-blue-200/90 space-y-1">
                  <li>✓ Select a city and date to generate baseline prediction</li>
                  <li>✓ Use sliders to simulate temperature and rainfall changes</li>
                  <li>✓ Click scenario buttons for quick what-if simulations</li>
                  <li>✓ See real-time updates in results and graphs</li>
                  <li>✓ Read AI insights to understand climate impacts</li>
                </ul>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      )}
    </motion.div>
  );
}
