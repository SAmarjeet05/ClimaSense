"""
Authentication Routes - Register, login, and user management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserCreate
)
from app.services import auth_service
from app.models.user import User
from datetime import timedelta

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# DEPENDENCIES
# ============================================================

def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
) -> User:
    """
    Get current authenticated user from token.
    
    This function extracts and validates the JWT token from 
    the Authorization header, then retrieves the corresponding user.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = auth_service.decode_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_service.get_user_by_email(db, email=token_data["email"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


# ============================================================
# REGISTER ENDPOINT
# ============================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Parameters:
    - name: Full name (2-255 characters)
    - email: Email address (must be valid)
    - password: Password (minimum 8 characters)
    
    Returns:
    - User object with id, name, email, role, created_at
    """
    try:
        # Create new user
        user_create = UserCreate(
            name=request.name,
            email=request.email,
            password=request.password,
            role="user"  # New users are regular users by default
        )
        
        user = auth_service.create_user(db, user_create)
        
        return user
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


# ============================================================
# LOGIN ENDPOINT
# ============================================================

@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and receive JWT access token.
    
    Parameters:
    - email: User email
    - password: User password
    
    Returns:
    - access_token: JWT token for authentication
    - token_type: Bearer token
    - user: Current user data
    """
    # Authenticate user
    user = auth_service.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


# ============================================================
# GET CURRENT USER ENDPOINT
# ============================================================

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Requires:
    - Valid JWT token in Authorization header
    
    Returns:
    - Current user data
    """
    return UserResponse.from_orm(current_user)


# ============================================================
# LOGOUT ENDPOINT
# ============================================================

@router.post("/logout")
def logout():
    """
    Logout (client-side: remove token from localStorage)
    """
    return {
        "message": "Logged out successfully",
        "detail": "Remove token from client storage"
    }


# ============================================================
# ADMIN-ONLY ENDPOINT (example)
# ============================================================

@router.get("/admin/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all users (Admin only).
    
    Requires:
    - Admin role
    """
    if not auth_service.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = db.query(User).all()
    return {"users": [UserResponse.from_orm(u) for u in users]}
