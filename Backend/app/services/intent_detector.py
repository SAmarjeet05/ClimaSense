"""
Intent Detection Service for AI Assistant
Classifies user queries to determine which APIs to call
"""
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class IntentDetector:
    """Detects user intent from natural language queries"""
    
    INTENTS = {
        "compare": ["compare", "difference", "vs", "versus", "which is better", "hottest", "coldest", "warmest", "highest", "lowest"],
        "weather": ["weather", "climate", "temperature", "how is", "what is the", "tell me about", "what about", "current"],
        "risk": ["risk", "danger", "unsafe", "high risk", "anomaly", "unstable", "threat", "hazard"],
        "forecast": ["future", "predict", "will", "tomorrow", "next", "2030", "2050", "forecast", "temperature rise"],
        "trend": ["trend", "pattern", "history", "past", "how has", "over time", "evolution"],
        "simulate": ["simulate", "simulate", "impact", "if", "+2", "+3", "warming", "scenario"],
        "list": ["list", "show", "cities", "states", "all", "top", "available"]
    }
    
    @staticmethod
    def extract_cities(query: str) -> List[str]:
        """
        Extract city names from query
        Uses pattern matching and keyword detection
        """
        # Common Indian cities
        cities = [
            "Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Hyderabad",
            "Pune", "Jaipur", "Ahmedabad", "Agartala", "Aizawl", "Amritsar",
            "Aurangabad", "Bhopal", "Chandigarh", "Coimbatore", "Cuttack", "Daman",
            "Darjeeling", "Durgapur", "Guwahati", "Gwalior", "Hamirpur", "Haridwar",
            "Hissar", "Indore", "Itanagar", "Jabalpur", "Jamshedpur", "Jodhpur",
            "Kanpur", "Kottayam", "Lucknow", "Ludhiana", "Madurai", "Meerut",
            "Mysore", "Nagpur", "Nashik"
        ]
        
        found_cities = []
        for city in cities:
            if city.lower() in query.lower():
                found_cities.append(city)
        
        return found_cities
    
    @staticmethod
    def classify_intent(query: str) -> str:
        """
        Classify the intent of the query with proper priority
        
        Priority order:
        1. Forecast (if contains year 2025+ or future keywords)
        2. Risk (specific risk keywords)
        3. Compare
        4. Weather
        5. Trend
        6. Other
        
        Args:
            query: User query string
            
        Returns:
            Intent type: "compare", "risk", "forecast", "trend", "simulate", "list", or "general"
        """
        query_lower = query.lower()
        
        # PRIORITY 0: Check for MAP_ACTION intent (UI navigation - highest priority)
        # Check if query explicitly asks to show something on map
        if "map" in query_lower and any(indicator in query_lower for indicator in ["show", "display", "view", "on map"]):
            # If it also contains visualization mode keywords, it's definitely map_action
            if any(mode in query_lower for mode in ["risk", "temperature", "rainfall", "rain", "temp", "distribution"]):
                logger.info(f"Detected intent: map_action")
                return "map_action"
        
        # PRIORITY 1: Check for FORECAST intent (years + future keywords)
        forecast_keywords = ["predict", "forecast", "will", "future", "2025", "2026", "2027", "2028", "2029", "2030", "2031", "2032", "2040", "2050"]
        for keyword in forecast_keywords:
            if keyword in query_lower:
                logger.info(f"Detected intent: forecast (keyword: {keyword})")
                return "forecast"
        
        # PRIORITY 2: Check for RISK intent
        risk_keywords = ["risk", "danger", "unsafe", "high risk", "anomaly", "unstable", "threat", "hazard"]
        for keyword in risk_keywords:
            if keyword in query_lower:
                logger.info(f"Detected intent: risk (keyword: {keyword})")
                return "risk"
        
        # PRIORITY 3: Check for COMPARE intent
        compare_keywords = ["compare", "difference", "vs", "versus", "which is better", "hottest", "coldest", "warmest", "highest", "lowest"]
        for keyword in compare_keywords:
            if keyword in query_lower:
                logger.info(f"Detected intent: compare (keyword: {keyword})")
                return "compare"
        
        # PRIORITY 4: Check for TREND intent
        trend_keywords = ["trend", "pattern", "history", "past", "how has", "over time", "evolution", "historical"]
        for keyword in trend_keywords:
            if keyword in query_lower:
                logger.info(f"Detected intent: trend (keyword: {keyword})")
                return "trend"
        
        # PRIORITY 5: Check for SCENARIO intent (specific +2°C, +3°C temperature rise queries)
        # This is for "What happens if temperature rises by 2°C?" type questions
        # Must have a temperature value like +2°C, 2 degrees, etc.
        has_temperature_value = re.search(
            r'(?:\+|-)?(\d+)\s*(?:°?C|degree)',
            query_lower,
            re.IGNORECASE
        )
        
        # Check for scenario-related keywords
        scenario_keywords = ["happens", "happens if", "what if", "what would", "impact", "effect", "consequence", "scenario", "warming", "warming scenario"]
        has_scenario_keyword = any(kw in query_lower for kw in scenario_keywords)
        
        if has_temperature_value and has_scenario_keyword:
            logger.info(f"Detected intent: scenario (temperature value with scenario keyword)")
            return "scenario"
        
        # PRIORITY 6: Check for SIMULATION intent (what-if scenarios)
        simulation_keywords = ["simulate", "what if", "what happens", "if", "increase", "decrease", "drop", "drought", "heatwave", "scenario", "happens if", "impact of"]
        for keyword in simulation_keywords:
            if keyword in query_lower:
                # Avoid false positives with generic "if" - need more context
                if keyword == "if" and len(query) < 15:
                    continue
                logger.info(f"Detected intent: simulation (keyword: {keyword})")
                return "simulation"
        
        # PRIORITY 7: Check for WEATHER intent (catch-all for climate questions)
        weather_keywords = ["weather", "climate", "temperature", "how is", "what is the", "tell me about", "what about", "current", "rainfall", "rain"]
        for keyword in weather_keywords:
            if keyword in query_lower:
                logger.info(f"Detected intent: weather (keyword: {keyword})")
                return "weather"
        
        # PRIORITY 8: Check for LIST intent
        list_keywords = ["list", "show", "cities", "states", "all", "top", "available"]
        for keyword in list_keywords:
            if keyword in query_lower:
                logger.info(f"Detected intent: list (keyword: {keyword})")
                return "list"
        
        logger.info("Detected intent: general")
        return "general"
    
    @staticmethod
    def parse_query(query: str) -> Dict:
        """
        Parse query into components
        
        Returns:
            {
                "intent": "compare|risk|forecast|...",
                "cities": ["Delhi", "Mumbai"],
                "parameters": {"type": "temperature", "year": 2030}
            }
        """
        intent = IntentDetector.classify_intent(query)
        cities = IntentDetector.extract_cities(query)
        
        parameters = {}
        
        # Extract year/date
        year_match = re.search(r'(20\d\d|\d{4})', query)
        if year_match:
            parameters['year'] = int(year_match.group(1))
        
        # Extract temperature change with better pattern matching
        # Pattern 1: "increases by 2", "rises +3°C", etc.
        temp_patterns = [
            r'(?:increase|rise|up by|goes up|hotter)[\s\w]*?by[\s]*(\d+)',  # "increases by 2" or "increases by +2"
            r'(?:\+|-)?(\d+)\s*°?C.*(?:increase|rise|gain|warm)',  # "2°C increase"
            r'(?:increase|rise|gain|warm).*(\d+)\s*(?:°?C|degree)',  # "increase of 2°C"
            r'(?:\+|-)?(\d+)\s*°?C',  # "+2°C" or "-3°C"
        ]
        
        for pattern in temp_patterns:
            temp_match = re.search(pattern, query, re.IGNORECASE)
            if temp_match:
                temp_value = int(temp_match.group(1))
                # Determine sign
                if re.search(r'decrease|drop|cool|cold|lower', query, re.IGNORECASE):
                    parameters['temperature_change'] = -temp_value
                elif re.search(r'\-\d+', query):
                    parameters['temperature_change'] = -temp_value
                else:
                    parameters['temperature_change'] = temp_value
                break
        
        # Extract rainfall change with better pattern matching
        # Pattern 1: "drops by 30%", "increases 40%", etc.
        rain_patterns = [
            r'(?:drop|decrease|fall)[\s\w]*?(?:by|of)[\s]*(\d+)%',  # "drops by 30%" or "drops of 30%"
            r'(?:increase|rise)[\s\w]*?(?:by|of)[\s]*(\d+)%',  # "increases by 30%" or "increases of 30%"
            r'(\d+)%.*(?:rainfall|rain)',  # "30% rainfall"
        ]
        
        for pattern in rain_patterns:
            rain_match = re.search(pattern, query, re.IGNORECASE)
            if rain_match:
                rain_value = int(rain_match.group(1))
                if re.search(r'drop|decrease|fall', query, re.IGNORECASE):
                    parameters['rainfall_change'] = -rain_value
                elif re.search(r'increase|rise', query, re.IGNORECASE):
                    parameters['rainfall_change'] = rain_value
                else:
                    parameters['rainfall_change'] = -rain_value  # Default to decrease
                break
        
        # Handle drought keyword as -40% rainfall (if no explicit percentage given)
        if 'drought' in query.lower() and 'rainfall_change' not in parameters:
            parameters['rainfall_change'] = -40
        
        # Handle heatwave keyword as +3°C temperature (if no explicit degree given)
        if 'heatwave' in query.lower() and 'temperature_change' not in parameters:
            parameters['temperature_change'] = 3
        
        # Extract metric type
        if 'temperature' in query.lower():
            parameters['metric'] = 'temperature'
        elif 'rainfall' in query.lower() or 'rain' in query.lower():
            parameters['metric'] = 'rainfall'
        elif 'risk' in query.lower():
            parameters['metric'] = 'risk'
        
        return {
            "intent": intent,
            "cities": cities,
            "parameters": parameters,
            "raw_query": query
        }
    
    @staticmethod
    def extract_map_mode(query: str) -> str:
        """
        Extract the map visualization mode from query
        
        Returns:
            Map mode: "risk", "temperature", or "rainfall"
        """
        q = query.lower()
        
        if "risk" in q:
            return "risk"
        if "temperature" in q or "temp" in q:
            return "temperature"
        if "rainfall" in q or "rain" in q:
            return "rainfall"
        
        # Default to temperature if no specific mode mentioned
        return "temperature"
