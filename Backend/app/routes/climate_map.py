"""
Climate Map Routes - Interactive map data endpoints for years 2020-2050
Supports switching between Temperature, Rainfall, and Risk visualization modes
"""
from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Dict, Optional
from datetime import datetime, date as date_type
from app.services import ml_service_v2 as ml_service
import logging

router = APIRouter(
    prefix="/api",
    tags=["Climate Map"]
)

logger = logging.getLogger(__name__)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_risk(temp: float, rain: float, latitude: float) -> int:
    """
    Calculate climate risk score based on temperature, rainfall, and latitude.
    
    Uses graduated risk bands appropriate for India's climate range.
    Base risk accounts for tropical location. Temperature and rainfall ranges
    add risk progressively.
    """
    risk = 40  # Base risk for tropical India
    
    # Temperature: Graduated bands (not binary thresholds)
    if temp >= 40:
        risk += min(35, (temp - 40) * 3)
    elif temp >= 35:
        risk += min(25, (temp - 35) * 2)
    elif temp >= 30:
        risk += min(15, (temp - 30) * 1.5)
    elif temp < 10:
        risk += min(15, (10 - temp) * 1.5)
    
    # Rainfall: Graduated bands (not binary thresholds)
    if rain > 150:
        risk += min(25, (rain - 150) * 0.15)
    elif rain > 100:
        risk += min(15, (rain - 100) * 0.3)
    elif rain < 2:
        risk += 25
    elif rain < 5:
        risk += min(15, (5 - rain) * 3)
    
    # Tropical multiplier (India entirely within tropical zone)
    if abs(latitude) < 23.5:
        risk = int(risk * 1.1)
    
    return min(100, max(0, risk))


def get_color_for_value(value: float, mode: str) -> str:
    """
    Get hex color for visualization based on mode and value.
    
    Temperature: Blue (cold) -> Green (mild) -> Yellow (warm) -> Red (hot)
    Rainfall: Light colors (dry) -> Dark blue (heavy rain)
    Risk: Green (low) -> Yellow (medium) -> Red (high)
    """
    if mode == "temp":
        if value < 0:
            return "#0066ff"  # Dark blue: Extremely cold
        elif value < 10:
            return "#0099ff"  # Light blue: Very cold
        elif value < 15:
            return "#00ccff"  # Cyan: Cold
        elif value < 20:
            return "#00ff99"  # Light green: Cool
        elif value < 25:
            return "#00ff00"  # Green: Mild
        elif value < 30:
            return "#ffff00"  # Yellow: Warm
        elif value < 35:
            return "#ffaa00"  # Orange: Hot
        elif value < 40:
            return "#ff6600"  # Dark orange: Very hot
        else:
            return "#ff0000"  # Red: Extremely hot
    
    elif mode == "rain":
        if value < 1:
            return "#ffe6cc"  # Very light: Dry
        elif value < 10:
            return "#d9b3ff"  # Light purple: Light rain
        elif value < 50:
            return "#99ccff"  # Light blue: Moderate rain
        elif value < 100:
            return "#6666ff"  # Medium blue: Heavy rain
        elif value < 150:
            return "#0099ff"  # Darker blue: Very heavy
        else:
            return "#0033cc"  # Dark blue: Extreme rain
    
    else:  # mode == "risk"
        if value < 33:
            return "#00ff00"  # Green: Low risk
        elif value < 66:
            return "#ffff00"  # Yellow: Medium risk
        else:
            return "#ff0000"  # Red: High risk


def get_radius_for_value(value: float, mode: str) -> float:
    """Get marker radius based on value and mode."""
    # Make radius proportional to value but reasonable for map markers
    if mode == "temp":
        return max(8, min(25, 8 + (value / 5)))  # 8-25 based on temperature
    elif mode == "rain":
        return max(8, min(25, 8 + (value / 10)))  # 8-25 based on rainfall
    else:  # risk
        return max(8, min(25, 8 + (value / 5)))  # 8-25 based on risk


# ============================================================
# API ENDPOINTS
# ============================================================

@router.get("/climate-map/data", tags=["Climate Map"])
def get_climate_map_data(
    year: int = Query(2026, ge=2020, le=2050, description="Year for prediction (2020-2050)"),
    mode: str = Query("temp", regex="^(temp|rain|risk)$", description="Visualization mode: temp, rain, or risk"),
    month: int = Query(6, ge=1, le=12, description="Month for prediction (1-12)"),
    day: int = Query(15, ge=1, le=28, description="Day for prediction (1-28)")
):
    """
    Get climate data for all Indian cities for interactive map visualization.
    
    Supports switching between Temperature, Rainfall, and Risk visualization modes.
    
    Parameters:
    - year: Target year for prediction (2020-2050)
    - mode: Visualization mode (temp, rain, risk)
    - month: Month (1-12), default June
    - day: Day (1-28), default 15
    
    Returns:
    - List of cities with their climate metrics and visualization properties
    
    Example:
        GET /api/climate-map/data?year=2028&mode=temp&month=6&day=15
        GET /api/climate-map/data?year=2035&mode=rain&month=8&day=1
        GET /api/climate-map/data?year=2050&mode=risk&month=12&day=20
    """
    try:
        logger.info(f"🗺️ Fetching climate map data: year={year}, mode={mode}, month={month}, day={day}")
        
        # Get available cities
        cities = ml_service.get_available_cities()
        if not cities:
            raise HTTPException(status_code=404, detail="No cities available in dataset")
        
        result = []
        
        # Process each city
        for city in cities:
            try:
                # Get city coordinates
                lat, lng = ml_service.get_city_coordinates(city)
                
                # Predict temperature and rainfall for given date
                temp = ml_service.predict_statistical_temperature(
                    year=year,
                    month=month,
                    day=day,
                    city=city,
                    latitude=lat,
                    longitude=lng
                )
                
                rain = ml_service.predict_statistical_rainfall(
                    year=year,
                    month=month,
                    day=day,
                    city=city,
                    latitude=lat,
                    longitude=lng
                )
                
                # Ensure non-negative rainfall
                rain = max(0.0, rain)
                
                # Calculate risk score
                risk = calculate_risk(temp, rain, lat)
                
                # Determine value based on mode
                if mode == "temp":
                    display_value = temp
                elif mode == "rain":
                    display_value = rain
                else:  # risk
                    display_value = risk
                
                # Get visualization properties
                color = get_color_for_value(display_value, mode)
                radius = get_radius_for_value(display_value, mode)
                
                # Add to result
                result.append({
                    "city": city,
                    "lat": lat,
                    "lng": lng,
                    "temperature": round(temp, 2),
                    "rainfall": round(rain, 2),
                    "risk": risk,
                    "value": round(display_value, 2),  # Current display value based on mode
                    "color": color,
                    "radius": radius,
                    "mode": mode
                })
                
            except Exception as city_err:
                logger.warning(f"⚠️  Error processing city {city}: {str(city_err)}")
                # Skip this city but continue with others
                continue
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate predictions for any cities"
            )
        
        logger.info(f"✅ Generated map data for {len(result)} cities")
        
        return {
            "success": True,
            "year": year,
            "month": month,
            "day": day,
            "mode": mode,
            "timestamp": datetime.utcnow().isoformat(),
            "cities_count": len(result),
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating climate map data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate map data: {str(e)}"
        )


@router.get("/climate-map/year-range", tags=["Climate Map"])
def get_map_year_range():
    """
    Get supported year range for map predictions.
    
    Returns:
    - min_year: Minimum year for predictions (2020)
    - max_year: Maximum year for predictions (2050)
    
    Example:
        GET /api/climate-map/year-range
    """
    return {
        "min_year": 2020,
        "max_year": 2050,
        "default_year": 2026,
        "description": "Climate map supports predictions from 2020 to 2050"
    }


@router.get("/climate-map/modes", tags=["Climate Map"])
def get_map_modes():
    """
    Get available visualization modes for climate map.
    
    Returns:
    - List of supported modes with descriptions
    
    Example:
        GET /api/climate-map/modes
    """
    return {
        "modes": [
            {
                "id": "temp",
                "name": "Temperature",
                "description": "Temperature visualization with color gradient from blue (cold) to red (hot)",
                "emoji": "🌡️",
                "unit": "°C"
            },
            {
                "id": "rain",
                "name": "Rainfall",
                "description": "Rainfall visualization with color gradient from yellow (dry) to dark blue (heavy rain)",
                "emoji": "🌧️",
                "unit": "mm"
            },
            {
                "id": "risk",
                "name": "Climate Risk",
                "description": "Climate risk score visualization with color gradient from green (low) to red (high)",
                "emoji": "⚠️",
                "unit": "Score (0-100)"
            }
        ]
    }


@router.get("/climate-map/city-history/{city}", tags=["Climate Map"])
def get_city_history(
    city: str,
    month: int = Query(6, ge=1, le=12, description="Month for historical data (1-12)"),
    day: int = Query(15, ge=1, le=28, description="Day for historical data (1-28)"),
    mode: str = Query("temp", regex="^(temp|rain|risk)$", description="Data mode: temp, rain, or risk"),
    years_back: int = Query(10, ge=1, le=30, description="How many years back to fetch (1-30)"),
    years_ahead: int = Query(5, ge=0, le=30, description="How many years ahead to forecast (0-30)")
):
    """
    Get historical and forecast data for a SINGLE city (optimized for performance).
    
    ⚡ PERFORMANCE OPTIMIZED:
    - Fetches data for only the requested city
    - No need to filter through all cities
    - Single database query instead of multiple map queries
    - Perfect for trend graphs and detailed analysis
    
    Parameters:
    - city: City name (case-insensitive)
    - month: Month (1-12), default June
    - day: Day (1-28), default 15
    - mode: Data type (temp, rain, risk)
    - years_back: Years of historical data to fetch (default 10)
    - years_ahead: Years of forecast data to fetch (default 5)
    
    Returns:
    - Historical data for past years
    - Forecast data for future years
    - Each record includes temperature, rainfall, and risk
    
    Example:
        GET /api/climate-map/city-history/Delhi?month=6&day=15&mode=temp&years_back=10&years_ahead=5
        GET /api/climate-map/city-history/Mumbai?month=7&mode=rain
    """
    try:
        logger.info(f"📍 Fetching single-city history: city={city}, month={month}, day={day}, mode={mode}, back={years_back}, ahead={years_ahead}")
        
        # Get city coordinates
        lat, lng = ml_service.get_city_coordinates(city)
        current_year = datetime.now().year
        
        # Build historical and forecast data
        history = []
        forecast = []
        
        # Historical data (past years)
        start_year = max(2020, current_year - years_back)
        for year in range(start_year, current_year + 1):
            try:
                temp = ml_service.predict_statistical_temperature(
                    year=year, month=month, day=day,
                    city=city, latitude=lat, longitude=lng
                )
                rain = ml_service.predict_statistical_rainfall(
                    year=year, month=month, day=day,
                    city=city, latitude=lat, longitude=lng
                )
                rain = max(0.0, rain)
                risk = calculate_risk(temp, rain, lat)
                
                # Determine value based on mode
                if mode == "temp":
                    value = temp
                elif mode == "rain":
                    value = rain
                else:  # risk
                    value = risk
                
                history.append({
                    "year": year,
                    "temperature": round(temp, 2),
                    "rainfall": round(rain, 2),
                    "risk": risk,
                    "value": round(value, 2),
                    "is_historical": True
                })
            except Exception as e:
                logger.warning(f"⚠️  Error fetching data for {city} year {year}: {str(e)}")
                continue
        
        # Forecast data (future years)
        for year in range(current_year + 1, current_year + 1 + years_ahead):
            try:
                temp = ml_service.predict_statistical_temperature(
                    year=year, month=month, day=day,
                    city=city, latitude=lat, longitude=lng
                )
                rain = ml_service.predict_statistical_rainfall(
                    year=year, month=month, day=day,
                    city=city, latitude=lat, longitude=lng
                )
                rain = max(0.0, rain)
                risk = calculate_risk(temp, rain, lat)
                
                # Determine value based on mode
                if mode == "temp":
                    value = temp
                elif mode == "rain":
                    value = rain
                else:  # risk
                    value = risk
                
                forecast.append({
                    "year": year,
                    "temperature": round(temp, 2),
                    "rainfall": round(rain, 2),
                    "risk": risk,
                    "value": round(value, 2),
                    "is_historical": False
                })
            except Exception as e:
                logger.warning(f"⚠️  Error forecasting data for {city} year {year}: {str(e)}")
                continue
        
        # Combine all data
        all_data = history + forecast
        
        if not all_data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for city: {city}"
            )
        
        logger.info(f"✅ Generated {len(history)} historical and {len(forecast)} forecast records for {city}")
        
        return {
            "success": True,
            "city": city,
            "latitude": lat,
            "longitude": lng,
            "month": month,
            "day": day,
            "mode": mode,
            "timestamp": datetime.utcnow().isoformat(),
            "historical_records": len(history),
            "forecast_records": len(forecast),
            "data": all_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching city history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch city history: {str(e)}"
        )
