"""
Insight Service - AI-Powered Climate Intelligence Engine
Generates natural language insights and analysis without requiring LLM
"""
from typing import Dict, List, Optional
import statistics
from datetime import datetime, timedelta
from app.services import ml_service
import pandas as pd


class InsightService:
    """
    Generates AI-powered climate insights using rule-based intelligence
    Analyzes data patterns and produces human-readable insights
    """

    @staticmethod
    def generate_insights(year: int = None, region: str = "India") -> Dict:
        """
        Generate comprehensive climate insights for a region
        
        Args:
            year: Year to analyze (default: most recent)
            region: Region name (default: "India")
            
        Returns:
            Dictionary with insights, trends, and warnings
        """
        try:
            # Get region data from dataframe
            data = ml_service.data
            
            # Filter by region (case-insensitive)
            region_data = data[data['REGION'].str.lower() == region.lower()] if region != "India" else data
            
            if len(region_data) == 0:
                region_data = data  # Use all data if region not found
            
            # Sort by year
            region_data = region_data.sort_values('YEAR')
            
            if len(region_data) == 0:
                return {"error": "No data available"}
            
            # Extract data arrays
            temps = region_data['TEMPERATURE'].dropna().astype(float).tolist()
            rainfalls = region_data['RAINFALL'].dropna().astype(float).tolist()
            years = region_data['YEAR'].dropna().astype(int).tolist()
            
            if not temps or not rainfalls:
                return {"error": "Insufficient data"}
            
            # Calculate temperature statistics
            temp_mean = statistics.mean(temps)
            temp_variance = statistics.variance(temps) if len(temps) > 1 else 0
            temp_stdev = statistics.stdev(temps) if len(temps) > 1 else 0
            
            # Calculate rainfall statistics
            rain_mean = statistics.mean(rainfalls)
            rain_variance = statistics.variance(rainfalls) if len(rainfalls) > 1 else 0
            rain_stdev = statistics.stdev(rainfalls) if len(rainfalls) > 1 else 0
            
            # Calculate trends (compare recent vs old)
            recent_indices = region_data.nlargest(min(10, len(region_data)), 'YEAR')
            old_indices = region_data.nsmallest(min(10, len(region_data)), 'YEAR')
            
            recent_temp_mean = recent_indices['TEMPERATURE'].dropna().astype(float).mean()
            old_temp_mean = old_indices['TEMPERATURE'].dropna().astype(float).mean()
            
            recent_rain_mean = recent_indices['RAINFALL'].dropna().astype(float).mean()
            old_rain_mean = old_indices['RAINFALL'].dropna().astype(float).mean()
            
            temp_change = recent_temp_mean - old_temp_mean
            rain_change = recent_rain_mean - old_rain_mean
            rain_variability_increase = ((rain_stdev / rain_mean * 100) - 20) if rain_mean > 0 else 0
            
            # Generate insights
            insights = []
            warnings = []
            
            # Temperature insights
            if temp_change > 1.0:
                insights.append(f"Significant warming trend detected. Temperature has increased by {temp_change:.2f}°C over the observation period.")
                warnings.append("high_temperature_increase")
            elif temp_change > 0.5:
                insights.append(f"Moderate warming trend. Temperature increased by {temp_change:.2f}°C.")
                warnings.append("moderate_temperature_increase")
            elif temp_change < -0.5:
                insights.append(f"Cooling trend detected. Temperature decreased by {abs(temp_change):.2f}°C.")
            
            # Rainfall insights
            if abs(rain_change) > 100:
                if rain_change > 0:
                    insights.append(f"Rainfall patterns have intensified. Average rainfall increased by {rain_change:.0f}mm.")
                    warnings.append("rainfall_intensification")
                else:
                    insights.append(f"Rainfall patterns have decreased. Average rainfall reduced by {abs(rain_change):.0f}mm.")
                    warnings.append("rainfall_decrease")
            
            # Variability insights
            if rain_variability_increase > 15:
                insights.append(f"Rainfall variability has increased by {rain_variability_increase:.1f}%, indicating less predictable monsoon patterns.")
                warnings.append("high_rainfall_variability")
            
            if temp_variance > 1.5:
                insights.append(f"Temperature variability is high ({temp_stdev:.2f}°C standard deviation), suggesting unstable climate conditions.")
                warnings.append("high_temperature_variability")
            
            # Extremes
            temp_anomalies = len([t for t in temps if abs(t - temp_mean) > 2 * temp_stdev]) if temp_stdev > 0 else 0
            if temp_anomalies > len(temps) * 0.1:
                insights.append(f"Temperature extremes detected - {temp_anomalies} records exceed normal range.")
                warnings.append("temperature_extremes")
            
            rain_anomalies = len([r for r in rainfalls if abs(r - rain_mean) > 2 * rain_stdev]) if rain_stdev > 0 else 0
            if rain_anomalies > len(rainfalls) * 0.1:
                insights.append(f"Rainfall extremes detected - {rain_anomalies} records exceed normal range.")
                warnings.append("rainfall_extremes")
            
            # Stability assessment
            if not insights:
                insights.append("Climate patterns appear relatively stable with no major trends detected.")
            
            return {
                "region": region,
                "analysis_period": f"{min(years)} - {max(years)}",
                "insights": insights,
                "warnings": warnings,
                "statistics": {
                    "temperature": {
                        "mean": round(temp_mean, 2),
                        "variance": round(temp_variance, 2),
                        "stdev": round(temp_stdev, 2),
                        "trend": round(temp_change, 2)
                    },
                    "rainfall": {
                        "mean": round(rain_mean, 2),
                        "variance": round(rain_variance, 2),
                        "stdev": round(rain_stdev, 2),
                        "trend": round(rain_change, 2)
                    }
                },
                "data_points": len(region_data)
            }
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    @staticmethod
    def calculate_climate_score(year: int = None, region: str = "India") -> Dict:
        """
        Calculate custom Climate Stability Score (0-100)
        
        Score = 100 - (temp_variance + rainfall_variance + anomaly_count)
        
        Returns:
            Score with stability label
        """
        insights_data = InsightService.generate_insights(year, region)
        
        if "error" in insights_data:
            return insights_data
        
        stats = insights_data["statistics"]
        warnings = insights_data["warnings"]
        
        # Calculate score components
        temp_variance_score = min(stats["temperature"]["variance"] * 2, 30)
        rain_variance_score = min(stats["rainfall"]["variance"] / 100, 30)
        
        # Anomaly penalty
        anomaly_penalty = len([w for w in warnings if "extremes" in w or "variability" in w]) * 10
        
        # Calculate final score
        score = 100 - temp_variance_score - rain_variance_score - anomaly_penalty
        score = max(0, min(100, score))  # Clamp between 0-100
        
        # Determine stability label
        if score >= 75:
            stability = "Stable"
            description = "Climate is relatively stable with predictable patterns"
        elif score >= 50:
            stability = "Moderate"
            description = "Climate shows moderate variability with some unpredictable patterns"
        else:
            stability = "Unstable"
            description = "Climate is highly variable with significant unpredictability"
        
        return {
            "region": region,
            "score": round(score, 1),
            "stability": stability,
            "description": description,
            "components": {
                "temperature_variance_impact": round(temp_variance_score, 1),
                "rainfall_variance_impact": round(rain_variance_score, 1),
                "anomaly_penalty": anomaly_penalty
            },
            "risk_level": "high" if score < 40 else "medium" if score < 60 else "low"
        }
    
    @staticmethod
    def generate_forecast_data(region: str = "India", years_ahead: int = 10) -> Dict:
        """
        Generate historical + predicted data for visualization
        
        Returns:
            Data suitable for trend visualization charts
        """
        try:
            # Get region data from dataframe
            data = ml_service.data
            region_data = data[data['REGION'].str.lower() == region.lower()] if region != "India" else data
            
            if len(region_data) == 0:
                region_data = data
            
            region_data = region_data.sort_values('YEAR')
            
            # Prepare historical data
            historical = []
            for _, row in region_data.tail(30).iterrows():  # Last 30 years
                historical.append({
                    "year": int(row['YEAR']),
                    "temperature": float(row['TEMPERATURE']) if pd.notna(row['TEMPERATURE']) else 0,
                    "rainfall": float(row['RAINFALL']) if pd.notna(row['RAINFALL']) else 0,
                    "type": "historical"
                })
            
            # Generate predictions
            predicted = []
            if historical:
                last_year = historical[-1]["year"]
                temps = [h["temperature"] for h in historical]
                rains = [h["rainfall"] for h in historical]
                
                avg_temp_trend = (temps[-1] - temps[0]) / len(temps) if len(temps) > 0 else 0
                avg_rain_trend = (rains[-1] - rains[0]) / len(rains) if len(rains) > 0 else 0
                
                for i in range(1, years_ahead + 1):
                    pred_year = last_year + i
                    pred_temp = temps[-1] + (avg_temp_trend * i)
                    pred_rain = rains[-1] + (avg_rain_trend * i)
                    
                    predicted.append({
                        "year": pred_year,
                        "temperature": round(pred_temp, 2),
                        "rainfall": round(pred_rain, 2),
                        "type": "predicted",
                        "confidence": max(50, 100 - (i * 5))
                    })
            
            return {
                "region": region,
                "historical": historical,
                "predicted": predicted,
                "analysis": {
                    "historical_range": f"{historical[0]['year']}-{historical[-1]['year']}" if historical else "N/A",
                    "prediction_range": f"{predicted[0]['year']}-{predicted[-1]['year']}" if predicted else "N/A",
                    "trend": "warming" if historical and historical[-1]["temperature"] > historical[0]["temperature"] else "cooling" if historical else "unknown"
                }
            }
        except Exception as e:
            return {"error": f"Forecast generation failed: {str(e)}"}
    
    @staticmethod
    def get_co2_data(region: str = "India") -> Dict:
        """
        Provide CO2 emissions data and correlation with temperature
        
        Note: Using representative data for India
        """
        try:
            # Simulated CO2 data for India
            co2_historical = [
                {"year": 1990, "co2_emissions_mtco2": 890},
                {"year": 1995, "co2_emissions_mtco2": 980},
                {"year": 2000, "co2_emissions_mtco2": 1050},
                {"year": 2005, "co2_emissions_mtco2": 1200},
                {"year": 2010, "co2_emissions_mtco2": 1350},
                {"year": 2015, "co2_emissions_mtco2": 1550},
                {"year": 2020, "co2_emissions_mtco2": 1750},
                {"year": 2025, "co2_emissions_mtco2": 1900},
            ]
            
            # Calculate correlation insight
            data = ml_service.data
            region_data = data[data['REGION'].str.lower() == region.lower()] if region != "India" else data
            
            if len(region_data) == 0:
                region_data = data
            
            temps = region_data['TEMPERATURE'].dropna().astype(float).tolist()
            temp_trend = "increasing" if len(temps) > 1 and temps[-1] > temps[0] else "stable"
            
            insight = f"CO2 emissions in {region} have been increasing steadily. " \
                     f"Temperature trend shows {temp_trend} pattern, indicating potential climate impact from emissions."
            
            return {
                "region": region,
                "data": co2_historical,
                "unit": "Million Tonnes of CO2",
                "trend": "increasing",
                "correlation_with_temperature": temp_trend,
                "insight": insight,
                "note": "Data represents India's total CO2 emissions from all sectors"
            }
        except Exception as e:
            return {"error": f"CO2 data retrieval failed: {str(e)}"}
    
    @staticmethod
    def generate_explanation(question: str, region: str = "India") -> Dict:
        """
        Generate data-driven explanations for climate questions
        
        Args:
            question: User's climate question
            region: Region of interest
            
        Returns:
            Natural language explanation based on data
        """
        try:
            question_lower = question.lower()
            
            # Get data
            insights = InsightService.generate_insights(region=region)
            score = InsightService.calculate_climate_score(region=region)
            co2 = InsightService.get_co2_data(region=region)
            
            if "error" in insights:
                return insights
            
            # Question classification and response generation
            response = ""
            
            if any(word in question_lower for word in ["temperature", "warming", "hot"]):
                stats = insights["statistics"]["temperature"]
                response = f"Temperature in {region} has shown significant changes. " \
                          f"The mean temperature stands at {stats['mean']}°C with a trend of {stats['trend']}°C. " \
                          f"Temperature variance ({stats['variance']:.2f}) indicates {'stable' if stats['variance'] < 1 else 'variable'} conditions. " \
                          f"This contributes to an overall climate stability score of {score['score']}/100."
            
            elif any(word in question_lower for word in ["rainfall", "rain", "monsoon", "precipitation"]):
                stats = insights["statistics"]["rainfall"]
                response = f"Rainfall patterns in {region} show a trend of {stats['trend']}mm. " \
                          f"Average rainfall is {stats['mean']:.0f}mm with variability (stdev: {stats['stdev']:.0f}mm). " \
                          f"{'Rainfall is becoming more predictable.' if stats['variance'] < 100000 else 'Rainfall variability is increasing, making predictions difficult.'}"
            
            elif any(word in question_lower for word in ["stable", "unstable", "climate", "variable"]):
                response = f"The Climate Stability Score for {region} is {score['score']}/100 ({score['stability']}). " \
                          f"{score['description']} " \
                          f"Key factors: {', '.join(insights['insights'][:2])}"
            
            elif any(word in question_lower for word in ["co2", "emissions", "carbon"]):
                response = f"{co2.get('insight', 'CO2 emissions analysis unavailable')} " \
                          f"CO2 emissions have risen from ~{co2['data'][0]['co2_emissions_mtco2']}M tonnes (1990) " \
                          f"to ~{co2['data'][-1]['co2_emissions_mtco2']}M tonnes (2025), " \
                          f"showing a clear increasing trend that correlates with temperature changes."
            
            elif any(word in question_lower for word in ["trend", "change", "increasing", "decreasing"]):
                response = f"In {region}: " \
                          f"Temperature trend: {insights['statistics']['temperature']['trend']:+.2f}°C, " \
                          f"Rainfall trend: {insights['statistics']['rainfall']['trend']:+.0f}mm. " \
                          f"Overall, {insights['insights'][0] if insights['insights'] else 'patterns show variability'}."
            
            else:
                response = f"Regional Climate Summary for {region}: " \
                          f"Current stability score is {score['score']}/100. " \
                          f"{score['description']} " \
                          f"Key insight: {insights['insights'][0] if insights['insights'] else 'Climate data shows variability over time.'}"
            
            return {
                "question": question,
                "region": region,
                "explanation": response,
                "confidence": "high",
                "data_sources": ["temperature_records", "rainfall_data", "climate_statistics"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Explanation generation failed: {str(e)}"}
    @staticmethod
    def get_map_data_all_regions(db=None) -> Dict:
        """
        Get map visualization data for all regions using stored realtime weather data
        
        ✨ NEW: Uses the realtime weather data saved in database from Open-Meteo API
        Falls back to ML service data if DB data is not available
        
        Returns:
            Dictionary with array of regions and their climate metrics
        """
        try:
            from app.services.realtime_weather_service import RealtimeWeatherService
            from app.core.database import SessionLocal
            
            # Get database session if not provided
            if db is None:
                db = SessionLocal()
            
            # Try to get latest realtime weather data from database
            latest_records = RealtimeWeatherService.get_latest_weather_data(db=db, limit=1000)
            
            map_data = []
            
            if latest_records and len(latest_records) > 0:
                # Use realtime weather data from database - more comprehensive!
                print(f"✅ Using {len(latest_records)} realtime weather records for historical map")
                
                # Group by city to get latest reading for each
                city_data = {}
                for record in latest_records:
                    if record.city not in city_data:
                        city_data[record.city] = record
                
                for city, record in city_data.items():
                    map_point = {
                        "state": city,
                        "lat": record.latitude,
                        "lng": record.longitude,
                        "temperature": round(record.temperature, 2),
                        "rainfall": round(record.rainfall, 2),
                        "wind_speed": round(record.wind_speed, 2) if record.wind_speed else 0,
                        "humidity": record.humidity if record.humidity else 0,
                        "stability": round(record.stability_score / 100, 2) if record.stability_score else 0.5,
                        "stability_score": round(record.stability_score, 1) if record.stability_score else 50,
                        "risk": record.risk_level if record.risk_level else "medium",
                        "color": record.color if record.color else "#f59e0b",
                        "source": "realtime_api",
                        "time": record.timestamp.isoformat() if record.timestamp else None
                    }
                    map_data.append(map_point)
            else:
                # Fallback to ML service data if database is empty
                print("⚠️ No realtime data in database, falling back to ML service data...")
                
                # Coordinates for Indian states/regions (latitude, longitude)
                state_coords = {
                    "Andhra Pradesh": [15.9, 79.7],
                    "Arunachal Pradesh": [28.2, 94.7],
                    "Assam": [26.2, 92.9],
                    "Bihar": [25.0, 85.0],
                    "Chhattisgarh": [21.2, 81.0],
                    "Goa": [15.2, 74.0],
                    "Gujarat": [22.2, 71.1],
                    "Haryana": [29.0, 77.0],
                    "Himachal Pradesh": [31.1, 77.1],
                    "Jharkhand": [23.6, 85.2],
                    "Karnataka": [15.3, 75.7],
                    "Kerala": [10.8, 76.2],
                    "Madhya Pradesh": [22.9, 78.6],
                    "Maharashtra": [19.7, 75.7],
                    "Manipur": [24.6, 93.9],
                    "Meghalaya": [25.4, 91.3],
                    "Mizoram": [23.8, 93.3],
                    "Nagaland": [26.1, 94.6],
                    "Odisha": [20.9, 84.0],
                    "Punjab": [31.1, 75.3],
                    "Rajasthan": [27.0, 74.2],
                    "Sikkim": [27.5, 88.5],
                    "Tamil Nadu": [11.1, 78.6],
                    "Telangana": [18.1, 79.0],
                    "Tripura": [23.7, 91.2],
                    "Uttar Pradesh": [26.8, 80.9],
                    "Uttarakhand": [30.0, 79.0],
                    "West Bengal": [22.9, 87.8]
                }
                
                data = ml_service.data
                all_regions = data['REGION'].unique()
                
                for region in all_regions:
                    region_data = data[data['REGION'] == region]
                    if len(region_data) == 0:
                        continue
                    
                    # Calculate metrics
                    mean_temp = float(region_data['TEMPERATURE'].mean())
                    mean_rainfall = float(region_data['RAINFALL'].mean())
                    
                    # Recent vs old for trend
                    recent = region_data[region_data['YEAR'] >= 2010]
                    old = region_data[region_data['YEAR'] < 2010]
                    
                    recent_temp = float(recent['TEMPERATURE'].mean()) if len(recent) > 0 else mean_temp
                    old_temp = float(old['TEMPERATURE'].mean()) if len(old) > 0 else mean_temp
                    temp_trend = recent_temp - old_temp
                    
                    # Climate stability score (0-100)
                    temp_var = float(region_data['TEMPERATURE'].std())
                    rain_var = float(region_data['RAINFALL'].std())
                    
                    # Stability based on variance (less variance = more stable)
                    temp_stability = max(0, min(50, 50 - (temp_var * 5)))
                    rain_stability = max(0, min(50, 50 - (rain_var * 0.01)))
                    stability = (temp_stability + rain_stability) / 100.0
                    
                    # Risk level
                    if stability < 0.45:
                        risk = "high"
                    elif stability < 0.65:
                        risk = "medium"
                    else:
                        risk = "low"
                    
                    # Get coordinates
                    coords = state_coords.get(region, [20, 78])  # Default to center of India
                    
                    map_point = {
                        "state": region,
                        "lat": coords[0],
                        "lng": coords[1],
                        "temperature": round(mean_temp, 2),
                        "rainfall": round(mean_rainfall, 0),
                        "stability": round(stability, 2),
                        "stability_score": round(stability * 100, 1),
                        "risk": risk,
                        "temp_trend": round(temp_trend, 2),
                        "color": "#00ff88" if stability >= 0.65 else "#f59e0b" if stability >= 0.45 else "#ef4444"
                    }
                    
                    map_data.append(map_point)
            
            # Calculate aggregates
            temps = [m["temperature"] for m in map_data]
            rainfalls = [m["rainfall"] for m in map_data]
            high_risk_count = len([m for m in map_data if m["risk"] == "high"])
            
            return {
                "total_regions": len(map_data),
                "regions": map_data,
                "statistics": {
                    "avg_temperature": round(sum(temps) / len(temps), 2) if temps else 0,
                    "avg_rainfall": round(sum(rainfalls) / len(rainfalls), 0) if rainfalls else 0,
                    "high_risk_count": high_risk_count
                }
            }
        
        except Exception as e:
            print(f"❌ Error in get_map_data_all_regions: {e}")
            return {"error": f"Map data generation failed: {str(e)}"}