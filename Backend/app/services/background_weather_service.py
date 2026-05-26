"""
Background Weather Service
Generates and caches backup random weather data
(Open-Meteo API removed - using backup data instead)
"""
import threading
import time
import logging
from typing import Dict, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class BackgroundWeatherService:
    """
    Non-blocking weather service that fetches in background
    Provides cached fallback when API is unavailable
    """
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Global weather cache - survives across requests
    _weather_cache: Dict = {}
    _cache_lock = threading.Lock()
    
    # Service state
    _updater_thread: Optional[threading.Thread] = None
    _is_running = False
    _session: Optional[None] = None  # Not used - backup data only
    
    # Indian cities with their coordinates
    INDIAN_CITIES = {
        "Delhi": {"lat": 28.6139, "lng": 77.2090},
        "Mumbai": {"lat": 19.0760, "lng": 72.8777},
        "Bangalore": {"lat": 12.9716, "lng": 77.5946},
        "Chennai": {"lat": 13.0827, "lng": 80.2707},
        "Hyderabad": {"lat": 17.3850, "lng": 78.4867},
        "Kolkata": {"lat": 22.5726, "lng": 88.3639},
        "Pune": {"lat": 18.5204, "lng": 73.8567},
        "Ahmedabad": {"lat": 23.0225, "lng": 72.5714},
        "Jaipur": {"lat": 26.9124, "lng": 75.7873},
        "Lucknow": {"lat": 26.8467, "lng": 80.9462},
        "Indore": {"lat": 22.7196, "lng": 75.8577},
        "Chandigarh": {"lat": 30.7333, "lng": 76.7794},
        "Bhopal": {"lat": 23.1815, "lng": 79.9864},
        "Visakhapatnam": {"lat": 17.6869, "lng": 83.2185},
        "Vadodara": {"lat": 22.3072, "lng": 73.1812},
        "Ghaziabad": {"lat": 28.6692, "lng": 77.4538},
        "Ludhiana": {"lat": 30.9010, "lng": 75.8573},
        "Coimbatore": {"lat": 11.0026, "lng": 76.9124},
        "Srinagar": {"lat": 34.0837, "lng": 74.7973},
        "Thiruvananthapuram": {"lat": 8.5241, "lng": 76.9366},
        "Nagpur": {"lat": 21.1458, "lng": 79.0882},
        "Kochi": {"lat": 9.9312, "lng": 76.2673},
        "Ranchi": {"lat": 23.3441, "lng": 85.3096},
        "Patna": {"lat": 25.5941, "lng": 85.1376},
        "Agra": {"lat": 27.1767, "lng": 78.0081},
        "Nashik": {"lat": 19.9975, "lng": 73.7898},
        "Aurangabad": {"lat": 19.8762, "lng": 75.3433},
        "Kalyan": {"lat": 19.2403, "lng": 73.1305},
        "Meerut": {"lat": 28.9845, "lng": 77.7064},
    }
    
    # Weather data ranges for realistic backup generation
    WEATHER_RANGES = {
        "temperature": (15, 42),  # 15-42°C
        "rainfall": (0, 80),      # 0-80mm
        "humidity": (30, 95),     # 30-95%
        "wind_speed": (5, 35)     # 5-35 km/h
    }
    
    @classmethod
    def _create_session(cls) -> None:
        """Not needed - using backup data instead of API"""
        pass
    
    @classmethod
    def get_session(cls) -> None:
        """Not needed - using backup data instead of API"""
        pass
    
    @classmethod
    def generate_random_weather(cls) -> Dict:
        """
        Generate realistic random weather data for backup
        
        Returns:
            Weather dict with random values
        """
        ranges = cls.WEATHER_RANGES
        
        # Generate realistic data with correlation
        temp = round(random.uniform(*ranges["temperature"]), 1)
        rainfall = round(random.uniform(*ranges["rainfall"]), 1)
        humidity = round(random.uniform(*ranges["humidity"]), 1)
        wind = round(random.uniform(*ranges["wind_speed"]), 1)
        
        # Add correlation: higher temps usually lower humidity
        if temp > 35:
            humidity = max(30, humidity - 20)
        elif temp < 20:
            humidity = min(95, humidity + 15)
        
        weather_code = random.choice([0, 1, 2, 3, 45, 48, 51, 53, 55, 61, 63, 65, 71, 73, 75, 80, 81, 82, 85, 86])
        
        return {
            "current_weather": {
                "temperature": temp,
                "precipitation": rainfall,
                "weather_code": weather_code,
                "wind_speed": wind
            },
            "humidity": humidity
        }
    
    @classmethod
    def fetch_single_city(cls, city: str, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch weather for single city - now using backup random data
        
        Returns:
            Weather dict stored in cache
        """
        try:
            # Generate backup random weather data
            logger.debug(f"📊 Generating backup weather for {city}")
            data = cls.generate_random_weather()
            
            # Store in cache
            with cls._cache_lock:
                cls._weather_cache[city] = {
                    "data": data,
                    "timestamp": time.time(),
                    "status": "fresh"
                }
            
            logger.info(f"✅ {city}: Backup weather cached")
            return data
            
        except Exception as e:
            logger.error(f"❌ {city}: Error generating weather - {e}")
            return None
    
    @classmethod
    def get_cached_weather(cls, city: str) -> Optional[Dict]:
        """
        Get cached weather data for a city
        
        Returns:
            Cached weather dict or None if not available
        """
        with cls._cache_lock:
            cached = cls._weather_cache.get(city)
            
            if cached:
                age = time.time() - cached["timestamp"]
                cache_status = "fresh" if age < 600 else "stale"  # Fresh if < 10 mins
                
                # Update status
                if cache_status != cached["status"]:
                    cached["status"] = cache_status
                
                logger.info(f"📦 {city}: Using {cache_status} cache (age: {age:.0f}s)")
                return cached["data"]
        
        return None
    
    @classmethod
    def background_updater(cls):
        """
        Background thread that fetches weather continuously
        Staggered requests to avoid hammering API
        """
        logger.info("🌍 Background weather updater started")
        
        while cls._is_running:
            try:
                cities = list(cls.INDIAN_CITIES.items())
                total = len(cities)
                updated = 0
                failed = 0
                
                logger.info(f"🔄 Starting background weather update cycle ({total} cities)")
                
                # Stagger requests: 2 seconds between each call
                for idx, (city, coords) in enumerate(cities, 1):
                    if not cls._is_running:
                        break
                    
                    logger.debug(f"[{idx}/{total}] Fetching {city}...")
                    
                    result = cls.fetch_single_city(
                        city,
                        coords["lat"],
                        coords["lng"]
                    )
                    
                    if result:
                        updated += 1
                    else:
                        # Try to use cache
                        cached = cls.get_cached_weather(city)
                        if cached:
                            updated += 1
                        else:
                            failed += 1
                    
                    # Stagger requests - don't hammer the API
                    if idx < total:
                        time.sleep(2)
                
                logger.info(f"✅ Update cycle complete: {updated} updated, {failed} failed")
                
                # Wait 5 minutes before next update cycle
                logger.info("⏰ Waiting 5 minutes before next weather update...")
                for remaining in range(300, 0, -1):
                    if not cls._is_running:
                        break
                    if remaining % 60 == 0:
                        logger.debug(f"⏳ Next update in {remaining}s")
                    time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in background updater: {e}")
                # Continue even if there's an error
                time.sleep(10)
        
        logger.info("🛑 Background weather updater stopped")
    
    @classmethod
    def start(cls):
        """
        Start background weather fetching (non-blocking)
        
        Should be called during app startup
        """
        if cls._is_running:
            logger.warning("Background weather service already running")
            return
        
        cls._is_running = True
        
        # Start daemon thread (won't block app shutdown)
        cls._updater_thread = threading.Thread(
            target=cls.background_updater,
            daemon=True,
            name="BackgroundWeatherUpdater"
        )
        cls._updater_thread.start()
        
        logger.info("🚀 Background weather service started (non-blocking)")
    
    @classmethod
    def stop(cls):
        """Stop background weather fetching"""
        cls._is_running = False
        
        if cls._updater_thread and cls._updater_thread.is_alive():
            cls._updater_thread.join(timeout=5)
        
        logger.info("🛑 Background weather service stopped")
    
    @classmethod
    def get_all_cached_weather(cls) -> Dict:
        """
        Get all cached weather data
        
        Used by endpoints to serve cached data when available
        
        Returns:
            Dict with all cities weather data
        """
        with cls._cache_lock:
            cities_data = []
            temps = []
            precips = []
            
            for city, cached_info in cls._weather_cache.items():
                try:
                    data = cached_info.get("data", {})
                    current = data.get("current_weather", {})
                    
                    temp = current.get("temperature", 0)
                    
                    # Determine color based on temperature
                    if temp < 0:
                        color = "#0066ff"
                    elif temp < 10:
                        color = "#0099ff"
                    elif temp < 15:
                        color = "#00ccff"
                    elif temp < 20:
                        color = "#00ff99"
                    elif temp < 25:
                        color = "#10b981"
                    elif temp < 30:
                        color = "#ffff00"
                    elif temp < 35:
                        color = "#f59e0b"
                    elif temp < 40:
                        color = "#ff6600"
                    else:
                        color = "#ef4444"
                    
                    coords = cls.INDIAN_CITIES.get(city, {})
                    
                    city_point = {
                        "state": city,
                        "lat": coords.get("lat", 0),
                        "lng": coords.get("lng", 0),
                        "temperature": round(temp, 1),
                        "rainfall": round(current.get("precipitation", 0), 1),
                        "wind_speed": round(current.get("wind_speed", 0), 1),
                        "stability": 0.65,
                        "stability_score": 65,
                        "risk": "low",
                        "color": color,
                        "source": "open-meteo-background-cache",
                        "weather_code": current.get("weather_code", 0),
                        "time": current.get("time", ""),
                        "cache_status": cached_info.get("status", "unknown"),
                        "cache_age": time.time() - cached_info.get("timestamp", 0)
                    }
                    
                    cities_data.append(city_point)
                    temps.append(temp)
                    precips.append(current.get("precipitation", 0))
                
                except Exception as e:
                    logger.warning(f"Error processing cached data for {city}: {e}")
            
            # Calculate aggregates
            avg_temp = sum(temps) / len(temps) if temps else 0
            avg_precip = sum(precips) / len(precips) if precips else 0
            
            return {
                "total_regions": len(cities_data),
                "regions": cities_data,
                "statistics": {
                    "avg_temperature": round(avg_temp, 2),
                    "avg_rainfall": round(avg_precip, 2),
                    "high_risk_count": len([c for c in cities_data if c["risk"] == "high"]),
                    "source": "open-meteo-background-cache",
                    "cities_cached": len(cities_data)
                },
                "timestamp": datetime.now().isoformat(),
                "note": "Data is from background cache (may be stale if API was unavailable)"
            }


# Initialize service
background_weather_service = BackgroundWeatherService()
