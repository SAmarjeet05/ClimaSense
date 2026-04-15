"""
Prediction Log Model - Track all user predictions
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class PredictionLog(Base):
    """
    Prediction Log database model
    
    Tracks every prediction made by users.
    
    Fields:
    - id: Unique prediction ID
    - user_id: User who made the prediction (FK)
    - year: Year for prediction
    - month: Month for prediction
    - region: Region or location
    - predicted_temperature: Predicted temperature (°C)
    - predicted_rainfall: Predicted rainfall (mm)
    - created_at: Prediction timestamp
    """
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    region = Column(String(255), default="India")
    predicted_temperature = Column(Float, nullable=False)
    predicted_rainfall = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    user = relationship("User", back_populates="predictions")

    def __repr__(self):
        return f"<PredictionLog(id={self.id}, user_id={self.user_id}, year={self.year}, month={self.month})>"
