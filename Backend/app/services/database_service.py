"""
Database Service - Handle prediction logging and system logs
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.prediction_log import PredictionLog
from app.models.system_log import SystemLog
from app.models.dataset import Dataset


class DatabaseService:
    """Service layer for database operations"""

    @staticmethod
    def save_prediction(
        db: Session,
        user_id: int,
        year: int,
        month: int,
        predicted_temperature: float,
        predicted_rainfall: float,
        region: str = "India"
    ) -> PredictionLog:
        """
        Save a prediction to the database
        
        Args:
            db: Database session
            user_id: ID of the user making the prediction
            year: Year for prediction
            month: Month for prediction
            predicted_temperature: Predicted temperature value
            predicted_rainfall: Predicted rainfall value
            region: Geographic region (default: "India")
            
        Returns:
            PredictionLog: Created prediction log entry
        """
        prediction = PredictionLog(
            user_id=user_id,
            year=year,
            month=month,
            region=region,
            predicted_temperature=predicted_temperature,
            predicted_rainfall=predicted_rainfall
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction

    @staticmethod
    def get_user_predictions(db: Session, user_id: int, limit: int = 100) -> list:
        """
        Retrieve all predictions made by a user
        
        Args:
            db: Database session
            user_id: ID of the user
            limit: Maximum number of records to return
            
        Returns:
            List of PredictionLog entries
        """
        return db.query(PredictionLog).filter(
            PredictionLog.user_id == user_id
        ).order_by(
            PredictionLog.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def log_system_activity(
        db: Session,
        action: str,
        user_id: int = None,
        details: str = None
    ) -> SystemLog:
        """
        Log a system activity or user action
        
        Args:
            db: Database session
            action: Action description (e.g., "prediction_made", "dataset_uploaded")
            user_id: ID of the user performing the action (optional)
            details: Additional details about the action
            
        Returns:
            SystemLog: Created log entry
        """
        log = SystemLog(
            action=action,
            user_id=user_id,
            details=details
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_system_logs(db: Session, limit: int = 100) -> list:
        """
        Retrieve recent system logs (admin access required)
        
        Args:
            db: Database session
            limit: Maximum number of records to return
            
        Returns:
            List of SystemLog entries
        """
        return db.query(SystemLog).order_by(
            SystemLog.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_user_activity_logs(db: Session, user_id: int, limit: int = 50) -> list:
        """
        Retrieve activity logs for a specific user
        
        Args:
            db: Database session
            user_id: ID of the user
            limit: Maximum number of records to return
            
        Returns:
            List of SystemLog entries for the user
        """
        return db.query(SystemLog).filter(
            SystemLog.user_id == user_id
        ).order_by(
            SystemLog.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def save_dataset(
        db: Session,
        name: str,
        file_path: str,
        uploaded_by: int = None
    ) -> Dataset:
        """
        Save dataset metadata to the database
        
        Args:
            db: Database session
            name: Dataset name/description
            file_path: Path where the dataset file is stored
            uploaded_by: ID of the admin user who uploaded it
            
        Returns:
            Dataset: Created dataset entry
        """
        dataset = Dataset(
            name=name,
            file_path=file_path,
            uploaded_by=uploaded_by
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    @staticmethod
    def get_datasets(db: Session) -> list:
        """
        Retrieve all datasets
        
        Args:
            db: Database session
            
        Returns:
            List of Dataset entries
        """
        return db.query(Dataset).order_by(
            Dataset.uploaded_at.desc()
        ).all()

    @staticmethod
    def get_dataset_by_name(db: Session, name: str) -> Dataset:
        """
        Retrieve a dataset by name
        
        Args:
            db: Database session
            name: Dataset name
            
        Returns:
            Dataset entry or None
        """
        return db.query(Dataset).filter(
            Dataset.name == name
        ).first()

    @staticmethod
    def get_dataset_by_id(db: Session, dataset_id: int) -> Dataset:
        """
        Retrieve a dataset by ID
        
        Args:
            db: Database session
            dataset_id: Dataset ID
            
        Returns:
            Dataset entry or None
        """
        return db.query(Dataset).filter(
            Dataset.id == dataset_id
        ).first()

    @staticmethod
    def save_dataset_rows(
        db: Session,
        dataset_id: int,
        rows: list
    ) -> int:
        """
        Save multiple dataset rows to the database
        
        Args:
            db: Database session
            dataset_id: ID of the dataset these rows belong to
            rows: List of row dictionaries, each row is a dict with column names as keys
            
        Returns:
            Number of rows inserted
        """
        from app.models.dataset_row import DatasetRow
        
        dataset_rows = []
        for row_index, row_data in enumerate(rows):
            dataset_row = DatasetRow(
                dataset_id=dataset_id,
                row_index=row_index,
                data=row_data  # Store as JSON
            )
            dataset_rows.append(dataset_row)
        
        db.add_all(dataset_rows)
        db.commit()
        
        return len(dataset_rows)

    @staticmethod
    def get_dataset_rows(
        db: Session,
        dataset_id: int,
        limit: int = 1000,
        offset: int = 0
    ) -> list:
        """
        Retrieve rows from a dataset
        
        Args:
            db: Database session
            dataset_id: ID of the dataset
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            
        Returns:
            List of DatasetRow objects
        """
        from app.models.dataset_row import DatasetRow
        
        return db.query(DatasetRow).filter(
            DatasetRow.dataset_id == dataset_id
        ).order_by(
            DatasetRow.row_index
        ).offset(offset).limit(limit).all()

    @staticmethod
    def get_dataset_row_count(
        db: Session,
        dataset_id: int
    ) -> int:
        """
        Get total number of rows in a dataset
        
        Args:
            db: Database session
            dataset_id: ID of the dataset
            
        Returns:
            Number of rows
        """
        from app.models.dataset_row import DatasetRow
        
        return db.query(DatasetRow).filter(
            DatasetRow.dataset_id == dataset_id
        ).count()
