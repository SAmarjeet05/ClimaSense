"""
FastAPI Application Entry Point
Phase 5 - Real-Time Weather Data & AI Intelligence
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes
from app.routes import climate, climate_map, auth, admin, intelligence, assistant
from app.core.database import create_tables, get_db
from app.services.weather_scheduler import WeatherUpdateScheduler
from app.services.realtime_weather_service import RealtimeWeatherService

# Import models to ensure they're registered
from app.models.user import User
from app.models.prediction_log import PredictionLog
from app.models.dataset import Dataset
from app.models.dataset_row import DatasetRow
from app.models.system_log import SystemLog
from app.models.realtime_weather import RealtimeWeatherData

# Create database tables on startup
print("Initializing database...")
create_tables()
print("✅ All models registered and tables created (including realtime_weather_data)")


# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app startup and shutdown events
    Initializes scheduler and runs first weather update
    """
    # STARTUP EVENT
    print("\n" + "="*60)
    print("🌍 CLIMATE INTELLIGENCE PLATFORM STARTING UP")
    print("="*60)
    
    try:
        # Get database session for initial update
        db = next(get_db())
        
        # Run initial weather update to populate real-time data
        print("\n📡 Fetching initial real-time weather data from Open-Meteo...")
        try:
            results = RealtimeWeatherService.update_all_cities_from_api(db)
            logger.info(f"✅ Initial weather update: {results['success']} cities updated")
            print(f"   - {results['created']} cities created")
            print(f"   - {results['updated']} cities updated")
            print(f"   - {results['failed']} cities failed")
        except Exception as e:
            logger.error(f"Initial weather update error: {str(e)}")
            print(f"   ⚠️ Initial update encountered issues: {str(e)}")
        finally:
            db.close()
        
        # Start the weather update scheduler
        print("\n⏱️  Starting automatic weather update scheduler...")
        try:
            # Get a new session for scheduler
            from app.core.database import SessionLocal
            WeatherUpdateScheduler.start_scheduler(SessionLocal)
            print("   ✅ Scheduler started - will update every 30 minutes")
        except Exception as e:
            logger.error(f"Scheduler startup error: {str(e)}")
            print(f"   ⚠️ Scheduler error (manual updates still available): {str(e)}")
        
        print("\n" + "="*60)
        print("✅ APPLICATION READY")
        print("="*60)
        print("Endpoints available:")
        print("  📚 API Docs: http://localhost:8001/docs")
        print("  🗺️  Real-time weather: GET /api/realtime/latest-data")
        print("  📊 Weather stats: GET /api/realtime/stats")
        print("  🔄 Manual update: POST /api/realtime/update-weather")
        print("  ⏱️  Scheduler status: GET /api/realtime/scheduler-status")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        print(f"\n⚠️ Startup error: {str(e)}\n")
    
    # Yield control to the application
    yield
    
    # SHUTDOWN EVENT
    print("\n" + "="*60)
    print("⏹️  SHUTTING DOWN")
    print("="*60)
    try:
        WeatherUpdateScheduler.stop_scheduler()
        print("✅ Scheduler stopped")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")
    print("="*60 + "\n")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Climate Change Data Analysis API",
    description="Phase 5 - AI-Powered Climate Intelligence Platform with Real-Time Weather Data",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware - configure for production/development
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
# Always allow localhost for development
if "localhost" not in str(allowed_origins):
    allowed_origins = ["http://localhost:5173", "http://localhost:3000"] + allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(climate.router)
app.include_router(climate_map.router)
app.include_router(admin.router)
app.include_router(intelligence.router)
app.include_router(assistant.router)

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Welcome to the Climate Change Data Analysis API"""
    return {
        "message": "🌍 Climate Change Data Analysis API - Phase 5: AI Intelligence",
        "version": "5.0.0",
        "architecture": "AI-Powered Intelligence + Real-Time Weather Data + Database Integration",
        "status": "running",
        "real_time_features": {
            "weather_updates": "Automatic every 30 minutes",
            "data_sources": ["Open-Meteo API (real-time weather)", "Historical climate database"],
            "cities_covered": 39,
            "coverage": "Entire India"
        },
        "documentation": "http://127.0.0.1:8001/docs",
        "real_time_endpoints": {
            "latest_data": "GET /api/realtime/latest-data",
            "statistics": "GET /api/realtime/stats",
            "manual_update": "POST /api/realtime/update-weather",
            "scheduler_status": "GET /api/realtime/scheduler-status",
            "generate_insights": "POST /api/realtime/generate-insights"
        },
        "authentication": {
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "get_me": "GET /auth/me",
            "note": "After login, use token in Swagger Authorize button"
        },
        "next_steps": [
            "1. POST to /auth/register to create account",
            "2. POST to /auth/login to get JWT token",
            "3. Click Authorize in Swagger and paste token",
            "4. Access real-time data endpoints",
            "5. View results in climate heatmap"
        ]
    }


@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Climate Data Analysis API",
        "version": "5.0.0",
        "real_time_weather": "enabled",
        "scheduler": "active"
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server...")
    print("📚 API Documentation: http://127.0.0.1:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)
