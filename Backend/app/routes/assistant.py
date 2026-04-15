"""
Assistant API Routes
Handles /api/assistant/* endpoints for AI assistant functionality
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assistant", tags=["assistant"])

class AssistantQueryRequest(BaseModel):
    query: str
    user_id: Optional[int] = None

class AssistantResponse(BaseModel):
    status: str
    query: str
    intent: str
    answer: str
    data: dict = {}
    suggested_action: str
    action_url: str
    timestamp: str

@router.post("/query", response_model=dict)
async def query_assistant(request: AssistantQueryRequest):
    """
    Process a natural language query and return AI-powered response
    
    Args:
        request: {
            "query": "Will Delhi become hotter?",
            "user_id": 1 (optional)
        }
    
    Returns:
        {
            "status": "success",
            "query": "Will Delhi become hotter?",
            "intent": "forecast",
            "answer": "Based on projections...",
            "data": {...},
            "suggested_action": "View forecast",
            "action_url": "/forecast"
        }
    """
    try:
        from app.services.assistant_service import AssistantService
        
        service = AssistantService()
        response = await service.query_assistant(
            query=request.query,
            user_id=request.user_id
        )
        
        # Log if DatabaseService exists
        try:
            from app.services.database import DatabaseService
            db = DatabaseService()
            if request.user_id:
                db.log_system_activity(
                    user_id=request.user_id,
                    action="assistant_query",
                    details=f"Intent: {response.get('intent')}, Query: {request.query[:100]}"
                )
        except Exception as log_err:
            logger.warning(f"Could not log activity: {log_err}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in query_assistant endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intents")
async def get_available_intents():
    """Get list of available intents"""
    from app.services.intent_detector import IntentDetector
    
    return {
        "status": "success",
        "intents": list(IntentDetector.INTENTS.keys()),
        "descriptions": {
            "compare": "Compare climate data between two cities",
            "risk": "Analyze climate risks and anomalies",
            "forecast": "Get weather forecasts and predictions",
            "trend": "View historical climate trends",
            "simulate": "Simulate climate change scenarios",
            "list": "List all available cities",
            "general": "General climate information queries"
        }
    }

@router.get("/suggested-queries")
async def get_suggested_queries():
    """Get list of suggested queries for UI"""
    return {
        "status": "success",
        "suggested_queries": [
            "Will Delhi become hotter in the future?",
            "Compare temperature in Mumbai and Bangalore",
            "What cities have high climate risk?",
            "Show me historical trends for rainfall",
            "What's the forecast for the next 7 days?",
            "List all available cities",
            "How much will temperature increase by 2050?"
        ]
    }

@router.post("/explain", response_model=dict)
async def explain_intent(request: AssistantQueryRequest):
    """
    Explain what intent will be detected for a given query
    (Useful for debugging/testing)
    """
    try:
        from app.services.intent_detector import IntentDetector
        
        parsed = IntentDetector.parse_query(request.query)
        
        return {
            "status": "success",
            "query": request.query,
            "intent": parsed["intent"],
            "cities_detected": parsed["cities"],
            "parameters": parsed["parameters"]
        }
        
    except Exception as e:
        logger.error(f"Error explaining intent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
