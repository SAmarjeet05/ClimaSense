"""
Dataset Model - Store uploaded dataset information
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Dataset(Base):
    """
    Dataset database model
    
    Tracks uploaded datasets and their file locations.
    
    Fields:
    - id: Unique dataset ID
    - name: Name/description of the dataset
    - file_path: Path where the file is stored
    - uploaded_by: Admin user ID who uploaded it
    - uploaded_at: Timestamp when uploaded
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    file_path = Column(String(512), nullable=False, unique=True)
    uploaded_by = Column(Integer, nullable=True)  # Admin user ID
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name})>"
