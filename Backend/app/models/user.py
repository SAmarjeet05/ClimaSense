"""
User Model - SQLAlchemy ORM model
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """
    User database model
    
    Fields:
    - id: Unique identifier
    - name: User's full name
    - email: Unique email address
    - password: Hashed password
    - role: User role (user/admin)
    - created_at: Account creation timestamp
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # "user" or "admin"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    predictions = relationship("PredictionLog", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("SystemLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
