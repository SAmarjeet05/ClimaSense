"""
FastAPI Application Entry Point
Phase 5 - Real-Time Weather Data & AI Intelligence
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
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
from app.services.background_weather_service import BackgroundWeatherService

# Import models to ensure they're registered
from app.models.user import User
from app.models.prediction_log import PredictionLog
from app.models.dataset import Dataset
from app.models.dataset_row import DatasetRow
from app.models.system_log import SystemLog
from app.models.realtime_weather import RealtimeWeatherData

# Create database tables on startup
try:
    print("Initializing database...")
    create_tables()
    print("✅ All models registered and tables created (including realtime_weather_data)")
except Exception as db_error:
    print(f"❌ DATABASE INITIALIZATION ERROR: {str(db_error)}")
    logger.error(f"Database initialization failed: {str(db_error)}", exc_info=True)
    # Continue anyway - app can still handle requests


# ============================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app startup and shutdown events
    Starts background weather updates (non-blocking)
    """
    # STARTUP EVENT
    print("\n" + "="*60)
    print("🌍 CLIMATE INTELLIGENCE PLATFORM STARTING UP")
    print("="*60)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Initialize database
        print("\n📝 Step 1: Initializing database...")
        db = next(get_db())
        print("✅ Database session obtained")
        db.close()
        print("✅ Database ready")
        
        # Start background weather service (NON-BLOCKING)
        print("\n📡 Step 2: Starting background weather service...")
        try:
            BackgroundWeatherService.start()
            print("   ✅ Background weather service started")
            print("   - Weather will be fetched continuously every 5 minutes")
            print("   - Staggered requests prevent API hammering")
            print("   - Cached data used during API outages")
        except Exception as e:
            logger.error(f"Background weather service startup error: {str(e)}")
            print(f"   ⚠️ Warning: {str(e)}")
        
        # Optional: Start the weather update scheduler (if needed)
        print("\n⏱️  Step 3: Starting optional scheduled updates...")
        try:
            from app.core.database import SessionLocal
            WeatherUpdateScheduler.start_scheduler(SessionLocal)
            print("   ✅ Scheduler started - additional update mechanism running")
        except Exception as e:
            logger.error(f"Scheduler startup error: {str(e)}")
            print(f"   ⚠️ Scheduler not available: {str(e)}")
        
        print("\n" + "="*60)
        print("✅ APPLICATION READY - ALL ROUTES AVAILABLE")
        print("="*60)
        print("Access the API:")
        print("  🌐 Root: https://climasense-production.up.railway.app/")
        print("  📚 Docs: https://climasense-production.up.railway.app/docs")
        print("  🏥 Health: https://climasense-production.up.railway.app/health")
        print("  🌡️  Weather: https://climasense-production.up.railway.app/api/realtime-weather")
        print("="*60 + "\n")
        print("🚀 STARTUP COMPLETE - APP IS FULLY OPERATIONAL")
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
        BackgroundWeatherService.stop()
        print("✅ Background weather service stopped")
    except Exception as e:
        logger.error(f"Weather service shutdown error: {str(e)}")
    
    try:
        WeatherUpdateScheduler.stop_scheduler()
        print("✅ Scheduler stopped")
    except Exception as e:
        logger.error(f"Scheduler shutdown error: {str(e)}")
    
    print("="*60 + "\n")


# Initialize FastAPI app with lifespan
print("\n" + "="*60)
print("🔧 CREATING FASTAPI APPLICATION INSTANCE...")
print("="*60)

app = FastAPI(
    title="Climate Change Data Analysis API",
    description="Phase 5 - AI-Powered Climate Intelligence Platform with Real-Time Weather Data",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

print("✅ FastAPI app instance created successfully")
print("="*60 + "\n")

# Add CORS middleware - configure for production/development
# Production: allow frontend from Vercel/Railway
allowed_origins = [
    # Development
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    # Production - Common Vercel domains
    "https://clima-sense-teal.vercel.app",
    "https://climasense-frontend.vercel.app",
    "https://climasense-production.vercel.app",
    "https://clima-sense.vercel.app",
]

# Add any additional origins from environment variable
env_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
allowed_origins.extend([origin.strip() for origin in env_origins if origin.strip()])

# For production on Railway, if frontend URL is known, add it
frontend_url = os.getenv("FRONTEND_URL", "")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)
    logger.info(f"✅ Added FRONTEND_URL to CORS: {frontend_url}")

# Log CORS configuration
logger.info(f"🔐 CORS Allowed Origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
print("\n📌 Registering API routers...")
try:
    print("  ✓ Including auth router (prefix: /auth)")
    app.include_router(auth.router)
    print("  ✓ Including climate router (prefix: /api)")
    app.include_router(climate.router)
    print("  ✓ Including climate_map router (prefix: /api)")
    app.include_router(climate_map.router)
    print("  ✓ Including admin router (prefix: /api/admin)")
    app.include_router(admin.router)
    print("  ✓ Including intelligence router (prefix: /api)")
    app.include_router(intelligence.router)
    print("  ✓ Including assistant router (prefix: /api/assistant)")
    app.include_router(assistant.router)
    print("✅ All routers registered successfully\n")
except Exception as router_error:
    print(f"❌ ERROR REGISTERING ROUTERS: {str(router_error)}")
    logger.error(f"Router registration failed: {str(router_error)}", exc_info=True)
    raise

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
    print("\n" + "="*60)
    print("🚀 STARTING FASTAPI SERVER WITH UVICORN")
    print("="*60)
    print(f"⏰ Start time: {datetime.now().isoformat()}")
    print(f"🌐 Host: 0.0.0.0, Port: 8001")
    print(f"📚 API Documentation: http://127.0.0.1:8001/docs")
    print(f"🏥 Health check: http://127.0.0.1:8001/health")
    print("="*60 + "\n")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
    except Exception as e:
        print(f"\n❌ FATAL ERROR: Failed to start uvicorn: {str(e)}")
        logger.error(f"Uvicorn startup failed: {str(e)}", exc_info=True)
        raise
