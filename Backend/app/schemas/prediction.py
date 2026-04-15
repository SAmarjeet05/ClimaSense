"""
Pydantic Schemas - Request/Response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class PredictionInput(BaseModel):
    """Input schema for single prediction (simplified - backend auto-genera features)"""
    year: int = Field(..., ge=1900, le=2100, description="Year for prediction (1900-2100)")
    month: int = Field(..., ge=1, le=12, description="Month for prediction (1-12)")
    day: int = Field(default=15, ge=1, le=31, description="Day of month (optional, default: 15)")
    city: str = Field(..., description="City name for prediction")
    latitude: float = Field(default=23.0, description="Latitude coordinate (optional)")
    longitude: float = Field(default=82.0, description="Longitude coordinate (optional)")


class NowcastInput(BaseModel):
    """Input schema for next-day nowcast (short-term ML prediction with real lag data)"""
    city: str = Field(..., description="City name for prediction")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    # Last 7 days of actual temperature data (Celsius)
    temp_lag1: float = Field(..., description="Temperature lag 1 day (most recent)")
    temp_lag3: float = Field(..., description="Temperature lag 3 days")
    temp_lag7: float = Field(..., description="Temperature lag 7 days")
    # Last 7 days of actual rainfall data (mm)
    rain_lag1: float = Field(..., description="Rainfall lag 1 day (most recent)")
    rain_lag3: float = Field(..., description="Rainfall lag 3 days")
    rain_lag7: float = Field(..., description="Rainfall lag 7 days")


class PredictionOutput(BaseModel):
    """Output schema for predictions (v2 production models)"""
    year: int
    month: int
    day: int
    city: str
    temperature_celsius: float = Field(description="Predicted temperature in Celsius")
    rainfall_mm: float = Field(description="Predicted rainfall in mm")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Model confidence (0-1 scale)")


class NowcastOutput(BaseModel):
    """Output schema for nowcast (next-day ML prediction)"""
    city: str
    prediction_date: str = Field(description="Date of prediction (next day)")
    temperature_celsius: float = Field(description="Next-day temperature prediction")
    rainfall_mm: float = Field(description="Next-day rainfall prediction")
    confidence: float = Field(default=0.80, ge=0.0, le=1.0, description="Model confidence")


class TrendsResponse(BaseModel):
    """Response schema for trends endpoint"""
    years: List[int]
    months: List[int]
    regions: List[str]
    temperatures: List[float]
    rainfalls: List[float]


class DataRecord(BaseModel):
    """Single climate data record"""
    YEAR: int
    MONTH: int
    REGION: str
    TEMPERATURE: float
    RAINFALL: float
    ANOMALY: Optional[int] = None


class DataResponse(BaseModel):
    """Response schema for data endpoint"""
    total_records: int
    returned: int
    data: List[DataRecord]


class FilterResponse(BaseModel):
    """Response schema for filter endpoint"""
    filters_applied: dict
    total_found: int
    data: List[DataRecord]


class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str
    models_loaded: bool
    data_records: int


class StatsResponse(BaseModel):
    """Response schema for statistics"""
    total_records: int
    years_range: dict
    regions: List[str]
    temperature: dict
    rainfall: dict


class BatchPredictionRequest(BaseModel):
    """Request schema for batch predictions"""
    predictions: List[PredictionInput]


class BatchPredictionResponse(BaseModel):
    """Response schema for batch predictions"""
    predictions: List[PredictionOutput]


class SimulationInput(BaseModel):
    """Input schema for climate simulation (what-if analysis)"""
    year: int = Field(..., ge=1900, le=2100, description="Year for prediction")
    month: int = Field(..., ge=1, le=12, description="Month for prediction")
    day: int = Field(default=15, ge=1, le=31, description="Day of month")
    city: str = Field(..., description="City name for simulation")
    temp_delta: float = Field(default=0, ge=-10, le=10, description="Temperature change in °C (-10 to +10)")
    rain_delta: float = Field(default=0, ge=-100, le=100, description="Rainfall change in % (-100 to +100)")


class SimulationOutput(BaseModel):
    """Output schema for climate simulation results"""
    # Baseline (original prediction)
    baseline_temperature: float = Field(description="Baseline temperature prediction (°C)")
    baseline_rainfall: float = Field(description="Baseline rainfall prediction (mm)")
    baseline_risk: int = Field(description="Baseline risk score (0-100)")
    
    # Simulated (with changes applied)
    simulated_temperature: float = Field(description="Temperature after simulation (°C)")
    simulated_rainfall: float = Field(description="Rainfall after simulation (mm)")
    simulated_risk: int = Field(description="Risk score after simulation (0-100)")
    
    # Changes
    temperature_change: float = Field(description="Temperature change from baseline (°C)")
    rainfall_change: float = Field(description="Rainfall change from baseline (%)")
    risk_change: int = Field(description="Risk score change from baseline")
    
    # Metadata
    city: str
    year: int
    month: int
    day: int
    simulation_params: dict = Field(description="Applied simulation parameters")
    insight: str = Field(description="AI-generated insight about the simulation")


class TrendDataPoint(BaseModel):
    """Single data point in a trend"""
    year: int
    value: float


class TemperatureTrendsResponse(BaseModel):
    """Response schema for temperature trends"""
    trend_type: str = Field(default="annual", description="annual or statewise")
    unit: str = Field(default="°C", description="Temperature unit")
    data: List[TrendDataPoint]
    record_count: int


class RainfallTrendsResponse(BaseModel):
    """Response schema for rainfall trends"""
    trend_type: str = Field(default="annual", description="annual or statewise")
    unit: str = Field(default="mm", description="Rainfall unit")
    data: List[TrendDataPoint]
    record_count: int


class StateWiseTrendsResponse(BaseModel):
    """Response schema for statewise trends"""
    region: str
    years: List[int]
    values: List[float]
    count: int
