"""
Ollama Integration Service
Connects to local Ollama instance for LLM-powered insights
"""
import requests
import json
from typing import Optional, Dict, Any
from app.services import ml_service_v2

class OllamaService:
    """Service for interacting with local Ollama LLM"""
    
    # Ollama API endpoint
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/api"
    
    # Model configuration
    DEFAULT_MODEL = "mistral:latest"  # Fast, good quality
    BACKUP_MODEL = "llama3:8b"  # More capable but slower
    
    @staticmethod
    def is_ollama_available() -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{OllamaService.OLLAMA_API_URL}/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
            return False
    
    @staticmethod
    def generate_climate_insights(cities_data: Dict[str, Any], comparison_context: Optional[str] = None) -> str:
        """
        Generate intelligent AI insights using Ollama LLM
        
        Args:
            cities_data: Dictionary with temperature, rainfall, stability data
            comparison_context: Optional context for comparing two cities
            
        Returns:
            LLM-generated insight string
        """
        try:
            if not OllamaService.is_ollama_available():
                return OllamaService._generate_fallback_insights(cities_data)
            
            # Prepare context for the LLM
            prompt = OllamaService._build_insights_prompt(cities_data, comparison_context)
            
            # Call Ollama with streaming disabled for consistent output
            response = requests.post(
                f"{OllamaService.OLLAMA_API_URL}/generate",
                json={
                    "model": OllamaService.DEFAULT_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "num_predict": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                insight_text = result.get("response", "").strip()
                
                # Ensure we get quality output
                if insight_text and len(insight_text) > 20:
                    return insight_text
            
            # Fallback if LLM call fails
            return OllamaService._generate_fallback_insights(cities_data)
            
        except Exception as e:
            print(f"⚠️ Error generating Ollama insights: {e}")
            return OllamaService._generate_fallback_insights(cities_data)
    
    @staticmethod
    def _build_insights_prompt(cities_data: Dict[str, Any], comparison_context: Optional[str]) -> str:
        """Build an intelligent prompt for the LLM"""
        
        prompt = """You are a climate analysis expert. Based on the provided climate data, 
generate a brief, insightful analysis (2-3 sentences) about what the data reveals about 
climate patterns and trends. Be specific with numbers and observations.

"""
        
        if comparison_context:
            prompt += f"Context: {comparison_context}\n\n"
        
        # Add structured data
        prompt += "Climate Data:\n"
        
        if isinstance(cities_data, dict):
            for key, value in cities_data.items():
                if isinstance(value, dict):
                    prompt += f"{key}:\n"
                    for k, v in value.items():
                        prompt += f"  {k}: {v}\n"
                else:
                    prompt += f"{key}: {value}\n"
        
        prompt += "\nProvide a concise, data-driven insight:"
        
        return prompt
    
    @staticmethod
    def _generate_fallback_insights(cities_data: Dict[str, Any]) -> str:
        """Generate insights when Ollama is unavailable"""
        
        insights = []
        
        # Try to extract meaningful patterns from data
        if isinstance(cities_data, dict):
            # Temperature analysis
            temps = []
            for city, data in cities_data.items():
                if isinstance(data, dict) and 'temperature' in data:
                    temps.append(float(data['temperature']))
            
            if temps:
                avg_temp = sum(temps) / len(temps)
                if avg_temp > 30:
                    insights.append(f"India experiencing warm conditions with average temperature {avg_temp:.1f}°C.")
                elif avg_temp < 20:
                    insights.append(f"Cooler climate detected across regions, averaging {avg_temp:.1f}°C.")
                else:
                    insights.append(f"Moderate temperatures observed at {avg_temp:.1f}°C average.")
            
            # Rainfall analysis
            rains = []
            for city, data in cities_data.items():
                if isinstance(data, dict) and 'rainfall' in data:
                    rains.append(float(data['rainfall']))
            
            if rains:
                avg_rain = sum(rains) / len(rains)
                if avg_rain > 50:
                    insights.append(f"Significant rainfall activity detected averaging {avg_rain:.1f}mm.")
                elif avg_rain < 10:
                    insights.append(f"Low precipitation observed at {avg_rain:.1f}mm average.")
        
        if not insights:
            insights.append("Climate data analysis indicates variable patterns across monitored regions.")
        
        return " ".join(insights[:2])  # Return top 2 insights
    
    @staticmethod
    def generate_comparison_analysis(city1_data: Dict, city2_data: Dict, metric: str = "stability") -> str:
        """
        Generate comparative analysis between two cities using Ollama
        
        Args:
            city1_data: Climate data for city 1
            city2_data: Climate data for city 2
            metric: Metric to compare (stability, temperature, rainfall)
            
        Returns:
            Comparative insight string
        """
        try:
            if not OllamaService.is_ollama_available():
                return "Data shows different climate patterns between the two regions."
            
            prompt = f"""Compare these two cities' climate data and provide a brief analysis 
of which has more favorable climate conditions and why:

City 1 Data:
{json.dumps(city1_data, indent=2)}

City 2 Data:
{json.dumps(city2_data, indent=2)}

Comparison Metric: {metric}

Provide a concise, specific comparison (2-3 sentences):"""
            
            response = requests.post(
                f"{OllamaService.OLLAMA_API_URL}/generate",
                json={
                    "model": OllamaService.DEFAULT_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.6,
                    "num_predict": 150
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "").strip()
                return analysis if analysis else "Cities show distinct climate characteristics."
            
            return "Climate comparison indicates regional variations in weather patterns."
            
        except Exception as e:
            print(f"⚠️ Comparison analysis error: {e}")
            return "Both cities demonstrate unique climate patterns worth monitoring."
    
    @staticmethod
    def generate_anomaly_explanation(anomaly_data: Dict, city: str) -> str:
        """
        Generate explanation for detected anomalies using Ollama
        
        Args:
            anomaly_data: Anomaly information
            city: City name
            
        Returns:
            Explanation string
        """
        try:
            if not OllamaService.is_ollama_available():
                return f"Anomalous weather pattern detected in {city}."
            
            prompt = f"""Explain why this weather anomaly is significant for {city}:

Anomaly Details:
Type: {anomaly_data.get('type', 'unknown')}
Year: {anomaly_data.get('year', 'unknown')}
Value: {anomaly_data.get('value', 'N/A')}
Deviation from Normal: {anomaly_data.get('deviation', 'N/A')}
Severity: {anomaly_data.get('severity', 'unknown')}

Provide a brief, informative explanation (1-2 sentences):"""
            
            response = requests.post(
                f"{OllamaService.OLLAMA_API_URL}/generate",
                json={
                    "model": OllamaService.DEFAULT_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5,
                    "num_predict": 100
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                explanation = result.get("response", "").strip()
                return explanation if explanation else f"Notable weather pattern detected in {city}."
            
            return f"Significant climate variation observed in {city}."
            
        except Exception as e:
            print(f"⚠️ Anomaly explanation error: {e}")
            return f"Unusual weather pattern detected in {city}."

    @staticmethod
    def generate_short_comparison(city1_data: Dict, city2_data: Dict, mode: str = "temperature") -> str:
        """
        Generate SHORT comparison insight between two cities (mode-specific)
        
        Args:
            city1_data: Climate metrics for city 1
            city2_data: Climate metrics for city 2
            mode: Analysis mode (temperature, rainfall, risk)
            
        Returns:
            Brief 1-2 sentence comparison focused on the selected mode
        """
        try:
            if not OllamaService.is_ollama_available():
                city1_name = list(city1_data.keys())[0]
                city2_name = list(city2_data.keys())[0]
                return f"{city1_name} and {city2_name} show different {mode} patterns."
            
            # Extract city names and data
            city1_name = list(city1_data.keys())[0]
            city1_metrics = city1_data[city1_name]
            city2_name = list(city2_data.keys())[0]
            city2_metrics = city2_data[city2_name]
            
            # Build mode-specific prompt
            if mode == "temperature":
                focus = f"temperature patterns. {city1_name}: {city1_metrics['temperature']}°C, {city2_name}: {city2_metrics['temperature']}°C"
                question = f"Which city has more favorable/stable temperatures and why?"
            elif mode == "rainfall":
                focus = f"rainfall patterns. {city1_name}: {city1_metrics['rainfall']}mm, {city2_name}: {city2_metrics['rainfall']}mm"
                question = f"Which city has more predictable rainfall and why?"
            else:  # risk
                focus = f"climate risk levels. {city1_name}: {city1_metrics['stability']:.1f}/100 stability, {city2_name}: {city2_metrics['stability']:.1f}/100 stability"
                question = f"Which city represents lower climate risk and why?"
            
            prompt = f"""Compare {city1_name} and {city2_name} specifically on {focus}

{question}
Give ONE concise sentence explaining the comparison:"""
            
            response = requests.post(
                f"{OllamaService.OLLAMA_API_URL}/generate",
                json={
                    "model": OllamaService.DEFAULT_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5,
                    "num_predict": 60  # Keep response short
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                insight = result.get("response", "").strip()
                # Clean up - remove any trailing incomplete sentences
                sentences = insight.split('. ')
                if len(sentences) > 1:
                    return sentences[0] + '.'
                return insight if insight else f"{city1_name} and {city2_name} show distinct {mode} characteristics."
            
            return f"{city1_name} and {city2_name} have different {mode} profiles."
            
        except Exception as e:
            print(f"⚠️ Short comparison error: {e}")
            city1_name = list(city1_data.keys())[0]
            city2_name = list(city2_data.keys())[0]
            return f"Climate {mode} comparison between {city1_name} and {city2_name} shows regional variations."

    @staticmethod
    def generate_overall_assessment(city1: str, stability1: float, temp1: float, rain1: float,
                                   city2: str, stability2: float, temp2: float, rain2: float,
                                   winner: str, mode: str = "temperature") -> str:
        """
        Generate COMPREHENSIVE overall assessment for comparison summary (mode-specific)
        
        Args:
            city1, city2: City names
            stability1, stability2: Stability scores (0-100)
            temp1, temp2: Average temperatures
            rain1, rain2: Average rainfall
            winner: Which city is more stable
            mode: Analysis mode (temperature, rainfall, risk)
            
        Returns:
            Detailed 3-4 sentence overall assessment focused on the selected mode
        """
        try:
            if not OllamaService.is_ollama_available():
                return OllamaService._generate_fallback_assessment(city1, city2, winner, stability1, stability2, mode)
            
            # Build mode-specific prompt
            if mode == "temperature":
                metric_focus = f"temperature stability and patterns. {city1} averages {temp1:.1f}°C while {city2} averages {temp2:.1f}°C"
                analysis_point = "temperature variations affect comfort and infrastructure needs"
            elif mode == "rainfall":
                metric_focus = f"rainfall patterns and precipitation. {city1} receives {rain1:.1f}mm average rainfall, {city2} receives {rain2:.1f}mm"
                analysis_point = "rainfall differences impact agriculture, water resources, and flood risk"
            else:  # risk
                metric_focus = f"overall climate risk. {city1} has a stability score of {stability1:.1f}/100, {city2} has {stability2:.1f}/100"
                analysis_point = "climate risk affects long-term planning and climate resilience"
            
            prompt = f"""Provide an overall climate summary comparing {city1} and {city2} from a {mode} perspective:

{metric_focus}
Winner (More favorable {mode}: {winner}
Stability difference: {abs(stability1 - stability2):.1f} points

Focus your assessment on:
1) Which city has better {mode} conditions and why
2) Specific {mode} differences between them
3) How these {mode} differences matter ({analysis_point})
4) Key {mode} patterns to note

Provide a comprehensive 3-4 sentence assessment with specific numbers:"""
            
            response = requests.post(
                f"{OllamaService.OLLAMA_API_URL}/generate",
                json={
                    "model": OllamaService.DEFAULT_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.6,
                    "num_predict": 200  # Allow longer response for assessment
                },
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                assessment = result.get("response", "").strip()
                
                # Ensure we have meaningful output
                if assessment and len(assessment) > 50:
                    # Clean up excessive output
                    sentences = assessment.split('. ')
                    # Keep first 3-4 sentences
                    cleaned = '. '.join(sentences[:4])
                    if not cleaned.endswith('.'):
                        cleaned += '.'
                    return cleaned
                
                return OllamaService._generate_fallback_assessment(city1, city2, winner, stability1, stability2, mode)
            
            return OllamaService._generate_fallback_assessment(city1, city2, winner, stability1, stability2, mode)
            
        except Exception as e:
            print(f"⚠️ Overall assessment error: {e}")
            return OllamaService._generate_fallback_assessment(city1, city2, winner, stability1, stability2, mode)

    @staticmethod
    def _generate_fallback_assessment(city1: str, city2: str, winner: str, stability1: float, stability2: float, mode: str = "temperature") -> str:
        """Generate fallback assessment when Ollama is unavailable"""
        
        if mode == "temperature":
            if winner == "Equal":
                return f"{city1} and {city2} demonstrate comparable temperature stability. Both regions experience similar temperature ranges, making them equally suitable for temperature-sensitive applications."
            elif winner == city1:
                return f"{city1} shows superior temperature stability with a lower temperature variance. The more consistent temperatures in {city1} make it more favorable for temperature-sensitive operations."
            else:
                return f"{city2} demonstrates superior temperature stability with more predictable temperature patterns. The greater temperature consistency in {city2} provides more favorable conditions."
        
        elif mode == "rainfall":
            if winner == "Equal":
                return f"{city1} and {city2} demonstrate comparable rainfall patterns and predictability. Both regions have similar precipitation characteristics affecting agriculture and water resources similarly."
            elif winner == city1:
                return f"{city1} shows more predictable rainfall patterns compared to {city2}. The rainfall consistency in {city1} makes it more favorable for agricultural planning and water resource management."
            else:
                return f"{city2} demonstrates more stable rainfall patterns with predictable precipitation. The rainfall predictability in {city2} provides advantages for agricultural and water-related sectors."
        
        else:  # risk
            if winner == "Equal":
                return f"{city1} and {city2} present equal overall climate risk ({stability1:.1f} and {stability2:.1f} stability scores). Both regions face similar climate challenges and vulnerabilities."
            elif winner == city1:
                diff = stability1 - stability2
                return f"{city1} represents lower climate risk with a stability score of {stability1:.1f}/100, {diff:.1f} points higher than {city2}. The greater climate stability in {city1} makes it a more resilient location for long-term planning."
            else:
                diff = stability2 - stability1
                return f"{city2} represents lower climate risk with a stability score of {stability2:.1f}/100, outperforming {city1} by {diff:.1f} points. The superior climate stability in {city2} provides better long-term climate resilience."

