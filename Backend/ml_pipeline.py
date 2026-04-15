import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

import warnings
warnings.filterwarnings('ignore')

# Constants
MONTHS_MAPPING = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4,
    'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
    'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}

def load_data(data_dir: str):
    """Loads all required datasets using pandas."""
    print("Loading datasets...")
    try:
        rainfall_df = pd.read_csv(os.path.join(data_dir, 'rainfall.csv'))
        temp_df = pd.read_csv(os.path.join(data_dir, 'temp_mean.csv'))
        # daily_rainfall_df = pd.read_csv(os.path.join(data_dir, 'daily_rainfall.csv')) # Could be used if required
        
        return rainfall_df, temp_df
    except Exception as e:
        print(f"Error loading datasets: {e}")
        return None, None

def preprocess_data(rainfall_df: pd.DataFrame, temp_df: pd.DataFrame):
    """
    Handles missing values, converts from wide to long format, 
    standardizes column names and data types.
    """
    print("Preprocessing datasets...")

    # Define columns to keep for monthly melting
    months_cols = list(MONTHS_MAPPING.keys())

    # 1. Preprocess Rainfall Data
    # Convert month columns to numeric, coercing errors to NaN
    for col in months_cols:
        rainfall_df[col] = pd.to_numeric(rainfall_df[col], errors='coerce')

    # Fill missing values
    rainfall_df = rainfall_df.fillna(rainfall_df.select_dtypes(include='number').mean())
    
    # Melt from wide to long
    rain_long = pd.melt(
        rainfall_df, 
        id_vars=['SUBDIVISION', 'YEAR'], 
        value_vars=months_cols, 
        var_name='MONTH_NAME', 
        value_name='RAINFALL'
    )
    
    # Standardize names and mapping
    rain_long.rename(columns={'SUBDIVISION': 'REGION'}, inplace=True)
    rain_long['MONTH'] = rain_long['MONTH_NAME'].map(MONTHS_MAPPING)
    rain_long.drop(columns=['MONTH_NAME'], inplace=True)

    # 2. Preprocess Temperature Data
    # Convert month columns to numeric, coercing errors to NaN
    for col in months_cols:
        temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce')

    # Fill missing values
    temp_df = temp_df.fillna(temp_df.select_dtypes(include='number').mean())
    
    # Melt from wide to long
    temp_long = pd.melt(
        temp_df, 
        id_vars=['YEAR'], 
        value_vars=months_cols, 
        var_name='MONTH_NAME', 
        value_name='TEMPERATURE'
    )
    
    # Mapping
    temp_long['MONTH'] = temp_long['MONTH_NAME'].map(MONTHS_MAPPING)
    temp_long.drop(columns=['MONTH_NAME'], inplace=True)
    
    res = {
        'rain': rain_long,
        'temp': temp_long
    }
    return res

def merge_data(rain_long: pd.DataFrame, temp_long: pd.DataFrame):
    """
    Merges rainfall and temperature datasets, handles granularity mismatches,
    adds REGION consistently.
    """
    print("Merging datasets...")
    
    # Since temperature data is country-level (no region), we merge on YEAR and MONTH 
    # to broadcast the temperature to all regions for that specific month & year.
    merged_df = pd.merge(rain_long, temp_long, on=['YEAR', 'MONTH'], how='left')
    
    # Handle regions that might be missing
    merged_df['REGION'] = merged_df['REGION'].fillna("India")
    
    # If there are any residual missing temperatures, fill with the monthly mean
    merged_df['TEMPERATURE'] = merged_df.groupby('MONTH')['TEMPERATURE'].transform(lambda x: x.fillna(x.mean()))
    merged_df['RAINFALL'] = merged_df.groupby('MONTH')['RAINFALL'].transform(lambda x: x.fillna(x.mean()))

    # Ensure no nulls
    merged_df.dropna(inplace=True)
    
    # Ensure consistent data types
    merged_df['YEAR'] = merged_df['YEAR'].astype(int)
    merged_df['MONTH'] = merged_df['MONTH'].astype(int)
    merged_df['TEMPERATURE'] = merged_df['TEMPERATURE'].astype(float)
    merged_df['RAINFALL'] = merged_df['RAINFALL'].astype(float)
    
    # Sort for sequential rolling features
    merged_df.sort_values(by=['REGION', 'YEAR', 'MONTH'], inplace=True)
    merged_df.reset_index(drop=True, inplace=True)

    return merged_df

def feature_engineering(df: pd.DataFrame):
    """
    Creates rolling averages and time-based features.
    Normalizes/scales the features cleanly.
    Returns both engineered data and the scaler for later use.
    """
    print("Performing feature engineering...")
    
    df_feat = df.copy()

    # Time-based features
    # (Using YEAR and MONTH as continuous values can act as trend features)
    
    # Rolling averages grouped by region over the last 3 time steps
    df_feat['RAIN_ROLLING_3'] = df_feat.groupby('REGION')['RAINFALL'].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
    df_feat['TEMP_ROLLING_3'] = df_feat.groupby('REGION')['TEMPERATURE'].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
    
    # One-hot encode the REGION just for model inputs if needed, or use label encoding
    df_feat['REGION_CODE'] = df_feat['REGION'].astype('category').cat.codes
    
    # Scaling the main continuous variables
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df_feat[['YEAR', 'MONTH', 'RAIN_ROLLING_3', 'TEMP_ROLLING_3', 'REGION_CODE']])
    
    scal_df = pd.DataFrame(scaled_features, columns=['YEAR_SCALED', 'MONTH_SCALED', 'RAIN_ROLL_SCALED', 'TEMP_ROLL_SCALED', 'REGION_SCALED'])
    df_feat = pd.concat([df_feat, scal_df], axis=1)

    return df_feat, scaler

def train_models(df: pd.DataFrame):
    """
    Trains Temp prediction, Rainfall prediction, and Anomaly detection models.
    Evaluates and prints performance metrics.
    """
    print("Training models...")
    models = {}

    # Define common features for regression
    X = df[['YEAR_SCALED', 'MONTH_SCALED', 'REGION_SCALED']]
    
    # 1. Temperature Prediction Model (Random Forest)
    print("-> Training Temperature Prediction Model...")
    y_temp = df['TEMPERATURE']
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(X, y_temp, test_size=0.2, random_state=42)
    
    temp_model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    temp_model.fit(X_train_t, y_train_t)
    temp_preds = temp_model.predict(X_test_t)
    
    print(f"   Temperature Model R²: {r2_score(y_test_t, temp_preds):.4f}")
    print(f"   Temperature Model MAE: {mean_absolute_error(y_test_t, temp_preds):.4f}")
    models['temp_model'] = temp_model

    # 2. Rainfall Prediction Model (Linear Regression / Random Forest)
    print("-> Training Rainfall Prediction Model...")
    y_rain = df['RAINFALL']
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X, y_rain, test_size=0.2, random_state=42)
    
    rain_model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    rain_model.fit(X_train_r, y_train_r)
    rain_preds = rain_model.predict(X_test_r)
    
    print(f"   Rainfall Model R²: {r2_score(y_test_r, rain_preds):.4f}")
    print(f"   Rainfall Model MAE: {mean_absolute_error(y_test_r, rain_preds):.4f}")
    models['rain_model'] = rain_model

    # 3. Anomaly Detection Model (Isolation Forest)
    # Using raw YEAR, MONTH, TEMPERATURE, RAINFALL to find anomalies
    print("-> Training Anomaly Detection Model...")
    anomaly_features = df[['TEMPERATURE', 'RAINFALL', 'RAIN_ROLLING_3', 'TEMP_ROLLING_3']]
    
    iso_forest = IsolationForest(contamination=0.01, random_state=42, n_jobs=-1)
    iso_forest.fit(anomaly_features)
    
    # Predict anomalies (-1 for anomaly, 1 for normal)
    df['ANOMALY'] = iso_forest.predict(anomaly_features)
    
    detected = df[df['ANOMALY'] == -1]
    print(f"   Detected {len(detected)} anomalies out of {len(df)} records (1% contamination set).")
    
    models['anomaly_model'] = iso_forest
    
    # Print Sample Outputs
    print("\n--- Sample Predictions (Rainfall) ---")
    sample_X = X_test_r.head(5)
    sample_actual = y_test_r.head(5).values
    sample_preds = rain_model.predict(sample_X)
    for i in range(5):
        print(f"Actual: {sample_actual[i]:.2f} mm | Predicted: {sample_preds[i]:.2f} mm")

    print("\n--- Sample Anomalies Detected ---")
    print(detected[['YEAR', 'MONTH', 'REGION', 'TEMPERATURE', 'RAINFALL']].head(5).to_string(index=False))

    return models

def save_models(models: dict, out_dir: str):
    """Saves all trained models using joblib."""
    print(f"\nSaving models to {out_dir}...")
    os.makedirs(out_dir, exist_ok=True)
    
    for model_name, model in models.items():
        save_path = os.path.join(out_dir, f"{model_name}.pkl")
        joblib.dump(model, save_path)
        print(f"Saved {model_name}.pkl")

def save_processed_data(df: pd.DataFrame, out_path: str):
    """Saves processed data for frontend and API usage."""
    print(f"\nSaving processed data to {out_path}...")
    # Select and rename columns for the API
    api_df = df[['YEAR', 'MONTH', 'REGION', 'TEMPERATURE', 'RAINFALL', 'ANOMALY']].copy()
    api_df.to_csv(out_path, index=False)
    print(f"Saved processed.csv ({len(api_df)} records)")

def main():
    print("=========================================")
    print("Climate Change Data Analysis Pipeline")
    print("=========================================")
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    MODELS_DIR = os.path.join(BASE_DIR, 'models')

    # 1. Load Data
    rainfall_df, temp_df = load_data(DATA_DIR)
    if rainfall_df is None or temp_df is None:
        print("Pipeline aborted due to data loading failure.")
        return

    # 2. Preprocess Data
    data_dict = preprocess_data(rainfall_df, temp_df)

    # 3. Merge Data
    merged_df = merge_data(data_dict['rain'], data_dict['temp'])

    # 4. Feature Engineering
    engineered_df, feature_scaler = feature_engineering(merged_df)

    # 5. Train and Evaluate Models
    trained_models = train_models(engineered_df)

    # 6. Save Models
    save_models(trained_models, MODELS_DIR)
    
    # Save Feature Scaler
    scaler_path = os.path.join(MODELS_DIR, 'feature_scaler.pkl')
    joblib.dump(feature_scaler, scaler_path)
    print(f"Saved feature_scaler.pkl")
    
    # 7. Save Processed Data for API
    processed_data_path = os.path.join(BASE_DIR, 'data', 'processed.csv')
    save_processed_data(engineered_df, processed_data_path)
    
    print("=========================================")
    print("Pipeline Execution Completed Successfully.")
    print("=========================================")

if __name__ == "__main__":
    main()
