"""
Real-Time Weather Data Service
Generates backup random weather data (Open-Meteo API removed)
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.realtime_weather import RealtimeWeatherData
import random

logger = logging.getLogger(__name__)

# Indian cities with their coordinates
CITIES_COORDINATES = {
    "Delhi": (28.7041, 77.1025),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Jaipur": (26.9124, 75.7873),
    "Ahmedabad": (23.0225, 72.5714),
    "Agartala": (23.8103, 91.2868),
    "Aizawl": (23.1815, 92.7879),
    "Amritsar": (31.6340, 74.8711),
    "Aurangabad": (19.8762, 75.3433),
    "Bhopal": (23.1815, 79.9864),
    "Chandigarh": (30.7333, 76.8277),
    "Coimbatore": (11.0066, 76.9485),
    "Cuttack": (20.4625, 85.8830),
    "Daman": (20.4283, 72.8479),
    "Darjeeling": (27.0360, 88.2667),
    "Durgapur": (23.1899, 87.3107),
    "Guwahati": (26.1445, 91.7362),
    "Gwalior": (26.2389, 78.1770),
    "Hamirpur": (32.1744, 76.5145),
    "Haridwar": (29.9457, 78.1642),
    "Hissar": (29.1724, 75.7339),
    "Indore": (22.7196, 75.8577),
    "Itanagar": (28.8276, 93.6053),
    "Jabalpur": (23.1815, 79.9864),
    "Jamshedpur": (22.8047, 84.8430),
    "Jodhpur": (26.2389, 73.0243),
    "Kanpur": (26.4499, 80.3319),
    "Kottayam": (9.5941, 76.5214),
    "Lucknow": (26.8467, 80.9462),
    "Ludhiana": (30.9010, 75.8573),
    "Madurai": (9.9252, 78.1198),
    "Meerut": (28.9845, 77.7064),
    "Mysore": (12.2958, 76.6394),
    "Nagpur": (21.1458, 79.0882),
    "Nashik": (19.9975, 73.7898),
}


class RealtimeWeatherService:
    """Service for managing real-time weather data - using backup random data"""

    OPEN_METEO_API = "https://api.open-meteo.com/v1/forecast"  # Deprecated
    
    # Realistic weather ranges for Indian cities
    WEATHER_RANGES = {
        "temperature": (15, 42),  # 15-42°C
        "rainfall": (0, 80),      # 0-80mm
        "humidity": (30, 95),     # 30-95%
        "wind_speed": (5, 35)     # 5-35 km/h
    }

    @staticmethod
    def save_weather_data(
        db: Session,
        city: str,
        latitude: float,
        longitude: float,
        temperature: float,
        rainfall: float = 0.0,
        wind_speed: float = 0.0,
        humidity: float = 0.0,
        weather_code: int = 0,
        stability_score: float = 65.0,
        risk_level: str = "low",
        color: str = "#00ff00",
        source: str = "open-meteo-realtime",
        timestamp: Optional[datetime] = None
    ) -> RealtimeWeatherData:
        """
        Save a single weather data point to database
        
        Args:
            db: Database session
            city: City/state name
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            temperature: Temperature in Celsius
            rainfall: Rainfall in mm
            wind_speed: Wind speed in km/h
            humidity: Humidity percentage
            weather_code: Weather code from API
            stability_score: Stability score (0-100)
            risk_level: Risk level (low/medium/high)
            color: Color code for visualization
            source: Data source
            timestamp: Timestamp from API
            
        Returns:
            Saved RealtimeWeatherData object
        """
        try:
            # Create new weather data record
            weather_data = RealtimeWeatherData(
                city=city,
                latitude=latitude,
                longitude=longitude,
                temperature=temperature,
                rainfall=rainfall,
                wind_speed=wind_speed,
                humidity=humidity,
                weather_code=weather_code,
                stability_score=stability_score,
                risk_level=risk_level,
                color=color,
                source=source,
                timestamp=timestamp or datetime.utcnow()
            )
            
            # Save to database
            db.add(weather_data)
            db.commit()
            db.refresh(weather_data)
            
            return weather_data
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save weather data: {str(e)}")

    @staticmethod
    def save_batch_weather_data(
        db: Session,
        weather_records: List[Dict]
    ) -> List[RealtimeWeatherData]:
        """
        Save multiple weather data points in batch
        
        Args:
            db: Database session
            weather_records: List of weather data dictionaries
            
        Returns:
            List of saved RealtimeWeatherData objects
        """
        try:
            saved_records = []
            
            for record in weather_records:
                weather_data = RealtimeWeatherData(
                    city=record.get("state", record.get("city", "Unknown")),
                    latitude=record.get("lat", 0),
                    longitude=record.get("lng", 0),
                    temperature=record.get("temperature", 0),
                    rainfall=record.get("rainfall", 0),
                    wind_speed=record.get("wind_speed", 0),
                    humidity=record.get("humidity", 0),
                    weather_code=record.get("weather_code", 0),
                    stability_score=record.get("stability_score", 65),
                    risk_level=record.get("risk", "low"),
                    color=record.get("color", "#00ff00"),
                    source=record.get("source", "open-meteo-realtime"),
                    timestamp=record.get("time")
                )
                saved_records.append(weather_data)
            
            # Bulk insert
            db.add_all(saved_records)
            db.commit()
            
            # Refresh all records
            for record in saved_records:
                db.refresh(record)
            
            return saved_records
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save batch weather data: {str(e)}")

    @staticmethod
    def get_latest_weather_data(
        db: Session,
        city: Optional[str] = None,
        limit: int = 29
    ) -> List[RealtimeWeatherData]:
        """
        Get latest weather data for all cities or a specific city
        
        Args:
            db: Database session
            city: Optional city filter
            limit: Maximum number of records
            
        Returns:
            List of RealtimeWeatherData objects
        """
        try:
            query = db.query(RealtimeWeatherData)
            
            if city:
                query = query.filter(RealtimeWeatherData.city == city)
            
            # Get latest records per city
            # Order by created_at desc and limit
            records = query.order_by(
                RealtimeWeatherData.city,
                RealtimeWeatherData.created_at.desc()
            ).limit(limit).all()
            
            return records
            
        except Exception as e:
            raise Exception(f"Failed to get weather data: {str(e)}")

    @staticmethod
    def get_weather_data_by_date_range(
        db: Session,
        start_date: datetime,
        end_date: datetime,
        city: Optional[str] = None
    ) -> List[RealtimeWeatherData]:
        """
        Get weather data for a date range
        
        Args:
            db: Database session
            start_date: Start datetime
            end_date: End datetime
            city: Optional city filter
            
        Returns:
            List of RealtimeWeatherData objects
        """
        try:
            query = db.query(RealtimeWeatherData).filter(
                RealtimeWeatherData.created_at >= start_date,
                RealtimeWeatherData.created_at <= end_date
            )
            
            if city:
                query = query.filter(RealtimeWeatherData.city == city)
            
            records = query.order_by(RealtimeWeatherData.created_at.desc()).all()
            
            return records
            
        except Exception as e:
            raise Exception(f"Failed to get weather data by date range: {str(e)}")

    @staticmethod
    def get_weather_stats(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get aggregate weather statistics
        
        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with weather statistics
        """
        try:
            query = db.query(RealtimeWeatherData)
            
            if start_date:
                query = query.filter(RealtimeWeatherData.created_at >= start_date)
            
            if end_date:
                query = query.filter(RealtimeWeatherData.created_at <= end_date)
            
            records = query.all()
            
            if not records:
                return {
                    "total_records": 0,
                    "error": "No weather data available"
                }
            
            temperatures = [r.temperature for r in records]
            rainfalls = [r.rainfall for r in records]
            
            return {
                "total_records": len(records),
                "total_cities": len(set(r.city for r in records)),
                "avg_temperature": round(sum(temperatures) / len(temperatures), 2),
                "min_temperature": round(min(temperatures), 2),
                "max_temperature": round(max(temperatures), 2),
                "avg_rainfall": round(sum(rainfalls) / len(rainfalls), 2),
                "total_rainfall": round(sum(rainfalls), 2),
                "high_risk_count": len([r for r in records if r.risk_level == "high"]),
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to get weather statistics: {str(e)}")

    @staticmethod
    def cleanup_old_data(db: Session, days: int = 30) -> int:
        """
        Delete weather data older than specified days
        
        Args:
            db: Database session
            days: Delete data older than this many days
            
        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted = db.query(RealtimeWeatherData).filter(
                RealtimeWeatherData.created_at < cutoff_date
            ).delete()
            
            db.commit()
            
            return deleted
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to cleanup old data: {str(e)}")

    # ========================== BACKUP RANDOM DATA GENERATION ==========================

    @staticmethod
    def generate_random_weather() -> Dict:
        """
        Generate realistic random weather data (backup for API outages)
        
        Returns:
            Dictionary with random weather data
        """
        ranges = RealtimeWeatherService.WEATHER_RANGES
        
        # Generate realistic data with some correlation
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
            "temperature": temp,
            "rainfall": rainfall,
            "humidity": humidity,
            "wind_speed": wind,
            "weather_code": weather_code,
            "timestamp": datetime.utcnow(),
            "is_real_data": 0,  # Mark as backup data
            "data_quality_notes": "Backup random data (API unavailable)"
        }

    @staticmethod
    def fetch_weather_from_api(city: str, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch weather data - now using backup random data instead of API
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with weather data
        """
        try:
            # Generate backup random data
            logger.info(f"📊 Generating backup weather data for {city}")
            weather_data = RealtimeWeatherService.generate_random_weather()
            logger.info(f"✅ {city}: {weather_data['temperature']}°C (backup data)")
            return weather_data
            
        except Exception as e:
            logger.error(f"❌ Error generating weather data for {city}: {str(e)}")
            return None

    @staticmethod
    def calculate_stability_and_risk(temp: float, rainfall: float) -> Tuple[float, str]:
        """
        Calculate stability score and risk level from weather values
        
        Args:
            temp: Temperature in Celsius
            rainfall: Rainfall in mm
            
        Returns:
            Tuple of (stability_score, risk_level)
        """
        score = 100
        risk = "low"
        
        # Temperature extremes (15-45°C normal for India)
        if temp < 5 or temp > 45:
            score -= 25
            risk = "high"
        elif temp < 10 or temp > 42:
            score -= 15
            risk = "medium"
        elif temp < 15 or temp > 38:
            score -= 5
        
        # Heavy rainfall
        if rainfall > 100:
            score -= 20
            if risk == "low": risk = "medium"
        elif rainfall > 50:
            score -= 10
            if risk == "low": risk = "medium"
        elif rainfall > 20:
            score -= 3
        
        score = max(0, min(100, score))
        
        if risk == "low" and score < 40:
            risk = "medium"
        if score < 25:
            risk = "high"
            
        return score, risk

    @staticmethod
    def get_color_for_risk(risk_level: str) -> str:
        """Get color code based on risk level"""
        colors = {
            "low": "#00ff00",      # Green
            "medium": "#ffff00",   # Yellow
            "high": "#ff0000"      # Red
        }
        return colors.get(risk_level, "#00ff00")

    @staticmethod
    def update_all_cities_from_api(db: Session) -> Dict:
        """
        Fetch and update weather data for all Indian cities from Open-Meteo API
        
        Args:
            db: Database session
            
        Returns:
            Summary dictionary with success/failure counts
        """
        results = {
            "success": 0,
            "failed": 0,
            "updated": 0,
            "created": 0,
            "cities": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"🌍 Starting weather update for {len(CITIES_COORDINATES)} Indian cities...")
        
        # Collect all records before committing (to ensure same timestamp)
        records_to_save = []
        
        for city, (lat, lon) in CITIES_COORDINATES.items():
            try:
                # Fetch real weather data from API
                weather_data = RealtimeWeatherService.fetch_weather_from_api(city, lat, lon)
                
                if weather_data is None:
                    results["failed"] += 1
                    results["cities"][city] = "API fetch failed"
                    logger.warning(f"❌ {city}: API fetch failed")
                    continue
                
                # Calculate stability and risk
                stability, risk = RealtimeWeatherService.calculate_stability_and_risk(
                    weather_data["temperature"],
                    weather_data["rainfall"]
                )
                
                # Get color
                color = RealtimeWeatherService.get_color_for_risk(risk)
                
                # Create a NEW record for historical tracking
                # This keeps historical data for each update cycle
                new_record = RealtimeWeatherData(
                    city=city,
                    latitude=lat,
                    longitude=lon,
                    temperature=weather_data["temperature"],
                    rainfall=weather_data["rainfall"],
                    humidity=weather_data["humidity"],
                    wind_speed=weather_data["wind_speed"],
                    weather_code=weather_data["weather_code"],
                    stability_score=stability,
                    risk_level=risk,
                    color=color,
                    source="open-meteo-api",
                    timestamp=weather_data["timestamp"],
                    is_real_data=weather_data.get("is_real_data", 1),
                    data_quality_notes=weather_data.get("data_quality_notes", "Complete API response")
                )
                records_to_save.append(new_record)
                results["created"] += 1
                logger.info(f"✅ {city}: Prepared ({weather_data['temperature']}°C, {weather_data['rainfall']}mm)")
                
                results["success"] += 1
                results["cities"][city] = {
                    "temperature": weather_data["temperature"],
                    "rainfall": weather_data["rainfall"],
                    "humidity": weather_data["humidity"],
                    "stability": stability,
                    "risk": risk
                }
                
            except Exception as e:
                logger.error(f"❌ {city}: {str(e)}")
                results["failed"] += 1
                results["cities"][city] = f"Error: {str(e)}"
        
        # Commit all records at once (they'll share the same created_at timestamp)
        try:
            if records_to_save:
                db.add_all(records_to_save)
                db.commit()
                logger.info(f"✅ Batch committed: {len(records_to_save)} records saved")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Batch commit failed: {str(e)}")
            results["created"] = 0
        
        logger.info(f"✅ Update complete: {results['created']} created, {results['updated']} updated, {results['failed']} failed")
        return results

    @staticmethod
    def get_latest_by_city(db: Session) -> Dict[str, Dict]:
        """
        Get latest weather data for each city
        
        Args:
            db: Database session
            
        Returns:
            Dictionary mapping city names to latest weather data
        """
        data = {}
        
        for city in CITIES_COORDINATES.keys():
            record = db.query(RealtimeWeatherData)\
                .filter(RealtimeWeatherData.city == city)\
                .order_by(RealtimeWeatherData.timestamp.desc())\
                .first()
            
            if record:
                data[city] = {
                    "city": record.city,
                    "latitude": record.latitude,
                    "longitude": record.longitude,
                    "temperature": record.temperature,
                    "rainfall": record.rainfall,
                    "humidity": record.humidity,
                    "wind_speed": record.wind_speed,
                    "stability_score": record.stability_score,
                    "risk_level": record.risk_level,
                    "color": record.color,
                    "timestamp": record.timestamp.isoformat() if record.timestamp else None
                }
        
        return data

    @staticmethod
    def get_aggregate_stats(db: Session) -> Dict:
        """
        Get aggregate statistics from latest data for all cities
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with aggregated statistics
        """
        latest_records = []
        
        for city in CITIES_COORDINATES.keys():
            record = db.query(RealtimeWeatherData)\
                .filter(RealtimeWeatherData.city == city)\
                .order_by(RealtimeWeatherData.timestamp.desc())\
                .first()
            
            if record:
                latest_records.append(record)
        
        if not latest_records:
            return {
                "avg_temperature": 0,
                "avg_rainfall": 0,
                "avg_stability": 0,
                "total_cities": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        temps = [r.temperature for r in latest_records]
        rains = [r.rainfall for r in latest_records]
        stabilities = [r.stability_score for r in latest_records]
        
        return {
            "avg_temperature": round(sum(temps) / len(temps), 1),
            "avg_rainfall": round(sum(rains) / len(rains), 1),
            "avg_stability": round(sum(stabilities) / len(stabilities), 1),
            "total_cities": len(latest_records),
            "high_risk_cities": sum(1 for r in latest_records if r.risk_level == "high"),
            "medium_risk_cities": sum(1 for r in latest_records if r.risk_level == "medium"),
            "low_risk_cities": sum(1 for r in latest_records if r.risk_level == "low"),
            "hottest_city": max(latest_records, key=lambda r: r.temperature).city if latest_records else None,
            "coolest_city": min(latest_records, key=lambda r: r.temperature).city if latest_records else None,
            "wettest_city": max(latest_records, key=lambda r: r.rainfall).city if latest_records else None,
            "driest_city": min(latest_records, key=lambda r: r.rainfall).city if latest_records else None,
            "timestamp": datetime.utcnow().isoformat()
        }
