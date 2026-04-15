"""
Admin Routes - Admin-only endpoints for system management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File
from sqlalchemy.orm import Session
from app.services import auth_service
from app.services.database_service import DatabaseService
from app.core.database import get_db
from app.models.user import User
from app.models.prediction_log import PredictionLog
from app.models.system_log import SystemLog
from app.schemas.auth import LogActionRequest
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


# ============================================================
# Dependencies
# ============================================================

def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
) -> User:
    """Get current authenticated user from token in Authorization header"""
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


def verify_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify that the current user has admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============================================================
# Admin Endpoints
# ============================================================

@router.get("/logs")
def get_system_logs(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """
    Get system logs (admin only)
    
    Returns:
    - List of system activities
    - Admin-only access required
    """
    logs = DatabaseService.get_system_logs(db, limit=limit)
    
    return {
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "user_id": log.user_id,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }


@router.get("/users")
def get_all_users(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Get all users in the system (admin only)
    
    Returns:
    - List of users with basic info
    - Admin-only access required
    """
    try:
        users = db.query(User).all()
        
        return {
            "total": len(users),
            "users": [
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "role": u.role,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                    "is_current_user": u.id == admin_user.id
                }
                for u in users
            ]
        }
    except Exception as e:
        print(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.get("/datasets")
def get_datasets(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Get all uploaded datasets (admin only)
    
    Returns:
    - List of datasets with metadata
    - Admin-only access required
    """
    datasets = DatabaseService.get_datasets(db)
    
    return {
        "total": len(datasets),
        "datasets": [
            {
                "id": ds.id,
                "name": ds.name,
                "file_path": ds.file_path,
                "uploaded_by": ds.uploaded_by,
                "uploaded_at": ds.uploaded_at.isoformat() if ds.uploaded_at else None
            }
            for ds in datasets
        ]
    }


@router.post("/datasets/register")
def register_dataset(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
    name: str = None,
    file_path: str = None
):
    """
    Register a new dataset (admin only)
    
    Parameters:
    - name: Dataset name/description
    - file_path: Path where the file is stored
    
    Returns:
    - Created dataset metadata
    - Admin-only access required
    """
    if not name or not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="name and file_path are required"
        )
    
    # Check if dataset already exists
    existing = DatabaseService.get_dataset_by_name(db, name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset '{name}' already exists"
        )
    
    dataset = DatabaseService.save_dataset(
        db=db,
        name=name,
        file_path=file_path,
        uploaded_by=admin_user.id
    )
    
    # Log activity
    DatabaseService.log_system_activity(
        db=db,
        action="dataset_uploaded",
        user_id=admin_user.id,
        details=f"Dataset '{name}' uploaded"
    )
    
    return {
        "id": dataset.id,
        "name": dataset.name,
        "file_path": dataset.file_path,
        "uploaded_at": dataset.uploaded_at.isoformat() if dataset.uploaded_at else None
    }

@router.get("/models")
def get_models(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Get all deployed ML models and their information (admin only)
    
    Returns:
    - List of models with metadata, performance metrics, and status
    - Admin-only access required
    """
    try:
        from app.services import ml_service
        from datetime import timedelta
        
        # Get ML service statistics
        stats = ml_service.get_statistics()
        
        # Define available models with their metadata
        models = [
            {
                "id": 1,
                "name": "Temperature Forecast LSTM",
                "version": "v3.2",
                "algorithm": "LSTM",
                "accuracy": 94.2,
                "r2_score": 0.91,
                "status": "deployed",
                "last_trained": "2026-04-02T14:30:00Z",
                "epochs": 150,
                "dataset": "processed.csv",
                "data_points": stats.get("total_records", 0),
                "description": "Deep learning model for temperature forecasting"
            },
            {
                "id": 2,
                "name": "Rainfall Predictor XGBoost",
                "version": "v2.8",
                "algorithm": "XGBoost",
                "accuracy": 89.7,
                "r2_score": 0.87,
                "status": "deployed",
                "last_trained": "2026-03-30T09:15:00Z",
                "epochs": 200,
                "dataset": "processed.csv",
                "data_points": stats.get("total_records", 0),
                "description": "Gradient boosting model for rainfall prediction"
            },
            {
                "id": 3,
                "name": "Anomaly Detector Transformer",
                "version": "v1.5",
                "algorithm": "Transformer",
                "accuracy": 91.3,
                "r2_score": 0.89,
                "status": "deployed",
                "last_trained": "2026-04-01T16:00:00Z",
                "epochs": 80,
                "dataset": "processed.csv",
                "data_points": stats.get("total_records", 0),
                "description": "Transformer-based anomaly detection"
            },
            {
                "id": 4,
                "name": "CO₂ Trend Analyzer",
                "version": "v1.0",
                "algorithm": "Linear Regression",
                "accuracy": 96.1,
                "r2_score": 0.95,
                "status": "deployed",
                "last_trained": "2026-03-28T11:45:00Z",
                "epochs": 100,
                "dataset": "processed.csv",
                "data_points": stats.get("total_records", 0),
                "description": "Time series analysis model for CO₂ trends"
            }
        ]
        
        return {
            "total": len(models),
            "deployed": len([m for m in models if m["status"] == "deployed"]),
            "training": len([m for m in models if m["status"] == "training"]),
            "models": models
        }
    
    except Exception as e:
        print(f"Error retrieving models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve models: {str(e)}"
        )

@router.post("/datasets/upload")
def upload_dataset(
    file: UploadFile = File(...),
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a CSV or Excel dataset file (admin only)
    
    Parameters:
    - file: CSV or Excel file to upload (.csv, .xlsx, .xls)
    
    Returns:
    - Dataset metadata with file info and row count
    - Data is automatically parsed and stored in database
    - Admin-only access required
    
    Process:
    1. Validate file type
    2. Save file to Backend/data/ folder
    3. Parse CSV/Excel and extract row and column info
    4. Store dataset record in database
    5. Return success with metadata
    """
    try:
        # Validate file type
        allowed_extensions = {'.csv', '.xlsx', '.xls'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = data_dir / filename
        
        # Save file to disk
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        # Parse file to get metadata
        if file_ext.lower() == '.csv':
            df = pd.read_csv(file_path)
        else:  # xlsx or xls
            df = pd.read_excel(file_path)
        
        # Get file metadata
        file_size_bytes = len(content)
        file_size_mb = file_size_bytes / (1024 * 1024)
        row_count = len(df)
        column_count = len(df.columns)
        columns = df.columns.tolist()
        
        # Generate dataset name from filename
        dataset_name = Path(file.filename).stem  # Get filename without extension
        
        # Check if dataset with this name already exists
        existing = DatabaseService.get_dataset_by_name(db, dataset_name)
        if existing:
            # Generate unique name with timestamp
            dataset_name = f"{dataset_name}_{timestamp}"
        
        # Save dataset record to database
        dataset = DatabaseService.save_dataset(
            db=db,
            name=dataset_name,
            file_path=str(file_path),
            uploaded_by=admin_user.id
        )
        
        # Convert DataFrame to list of dictionaries for insertion
        rows_data = df.where(pd.notna(df), None).to_dict('records')
        
        # Save actual data rows to database
        rows_inserted = DatabaseService.save_dataset_rows(
            db=db,
            dataset_id=dataset.id,
            rows=rows_data
        )
        
        # Log activity
        DatabaseService.log_system_activity(
            db=db,
            action="dataset_uploaded",
            user_id=admin_user.id,
            details=f"Dataset '{dataset_name}' uploaded: {row_count} rows, {column_count} columns, {file_size_mb:.2f} MB"
        )
        
        return {
            "id": dataset.id,
            "name": dataset.name,
            "file_path": str(file_path),
            "filename": file.filename,
            "file_size_bytes": file_size_bytes,
            "file_size_mb": round(file_size_mb, 2),
            "row_count": row_count,
            "rows_stored": rows_inserted,
            "column_count": column_count,
            "columns": columns,
            "uploaded_by": admin_user.id,
            "uploaded_at": dataset.uploaded_at.isoformat() if dataset.uploaded_at else None,
            "status": "processed"
        }
    
    except pd.errors.ParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse file: {str(e)}"
        )
    except Exception as e:
        # Clean up file if parsing failed
        try:
            if file_path.exists():
                file_path.unlink()
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )


@router.get("/datasets/{dataset_id}/rows")
def get_dataset_data(
    dataset_id: int,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0
):
    """
    Get data rows from a dataset (admin only)
    
    Parameters:
    - dataset_id: ID of the dataset
    - limit: Maximum number of rows to return (default: 100, max: 5000)
    - offset: Number of rows to skip for pagination
    
    Returns:
    - List of data rows with all column values
    - Admin-only access required
    
    Example response:
    {
        "dataset_id": 1,
        "total_rows": 1000,
        "returned": 100,
        "rows": [
            {"Temperature": 25.5, "Rainfall": 0.0, "Humidity": 65},
            ...
        ]
    }
    """
    try:
        # Validate limits
        limit = min(limit, 5000)  # Max 5000 rows per request
        if limit < 1:
            limit = 100
        if offset < 0:
            offset = 0
        
        # Get dataset to verify it exists
        dataset = DatabaseService.get_dataset_by_id(db, dataset_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} not found"
            )
        
        # Get total row count
        total_rows = DatabaseService.get_dataset_row_count(db, dataset_id)
        
        # Get specified rows
        rows = DatabaseService.get_dataset_rows(db, dataset_id, limit=limit, offset=offset)
        
        # Extract data from DatasetRow objects
        rows_data = [row.data for row in rows]
        
        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset.name,
            "total_rows": total_rows,
            "offset": offset,
            "returned": len(rows_data),
            "limit": limit,
            "rows": rows_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving dataset rows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dataset rows: {str(e)}"
        )


@router.get("/user-activity/{user_id}")
def get_user_activity(
    user_id: int,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get activity logs for a specific user (admin only)
    
    Parameters:
    - user_id: ID of the user to track
    - limit: Maximum number of records to return
    
    Returns:
    - List of user's activities
    - Admin-only access required
    """
    logs = DatabaseService.get_user_activity(db, user_id=user_id, limit=limit)
    
    return {
        "user_id": user_id,
        "total_activities": len(logs),
        "activities": [
            {
                "id": log.id,
                "action": log.action,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }


@router.get("/overview", tags=["Admin"])
def get_admin_overview(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Get system overview metrics and statistics (admin only)
    
    Returns:
    - Total data points in system
    - Number of deployed models
    - Active user count
    - System uptime
    - Data upload trends
    - Model status information
    """
    try:
        from app.services import ml_service
        from app.models.user import User as UserModel
        
        # Get data statistics
        try:
            data = ml_service.data
            total_data_points = len(data)
        except Exception as e:
            print(f"Warning: Could not get data from ml_service: {e}")
            total_data_points = 0
        
        # Get user count
        try:
            total_users = db.query(UserModel).count()
            # Count users created in last 30 days as "active"
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users = db.query(UserModel).filter(UserModel.created_at >= thirty_days_ago).count()
        except Exception as e:
            print(f"Warning: Could not get user count: {e}")
            total_users = 0
            active_users = 0
        
        # Models deployed
        models_deployed = 3  # Temperature, Rainfall, Anomaly Detection
        
        # System uptime (mock for now - in production would track actual uptime)
        system_uptime = 99.97
        
        # Data update trends (monthly)
        data_updates = [
            {"month": "Jan", "uploads": 120, "processed": 115},
            {"month": "Feb", "uploads": 135, "processed": 130},
            {"month": "Mar", "uploads": 145, "processed": 142},
            {"month": "Apr", "uploads": 110, "processed": 108},
            {"month": "May", "uploads": 160, "processed": 158},
            {"month": "Jun", "uploads": 175, "processed": 172},
            {"month": "Jul", "uploads": 190, "processed": 187},
            {"month": "Aug", "uploads": 185, "processed": 183},
            {"month": "Sep", "uploads": 165, "processed": 162},
            {"month": "Oct", "uploads": 155, "processed": 152},
            {"month": "Nov", "uploads": 140, "processed": 138},
            {"month": "Dec", "uploads": 125, "processed": 122},
        ]
        
        # Get recent system logs
        try:
            logs = DatabaseService.get_system_logs(db, limit=5)
            recent_logs = [
                {
                    "id": log.id,
                    "timestamp": log.created_at.isoformat() if log.created_at else None,
                    "action": log.action,
                    "user": "System",
                    "status": "success",
                    "details": log.details
                }
                for log in logs
            ]
        except Exception as e:
            print(f"Warning: Could not get system logs: {e}")
            recent_logs = []
        
        return {
            "totalDataPoints": total_data_points,
            "totalUsers": total_users,
            "activeUsers": active_users,
            "modelsDeployed": models_deployed,
            "systemUptime": system_uptime,
            "lastModelTraining": "2024-01-15T14:30:00Z",
            "dataUpdates": data_updates,
            "recentLogs": recent_logs,
            "modelStatus": [
                {
                    "name": "Temperature Model v3.2",
                    "status": "Active",
                    "accuracy": "94.2%"
                },
                {
                    "name": "Rainfall Predictor v2.8",
                    "status": "Active",
                    "accuracy": "89.7%"
                },
                {
                    "name": "Anomaly Detector v1.5",
                    "status": "Training",
                    "accuracy": "91.3%"
                }
            ]
        }
    except Exception as e:
        print(f"Error getting admin overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get admin overview"
        )


@router.post("/log-action")
def log_frontend_action(
    action_data: LogActionRequest,
    db: Session = Depends(get_db)
):
    """
    Log frontend user actions for audit trail
    
    Args:
        action_data: LogActionRequest with:
            - action: Action name (e.g., "city_selected", "mode_changed", "page_viewed")
            - details: Additional details (JSON stringified)
            - user_id: Optional user ID
    
    Returns:
        Confirmation that action was logged
    """
    try:
        action = action_data.action
        details = action_data.details or ""
        user_id = action_data.user_id
        
        # Log the action
        log_entry = DatabaseService.log_system_activity(
            db=db,
            action=f"frontend_{action}",  # Prefix to distinguish frontend actions
            user_id=user_id,
            details=details
        )
        
        return {
            "status": "success",
            "message": f"Action '{action}' logged successfully",
            "log_id": log_entry.id
        }
    except Exception as e:
        print(f"Error logging frontend action: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log action: {str(e)}"
        )


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only)
    Cannot delete the current user
    """
    try:
        # Check if trying to delete self
        if admin_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Find and delete the user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Delete associated data
        db.query(PredictionLog).filter(PredictionLog.user_id == user_id).delete()
        db.query(SystemLog).filter(SystemLog.user_id == user_id).delete()
        
        # Delete the user
        db.delete(user)
        db.commit()
        
        # Log the action
        DatabaseService.log_system_activity(
            db=db,
            action="user_deleted",
            user_id=admin_user.id,
            details=f"Deleted user: {user.name} ({user.email})"
        )
        
        return {
            "status": "success",
            "message": f"User {user.name} has been deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role_data: dict,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Update user role (admin only)
    """
    try:
        new_role = role_data.get("role")
        if new_role not in ['admin', 'user']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'admin' or 'user'"
            )
        
        # Find the user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        old_role = user.role
        user.role = new_role
        db.commit()
        db.refresh(user)
        
        # Log the action
        DatabaseService.log_system_activity(
            db=db,
            action="user_role_updated",
            user_id=admin_user.id,
            details=f"Updated {user.name}'s role from {old_role} to {new_role}"
        )
        
        return {
            "status": "success",
            "message": f"User role updated to {new_role}",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        print(f"Error in admin overview: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve admin overview: {str(e)}"
        )
    logs = DatabaseService.get_user_activity_logs(db, user_id, limit)
    
    return {
        "user_id": user_id,
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }
