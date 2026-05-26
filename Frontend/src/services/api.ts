import axios from 'axios';

const api = axios.create({
  baseURL: 'https://climasense-production.up.railway.app',
  timeout: 30000, // Increased to 30s for realtime-weather endpoint
  headers: { 'Content-Type': 'application/json' },
});

// Add token to requests with debugging
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('climaai_token');
  
  // Public endpoints that don't require authentication
  const publicEndpoints = ['/auth/login', '/auth/register'];
  const isPublicEndpoint = publicEndpoints.some(endpoint => config.url?.includes(endpoint));
  
  // Debug: Log token status
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log(`✓ Auth token attached to ${config.url}`);
  } else if (!isPublicEndpoint) {
    console.warn(`⚠ No auth token found for ${config.url}`);
  }
  
  return config;
}, (error) => {
  console.error('Request interceptor error:', error);
  return Promise.reject(error);
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('❌ 401 Unauthorized - Token may be invalid or expired');
      // Optionally clear token and redirect to login
      localStorage.removeItem('climaai_token');
      localStorage.removeItem('climaai_user');
    }
    return Promise.reject(error);
  }
);

// Auth API functions
export const authAPI = {
  register: async (userData: { name: string; email: string; password: string }) => {
    const response = await api.post('/auth/register', {
      name: userData.name,
      email: userData.email,
      password: userData.password,
      role: 'user',
    });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/current-user');
    return response.data;
  },
};

// ============================================================
// Phase 5 AI Intelligence API Functions
// ============================================================

export const intelligenceAPI = {
  // Get AI insights with natural language explanations
  getInsights: async () => {
    const response = await api.get('/api/insights');
    return response.data;
  },

  // Get climate score (0-100) with explanation
  getClimateScore: async () => {
    const response = await api.get('/api/climate-score');
    return response.data;
  },

  // Get climate forecast for next period
  getForecast: async () => {
    const response = await api.get('/api/forecast');
    return response.data;
  },

  // Get CO2 analysis and trends
  getCO2: async () => {
    const response = await api.get('/api/co2');
    return response.data;
  },

  // Get map data for all states
  getMapData: async () => {
    const response = await api.get('/api/map-data-all');
    return response.data;
  },

  // Get explanation for a specific metric
  explainMetric: async (metric: string) => {
    const response = await api.post('/api/explain', { metric });
    return response.data;
  },

  // Get comprehensive intelligence summary
  getIntelligenceSummary: async () => {
    const response = await api.get('/api/intelligence-summary');
    return response.data;
  },
};

// ============================================================
// Climate Data API Functions
// ============================================================

export const climateAPI = {
  // Get historical trends data
  getTrends: async () => {
    const response = await api.get('/api/trends');
    return response.data;
  },

  // Get unified trends (1901-2025) with both temperature and rainfall
  getUnifiedTrends: async () => {
    const response = await api.get('/api/trends/unified');
    return response.data;
  },

  // Get unified temperature trends (1901-2025)
  getUnifiedTemperatureTrends: async () => {
    const response = await api.get('/api/trends/unified/temperature');
    return response.data;
  },

  // Get unified rainfall trends (1901-2025)
  getUnifiedRainfallTrends: async () => {
    const response = await api.get('/api/trends/unified/rainfall');
    return response.data;
  },

  // Get current conditions
  getCurrentConditions: async () => {
    const response = await api.get('/api/current');
    return response.data;
  },

  // Get state-specific data
  getStateData: async (state?: string) => {
    const response = await api.get('/api/states', { params: { state } });
    return response.data;
  },

  // Get anomalies detected
  getAnomalies: async (limit: number = 100, region?: string) => {
    const response = await api.get('/api/anomalies', { 
      params: { limit, region } 
    });
    return response.data;
  },

  // Make predictions (requires city with coordinates)
  predict: async (year: number, month: number, day: number, city: string, latitude: number, longitude: number) => {
    const response = await api.post('/api/predict', { year, month, day, city, latitude, longitude });
    return response.data;
  },

  // Get forecast data (historical + predicted)
  getForecast: async (region: string = 'India', yearsAhead: number = 10, month: number = 6) => {
    const response = await api.get('/api/forecast', { params: { region, years_ahead: yearsAhead, month } });
    return response.data;
  },

  // ⚡ Get real-time weather data from Open-Meteo API
  getRealtimeWeather: async () => {
    const response = await api.get('/api/realtime-weather');
    return response.data;
  },

  // ⚡ Get real-time weather for specific location
  getLocationRealtimeWeather: async (latitude: number, longitude: number, city?: string) => {
    const response = await api.get('/api/realtime-weather/location', {
      params: { latitude, longitude, city }
    });
    return response.data;
  },

  // ⚡ Get weather forecast for specific location
  getRealtimeForecast: async (latitude: number, longitude: number, days: number = 7) => {
    const response = await api.get('/api/realtime-weather/forecast', {
      params: { latitude, longitude, days }
    });
    return response.data;
  },
};

// ============================================================
// Admin API Functions
// ============================================================

export const adminAPI = {
  // Get admin overview and system metrics
  getOverview: async () => {
    const response = await api.get('/api/admin/overview');
    return response.data;
  },

  // Get system logs
  getLogs: async (limit: number = 100) => {
    const response = await api.get('/api/admin/logs', { params: { limit } });
    return response.data;
  },

  // Get all users
  getUsers: async () => {
    const response = await api.get('/api/admin/users');
    return response.data;
  },

  // Get all ML models
  getModels: async () => {
    const response = await api.get('/api/admin/models');
    return response.data;
  },

  // Get all datasets
  getDatasets: async () => {
    const response = await api.get('/api/admin/datasets');
    return response.data;
  },

  // Upload a new dataset (CSV or Excel file)
  uploadDataset: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Create a special axios instance for file upload without JSON content-type
    const uploadApi = axios.create({
      baseURL: 'https://climasense-production.up.railway.app',
      timeout: 30000, // Longer timeout for file uploads
    });

    // Add token to requests
    uploadApi.interceptors.request.use((config) => {
      const token = localStorage.getItem('climaai_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    const response = await uploadApi.post('/api/admin/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get data rows from a dataset
  getDatasetRows: async (datasetId: number, limit: number = 100, offset: number = 0) => {
    const response = await api.get(`/api/admin/datasets/${datasetId}/rows`, {
      params: { limit, offset }
    });
    return response.data;
  },

  // Delete a user
  deleteUser: async (userId: number) => {
    const response = await api.delete(`/api/admin/users/${userId}`);
    return response.data;
  },

  // Update user role
  updateUserRole: async (userId: number, role: 'admin' | 'user') => {
    const response = await api.put(`/api/admin/users/${userId}/role`, { role });
    return response.data;
  },
};

// ============================================================
// Fallback Mock Data (used if API fails)
// ============================================================

export const mockTrendsData = Array.from({ length: 30 }, (_, i) => ({
  year: 1994 + i,
  temperature: 25.2 + Math.sin(i * 0.3) * 1.5 + i * 0.04,
  rainfall: 1100 + Math.sin(i * 0.5) * 200 + Math.random() * 50,
  co2: 360 + i * 2.3 + Math.random() * 5,
}));

export const mockStateData = [
  { state: 'Rajasthan', lat: 27.0, lng: 74.2, temp: 32.4, rainfall: 450, stability: 0.3, risk: 'high' },
  { state: 'Kerala', lat: 10.8, lng: 76.2, temp: 27.1, rainfall: 2800, stability: 0.7, risk: 'low' },
  { state: 'Maharashtra', lat: 19.7, lng: 75.7, temp: 28.5, rainfall: 1200, stability: 0.5, risk: 'medium' },
  { state: 'West Bengal', lat: 22.9, lng: 87.8, temp: 27.8, rainfall: 1800, stability: 0.6, risk: 'medium' },
  { state: 'Uttar Pradesh', lat: 26.8, lng: 80.9, temp: 26.5, rainfall: 900, stability: 0.4, risk: 'high' },
  { state: 'Tamil Nadu', lat: 11.1, lng: 78.6, temp: 29.2, rainfall: 950, stability: 0.6, risk: 'medium' },
  { state: 'Gujarat', lat: 22.2, lng: 71.1, temp: 29.8, rainfall: 800, stability: 0.4, risk: 'high' },
  { state: 'Karnataka', lat: 15.3, lng: 75.7, temp: 27.0, rainfall: 1200, stability: 0.6, risk: 'low' },
  { state: 'Madhya Pradesh', lat: 22.9, lng: 78.6, temp: 27.5, rainfall: 1100, stability: 0.5, risk: 'medium' },
  { state: 'Punjab', lat: 31.1, lng: 75.3, temp: 24.8, rainfall: 650, stability: 0.5, risk: 'medium' },
  { state: 'Assam', lat: 26.2, lng: 92.9, temp: 24.5, rainfall: 2200, stability: 0.55, risk: 'medium' },
  { state: 'Odisha', lat: 20.9, lng: 84.0, temp: 27.6, rainfall: 1500, stability: 0.45, risk: 'high' },
  { state: 'Jammu & Kashmir', lat: 33.7, lng: 76.5, temp: 14.2, rainfall: 700, stability: 0.65, risk: 'low' },
  { state: 'Himachal Pradesh', lat: 31.1, lng: 77.1, temp: 16.5, rainfall: 1100, stability: 0.7, risk: 'low' },
  { state: 'Bihar', lat: 25.0, lng: 85.0, temp: 26.8, rainfall: 1200, stability: 0.4, risk: 'high' },
  { state: 'Jharkhand', lat: 23.6, lng: 85.2, temp: 26.2, rainfall: 1300, stability: 0.45, risk: 'medium' },
  { state: 'Chhattisgarh', lat: 21.2, lng: 81.0, temp: 27.0, rainfall: 1400, stability: 0.5, risk: 'medium' },
  { state: 'Andhra Pradesh', lat: 15.9, lng: 79.7, temp: 28.8, rainfall: 900, stability: 0.5, risk: 'medium' },
  { state: 'Telangana', lat: 18.1, lng: 79.0, temp: 28.3, rainfall: 950, stability: 0.5, risk: 'medium' },
  { state: 'Goa', lat: 15.2, lng: 74.0, temp: 27.5, rainfall: 2900, stability: 0.7, risk: 'low' },
];

export const mockAnomalies = [
  { id: 1, date: '2024-06-15', region: 'Rajasthan', type: 'Extreme Heat', deviation: '+4.8°C', severity: 'critical', description: 'Record-breaking heatwave crossing 50°C' },
  { id: 2, date: '2024-07-22', region: 'Mumbai', type: 'Flood Event', deviation: '+320mm', severity: 'high', description: 'Unprecedented rainfall causing urban flooding' },
  { id: 3, date: '2024-03-10', region: 'Delhi NCR', type: 'Air Quality', deviation: 'AQI 480', severity: 'critical', description: 'Severe air pollution beyond hazardous levels' },
  { id: 4, date: '2024-01-05', region: 'Himachal Pradesh', type: 'Snowfall Deficit', deviation: '-45%', severity: 'medium', description: 'Significantly below-average winter snowfall' },
  { id: 5, date: '2024-08-18', region: 'Kerala', type: 'Monsoon Excess', deviation: '+180mm', severity: 'high', description: 'Above-normal monsoon causing landslides' },
  { id: 6, date: '2024-04-02', region: 'Tamil Nadu', type: 'Cyclone', deviation: 'Cat 3', severity: 'critical', description: 'Severe cyclonic storm making landfall' },
  { id: 7, date: '2024-09-12', region: 'Gujarat', type: 'Drought', deviation: '-62%', severity: 'high', description: 'Extended dry spell affecting agriculture' },
  { id: 8, date: '2024-11-28', region: 'Uttarakhand', type: 'Glacial Melt', deviation: '+2.1°C', severity: 'medium', description: 'Accelerated glacier retreat observed' },
];

export const mockInsights = [
  { id: 1, icon: '🌡️', title: 'Rising Temperatures', text: 'Average temperature across India has increased by 1.2°C over the last 30 years, with northern plains showing the steepest rise.', trend: 'up' as const, confidence: 94 },
  { id: 2, icon: '🌧️', title: 'Rainfall Variability', text: 'Monsoon rainfall patterns show 23% increased variability since 1990, indicating growing climate instability across western regions.', trend: 'up' as const, confidence: 87 },
  { id: 3, icon: '💨', title: 'CO₂ Acceleration', text: 'Carbon dioxide levels in Indian atmosphere have risen from 360 ppm to 420 ppm, accelerating at 2.3 ppm/year.', trend: 'up' as const, confidence: 98 },
  { id: 4, icon: '🏔️', title: 'Himalayan Ice Loss', text: 'Himalayan glaciers are losing ice mass at 7.7 Gt/year, threatening water security for 1.6 billion people downstream.', trend: 'down' as const, confidence: 91 },
  { id: 5, icon: '🌊', title: 'Sea Level Impact', text: 'Coastal regions face 3.2mm/year sea level rise. Mumbai and Chennai at highest risk by 2050.', trend: 'up' as const, confidence: 89 },
  { id: 6, icon: '🌾', title: 'Agricultural Stress', text: 'Crop yield predictions show 12% decline in wheat production by 2040 due to heat stress in Indo-Gangetic plains.', trend: 'down' as const, confidence: 82 },
];

export const mockAdminStats = {
  totalDataPoints: 2847563,
  modelsDeployed: 12,
  activeUsers: 384,
  systemUptime: 99.97,
  lastModelTraining: '2024-01-15T14:30:00Z',
  dataUpdates: Array.from({ length: 12 }, (_, i) => ({
    month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i],
    uploads: Math.floor(50 + Math.random() * 150),
    processed: Math.floor(40 + Math.random() * 140),
  })),
};

export const mockSystemLogs = [
  { id: 1, timestamp: '2024-01-15 14:30:22', action: 'Model Training', user: 'System', status: 'success', details: 'Temperature prediction model v3.2 trained successfully' },
  { id: 2, timestamp: '2024-01-15 13:15:08', action: 'Data Upload', user: 'admin@climaai.in', status: 'success', details: 'Uploaded IMD_rainfall_2023.csv (2.4MB)' },
  { id: 3, timestamp: '2024-01-15 12:00:00', action: 'Prediction', user: 'priya@climaai.in', status: 'success', details: 'Generated forecast for Maharashtra Q2 2024' },
  { id: 4, timestamp: '2024-01-14 22:45:33', action: 'System Alert', user: 'System', status: 'warning', details: 'High memory usage detected on prediction server' },
  { id: 5, timestamp: '2024-01-14 18:20:11', action: 'User Login', user: 'admin@climaai.in', status: 'success', details: 'Admin login from 192.168.1.45' },
  { id: 6, timestamp: '2024-01-14 16:10:45', action: 'Model Deploy', user: 'System', status: 'success', details: 'Rainfall anomaly model v2.1 deployed to production' },
  { id: 7, timestamp: '2024-01-14 14:05:22', action: 'Data Export', user: 'priya@climaai.in', status: 'success', details: 'Exported climate trends report for 2023' },
  { id: 8, timestamp: '2024-01-14 10:30:00', action: 'Backup', user: 'System', status: 'success', details: 'Daily database backup completed (12.4GB)' },
];

export default api;
