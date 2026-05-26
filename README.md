# ClimaSense - Intelligent Climate Analytics Dashboard

A comprehensive full-stack climate intelligence platform that combines real-time weather data, historical climate analysis, AI-powered insights, and machine learning predictions with an interactive map-based dashboard.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [Frontend Features](#frontend-features)
- [Backend Services](#backend-services)
- [AI & ML Capabilities](#ai--ml-capabilities)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## Project Overview

**ClimaSense** is an intelligent climate analytics platform designed to provide comprehensive weather insights, trends analysis, and predictions. It integrates:

- **Real-time Weather Data**: Live weather updates from multiple sources
- **Historical Climate Analysis**: Multi-year climate trend analysis
- **AI-Powered Assistant**: Natural language interface for climate queries using LLM (Groq/Together AI)
- **Machine Learning Predictions**: Temperature, rainfall, and anomaly predictions
- **Interactive Dashboard**: Map-based visualization with heatmaps and charts
- **Admin Panel**: Administrative controls for data management and user administration
- **User Authentication**: JWT-based authentication with role-based access

The platform is designed for climate analysts, researchers, meteorologists, and general users interested in climate data and forecasting.

---

## Key Features

### 🌍 Core Features
- **Real-Time Weather Monitoring**: Live weather data for multiple cities worldwide
- **Climate Trend Analysis**: Multi-year climate trend detection and visualization
- **Historical Data Analysis**: Comprehensive historical climate data processing
- **Weather Forecasting**: ML-based temperature and rainfall predictions
- **Anomaly Detection**: Identifies unusual weather patterns and anomalies
- **Comparative Analysis**: Compare climate metrics across multiple cities

### 🤖 AI & Intelligence Features
- **AI Assistant**: Conversational assistant for climate queries using Groq API
- **Intent Detection**: Intelligent detection of user intent (trends, forecasts, comparisons)
- **Data Summarization**: Automated summarization of climate data insights
- **Natural Language Processing**: Understand and respond to complex climate questions

### 📊 Analytics & Visualization
- **Interactive Maps**: Leaflet-based maps with heatmap layers
- **Climate Charts**: Recharts for visualizing temperature, rainfall, and trends
- **Real-time Dashboard**: Live dashboard with key metrics and indicators
- **Historical Charts**: Multi-year trend visualizations
- **Data Export**: Export climate data for external analysis

### 👤 User Management
- **User Registration & Login**: JWT-based authentication
- **Role-Based Access Control**: Admin, user, and analyst roles
- **Admin Panel**: User management, data administration, system logs
- **Audit Logging**: Complete system activity logging

### 📱 Frontend Features
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark/Light Theme Support**: Theme switching with next-themes
- **Interactive UI Components**: Built with Radix UI and Tailwind CSS
- **Real-time Updates**: Live data updates using React Query
- **Map Visualization**: Interactive maps with heatmaps and markers

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1 (Python 3.10.13)
- **Server**: Uvicorn 0.24.0
- **Database**: SQLAlchemy 2.0.23 with SQLite
- **Data Processing**: Pandas 2.1.3, NumPy 1.24.3
- **Machine Learning**: Scikit-learn 1.3.2, Joblib 1.3.2
- **API & HTTP**: Requests 2.31.0, HTTPx 0.25.0
- **Scheduling**: APScheduler 3.10.4
- **Authentication**: PassLib 1.7.4, Python-Jose 3.3.0
- **Validation**: Pydantic 2.5.0
- **Environment**: Python-dotenv 1.0.0
- **AI/LLM Integration**: Groq API, Ollama, Together AI

### Frontend
- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.0
- **Routing**: React Router DOM 6.20.0
- **State Management**: Zustand 4.4.1
- **API Client**: Axios 1.6.0
- **Data Fetching**: TanStack React Query 5.96.1
- **Styling**: Tailwind CSS 3.3.0, Tailwind Merge
- **UI Components**: Radix UI (Label, Slider, Tooltip, Toast, Slot)
- **Visualization**: Recharts 2.10.0, Leaflet 1.9.4, Leaflet.heat
- **Animation**: Framer Motion 10.16.0
- **Icons**: Lucide React 0.292.0
- **Markdown**: React Markdown 10.1.0
- **Notifications**: Sonner 2.0.7
- **Theme**: Next Themes 0.4.6

### DevOps & Deployment
- **Container**: Railway (NIXPACKS builder)
- **Environment**: Python 3.10.13
- **Frontend Hosting**: Vercel
- **Package Manager**: NPM (Frontend), Pip (Backend)

---

## Project Structure

```
ClimaSense/
├── Backend/                          # FastAPI Backend Application
│   ├── app/
│   │   ├── core/                    # Core configurations
│   │   │   ├── config.py
│   │   │   └── database.py          # Database setup & connection
│   │   ├── models/                  # SQLAlchemy ORM Models
│   │   │   ├── user.py              # User model with authentication
│   │   │   ├── prediction_log.py    # ML predictions storage
│   │   │   ├── realtime_weather.py  # Real-time weather data
│   │   │   ├── dataset.py           # Dataset management
│   │   │   ├── dataset_row.py       # Dataset rows
│   │   │   ├── system_log.py        # System activity logs
│   │   │   └── __init__.py
│   │   ├── routes/                  # API Endpoints
│   │   │   ├── climate.py           # Climate data endpoints
│   │   │   ├── climate_map.py       # Map & heatmap endpoints
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── admin.py             # Admin panel endpoints
│   │   │   ├── intelligence.py      # AI intelligence endpoints
│   │   │   ├── assistant.py         # AI assistant endpoints
│   │   │   └── __init__.py
│   │   ├── services/                # Business Logic Services
│   │   │   ├── auth_service.py      # Authentication logic
│   │   │   ├── database_service.py  # Database operations
│   │   │   ├── weather_scheduler.py # Scheduled weather updates
│   │   │   ├── realtime_weather_service.py # Real-time data fetching
│   │   │   ├── ml_service.py        # ML predictions (v1)
│   │   │   ├── ml_service_v2.py     # ML predictions (v2)
│   │   │   ├── assistant_service.py # AI assistant logic
│   │   │   ├── intent_detector.py   # User intent classification
│   │   │   ├── insight_service.py   # Data insights generation
│   │   │   ├── ollama_service.py    # Ollama LLM integration
│   │   │   ├── groq_service.py      # Groq API integration
│   │   │   ├── open_meteo_service.py # Open-Meteo API integration
│   │   │   └── __init__.py
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   └── main.py                  # FastAPI app entry point
│   ├── models/                      # ML Model storage & versioning
│   ├── data/                        # Static data & datasets
│   ├── test_data/                   # Test fixtures
│   ├── test_output/                 # Test output files
│   ├── tests/                       # Test suite
│   │   ├── test_api.py
│   │   ├── test_api_endpoints.py
│   │   ├── test_anomaly_detection.py
│   │   ├── test_forecast.py
│   │   └── [70+ more test files]
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment variables template
│   ├── .env                         # Environment variables (local)
│   ├── migrate_db.py               # Database migration script
│   ├── climate.db                  # SQLite database file
│   └── venv/                        # Python virtual environment
│
├── Frontend/                         # React + Vite Frontend Application
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   ├── services/               # API service clients
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── context/                # React context providers
│   │   ├── styles/                 # Global styles
│   │   ├── types/                  # TypeScript type definitions
│   │   ├── utils/                  # Utility functions
│   │   └── App.tsx                 # Main App component
│   ├── public/                      # Static assets
│   ├── dist/                        # Build output
│   ├── package.json                # Node dependencies
│   ├── package-lock.json           # Dependency lock file
│   ├── vite.config.ts              # Vite configuration
│   ├── tailwind.config.ts          # Tailwind CSS config
│   ├── tsconfig.json               # TypeScript configuration
│   ├── components.json             # shadcn/ui components config
│   ├── vercel.json                 # Vercel deployment config
│   ├── playwright.config.ts        # E2E test configuration
│   ├── index.html                  # HTML entry point
│   └── README.md                    # Frontend documentation
│
├── railway.json                     # Railway deployment config
├── runtime.txt                      # Python runtime version
└── README.md                        # This file

```

---

## Installation & Setup

### Prerequisites
- Python 3.10.13 or later
- Node.js 18+ and NPM
- Git
- Virtual environment manager (venv or conda)

### Backend Setup

1. **Navigate to Backend Directory**
   ```bash
   cd Backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd Frontend
   ```

2. **Install Node Dependencies**
   ```bash
   npm install
   ```

---

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `Backend/` directory with the following variables:

```env
# Groq API Configuration (Primary LLM)
# Get free API key from: https://console.groq.com
GROQ_API_KEY=gsk_your_groq_api_key_here

# Together AI Configuration (Fallback LLM)
# Get free API key from: https://www.together.ai
TOGETHER_API_KEY=your_together_api_key_here

# CORS Configuration - comma-separated frontend URLs
# Development: http://localhost:5173,http://localhost:3000
# Production: https://your-frontend.vercel.app
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Database Configuration
DATABASE_URL=sqlite:///./climate.db

# Admin Configuration
ADMIN_PASSWORD=your_secure_admin_password_here

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8001

# JWT Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create a `.env` file in the `Frontend/` directory:

```env
VITE_API_URL=http://localhost:8001
VITE_API_TIMEOUT=30000
```

---

## Running the Application

### Backend Development Server

```bash
cd Backend
# Make sure virtual environment is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

The backend API will be available at: `http://localhost:8001`

API Documentation (Swagger UI): `http://localhost:8001/docs`

### Frontend Development Server

```bash
cd Frontend
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### Running Both Concurrently

In one terminal:
```bash
cd Backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

In another terminal:
```bash
cd Frontend
npm run dev
```

---

## Database Models

### User Model
- **Purpose**: User authentication and account management
- **Fields**: ID, username, email, password_hash, role, created_at, updated_at
- **Relationships**: Has many prediction logs, system logs, datasets
- **Roles**: admin, user, analyst

### RealtimeWeatherData Model
- **Purpose**: Stores real-time weather information
- **Fields**: ID, city, country, temperature, humidity, rainfall, wind_speed, last_updated
- **Usage**: Updated every 30 minutes by scheduler
- **Data Source**: Open-Meteo API or Weather APIs

### PredictionLog Model
- **Purpose**: Stores ML model predictions
- **Fields**: ID, user_id, city, prediction_type, value, confidence, created_at
- **Prediction Types**: temperature_forecast, rainfall_forecast, anomaly_detection

### Dataset Model
- **Purpose**: Manages user-created datasets
- **Fields**: ID, user_id, name, description, created_at, updated_at
- **Relationships**: Has many dataset rows

### DatasetRow Model
- **Purpose**: Individual rows in datasets
- **Fields**: ID, dataset_id, data (JSON), created_at

### SystemLog Model
- **Purpose**: Audit and system activity logging
- **Fields**: ID, user_id, action, status, timestamp
- **Actions**: login, logout, data_export, admin_action, error

---

## API Endpoints

### Authentication Routes (`/api/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `POST /auth/refresh` - Refresh JWT token

### Climate Routes (`/api/climate`)
- `GET /climate/cities` - Get all available cities
- `GET /climate/historical/{city}` - Get historical climate data
- `GET /climate/trends/{city}` - Get climate trends for city
- `GET /climate/forecast/{city}` - Get weather forecast
- `GET /climate/realtime/{city}` - Get real-time weather
- `POST /climate/compare` - Compare multiple cities
- `GET /climate/anomalies/{city}` - Get weather anomalies

### Map Routes (`/api/map`)
- `GET /map/heatmap` - Get heatmap data
- `GET /map/markers` - Get map markers for cities
- `GET /map/layers` - Get available map layers
- `POST /map/export` - Export map data

### Intelligence Routes (`/api/intelligence`)
- `GET /intelligence/insights/{city}` - Get AI insights
- `POST /intelligence/analyze` - Analyze climate data
- `GET /intelligence/predictions` - Get ML predictions
- `POST /intelligence/anomaly-detection` - Detect anomalies

### Assistant Routes (`/api/assistant`)
- `POST /assistant/chat` - Chat with AI assistant
- `POST /assistant/analyze-query` - Analyze user query
- `GET /assistant/history` - Get chat history
- `POST /assistant/intent-detect` - Detect user intent

### Admin Routes (`/api/admin`)
- `GET /admin/users` - List all users
- `PUT /admin/users/{user_id}` - Update user
- `DELETE /admin/users/{user_id}` - Delete user
- `GET /admin/system-logs` - Get system logs
- `POST /admin/promote-admin` - Promote user to admin
- `GET /admin/statistics` - Get system statistics

---

## Frontend Features

### Pages & Views

1. **Dashboard Page**
   - Overview of current weather conditions
   - Key metrics and indicators
   - Recent alerts and anomalies
   - Quick action buttons

2. **Map View**
   - Interactive Leaflet map
   - Real-time heatmap overlay
   - City markers with climate data
   - Layer controls

3. **Analytics Page**
   - Multi-year climate trends
   - Comparative city analysis
   - Historical data charts
   - Custom report generation

4. **Forecast Page**
   - Temperature forecasts (1-7 days)
   - Rainfall predictions
   - Confidence indicators
   - Seasonal trends

5. **AI Assistant Page**
   - Chat interface with AI
   - Natural language queries
   - Real-time suggestions
   - Chat history

6. **Admin Panel**
   - User management
   - Data administration
   - System logs viewer
   - Configuration management

7. **Settings Page**
   - User preferences
   - Theme selection (dark/light)
   - Notification settings
   - API key management

### UI Components

- **Charts**: Recharts (Line, Bar, Area charts)
- **Maps**: Leaflet maps with heatmap layers
- **Forms**: Radix UI form controls
- **Tables**: Responsive data tables
- **Cards**: Component card layout system
- **Modals**: Dialog & toast notifications
- **Loading States**: Skeleton screens and spinners
- **Responsive Design**: Mobile-first approach

---

## Backend Services

### Authentication Service (`auth_service.py`)
- User registration and validation
- Password hashing with PassLib
- JWT token generation and validation
- Role-based access control

### Database Service (`database_service.py`)
- ORM operations and migrations
- Connection pooling
- Transaction management
- Query optimization

### Weather Scheduler (`weather_scheduler.py`)
- APScheduler-based scheduled tasks
- Real-time data updates (30-minute intervals)
- Automated data refresh
- Error recovery and retry logic

### Real-time Weather Service (`realtime_weather_service.py`)
- Integrates with Open-Meteo API
- Fetches current weather conditions
- Stores data in database
- Provides real-time endpoints

### ML Service (`ml_service.py` & `ml_service_v2.py`)
- Temperature prediction models
- Rainfall forecasting
- Anomaly detection
- Model training and evaluation
- Uses Scikit-learn for ML algorithms

### Assistant Service (`assistant_service.py`)
- Conversational AI logic
- Query processing
- Data summarization
- Response generation with LLM

### Intent Detector (`intent_detector.py`)
- User intent classification
- Query categorization (trends, forecast, comparison, etc.)
- Multi-intent detection
- Confidence scoring

### Groq Service (`groq_service.py`)
- Integration with Groq API
- LLM model selection and routing
- Token management
- Error handling and retries

### Ollama Service (`ollama_service.py`)
- Local Ollama LLM integration
- Fallback when cloud LLMs unavailable
- Model switching

### Open-Meteo Service (`open_meteo_service.py`)
- Free weather API integration
- Multi-city data fetching
- Historical weather data
- Forecast data retrieval

---

## AI & ML Capabilities

### Machine Learning Models

1. **Temperature Prediction Model**
   - Uses historical temperature data
   - Scikit-learn regression models
   - RMSE optimization
   - Confidence intervals

2. **Rainfall Prediction Model**
   - Seasonal pattern recognition
   - Multi-step forecasting
   - Probability estimation

3. **Anomaly Detection Model**
   - Isolation Forest algorithm
   - Statistical outlier detection
   - Real-time anomaly flagging
   - Historical pattern comparison

### AI Assistant Features

- **Natural Language Understanding**: Groq API integration
- **Intent Detection**: Classifies user queries into actions
- **Data Summarization**: Converts raw data into insights
- **Multi-turn Conversations**: Maintains context across queries
- **Fallback Responses**: Works with cached data if LLM unavailable

### Supported Query Types

1. **Trend Analysis**: "What are the trends in Delhi?"
2. **Forecasting**: "What's the forecast for Mumbai next week?"
3. **Comparison**: "Compare climate in Delhi vs Bangalore"
4. **Historical**: "Show me rainfall from 2020-2025"
5. **Anomalies**: "Detect unusual patterns in temp data"

---

## Testing

### Running Backend Tests

```bash
cd Backend

# Run all tests
pytest

# Run specific test file
pytest test_api.py -v

# Run with coverage
pytest --cov=app

# Run specific test function
pytest test_api.py::test_login -v

# Run tests matching pattern
pytest -k "forecast" -v
```

### Test Files Available

**70+ comprehensive test files including:**
- `test_api.py` - API endpoint tests
- `test_api_endpoints.py` - Detailed endpoint testing
- `test_anomaly_detection.py` - Anomaly detection tests
- `test_forecast.py` - Forecast model tests
- `test_forecast_cities.py` - Multi-city forecasting
- `test_heatmap_production.py` - Heatmap generation
- `test_scenario_endtoend.py` - End-to-end scenarios
- `test_phase*.py` - Phase-specific testing

### Frontend Testing

```bash
cd Frontend

# Run Vitest
npm run test

# Run Playwright E2E tests
npx playwright test

# Run with UI
npx playwright test --ui
```

### Manual Testing Checklist

- [ ] User Registration & Login
- [ ] Real-time weather updates
- [ ] Climate trend analysis
- [ ] Forecast generation
- [ ] Map heatmap rendering
- [ ] AI assistant responses
- [ ] Anomaly detection
- [ ] Admin panel functions
- [ ] Dark/light theme switching
- [ ] Mobile responsiveness

---

## Deployment

### Railway Deployment (Backend)

1. **Push code to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect Railway Project**
   - Go to Railway.app
   - Create new project
   - Connect GitHub repository
   - Railway auto-deploys with `railway.json` config

3. **Environment Variables on Railway**
   - Add all `.env` variables in Railway dashboard
   - Ensure `GROQ_API_KEY` and `TOGETHER_API_KEY` are set
   - Set production `ALLOWED_ORIGINS`

4. **Verify Deployment**
   ```bash
   curl https://your-railway-app.up.railway.app/docs
   ```

### Vercel Deployment (Frontend)

1. **Connect Frontend to Vercel**
   ```bash
   npm install -g vercel
   vercel
   ```

2. **Environment Variables**
   - Set `VITE_API_URL` to your backend URL
   - Configure `VITE_API_TIMEOUT`

3. **Build Settings**
   - Build command: `npm run build`
   - Output directory: `dist`

### Production Checklist

- [ ] Environment variables configured
- [ ] Database backups set up
- [ ] CORS origins configured
- [ ] SSL/TLS certificates
- [ ] API rate limiting enabled
- [ ] Logging configured
- [ ] Error monitoring (Sentry/etc)
- [ ] Performance monitoring
- [ ] Database indexes created
- [ ] Automated backups scheduled

---

## Key Files & Their Purposes

### Core Application Files
- **Backend/app/main.py** - FastAPI app initialization with lifespan events
- **Backend/app/core/database.py** - SQLAlchemy database setup and session management
- **Frontend/src/App.tsx** - Main React component with routing

### Critical Services
- **Backend/app/services/assistant_service.py** - AI assistant logic and data processing
- **Backend/app/services/ml_service.py** - Machine learning predictions
- **Backend/app/services/weather_scheduler.py** - Real-time data updates

### Route Handlers
- **Backend/app/routes/climate.py** - Climate data endpoints (3000+ lines)
- **Backend/app/routes/assistant.py** - AI assistant endpoints
- **Backend/app/routes/intelligence.py** - ML & intelligence endpoints

---

## Data Flow Architecture

```
Frontend (React)
    ↓
Axios HTTP Client
    ↓
FastAPI Backend (Port 8001)
    ↓
Services Layer (ML, AI, Database)
    ↓
Database (SQLite)
    ↓
External APIs (Groq, Open-Meteo, Together AI)
```

### Real-Time Data Flow

```
Open-Meteo API (Free)
    ↓
WeatherScheduler (Every 30 min)
    ↓
RealtimeWeatherService
    ↓
Database (realtime_weather_data table)
    ↓
Frontend Dashboard (Real-time updates)
```

---

## Performance Optimization

- **Database Indexing**: Indexes on frequently queried columns
- **Query Caching**: Redis-like caching for frequently accessed data
- **API Response Caching**: 30-minute cache for weather data
- **Frontend Code Splitting**: Lazy loading of page components
- **Image Optimization**: Compressed assets
- **API Rate Limiting**: Prevent abuse
- **Database Connection Pooling**: Reuse connections

---

## Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: PassLib with secure algorithms
- **CORS Configuration**: Restrict cross-origin requests
- **Environment Variables**: Sensitive data in .env
- **Role-Based Access Control**: Admin, user, analyst roles
- **Input Validation**: Pydantic schema validation
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Rate Limiting**: API rate limiting

---

## Troubleshooting

### Backend Issues

**ModuleNotFoundError: No module named 'app'**
```bash
# Ensure you're running from Backend directory with activated venv
cd Backend
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

**Database Error**
```bash
# Reset database
rm climate.db
python migrate_db.py
```

**Groq API Key Error**
```bash
# Verify .env has correct GROQ_API_KEY
# Get key from https://console.groq.com
```

### Frontend Issues

**npm install fails**
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**VITE_API_URL not working**
```bash
# Ensure .env file exists in Frontend/ directory
# Restart dev server after changing .env
```

---

## Future Enhancements

- [ ] Real-time notifications for weather alerts
- [ ] Advanced ML models (LSTM, Prophet)
- [ ] Mobile app (React Native)
- [ ] Satellite imagery integration
- [ ] User-created custom reports
- [ ] Data sharing and collaboration
- [ ] Advanced filtering and search
- [ ] Multi-language support
- [ ] Weather API alternatives
- [ ] Blockchain for data verification

---

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit pull request

---

## Project Statistics

- **Backend**: ~3000+ lines of Python code
- **Frontend**: ~5000+ lines of React/TypeScript
- **Test Files**: 70+ comprehensive test files
- **API Endpoints**: 40+ endpoints
- **Database Models**: 6 core models
- **Services**: 12+ service modules
- **ML Models**: 3+ trained models

---

## Support & Contact

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing test files for usage examples
- Review API documentation at `/docs` endpoint

---

## License

This project is developed as part of a climate intelligence platform. See LICENSE file for details.

---

## Changelog

### Phase 5 (Current)
- ✅ Real-time weather data integration
- ✅ AI assistant with natural language processing
- ✅ Advanced anomaly detection
- ✅ Map-based visualization
- ✅ Admin panel
- ✅ Role-based access control

### Phase 4
- ✅ Machine learning predictions
- ✅ Forecast generation
- ✅ Historical data analysis

### Phase 3
- ✅ Multi-city support
- ✅ User authentication

### Phase 2
- ✅ Basic climate data endpoints

### Phase 1
- ✅ Project initialization

---

**Last Updated**: May 26, 2026

For the latest updates and documentation, refer to individual component README files and inline code comments.
