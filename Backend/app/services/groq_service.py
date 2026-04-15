"""
Groq LLM Integration Service
Uses Groq API with Llama 3 models and Together AI as fallback
"""
import os
import json
import logging
from typing import Optional, Dict, Any
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GroqService:
    """Service for interacting with Groq LLM API (Llama 3) with fallback to Together AI"""
    
    # API Keys from environment
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
    
    # API Endpoints
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
    
    # Model Configuration
    PRIMARY_MODEL = "llama-3.1-8b-instant"  # Fast, good quality
    UPGRADE_MODEL = "llama-3.3-70b-versatile"  # More capable, production ready
    FALLBACK_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  # Together AI fallback
    
    # Rate limit tracking (simple in-memory tracking)
    _rate_limit_reset = {}
    _request_counts = {}
    
    @staticmethod
    def _is_rate_limited(provider: str) -> bool:
        """Check if provider is currently rate limited"""
        if provider not in GroqService._rate_limit_reset:
            return False
        
        reset_time = GroqService._rate_limit_reset[provider]
        if reset_time and datetime.now() < reset_time:
            logger.warning(f"⏱️  {provider} is rate limited until {reset_time}")
            return True
        
        # Reset if time has passed
        if reset_time and datetime.now() >= reset_time:
            GroqService._rate_limit_reset[provider] = None
        
        return False
    
    @staticmethod
    def _mark_rate_limited(provider: str, retry_after: int = 60):
        """Mark provider as rate limited"""
        GroqService._rate_limit_reset[provider] = datetime.now() + timedelta(seconds=retry_after)
        logger.warning(f"⚠️  {provider} rate limited, will retry after {retry_after}s")
    
    @staticmethod
    def is_available() -> bool:
        """Check if Groq API is available with valid API key"""
        if not GroqService.GROQ_API_KEY:
            logger.warning("❌ GROQ_API_KEY not set in environment")
            return bool(GroqService.TOGETHER_API_KEY)  # Fall back to Together AI
        return True
    
    @staticmethod
    def _call_groq(prompt: str, model: str = PRIMARY_MODEL, temperature: float = 0.7, max_tokens: int = 200) -> Optional[str]:
        """
        Call Groq API with specified model
        
        Args:
            prompt: The prompt to send
            model: Model to use (llama-3-8b-chat or llama-3-70b-chat)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None if failed
        """
        if not GroqService.GROQ_API_KEY:
            logger.warning("⚠️  GROQ_API_KEY not configured, skipping Groq")
            return None
        
        if GroqService._is_rate_limited("groq"):
            logger.info("⏱️  Groq rate limited, using fallback")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {GroqService.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a climate analysis expert. Provide accurate, concise insights."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            response = requests.post(
                GroqService.GROQ_API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                GroqService._mark_rate_limited("groq", retry_after)
                logger.warning(f"⚠️  Groq rate limited: {response.text}")
                return None
            
            if response.status_code == 401:
                logger.error("❌ Invalid Groq API key")
                return None
            
            if response.status_code != 200:
                logger.warning(f"⚠️  Groq API error {response.status_code}: {response.text}")
                return None
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            if content:
                logger.info(f"✅ Groq response generated ({len(content)} chars)")
                return content
            
            return None
            
        except requests.exceptions.Timeout:
            logger.warning("⏱️  Groq API timeout")
            return None
        except Exception as e:
            logger.error(f"❌ Groq API error: {str(e)}")
            return None
    
    @staticmethod
    def _call_together_ai(prompt: str, temperature: float = 0.7, max_tokens: int = 200) -> Optional[str]:
        """
        Call Together AI API as fallback with Mixtral model
        
        Args:
            prompt: The prompt to send
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None if failed
        """
        if not GroqService.TOGETHER_API_KEY:
            logger.warning("⚠️  TOGETHER_API_KEY not configured")
            return None
        
        if GroqService._is_rate_limited("together"):
            logger.info("⏱️  Together AI rate limited, using fallback")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {GroqService.TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": GroqService.FALLBACK_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a climate analysis expert. Provide accurate, concise insights."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                GroqService.TOGETHER_API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                GroqService._mark_rate_limited("together", retry_after)
                logger.warning(f"⚠️  Together AI rate limited: {response.text}")
                return None
            
            if response.status_code != 200:
                logger.warning(f"⚠️  Together AI error {response.status_code}: {response.text}")
                return None
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            if content:
                logger.info(f"✅ Together AI response generated ({len(content)} chars)")
                return content
            
            return None
            
        except requests.exceptions.Timeout:
            logger.warning("⏱️  Together AI timeout")
            return None
        except Exception as e:
            logger.error(f"❌ Together AI error: {str(e)}")
            return None
    
    @staticmethod
    def generate_response(prompt: str, use_large_model: bool = False, temperature: float = 0.7, max_tokens: int = 200) -> str:
        """
        Generate response using Groq with smart fallback strategy
        
        Strategy:
        1. Try Llama 3 8B (Groq) - Fast and efficient
        2. If rate limited, try Llama 3 70B (Groq) - More capable
        3. If both fail, try Together AI Mixtral - Fallback provider
        4. If all fail, return fallback text
        
        Args:
            prompt: The prompt to send
            use_large_model: Use 70B model instead of 8B
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        logger.info(f"🤖 Generating response (use_large={use_large_model})")
        
        # Strategy 1: Try primary Groq model
        model_to_use = GroqService.UPGRADE_MODEL if use_large_model else GroqService.PRIMARY_MODEL
        response = GroqService._call_groq(prompt, model_to_use, temperature, max_tokens)
        
        if response:
            return response
        
        logger.info("📊 Groq primary failed, trying upgrade model")
        
        # Strategy 2: Try upgrade Groq model if not already tried
        if not use_large_model:
            response = GroqService._call_groq(prompt, GroqService.UPGRADE_MODEL, temperature, max_tokens)
            if response:
                return response
        
        logger.info("🔄 Groq upgrade failed, trying Together AI fallback")
        
        # Strategy 3: Try Together AI
        response = GroqService._call_together_ai(prompt, temperature, max_tokens)
        
        if response:
            return response
        
        logger.warning("⚠️  All AI providers failed, returning placeholder")
        
        # Strategy 4: Return meaningful fallback
        return "Unable to generate response at this time. Please try again later."
    
    @staticmethod
    def generate_climate_insights(cities_data: Dict[str, Any], comparison_context: Optional[str] = None) -> str:
        """Generate intelligent AI insights"""
        
        prompt = GroqService._build_insights_prompt(cities_data, comparison_context)
        return GroqService.generate_response(prompt, temperature=0.7, max_tokens=200)
    
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
    def generate_comparison_analysis(city1_data: Dict, city2_data: Dict, metric: str = "stability") -> str:
        """Generate comparative analysis between two cities"""
        
        prompt = f"""Compare these two cities' climate data and provide a brief analysis 
of which has more favorable climate conditions and why:

City 1 Data:
{json.dumps(city1_data, indent=2)}

City 2 Data:
{json.dumps(city2_data, indent=2)}

Comparison Metric: {metric}

Provide a concise, specific comparison (2-3 sentences):"""
        
        return GroqService.generate_response(prompt, temperature=0.6, max_tokens=150)
    
    @staticmethod
    def generate_anomaly_explanation(anomaly_data: Dict, city: str) -> str:
        """Generate explanation for detected anomalies"""
        
        prompt = f"""Explain why this weather anomaly is significant for {city}:

Anomaly Details:
Type: {anomaly_data.get('type', 'unknown')}
Year: {anomaly_data.get('year', 'unknown')}
Value: {anomaly_data.get('value', 'N/A')}
Deviation from Normal: {anomaly_data.get('deviation', 'N/A')}
Severity: {anomaly_data.get('severity', 'unknown')}

Provide a brief, informative explanation (1-2 sentences):"""
        
        response = GroqService.generate_response(prompt, temperature=0.5, max_tokens=100)
        return response if response else f"Notable weather pattern detected in {city}."
    
    @staticmethod
    def generate_short_comparison(city1_data: Dict, city2_data: Dict, mode: str = "temperature") -> str:
        """Generate SHORT comparison insight between two cities (mode-specific)"""
        
        try:
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
            
            response = GroqService.generate_response(prompt, temperature=0.5, max_tokens=60)
            
            # Clean up - remove any trailing incomplete sentences
            sentences = response.split('. ')
            if len(sentences) > 1:
                return sentences[0] + '.'
            return response
            
        except Exception as e:
            logger.error(f"⚠️  Short comparison error: {e}")
            return f"Climate {mode} comparison between cities shows regional variations."
    
    @staticmethod
    def generate_overall_assessment(city1: str, stability1: float, temp1: float, rain1: float,
                                   city2: str, stability2: float, temp2: float, rain2: float,
                                   winner: str, mode: str = "temperature") -> str:
        """Generate COMPREHENSIVE overall assessment for comparison summary (mode-specific)"""
        
        try:
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
Winner (More favorable {mode}): {winner}
Stability difference: {abs(stability1 - stability2):.1f} points

Focus your assessment on:
1) Which city has better {mode} conditions and why
2) Specific {mode} differences between them
3) How these {mode} differences matter ({analysis_point})
4) Key {mode} patterns to note

Provide a comprehensive 3-4 sentence assessment with specific numbers:"""
            
            response = GroqService.generate_response(prompt, temperature=0.6, max_tokens=200)
            
            # Ensure we have meaningful output
            if response and len(response) > 50:
                # Clean up excessive output
                sentences = response.split('. ')
                # Keep first 3-4 sentences
                cleaned = '. '.join(sentences[:4])
                if not cleaned.endswith('.'):
                    cleaned += '.'
                return cleaned
            
            return response if response else f"Climate {mode} comparison between {city1} and {city2} shows distinct patterns."
            
        except Exception as e:
            logger.error(f"⚠️  Overall assessment error: {e}")
            return f"Climate {mode} comparison between {city1} and {city2} shows distinct patterns."
