"""
Backup Weather Data Service
Generates realistic random weather data (Open-Meteo API removed)
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class OpenMeteoService:
    """Service to generate backup random weather data"""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"  # Deprecated
    
    # Weather ranges for realistic data
    WEATHER_RANGES = {
        "temperature": (15, 42),
        "rainfall": (0, 80),
        "humidity": (30, 95),
        "wind_speed": (5, 35)
    }
    
    # Create session with retry strategy
    @staticmethod
    def _create_session_with_retries():
        """Not needed - using backup data instead of API"""
        return None
    
    # Session instance
    _session = None
    
    @classmethod
    def get_session(cls):
        """Not needed - using backup data instead of API"""
        return None
    
    @classmethod
    def generate_random_weather(cls) -> Dict:
        """Generate realistic random weather data"""
        ranges = cls.WEATHER_RANGES
        
        temp = round(random.uniform(*ranges["temperature"]), 1)
        rainfall = round(random.uniform(*ranges["rainfall"]), 1)
        humidity = round(random.uniform(*ranges["humidity"]), 1)
        wind = round(random.uniform(*ranges["wind_speed"]), 1)
        
        # Correlation: higher temps usually lower humidity
        if temp > 35:
            humidity = max(30, humidity - 20)
        elif temp < 20:
            humidity = min(95, humidity + 15)
        
        weather_code = random.choice([0, 1, 2, 3, 45, 48, 51, 53, 55, 61, 63, 65, 71, 73, 75, 80, 81, 82, 85, 86])
        
        return {
            "temperature": temp,
            "precipitation": rainfall,
            "humidity": humidity,
            "wind_speed": wind,
            "weather_code": weather_code
        }
    
    # Indian cities with their coordinates (latitude, longitude)
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

    @staticmethod
    def fetch_location_weather(latitude: float, longitude: float, city_name: str = None) -> Dict:
        """
        Fetch weather for a location - now using backup random data
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            city_name: Optional city name for reference
            
        Returns:
            Dictionary with backup random weather data
        """
        try:
            # Generate backup random data
            weather = OpenMeteoService.generate_random_weather()
            
            logger.info(f"📊 Generated backup weather for {city_name or 'location'}: {weather['temperature']}°C")
            
            return {
                "city": city_name or f"{latitude},{longitude}",
                "latitude": latitude,
                "longitude": longitude,
                "temperature": weather["temperature"],
                "wind_speed": weather["wind_speed"],
                "weather_code": weather["weather_code"],
                "time": datetime.now().isoformat(),
                "precipitation": weather["precipitation"],
                "humidity": weather["humidity"],
                "timestamp": datetime.now().isoformat(),
                "source": "backup-random-data"
            }
            
        except Exception as e:
            logger.error(f"Error generating weather for {city_name}: {e}")
            return {"error": f"Error generating weather data: {str(e)}"}

    @staticmethod
    def fetch_all_cities_weather() -> Dict:
        """
        Generate backup random weather for all Indian cities
        
        Returns:
            Dictionary with all cities weather data and aggregated stats
        """
        try:
            cities_data = []
            temps = []
            precips = []
            
            logger.info(f"📊 Generating backup weather for {len(OpenMeteoService.INDIAN_CITIES)} cities...")
            
            for city_name, coords in OpenMeteoService.INDIAN_CITIES.items():
                try:
                    # Generate random weather
                    weather = OpenMeteoService.generate_random_weather()
                    temp = weather["temperature"]
                    
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
                    
                    city_point = {
                        "state": city_name,
                        "lat": coords["lat"],
                        "lng": coords["lng"],
                        "temperature": round(temp, 1),
                        "rainfall": round(weather.get("precipitation", 0), 1),
                        "wind_speed": round(weather.get("wind_speed", 0), 1),
                        "stability": 0.65,
                        "stability_score": 65,
                        "risk": "low",
                        "color": color,
                        "source": "backup-random-data",
                        "weather_code": weather.get("weather_code", 0),
                        "time": datetime.now().isoformat(),
                        "humidity": round(weather.get("humidity", 50), 1)
                    }
                    
                    cities_data.append(city_point)
                    temps.append(temp)
                    precips.append(weather.get("precipitation", 0))
                    
                    logger.debug(f"✅ {city_name}: {temp}°C (backup)")
                    
                except Exception as e:
                    logger.warning(f"❌ Error generating data for {city_name}: {e}")
            
            logger.info(f"✅ Generated weather for {len(cities_data)} cities")
            
            # Calculate aggregates
            avg_temp = sum(temps) / len(temps) if temps else 0
            avg_precip = sum(precips) / len(precips) if precips else 0
            high_risk_count = len([c for c in cities_data if c["risk"] == "high"])
            
            return {
                "total_regions": len(cities_data),
                "regions": cities_data,
                "statistics": {
                    "avg_temperature": round(avg_temp, 2),
                    "avg_rainfall": round(avg_precip, 2),
                    "high_risk_count": high_risk_count,
                    "source": "backup-random-data",
                    "cities_generated": len(cities_data),
                    "failed_count": len(OpenMeteoService.INDIAN_CITIES) - len(cities_data)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating all weather data: {e}")
            return {
                "error": f"Failed to generate weather data: {str(e)}",
                "regions": [],
                "statistics": {}
            }

    @staticmethod
    def fetch_region_forecast(latitude: float, longitude: float, days: int = 7) -> Dict:
        """
        Generate backup random forecast data for a region
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days to forecast (default 7)
            
        Returns:
            Dictionary with backup forecast data
        """
        try:
            forecast_points = []
            ranges = OpenMeteoService.WEATHER_RANGES
            
            # Generate random forecast for next N days
            for i in range(days):
                temp_max = round(random.uniform(ranges["temperature"][0], ranges["temperature"][1]), 1)
                temp_min = round(max(temp_max - 5, ranges["temperature"][0]), 1)
                precip = round(random.uniform(ranges["rainfall"][0], ranges["rainfall"][1]), 1)
                
                forecast_points.append({
                    "date": datetime.now().isoformat(),
                    "temp_max": temp_max,
                    "temp_min": temp_min,
                    "precipitation": precip,
                    "source": "backup-random-data"
                })
            
            logger.info(f"📊 Generated forecast: {len(forecast_points)} days")
            
            return {
                "latitude": latitude,
                "longitude": longitude,
                "forecast": forecast_points,
                "days": len(forecast_points),
                "source": "backup-random-data"
            }
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return {"error": f"Failed to generate forecast data: {str(e)}"}


# Initialize service
open_meteo_service = OpenMeteoService()
