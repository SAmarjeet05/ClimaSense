"""
Open-Meteo API Service
Fetches real-time weather data for Indian cities/regions
"""
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class OpenMeteoService:
    """Service to fetch real-time weather data from Open-Meteo API"""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Indian cities with their coordinates (latitude, longitude)
    INDIAN_CITIES = {
        "Delhi": {"lat": 28.6139, "lng": 77.2090},
        "Mumbai": {"lat": 19.0760, "lng": 72.8777},
        "Bangalore": {"lat": 12.9716, "lng": 77.5946},
        "Chennai": {"lat": 13.0827, "lng": 80.2707},
        "Hyderabad": {"lat": 17.3850, "lng": 78.4867},
        "Kolkata": {"lat": 22.5726, "lng": 88.3639},
        "pune": {"lat": 18.5204, "lng": 73.8567},
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
        "Vadodara": {"lat": 22.3072, "lng": 73.1812},
        "Kalyan": {"lat": 19.2403, "lng": 73.1305},
        "Meerut": {"lat": 28.9845, "lng": 77.7064},
    }

    @staticmethod
    def fetch_location_weather(latitude: float, longitude: float, city_name: str = None) -> Dict:
        """
        Fetch current weather for a specific location using Open-Meteo API
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            city_name: Optional city name for reference
            
        Returns:
            Dictionary with current weather data or error
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": True,
                "hourly": "temperature_2m,precipitation,relative_humidity_2m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "IST"
            }
            
            response = requests.get(OpenMeteoService.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if "current_weather" not in data:
                return {"error": "No current weather data available"}
            
            current = data["current_weather"]
            
            return {
                "city": city_name or f"{latitude},{longitude}",
                "latitude": latitude,
                "longitude": longitude,
                "temperature": current.get("temperature", 0),
                "wind_speed": current.get("wind_speed", 0),
                "weather_code": current.get("weather_code", 0),
                "time": current.get("time", ""),
                "precipitation": 0,  # Will be from hourly data
                "humidity": 0,  # Will be from hourly data
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch weather data: {str(e)}"}
        except Exception as e:
            return {"error": f"Error processing weather data: {str(e)}"}

    @staticmethod
    def fetch_all_cities_weather() -> Dict:
        """
        Fetch real-time weather for all predefined Indian cities using PARALLEL requests
        
        Returns:
            Dictionary with all cities' weather data and aggregated stats
        """
        try:
            cities_data = []
            temps = []
            precips = []
            lock = threading.Lock()  # For thread-safe list operations
            
            def fetch_and_process_city(city_name: str, coords: Dict) -> Optional[Dict]:
                """Fetch weather for a single city"""
                try:
                    weather = OpenMeteoService.fetch_location_weather(
                        coords["lat"],
                        coords["lng"],
                        city_name
                    )
                    
                    if "error" in weather:
                        return None
                    
                    # Determine color based on temperature
                    temp = weather.get("temperature", 0)
                    if temp < 0:
                        color = "#0066ff"  # Dark Blue
                    elif temp < 10:
                        color = "#0099ff"  # Light Blue
                    elif temp < 15:
                        color = "#00ccff"  # Cyan
                    elif temp < 20:
                        color = "#00ff99"  # Light Green
                    elif temp < 25:
                        color = "#10b981"  # Green
                    elif temp < 30:
                        color = "#ffff00"  # Yellow
                    elif temp < 35:
                        color = "#f59e0b"  # Orange
                    elif temp < 40:
                        color = "#ff6600"  # Dark Orange
                    else:
                        color = "#ef4444"  # Red
                    
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
                        "source": "open-meteo-realtime",
                        "weather_code": weather.get("weather_code", 0),
                        "time": weather.get("time", "")
                    }
                    
                    # Thread-safe appending
                    with lock:
                        cities_data.append(city_point)
                        temps.append(temp)
                        precips.append(weather.get("precipitation", 0))
                    
                    return city_point
                except Exception as e:
                    print(f"Error fetching weather for {city_name}: {e}")
                    return None
            
            # Use ThreadPoolExecutor for parallel requests (max 10 concurrent)
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(fetch_and_process_city, city_name, coords): city_name
                    for city_name, coords in OpenMeteoService.INDIAN_CITIES.items()
                }
                
                # Wait for all tasks to complete
                completed = 0
                for future in as_completed(futures):
                    try:
                        future.result()
                        completed += 1
                    except Exception as e:
                        print(f"Error in parallel fetch: {e}")
            
            print(f"✅ Fetched weather for {completed} cities in parallel")
            
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
                    "source": "open-meteo-api",
                    "cities_fetched": completed
                },
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"❌ Error in fetch_all_cities_weather: {e}")
            return {
                "error": f"Failed to fetch cities weather data: {str(e)}",
                "regions": [],
                "statistics": {}
            }

    @staticmethod
    def fetch_region_forecast(latitude: float, longitude: float, days: int = 7) -> Dict:
        """
        Fetch weather forecast for a specific region
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days to forecast (default 7)
            
        Returns:
            Dictionary with forecast data
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "IST"
            }
            
            response = requests.get(OpenMeteoService.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if "daily" not in data:
                return {"error": "No forecast data available"}
            
            daily = data["daily"]
            forecast_points = []
            
            for i in range(min(days, len(daily["time"]))):
                forecast_points.append({
                    "date": daily["time"][i],
                    "temp_max": daily["temperature_2m_max"][i],
                    "temp_min": daily["temperature_2m_min"][i],
                    "precipitation": daily["precipitation_sum"][i]
                })
            
            return {
                "latitude": latitude,
                "longitude": longitude,
                "forecast": forecast_points,
                "days": len(forecast_points)
            }
            
        except Exception as e:
            return {"error": f"Failed to fetch forecast data: {str(e)}"}


# Initialize service
open_meteo_service = OpenMeteoService()
