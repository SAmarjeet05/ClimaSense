"""
System Log Model - Track system activity and user actions
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class SystemLog(Base):
    """
    System Log database model
    
    Tracks important system activities and user actions for audit trails.
    
    Fields:
    - id: Unique log ID
    - action: Description of the action (e.g., "prediction_made", "dataset_uploaded", "user_created")
    - user_id: User associated with the action (nullable for system actions)
    - details: Additional details about the action
    - created_at: Timestamp when the action occurred
    """
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(255), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    user = relationship("User", back_populates="logs")

    def __repr__(self):
        return f"<SystemLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
