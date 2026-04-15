"""
Dataset Row Model - Store actual data from uploaded datasets
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class DatasetRow(Base):
    """
    DatasetRow database model
    
    Stores the actual data rows from uploaded CSV/Excel files.
    Each row is stored as JSON to support flexible column structures.
    
    Fields:
    - id: Unique row ID
    - dataset_id: Foreign key to Dataset
    - row_index: Which row number in the original file
    - data: JSON object with all column values for this row
    - created_at: When this row was inserted
    """
    __tablename__ = "dataset_rows"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    row_index = Column(Integer, nullable=False)  # 0-based index in original file
    data = Column(JSON, nullable=False)  # {"Temperature": 25.5, "Rainfall": 0.0, ...}
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<DatasetRow(id={self.id}, dataset_id={self.dataset_id}, row_index={self.row_index})>"
