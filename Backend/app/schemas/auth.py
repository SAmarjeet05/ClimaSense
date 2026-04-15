"""
Authentication Schemas - Pydantic models for auth
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    """Request schema for user registration"""
    name: str = Field(..., min_length=2, max_length=255, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")


class LoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User data response (without password)"""
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Response schema after successful authentication"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class UserCreate(BaseModel):
    """Schema for creating user (internal use)"""
    name: str
    email: str
    password: str
    role: str = "user"


class TokenData(BaseModel):
    """JWT token payload data"""
    email: Optional[str] = None
    sub: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    status_code: int = 400


class LogActionRequest(BaseModel):
    """Schema for logging frontend user actions"""
    action: str = Field(..., description="Action name (e.g., 'city_selected', 'mode_changed')", min_length=1)
    details: Optional[str] = Field(None, description="Additional details") 
    user_id: Optional[int] = Field(None, description="Optional user ID")
