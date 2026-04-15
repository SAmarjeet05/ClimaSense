"""
ML Service Module
Handles all machine learning operations and data access
"""
import joblib
import pandas as pd
import os
from typing import List, Dict

# Get paths relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

print("Loading ML models...")
temp_model = joblib.load(os.path.join(MODELS_DIR, "temp_model.pkl"))
rain_model = joblib.load(os.path.join(MODELS_DIR, "rain_model.pkl"))

try:
    feature_scaler = joblib.load(os.path.join(MODELS_DIR, "feature_scaler.pkl"))
except Exception as e:
    feature_scaler = None
    print(f"Warning: feature_scaler.pkl not found - {e}")

print("Loading dataset...")
data = pd.read_csv(os.path.join(DATA_DIR, "processed.csv"))
print(f"✅ ML Service initialized with {len(data)} records")


def get_trends() -> Dict:
    """
    Get historical trends from processed dataset.
    
    Returns:
        Dictionary with years, months, regions, temperatures, and rainfalls
    """
    return {
        "years": data["YEAR"].tolist(),
        "months": data["MONTH"].tolist(),
        "regions": data["REGION"].tolist(),
        "temperatures": data["TEMPERATURE"].tolist(),
        "rainfalls": data["RAINFALL"].tolist()
    }


def get_statistics() -> Dict:
    """
    Get statistical summary of the dataset.
    
    Returns:
        Dictionary with statistics for temperature and rainfall
    """
    return {
        "total_records": len(data),
        "years_range": {
            "min": int(data["YEAR"].min()),
            "max": int(data["YEAR"].max())
        },
        "regions": data["REGION"].unique().tolist(),
        "temperature": {
            "mean": float(data["TEMPERATURE"].mean()),
            "std": float(data["TEMPERATURE"].std()),
            "min": float(data["TEMPERATURE"].min()),
            "max": float(data["TEMPERATURE"].max())
        },
        "rainfall": {
            "mean": float(data["RAINFALL"].mean()),
            "std": float(data["RAINFALL"].std()),
            "min": float(data["RAINFALL"].min()),
            "max": float(data["RAINFALL"].max())
        }
    }


def predict_temperature(year: int, month: int, region_code: float) -> float:
    """
    Predict temperature for given parameters.
    
    Args:
        year: Year for prediction
        month: Month for prediction (1-12)
        region_code: Region code
        
    Returns:
        Predicted temperature as float
    """
    year_norm = year / 2024.0
    month_norm = month / 12.0
    
    features = [[year_norm, month_norm, region_code]]
    pred = float(temp_model.predict(features)[0])
    
    # Post-processing: keep within realistic bounds
    pred = max(-10, min(50, pred))
    return pred


def predict_rainfall(year: int, month: int, region_code: float) -> float:
    """
    Predict rainfall for given parameters.
    
    Args:
        year: Year for prediction
        month: Month for prediction (1-12)
        region_code: Region code
        
    Returns:
        Predicted rainfall as float (non-negative)
    """
    year_norm = year / 2024.0
    month_norm = month / 12.0
    
    features = [[year_norm, month_norm, region_code]]
    pred = float(rain_model.predict(features)[0])
    
    # Post-processing: rainfall cannot be negative
    pred = max(0, pred)
    return pred


def get_data_records(limit: int = 100) -> List[Dict]:
    """
    Get processed data records with optional limit.
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of dictionaries containing data
    """
    return data.head(limit).to_dict('records')


def filter_data(year: int = None, month: int = None, region: str = None) -> List[Dict]:
    """
    Filter dataset by year, month, or region.
    
    Args:
        year: Optional year filter
        month: Optional month filter
        region: Optional region filter
        
    Returns:
        List of filtered records
    """
    filtered_df = data.copy()
    
    if year is not None:
        filtered_df = filtered_df[filtered_df["YEAR"] == year]
    if month is not None:
        filtered_df = filtered_df[filtered_df["MONTH"] == month]
    if region is not None:
        filtered_df = filtered_df[filtered_df["REGION"] == region]
    
    return filtered_df.to_dict('records')


def get_anomalies(limit: int = 100, region: str = None) -> Dict:
    """
    Get detected anomalies from the dataset.
    
    Args:
        limit: Maximum number of anomalies to return
        region: Optional region filter
        
    Returns:
        Dictionary with anomaly statistics and records
    """
    anomaly_df = data[data['ANOMALY'] == 1].copy()
    
    if region is not None:
        anomaly_df = anomaly_df[anomaly_df['REGION'] == region]
    
    # Calculate severity based on deviation from mean
    mean_temp = data['TEMPERATURE'].mean()
    mean_rain = data['RAINFALL'].mean()
    
    def calculate_severity(temp, rain):
        temp_dev = abs(temp - mean_temp) / mean_temp * 100 if mean_temp != 0 else 0
        rain_dev = abs(rain - mean_rain) / mean_rain * 100 if mean_rain != 0 else 0
        max_dev = max(temp_dev, rain_dev)
        
        if max_dev > 30:
            return "critical"
        elif max_dev > 20:
            return "high"
        elif max_dev > 10:
            return "medium"
        else:
            return "low"
    
    # Prepare anomaly records
    anomalies = []
    for idx, row in anomaly_df.head(limit).iterrows():
        severity = calculate_severity(row['TEMPERATURE'], row['RAINFALL'])
        temp_dev = abs(row['TEMPERATURE'] - mean_temp)
        rain_dev = abs(row['RAINFALL'] - mean_rain)
        
        anomalies.append({
            "id": idx,
            "date": f"{int(row['YEAR'])}-{int(row['MONTH']):02d}",
            "year": int(row['YEAR']),
            "month": int(row['MONTH']),
            "region": row['REGION'],
            "temperature": float(row['TEMPERATURE']),
            "rainfall": float(row['RAINFALL']),
            "temp_deviation": round(temp_dev, 2),
            "rain_deviation": round(rain_dev, 2),
            "severity": severity,
            "type": "Temperature Extremity" if temp_dev > rain_dev else "Rainfall Anomaly",
            "description": f"{'Temperature' if temp_dev > rain_dev else 'Rainfall'} deviation of {max(temp_dev, rain_dev):.1f} from mean"
        })
    
    return {
        "total_anomalies": len(anomaly_df),
        "region_filter": region,
        "returned": len(anomalies),
        "anomalies": anomalies,
        "statistics": {
            "mean_temperature": round(mean_temp, 2),
            "mean_rainfall": round(mean_rain, 2),
            "total_data_points": len(data)
        }
    }


def get_api_info() -> Dict:
    """
    Get information about the API, models, and dataset.
    
    Returns:
        Dictionary with API information
    """
    return {
        "api_version": "2.0.0",
        "phase": "Phase 2 - Clean Architecture",
        "models_available": {
            "temperature_prediction": "RandomForestRegressor",
            "rainfall_prediction": "RandomForestRegressor"
        },
        "dataset_info": {
            "total_records": len(data),
            "columns": data.columns.tolist(),
            "date_range": f"{int(data['YEAR'].min())} - {int(data['YEAR'].max())}",
            "regions": data["REGION"].unique().tolist()
        }
    }
