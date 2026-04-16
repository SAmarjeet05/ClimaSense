"""
AI Assistant Service
Orchestrates intent detection, API calls, and LLM-powered responses
"""
import logging
import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AssistantService:
    """Main service for AI assistant operations"""
    
    # Sample climate risk data for Indian cities
    SAMPLE_RISK_DATA = {
        "Delhi": {"risk_level": 9, "factors": ["Extreme heat", "Air pollution", "Water scarcity"]},
        "Mumbai": {"risk_level": 8, "factors": ["Monsoon floods", "Extreme heat", "Cyclones"]},
        "Kolkata": {"risk_level": 7, "factors": ["Cyclone impact", "Humidity", "Flooding"]},
        "Chennai": {"risk_level": 8, "factors": ["Cyclones", "Extreme heat", "Water stress"]},
        "Bangalore": {"risk_level": 3, "factors": ["Moderate climate", "Water shortage"]},
        "Hyderabad": {"risk_level": 5, "factors": ["Heat waves", "Drought"]},
        "Pune": {"risk_level": 4, "factors": ["Occasional drought", "Moderate heat"]},
        "Jaipur": {"risk_level": 6, "factors": ["Extreme heat", "Low rainfall", "Water scarcity"]},
        "Ahmedabad": {"risk_level": 7, "factors": ["Extreme heat", "Water scarcity"]},
        "Lucknow": {"risk_level": 6, "factors": ["Air pollution", "Extreme heat in summer"]},
        "Kanpur": {"risk_level": 9, "factors": ["Severe air pollution", "Extreme heat", "Industrial emissions"]},
        "Shimla": {"risk_level": 2, "factors": ["Mild climate", "Occasional landslides"]},
        "Darjeeling": {"risk_level": 2, "factors": ["Temperate climate", "Low risk"]},
        "Guwahati": {"risk_level": 4, "factors": ["Monsoon", "Occasional flooding"]},
        "Chandigarh": {"risk_level": 5, "factors": ["Extreme heat", "Dust storms"]}
    }
    
    # City characteristics for insights
    CITY_CHARACTERISTICS = {
        "Delhi": {"characteristic": "Northern plains", "temp_influence": "Extreme continental", "rain_influence": "Low monsoon impact"},
        "Mumbai": {"characteristic": "Coastal metro", "temp_influence": "Moderated by Arabian Sea", "rain_influence": "High monsoon influence"},
        "Bangalore": {"characteristic": "High elevation", "temp_influence": "Cooler due to 900m elevation", "rain_influence": "Moderate southwestern monsoon"},
        "Kolkata": {"characteristic": "Eastern plains", "temp_influence": "Humid subtropical", "rain_influence": "Very high monsoon impact"},
        "Chennai": {"characteristic": "Southern coastal", "temp_influence": "Tropical, moderated by sea", "rain_influence": "High pre-monsoon & NE monsoon"},
        "Hyderabad": {"characteristic": "Deccan plateau", "temp_influence": "Warm and dry", "rain_influence": "Moderate monsoon"},
        "Pune": {"characteristic": "Western plateau", "temp_influence": "Cooler than plains", "rain_influence": "Moderate Western Ghats impact"},
        "Jaipur": {"characteristic": "Desert region", "temp_influence": "Extreme heat", "rain_influence": "Very low rainfall"},
        "Ahmedabad": {"characteristic": "Semi-arid plains", "temp_influence": "Hot and dry", "rain_influence": "Low rainfall"},
        "Lucknow": {"characteristic": "Northern plains", "temp_influence": "Warm summers", "rain_influence": "Moderate monsoon"},
    }
    
    def __init__(self):
        # Use environment variable for backend URL, default to production
        import os
        self.backend_url = os.getenv("BACKEND_URL", "https://climasense-production.up.railway.app")
        # Fallback to localhost only in development
        if os.getenv("ENVIRONMENT") == "development":
            self.backend_url = "http://127.0.0.1:8000"
        
        self.ollama_url = "http://localhost:11434"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        logger.info(f"🔧 AssistantService initialized with backend_url: {self.backend_url}")
    
    async def query_assistant(self, query: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process user query and generate response
        
        Args:
            query: User's natural language query
            user_id: Optional user ID for logging
            
        Returns:
            {
                "intent": "compare|risk|...",
                "answer": "LLM-generated answer",
                "data": {...},
                "suggested_action": "Navigate to map|Show forecast|...",
                "action_url": "/map" | "/forecast" | ...
            }
        """
        from app.services.intent_detector import IntentDetector
        
        try:
            # Check for multi-query patterns (split by ? or " and ")
            import re
            query_parts = re.split(r'\?|\\band\\b', query)
            query_parts = [q.strip() for q in query_parts if q.strip()]
            
            # If multiple queries detected, handle each separately
            if len(query_parts) > 1:
                logger.info(f"Multi-query detected: {len(query_parts)} questions")
                combined_answers = []
                all_data = {}
                primary_intent = None
                
                for idx, part in enumerate(query_parts[:3]):  # Limit to 3 queries
                    parsed = IntentDetector.parse_query(part)
                    intent = parsed["intent"]
                    cities = parsed["cities"]
                    parameters = parsed["parameters"]
                    
                    # Get data
                    data = await self._fetch_data_for_intent(intent, cities, parameters)
                    
                    # Generate answer
                    answer = await self._generate_llm_response(intent, part, data, cities)
                    combined_answers.append(f"**Query {idx + 1}:** {answer}")
                    
                    all_data[f"query_{idx + 1}"] = data
                    
                    if idx == 0:
                        primary_intent = intent
                
                # Combine all answers
                combined_response = "\\n\\n".join(combined_answers)
                
                response = {
                    "status": "success",
                    "intent": f"multi-{primary_intent}",
                    "query": query,
                    "answer": combined_response,
                    "data": all_data,
                    "suggested_action": "View all results",
                    "action_url": "/dashboard",
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Multi-query response generated")
                return response
            
            # Single query - process normally
            parsed = IntentDetector.parse_query(query)
            intent = parsed["intent"]
            cities = parsed["cities"]
            parameters = parsed["parameters"]
            
            logger.info(f"🔍 Processing single query")
            logger.info(f"   ├─ Intent: {intent}")
            logger.info(f"   ├─ Cities: {cities}")
            logger.info(f"   └─ Parameters: {parameters}")
            
            # Handle MAP_ACTION separately - return navigation instruction instead of data
            if intent == "map_action":
                from app.services.intent_detector import IntentDetector as ID
                map_mode = ID.extract_map_mode(query)
                
                return {
                    "status": "success",
                    "intent": "map_action",
                    "query": query,
                    "action": "navigate_map",
                    "map_mode": map_mode,
                    "answer": f"Showing {map_mode} distribution on map",
                    "message": f"Showing {map_mode} distribution on map",
                    "suggested_action": f"View {map_mode} map",
                    "action_url": f"/map?mode={map_mode}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Handle COMPARE intent separately - navigate to comparison page with cities pre-selected
            if intent == "compare" and len(cities) >= 2:
                return {
                    "status": "success",
                    "intent": "compare_action",
                    "query": query,
                    "action": "navigate_compare",
                    "cities": cities[:2],  # Pass first 2 cities for comparison
                    "answer": f"Comparing {cities[0]} and {cities[1]}...",
                    "message": f"Comparing {cities[0]} and {cities[1]}...",
                    "suggested_action": f"Compare {cities[0]} vs {cities[1]}",
                    "action_url": f"/insights-comparison?city1={cities[0]}&city2={cities[1]}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Handle SCENARIO intent separately - navigate to climate map with scenario selected
            if intent == "scenario":
                # Extract temperature change from parameters
                temp_change = parameters.get("temperature_change", 2)
                
                # Map temperature change to scenario mode
                scenario_mode = "+2c"  # Default to +2°C
                if temp_change == 3:
                    scenario_mode = "+3c"  # If +3°C detected
                elif temp_change == 1:
                    scenario_mode = "+1c"  # If +1°C detected
                # For negative or other values, default to +2c or not supported yet
                elif temp_change < 0:
                    scenario_mode = "unknown"  # Cooling scenarios not yet mapped to modes
                
                scenario_label = f"+{temp_change}°C" if temp_change > 0 else f"{temp_change}°C"
                
                answer = f"Showing climate scenario: {scenario_label} temperature increase. This will display how India's climate regions would be affected if global temperatures rise by {temp_change} degrees Celsius."
                
                return {
                    "status": "success",
                    "intent": "scenario_action",
                    "query": query,
                    "action": "navigate_scenario",
                    "scenario_mode": scenario_mode,
                    "temperature_change": temp_change,
                    "answer": answer,
                    "message": answer,
                    "suggested_action": f"View {scenario_label} scenario",
                    "action_url": f"/map?scenario={scenario_mode}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get data based on intent
            logger.info(f"📥 Fetching data for intent: {intent}")
            data = await self._fetch_data_for_intent(intent, cities, parameters)
            logger.info(f"📤 Data fetched: type={data.get('type')}, has_raw_data={bool(data.get('data'))}")
            
            if data.get("error"):
                logger.error(f"❌ Error fetching data: {data.get('error')}")
            
            # Generate LLM response
            logger.info(f"🧠 Generating LLM response for intent: {intent}")
            answer = await self._generate_llm_response(intent, query, data, cities)
            logger.info(f"✅ LLM response generated ({len(answer)} chars)")
            
            # Suggest next action
            suggested_action, action_url = self._suggest_next_action(intent)
            
            response = {
                "status": "success",
                "intent": intent,
                "query": query,
                "answer": answer,
                "data": data,
                "suggested_action": suggested_action,
                "action_url": action_url,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Response generated for intent: {intent}")
            return response
            
        except Exception as e:
            logger.error(f"Error in query_assistant: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "answer": "I encountered an error processing your query. Please try again.",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _fetch_data_for_intent(self, intent: str, cities: List[str], parameters: Dict) -> Dict:
        """Fetch relevant data based on intent"""
        
        if intent == "map_action":
            # Map actions return navigation data, not analysis data
            from app.services.intent_detector import IntentDetector as ID
            map_mode = ID.extract_map_mode("")
            return {"type": "map", "mode": map_mode}
        elif intent == "scenario":
            # Scenario mode returns visualization data for climate map
            temp_change = parameters.get("temperature_change", 2)
            return {
                "type": "scenario",
                "temperature_change": temp_change,
                "message": f"Displaying {temp_change}°C warming scenario on climate map"
            }
        elif intent == "compare":
            return await self._get_comparison_data(cities, parameters)
        elif intent == "weather":
            return await self._get_weather_data(cities, parameters)
        elif intent == "risk":
            return await self._get_risk_data(cities, parameters)
        elif intent == "forecast":
            return await self._get_forecast_data(cities, parameters)
        elif intent == "trend":
            return await self._get_trend_data(cities, parameters)
        elif intent == "simulation":
            return await self._get_simulation_data(cities, parameters)
        elif intent == "list":
            return await self._get_cities_list()
        else:
            return {"type": "general_info"}
    
    async def _get_comparison_data(self, cities: List[str], parameters: Dict) -> Dict:
        """Fetch city comparison data"""
        try:
            if len(cities) >= 2:
                city1, city2 = cities[0], cities[1]
                metric = parameters.get("metric", "temperature")
                year = parameters.get("year", 2026)
                
                url = f"{self.backend_url}/api/compare-cities?city1={city1}&city2={city2}&mode={metric}&year={year}"
                response = await self.client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "type": "comparison",
                        "cities": [city1, city2],
                        "metric": metric,
                        "data": data
                    }
            
            return {"type": "comparison", "data": None}
        except Exception as e:
            logger.error(f"Error fetching comparison data: {str(e)}")
            return {"type": "comparison", "error": str(e)}
    
    async def _get_weather_data(self, cities: List[str], parameters: Dict) -> Dict:
        """Fetch current weather data for cities"""
        try:
            year = parameters.get("year", 2026)
            weather_data = {}
            
            # Fetch data for each city
            for city in cities[:5]:  # Limit to first 5 cities
                url = f"{self.backend_url}/api/climate-map/data?year={year}&mode=temp"
                response = await self.client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    # Try to filter data for this specific city
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if city.lower() in key.lower():
                                weather_data[city] = value
                                break
                    if city not in weather_data:
                        weather_data[city] = data
            
            return {
                "type": "weather",
                "cities": cities,
                "year": year,
                "data": weather_data
            }
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return {"type": "weather", "error": str(e)}
    
    async def _get_risk_data(self, cities: List[str], parameters: Dict) -> Dict:
        """Fetch risk/anomaly data"""
        try:
            year = parameters.get("year", 2026)
            region = cities[0] if cities else "India"
            
            # Use correct endpoint: /api/anomalies instead of /api/dashboard/anomalies-data
            url = f"{self.backend_url}/api/anomalies?region={region}"
            
            # Try to fetch from API
            api_data = None
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    api_data = response.json()
            except:
                pass
            
            # Use sample data as fallback or if API returns empty
            anomalies = []
            
            if api_data and isinstance(api_data, dict) and api_data.get("anomalies"):
                # Use API data if available
                anomalies = api_data.get("anomalies", [])
            else:
                # Generate anomalies from sample data
                for city, risk_info in self.SAMPLE_RISK_DATA.items():
                    anomalies.append({
                        "city": city,
                        "value": risk_info["risk_level"],
                        "factors": risk_info["factors"],
                        "description": f"Risk Level: {risk_info['risk_level']}/10"
                    })
            
            # Sort by risk level (value)
            anomalies_sorted = sorted(anomalies, key=lambda x: x.get("value", 0), reverse=True)
            
            # Filter for specific cities if mentioned
            if cities:
                filtered = [a for a in anomalies_sorted if a.get("city") in cities]
                if filtered:
                    anomalies_sorted = filtered
            
            # Get top cities
            top_cities = list(dict.fromkeys([a.get("city") for a in anomalies_sorted[:10]]))[:5]
            
            data = {
                "anomalies": anomalies_sorted,
                "year": year,
                "total_cities": len(set([a.get("city") for a in anomalies])),
                "high_risk_cities": [a for a in anomalies_sorted if a.get("value", 0) >= 7],
                "low_risk_cities": [a for a in anomalies_sorted if a.get("value", 0) <= 3]
            }
            
            return {
                "type": "risk",
                "cities": cities if cities else top_cities,
                "year": year,
                "data": data
            }
        except Exception as e:
            logger.error(f"Error fetching risk data: {str(e)}")
            return {"type": "risk", "error": str(e)}
    
    async def _get_forecast_data(self, cities: List[str], parameters: Dict) -> Dict:
        """Fetch/generate forecast data with actual predictions"""
        try:
            # Extract parameters safely
            from datetime import datetime
            month = parameters.get("month", datetime.now().month)
            years_ahead = parameters.get("years_ahead", 5)
            year = parameters.get("year", 2026)
            
            logger.info(f"📊 Fetching forecast for cities: {cities}, years_ahead: {years_ahead}")
            
            # Sample forecast data generator
            forecast_data = {}
            
            for city in cities[:3]:  # Limit to first 3 cities
                # Try to call forecast API with correct parameters
                try:
                    url = f"{self.backend_url}/api/forecast?region={city}&month={month}&years_ahead={years_ahead}"
                    logger.info(f"🌐 Calling: {url}")
                    response = await self.client.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        api_data = response.json()
                        logger.info(f"✅ Got forecast API response for {city}")
                        forecast_data[city] = api_data
                    else:
                        logger.warning(f"⚠️ Forecast API returned {response.status_code} for {city}, using fallback")
                        # Generate forecast from sample data
                        forecast_data[city] = self._generate_forecast(city, year, "temperature")
                except Exception as api_error:
                    logger.warning(f"⚠️ API call failed for {city}: {str(api_error)}, using fallback")
                    # Fallback: generate forecast
                    forecast_data[city] = self._generate_forecast(city, year, "temperature")
            
            if not forecast_data:
                logger.error(f"❌ No forecast data generated for cities: {cities}")
                raise Exception(f"Failed to generate forecast data for any city")
            
            logger.info(f"✅ Forecast data prepared for {len(forecast_data)} cities")
            
            return {
                "type": "forecast",
                "cities": cities,
                "month": month,
                "years_ahead": years_ahead,
                "year": year,
                "data": forecast_data
            }
        except Exception as e:
            logger.error(f"❌ Error fetching forecast data: {str(e)}")
            return {"type": "forecast", "error": str(e), "data": {}}
    
    def _generate_forecast(self, city: str, year: int, metric: str = "temperature") -> Dict:
        """Generate realistic forecast predictions for a city"""
        # Base current values (2026)
        current_year = 2026
        years_ahead = year - current_year
        
        # Sample base temperatures (average for 2026)
        base_temps = {
            "Delhi": 25.2,
            "Mumbai": 27.5,
            "Bangalore": 23.1,
            "Kolkata": 26.8,
            "Chennai": 28.4,
            "Hyderabad": 26.2,
            "Pune": 22.5,
            "Jaipur": 25.8,
            "Ahmedabad": 27.1,
            "Lucknow": 25.5
        }
        
        # Sample base rainfall (mm/year)
        base_rainfall = {
            "Delhi": 714,
            "Mumbai": 2248,
            "Bangalore": 980,
            "Kolkata": 1582,
            "Chennai": 1401,
            "Hyderabad": 813,
            "Pune": 728,
            "Jaipur": 625,
            "Ahmedabad": 632,
            "Lucknow": 1008
        }
        
        # ALWAYS return both temperature AND rainfall
        base_temp = base_temps.get(city, 25)
        base_rain = base_rainfall.get(city, 800)
        
        # Predict temperature: ~0.1°C increase per year
        predicted_temp = base_temp + (years_ahead * 0.1)
        
        # Predict rainfall: ~2% change per year
        predicted_rain = base_rain * (1 + (years_ahead * 0.02))
        
        # Get city characteristics for insights
        characteristics = self.CITY_CHARACTERISTICS.get(city, {
            "characteristic": "Indian city",
            "temp_influence": "Variable climate",
            "rain_influence": "Monsoon dependent"
        })
        
        return {
            "city": city,
            "year": year,
            "temperature": {
                "value": round(predicted_temp, 1),
                "unit": "°C",
                "change": round(years_ahead * 0.1, 1),
                "base": base_temp
            },
            "rainfall": {
                "value": round(predicted_rain, 1),
                "unit": "mm",
                "change": round(base_rain * (years_ahead * 0.02), 1),
                "base": base_rain
            },
            "characteristics": characteristics
        }
    
    async def _get_simulation_data(self, cities: List[str], parameters: Dict) -> Dict:
        """Generate simulation results for what-if scenarios"""
        try:
            if not cities:
                cities = ["Delhi"]
            
            city = cities[0]  # Use first city
            temp_change = parameters.get("temperature_change", 0)
            rain_change = parameters.get("rainfall_change", 0)
            
            # Get base data for current year
            base_temp = 25.0  # Current avg temp
            base_rain = 800.0  # Current avg rain
            
            # Sample base temperatures
            base_temps = {
                "Delhi": 25.2, "Mumbai": 27.5, "Bangalore": 23.1, "Kolkata": 26.8,
                "Chennai": 28.4, "Hyderabad": 26.2, "Pune": 22.5, "Jaipur": 25.8,
                "Ahmedabad": 27.1, "Lucknow": 25.5
            }
            
            # Sample base rainfall
            base_rainfall = {
                "Delhi": 714, "Mumbai": 2248, "Bangalore": 980, "Kolkata": 1582,
                "Chennai": 1401, "Hyderabad": 813, "Pune": 728, "Jaipur": 625,
                "Ahmedabad": 632, "Lucknow": 1008
            }
            
            base_temp = base_temps.get(city, 25.0)
            base_rain = base_rainfall.get(city, 800.0)
            
            # Calculate new values
            new_temp = base_temp + temp_change
            new_rain = base_rain * (1 + rain_change / 100) if rain_change != 0 else base_rain
            
            # Calculate risk impact
            risk_change = self._calculate_simulation_risk(city, temp_change, rain_change, base_temp, base_rain)
            
            # Get city characteristics
            characteristics = self.CITY_CHARACTERISTICS.get(city, {
                "characteristic": "Indian city",
                "temp_influence": "Variable climate",
                "rain_influence": "Monsoon dependent"
            })
            
            simulation_result = {
                "city": city,
                "baseline": {
                    "temperature": round(base_temp, 1),
                    "rainfall": round(base_rain, 1)
                },
                "scenario": {
                    "temperature_change": temp_change,
                    "rainfall_change": rain_change
                },
                "projected": {
                    "temperature": round(new_temp, 1),
                    "rainfall": round(new_rain, 1)
                },
                "risk_analysis": risk_change,
                "characteristics": characteristics
            }
            
            return {
                "type": "simulation",
                "cities": [city],
                "data": {"results": [simulation_result]},
                "insight": self._generate_simulation_insight(city, temp_change, rain_change, risk_change)
            }
        except Exception as e:
            logger.error(f"Error in simulation: {str(e)}")
            return {"type": "simulation", "error": str(e)}
    
    def _calculate_simulation_risk(self, city: str, temp_delta: float, rain_delta: float, base_temp: float, base_rain: float) -> Dict:
        """Calculate risk changes based on simulation parameters"""
        base_risk = self.SAMPLE_RISK_DATA.get(city, {}).get("risk_level", 5)
        
        # Risk factors
        risk_increase = 0
        
        # Temperature impact: Every 1°C increase adds risk
        if temp_delta > 0:
            risk_increase += temp_delta * 0.5  # 0.5 risk points per degree
        
        # Rainfall impact: Decrease by 10% adds 1 risk point
        if rain_delta < 0:
            risk_increase += abs(rain_delta) / 10
        
        # Drought scenario: significant risk
        if rain_delta <= -30:
            risk_increase += 2
        
        new_risk = min(10, base_risk + risk_increase)
        
        return {
            "base_level": base_risk,
            "projected_level": round(new_risk, 1),
            "change": round(risk_increase, 1),
            "severity": "Critical" if new_risk >= 8 else "High" if new_risk >= 6 else "Moderate" if new_risk >= 4 else "Low"
        }
    
    def _generate_simulation_insight(self, city: str, temp_delta: float, rain_delta: float, risk_data: Dict) -> str:
        """Generate insights from simulation scenario"""
        insights = []
        
        insights.append(f"**{city}** Scenario Analysis")
        
        # Temperature impact
        if temp_delta > 0:
            insights.append(f"• Temperature increase of {temp_delta}°C will lead to more intense heatwaves")
            if temp_delta >= 3:
                insights.append(f"• Critical: High-temperature scenario may impact agricultural productivity and water demand")
        elif temp_delta < 0:
            insights.append(f"• Temperature decrease of {abs(temp_delta)}°C (hypothetical)")
        
        # Rainfall impact
        if rain_delta < 0:
            insights.append(f"• Rainfall reduction of {abs(rain_delta)}% indicates potential drought conditions")
            if rain_delta <= -30:
                insights.append(f"• **Severe drought risk**: Water scarcity and crop failure scenarios possible")
        elif rain_delta > 0:
            insights.append(f"• Rainfall increase of {rain_delta}% may lead to flooding in monsoon regions")
        
        # Combined impact
        if temp_delta > 0 and rain_delta < 0:
            insights.append(f"• **Combined stress**: Heat + drought creates compounded vulnerability")
        
        # Risk assessment
        insights.append(f"• Risk Status: {risk_data['severity']} (Level {risk_data['projected_level']}/10)")
        
        return "\n".join(insights)
    
    async def _get_trend_data(self, cities: List[str], parameters: Dict) -> Dict:
        """Fetch historical trend data across multiple years"""
        try:
            # Fetch data for multiple years to show trends
            trend_data = {}
            current_year = parameters.get("year", 2026)
            years_to_fetch = [current_year - 5, current_year - 3, current_year - 1, current_year]
            
            for year in years_to_fetch:
                try:
                    # Fetch temperature and rainfall for each year
                    url = f"{self.backend_url}/api/climate-map/data?year={year}&mode=temperature"
                    response = await self.client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("data"):
                            trend_data[year] = data.get("data", {})
                except Exception as e:
                    logger.warning(f"Could not fetch trend data for year {year}: {str(e)}")
            
            if trend_data:
                # Calculate year-over-year changes for requested cities
                trend_analysis = {}
                for city in cities:
                    city_trends = []
                    sorted_years = sorted(trend_data.keys())
                    
                    # Extract city data across years
                    for year in sorted_years:
                        year_data = trend_data[year]
                        if isinstance(year_data, list):
                            city_data = next((c for c in year_data if c.get("city", "").lower() == city.lower()), None)
                            if city_data:
                                city_trends.append({
                                    "year": year,
                                    "temperature": city_data.get("temperature"),
                                    "rainfall": city_data.get("rainfall"),
                                    "risk": city_data.get("risk")
                                })
                    
                    if city_trends:
                        trend_analysis[city] = city_trends
                
                return {
                    "type": "trend",
                    "cities": cities,
                    "years": sorted(trend_data.keys()),
                    "trend_analysis": trend_analysis,
                    "raw_data": trend_data,
                    "data": {
                        "trend_analysis": trend_analysis,
                        "years": sorted(trend_data.keys()),
                        "raw_data": trend_data
                    }
                }
            
            return {"type": "trend", "data": None}
        except Exception as e:
            logger.error(f"Error fetching trend data: {str(e)}")
            return {"type": "trend", "error": str(e)}
    
    async def _get_cities_list(self) -> Dict:
        """Fetch list of all available cities"""
        try:
            url = f"{self.backend_url}/api/dashboard/heatmap-data?year=2026"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "type": "cities_list",
                    "data": data
                }
            
            return {"type": "cities_list", "data": None}
        except Exception as e:
            logger.error(f"Error fetching cities list: {str(e)}")
            return {"type": "cities_list", "error": str(e)}
    
    async def _generate_llm_response(self, intent: str, query: str, data: Dict, cities: List[str]) -> str:
        """Generate response using Groq LLM (with fallback to Together AI)"""
        try:
            from app.services.groq_service import GroqService
            
            # CRITICAL: Validate data before LLM
            logger.info(f"🧠 Generating LLM response for intent: {intent}")
            logger.info(f"📊 Data received: type={data.get('type')}, has_data={bool(data.get('data'))}")
            
            # Check if we have actual data
            raw_data = data.get("data", {})
            if not raw_data or (isinstance(raw_data, dict) and len(raw_data) == 0):
                logger.error(f"❌ EMPTY DATA ERROR: No data available for intent {intent}")
                # Don't send empty data to LLM - return error response instead
                error_msg = f"Unable to generate {intent} - no data available. Please try again or refine your query."
                logger.warning(f"🚫 Returning fallback for empty data: {error_msg}")
                return self._get_fallback_response(intent, data)
            
            # Prepare context for LLM
            context = self._prepare_context(intent, data, cities)
            cities_info = f"for {', '.join(cities)}" if cities else "in India"
            
            # Create intent-specific instructions
            intent_instructions = {
                "risk": """Analyze the climate risk data provided. You MUST:
1. Use the "high_risk_cities" and "low_risk_cities" from the data
2. For each city mentioned, provide its exact risk level (0-10 scale)
3. List the specific risk factors (from "factors" field)
4. Compare cities by their risk values
5. Answer questions like "which city is safest" by comparing risk levels
6. Do NOT say data is unavailable - use the anomalies data provided""",
                "forecast": """IMPORTANT: You are EXPLAINING predictions, NOT generating them.
The predictions have ALREADY BEEN GENERATED by our climate models.
Your job is to:
1. Take the predicted values from the raw_data (temperature/rainfall)
2. Format them clearly for the user
3. Explain the trend and implications
4. Use ONLY the values provided - do NOT estimate or guess
5. Show the city name, year, and exact predicted value""",
                "weather": "Provide detailed information about current weather and climate conditions. Include temperature, conditions, and seasonal patterns.",
                "compare": "Compare the climate conditions between the cities provided. Highlight differences and similarities in temperature, patterns, and risk factors.",
                "trend": """CRITICAL: Analyze historical climate trends using the provided data.
RULES FOR TREND ANALYSIS:
1. Extract the trend_analysis data which contains year-by-year values
2. For EACH city, show: temperature/rainfall year-over-year changes
3. Use EXACT values from the data (temperature in °C, rainfall in mm)
4. Calculate and show the change direction (warming/cooling, increase/decrease)
5. For each metric: starting year value, current year value, and total change
6. Do NOT provide generic climate information
7. Focus only on the specific cities mentioned in the data: {cities}
8. Format as: City: XY year trend showing Z°C change (or X mm rainfall change)
9. If data shows warming trend, mention the rate and risk implications
10. NEVER say "data unavailable" - the trend data IS provided""",
                "general": "Provide helpful climate information based on the data available."
            }
            
            specific_instruction = intent_instructions.get(intent, "")
            
            # For trend intent, format the trend_analysis explicitly
            trend_data_str = ""
            if intent == "trend" and "trend_analysis" in data:
                trend_analysis = data.get("trend_analysis", {})
                trend_lines = ["TREND ANALYSIS DATA:"]
                for city, trends_list in trend_analysis.items():
                    trend_lines.append(f"\n{city}:")
                    for trend_point in trends_list:
                        year = trend_point.get("year")
                        temp = trend_point.get("temperature")
                        rain = trend_point.get("rainfall")
                        trend_lines.append(f"  - Year {year}: Temperature {temp}°C, Rainfall {rain}mm")
                trend_data_str = "\n".join(trend_lines)
            
            prompt = f"""You are a climate data assistant with access to specific climate risk and weather data for Indian cities.

User Query: {query}

Climate Data Context:
{json.dumps(context, indent=2)}

{trend_data_str}

Task: {specific_instruction}

CRITICAL RULES FOR ALL RESPONSES:
1. ANALYZE ONLY the data provided above - it's your primary source of truth
2. NEVER say "data is unavailable" - the data IS provided
3. DO NOT provide generic climate facts or estimates
4. Stick to provided data - only use exact values from raw_data
5. When matching cities in questions, use the data provided

FOR FORECAST RESPONSES SPECIFICALLY:
- Extract predicted values directly from the forecast data
- Show city name + year + predicted value + unit
- Use format: "**City Name**: X°C in Year" or "**City Name**: X mm in Year"
- Explain the trend briefly (warming/cooling, increase/decrease)
- Do NOT estimate - use ONLY provided predictions

FOR RISK RESPONSES SPECIFICALLY:
- Use specific risk levels (X/10 scale)
- List the risk factors provided
- Identify high-risk (>=7), medium (4-6), low (<=3) cities

FOR TREND RESPONSES SPECIFICALLY:
- Use the TREND ANALYSIS DATA section above which shows year-by-year values
- Calculate the actual change: final_year_value - first_year_value
- Show the warming/cooling or increase/decrease direction
- Example: "Delhi shows a warming trend of 1.8°C (from 23.2°C in 2021 to 25.0°C in 2026)"
- Calculate rainfall changes the same way with actual mm values
- Do NOT estimate - use ONLY provided historical data

Format your response with:
- **Bold text** for cities and key values
- Bullet points for lists
- Emojis for emphasis (🌡️ temperature, 🌧️ rainfall, 🚨 high risk, 🌱 low risk)
- Clear headings (##) for sections
- Specific numbers - NO estimates or generic info

Answer:"""
            
            # Use Groq service with smart fallback
            # Use larger model for complex queries
            use_large_model = len(prompt) > 1000 or "compare" in intent or "trend" in intent
            
            logger.info(f"🚀 Calling LLM with model={'large' if use_large_model else 'default'}")
            answer = GroqService.generate_response(prompt, use_large_model=use_large_model, max_tokens=500)
            
            if answer and len(answer) > 20:
                logger.info(f"✅ LLM response generated for intent: {intent} ({len(answer)} chars)")
                return answer
            else:
                logger.warning(f"❌ LLM response too short or empty ({len(answer) if answer else 0} chars), using fallback")
                return self._get_fallback_response(intent, data)
                
        except Exception as e:
            logger.error(f"❌ Error generating LLM response: {str(e)}")
            return self._get_fallback_response(intent, data)
    
    def _prepare_context(self, intent: str, data: Dict, cities: List[str]) -> Dict:
        """Prepare relevant data context for LLM"""
        context = {
            "intent": intent,
            "cities": cities if cities else "All cities",
            "data_summary": self._summarize_data(data),
            "raw_data": data.get("data", {})  # Include actual data
        }
        return context
    
    def _summarize_data(self, data: Dict) -> str:
        """Summarize data for LLM context"""
        if not data or not data.get("data"):
            return "No specific data available"
        
        data_type = data.get("type", "unknown")
        cities = data.get("cities", [])
        raw_data = data.get("data", {})
        
        if data_type == "comparison":
            return f"Comparison data between {', '.join(cities) if cities else 'cities'}"
        elif data_type == "weather":
            cities_str = ", ".join(cities) if cities else "selected cities"
            return f"Current weather and climate data for {cities_str}"
        elif data_type == "risk":
            # Extract detailed risk information
            if isinstance(raw_data, dict):
                anomalies = raw_data.get("anomalies", [])
                high_risk = raw_data.get("high_risk_cities", [])
                low_risk = raw_data.get("low_risk_cities", [])
                
                if anomalies:
                    high_risk_names = ", ".join([a.get("city") for a in high_risk[:5]])
                    low_risk_names = ", ".join([a.get("city") for a in low_risk[:3]])
                    return f"Climate risk assessment for {len(set([a.get('city') for a in anomalies]))} Indian cities. High Risk: {high_risk_names}. Low Risk: {low_risk_names}. Total anomalies analyzed: {len(anomalies)}"
            return "Climate risk and anomaly analysis data available"
        elif data_type == "forecast":
            # Extract forecast predictions
            year = data.get("year", 2026)
            metric = data.get("metric", "temperature")
            
            if isinstance(raw_data, dict):
                forecasts = []
                for city, forecast_info in raw_data.items():
                    if isinstance(forecast_info, dict):
                        value = forecast_info.get("value", "N/A")
                        unit = forecast_info.get("unit", "")
                        forecasts.append(f"{city}: {value}{unit}")
                
                if forecasts:
                    forecast_str = ", ".join(forecasts)
                    return f"Climate {metric} forecast for {year}: {forecast_str}"
            
            return f"Climate predictions for {year} available"
        elif data_type == "trend":
            # Extract detailed trend information
            trend_analysis = data.get("trend_analysis", {})
            cities = data.get("cities", [])
            
            if trend_analysis:
                trend_summary = []
                for city, trends in trend_analysis.items():
                    if trends and len(trends) > 1:
                        first_year_temp = trends[0].get("temperature")
                        last_year_temp = trends[-1].get("temperature")
                        first_year_rain = trends[0].get("rainfall")
                        last_year_rain = trends[-1].get("rainfall")
                        first_year = trends[0].get("year")
                        last_year = trends[-1].get("year")
                        
                        if first_year_temp and last_year_temp:
                            temp_change = last_year_temp - first_year_temp
                            temp_dir = "warming" if temp_change > 0 else "cooling"
                            trend_summary.append(f"{city}: {temp_dir} trend ({abs(temp_change):.1f}°C change from {first_year} to {last_year})")
                
                if trend_summary:
                    return f"Historical climate trends: {'; '.join(trend_summary)}"
            
            return "Historical climate trends data available"
        
        return "Climate data"
    
    def _get_fallback_response(self, intent: str, data: Dict) -> str:
        """Fallback response when LLM is unavailable"""
        cities = data.get("cities", [])
        cities_str = ", ".join(cities) if cities else "Indian cities"
        year = data.get("year", 2026)
        metric = data.get("metric", "temperature")
        
        # Get detailed info if available
        details = ""
        
        if intent == "risk":
            raw_data = data.get("data", {})
            if isinstance(raw_data, dict):
                anomalies = raw_data.get("anomalies", [])
                high_risk_cities = raw_data.get("high_risk_cities", [])
                low_risk_cities = raw_data.get("low_risk_cities", [])
                
                # Build high risk section
                if high_risk_cities:
                    details += "## � High Risk Cities\n\n"
                    for city_data in high_risk_cities[:5]:
                        city = city_data.get("city", "Unknown")
                        value = city_data.get("value", "N/A")
                        factors = city_data.get("factors", [])
                        details += f"- **{city}**: Risk Level **{value}/10**\n"
                        if factors:
                            for factor in factors:
                                details += f"  • {factor}\n"
                
                # Build low risk section  
                if low_risk_cities:
                    details += "\n## 🌱 Low Risk Cities\n\n"
                    for city_data in low_risk_cities[:3]:
                        city = city_data.get("city", "Unknown")
                        value = city_data.get("value", "N/A")
                        details += f"- **{city}**: Risk Level **{value}/10** ✅\n"
                        
                # Answer specific questions
                if anomalies:
                    safest = min(anomalies, key=lambda x: x.get("value", 10))
                    highest = max(anomalies, key=lambda x: x.get("value", 0))
                    
                    details += f"\n## 📊 Summary\n\n"
                    details += f"- **Safest City**: {safest.get('city')} (Risk: {safest.get('value')}/10) 🌱\n"
                    details += f"- **Highest Risk City**: {highest.get('city')} (Risk: {highest.get('value')}/10) 🚨\n"
                    details += f"- **Total Cities Analyzed**: {len(set([a.get('city') for a in anomalies]))}\n"
        
        elif intent == "forecast":
            raw_data = data.get("data", {})
            details = f"## 🌡️ Climate Predictions for {year}\n\n"
            
            if isinstance(raw_data, dict) and raw_data:
                # Extract forecast data
                forecast_list = []
                if isinstance(raw_data, dict):
                    for city, forecast_info in raw_data.items():
                        if isinstance(forecast_info, dict):
                            forecast_list.append(forecast_info)
                
                # Show cards format
                details += "### Forecast Summary\n\n"
                details += "| City | Temperature | Rainfall |\n"
                details += "|------|-------------|----------|\n"
                for forecast_info in forecast_list:
                    city = forecast_info.get("city", "Unknown")
                    temp = forecast_info.get("temperature", {}).get("value", "N/A")
                    rain = forecast_info.get("rainfall", {}).get("value", "N/A")
                    details += f"| **{city}** | 🌡️ {temp}°C | 🌧️ {rain}mm |\n"
                
                # Add insights
                if forecast_list:
                    details += f"\n### � Key Insights\n\n"
                    details += "• " + self._generate_forecast_insights(forecast_list).replace("\n• ", "\n• ")
        
        elif intent == "simulation":
            results = data.get("data", {}).get("results", [])
            details = f"## 🔬 Climate Simulation Results\n\n"
            
            if results:
                for result in results:
                    city = result.get("city", "Unknown")
                    baseline_temp = result.get("baseline", {}).get("temperature", "N/A")
                    baseline_rain = result.get("baseline", {}).get("rainfall", "N/A")
                    scenario = result.get("scenario", {})
                    projected = result.get("projected", {})
                    risk = result.get("risk_analysis", {})
                    
                    details += f"### 📍 {city}\n\n"
                    details += "#### Baseline (Current 2026)\n"
                    details += f"- 🌡️ Temperature: {baseline_temp}°C\n"
                    details += f"- 🌧️ Rainfall: {baseline_rain}mm\n\n"
                    
                    details += "#### Scenario Changes\n"
                    temp_change = scenario.get("temperature_change", 0)
                    rain_change = scenario.get("rainfall_change", 0)
                    
                    if temp_change != 0:
                        details += f"- 🌡️ Temperature change: {'+' if temp_change > 0 else ''}{temp_change}°C\n"
                    if rain_change != 0:
                        details += f"- 🌧️ Rainfall change: {'+' if rain_change > 0 else ''}{rain_change}%\n"
                    
                    details += f"\n#### Projected Results\n"
                    details += f"- 🌡️ Temperature: {projected.get('temperature', 'N/A')}°C\n"
                    details += f"- 🌧️ Rainfall: {projected.get('rainfall', 'N/A')}mm\n\n"
                    
                    details += f"#### Risk Assessment\n"
                    details += f"- Current Risk Level: {risk.get('base_level', 'N/A')}/10\n"
                    details += f"- Projected Risk Level: **{risk.get('projected_level', 'N/A')}/10** {risk.get('severity', '')}\n"
                    details += f"- Risk Increase: {'+' if risk.get('change', 0) >= 0 else ''}{risk.get('change', 0)}\n\n"

        
        responses = {
            "compare": f"## Climate Comparison\n\nComparing {cities_str}. Based on the data, I can show you how these cities compare in climate patterns, temperature ranges, and seasonal variations.",
            "weather": f"## Weather & Climate for {cities_str}\n\n📍 Location: {cities_str}\n🌍 Current climate data shows the weather patterns for these cities. Temperature, humidity, and seasonal variations are key factors affecting the climate.",
            "risk": f"## Climate Risk Analysis\n\n{details}",
            "forecast": details if details else f"## Climate Forecast for {year}\n\n📈 The forecast shows predictions for future climate conditions in these cities.",
            "simulation": details if details else "## Climate Simulation\n\nCould not generate simulation results.",
            "trend": "## Historical Trends\n\n📊 Historical trends show how climate patterns have evolved over time.",
            "list": "## Available Cities\n\n🌏 Here are the available cities in our climate database.",
            "general": "## Climate Information\n\n🌍 I can help you explore climate data and trends for Indian cities. Ask me about specific cities, comparisons, or climate patterns!"
        }
        return responses.get(intent, "I can help you explore climate data.")
    
    def _generate_forecast_insights(self, forecast_data: List[Dict]) -> str:
        """Generate intelligent insights from forecast data"""
        if not forecast_data:
            return ""
        
        insights = []
        
        # Find warmest and coolest cities
        warmest = max(forecast_data, key=lambda x: x["temperature"]["value"])
        coolest = min(forecast_data, key=lambda x: x["temperature"]["value"])
        
        # Find cities with highest and lowest rainfall
        highest_rain = max(forecast_data, key=lambda x: x["rainfall"]["value"])
        lowest_rain = min(forecast_data, key=lambda x: x["rainfall"]["value"])
        
        # Build insights
        insights.append(f"**{warmest['city']}** shows highest temperature (~{warmest['temperature']['value']}°C) due to {warmest['characteristics']['temp_influence']}")
        insights.append(f"**{coolest['city']}** remains relatively cooler (~{coolest['temperature']['value']}°C) due to {coolest['characteristics']['temp_influence']}")
        
        if highest_rain['city'] != lowest_rain['city']:
            insights.append(f"**{highest_rain['city']}** shows highest rainfall (~{highest_rain['rainfall']['value']}mm) with strong {highest_rain['characteristics']['rain_influence']}")
            insights.append(f"**{lowest_rain['city']}** has lower rainfall (~{lowest_rain['rainfall']['value']}mm) in its {lowest_rain['characteristics']['rain_influence']}")
        
        # General warming trend
        avg_temp_change = sum([x["temperature"]["change"] for x in forecast_data]) / len(forecast_data)
        insights.append(f"Overall warming trend: +{avg_temp_change:.1f}°C expected across region")
        
        return "\n• ".join(insights)
    
    def _suggest_next_action(self, intent: str) -> tuple:
        """Suggest next action based on intent"""
        actions = {
            "map_action": ("Open map view", "/map"),
            "compare": ("View detailed comparison on map", "/map"),
            "weather": ("View on climate map", "/climate-map"),
            "risk": ("View risk analysis dashboard", "/dashboard"),
            "forecast": ("Explore forecast scenarios", "/forecast"),
            "simulation": ("Run another simulation", "/simulation"),
            "trend": ("View historical trends", "/dashboard"),
            "list": ("Explore cities on map", "/map"),
            "general": ("View climate dashboard", "/dashboard")
        }
        action, url = actions.get(intent, ("Explore more", "/dashboard"))
        return action, url
