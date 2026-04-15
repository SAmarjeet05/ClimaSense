"""
Real-Time Weather Data Model - Store all real-time weather API data
"""
from sqlalchemy import Column, Integer, Float, DateTime, String, Text
from sqlalchemy.sql import func
from app.core.database import Base


class RealtimeWeatherData(Base):
    """
    Real-Time Weather Data database model
    
    Stores all real-time weather data fetched from Open-Meteo API.
    
    Fields:
    - id: Unique record ID
    - city: City/State name
    - latitude: Location latitude
    - longitude: Location longitude
    - temperature: Current temperature (°C)
    - rainfall: Current rainfall/precipitation (mm)
    - wind_speed: Wind speed (km/h)
    - humidity: Relative humidity (%)
    - weather_code: Weather code (OME standard)
    - stability_score: Calculated stability (0-100)
    - risk_level: Risk level (low/medium/high)
    - color: Color code for visualization
    - source: Data source identifier
    - timestamp: When data was recorded
    - created_at: When record was saved to DB
    """
    __tablename__ = "realtime_weather_data"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(255), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False, default=0.0)
    wind_speed = Column(Float, nullable=False, default=0.0)
    humidity = Column(Float, nullable=False, default=0.0)
    weather_code = Column(Integer, nullable=False, default=0)
    stability_score = Column(Float, nullable=False, default=65.0)
    risk_level = Column(String(50), nullable=False, default="low")
    color = Column(String(50), nullable=False, default="#00ff00")
    source = Column(String(100), nullable=False, default="open-meteo-realtime")
    
    # Data quality indicator
    is_real_data = Column(Integer, nullable=False, default=1)  # 1=real API data, 0=fallback/demo data
    data_quality_notes = Column(String(255), nullable=True)  # Notes if data is incomplete or fallback
    
    # Timestamp from API
    timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # When this record was saved to DB
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<RealtimeWeatherData(id={self.id}, city={self.city}, temp={self.temperature}°C, rain={self.rainfall}mm)>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "city": self.city,
            "state": self.city,  # Alias for compatibility
            "lat": self.latitude,
            "lng": self.longitude,
            "temperature": self.temperature,
            "rainfall": self.rainfall,
            "wind_speed": self.wind_speed,
            "humidity": self.humidity,
            "weather_code": self.weather_code,
            "stability_score": self.stability_score,
            "risk": self.risk_level,
            "color": self.color,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
