"""
Process Temperature Data Pipeline
Converts .GRD temperature files from IMD folder to monthly time series

Pipeline Steps:
1. Load all .GRD files from Temperature 1951-2025 (trend) IMD folder
2. Extract grid data and convert to DataFrame
3. Map coordinates to regions and aggregate by year/month
4. Save as monthly time series

Output: data/preprocessed/temperature_final.csv
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import struct

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMP_FOLDER = DATA_DIR / "Temperature 1951-2025 (trend) IMD"
OUTPUT_DIR = DATA_DIR / "preprocessed"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("TEMPERATURE DATA PROCESSING PIPELINE")
print("=" * 70)

# ============================================================
# STEP 1: Load .GRD files from IMD folder
# ============================================================
print("\n[STEP 1] Loading temperature data from IMD folder...")

df = None
use_csv_fallback = False

if not TEMP_FOLDER.exists():
    print(f"[WARN] Temperature data folder not found at: {TEMP_FOLDER}")
    use_csv_fallback = True
else:
    # Get all .GRD files
    grd_files = sorted(list(TEMP_FOLDER.glob("*.GRD")))
    print(f"[OK] Found {len(grd_files)} GRD files in {TEMP_FOLDER.name}")
    
    if len(grd_files) > 0:
        # Load and process all GRD files
        print("\n  Loading and processing files...")
        all_data = []
        
        for idx, grd_file in enumerate(sorted(grd_files), 1):
            try:
                # Extract year from filename (e.g., Maxtemp_MaxT_2025.GRD -> 2025)
                year_str = grd_file.stem.split('_')[-1]
                try:
                    year = int(year_str)
                except:
                    year = None
                
                # Read binary GRD file
                with open(grd_file, 'rb') as f:
                    data_bytes = f.read()
                
                # GRD files are typically binary grid data. Try to interpret as float32 values
                # Assuming standard IMD format: monthly mean values (12 floats per record)
                num_values = len(data_bytes) // 4  # 4 bytes per float32
                
                values = struct.unpack(f'{num_values}f', data_bytes[:num_values * 4])
                
                # Assuming 12 months of data per file
                if num_values >= 12:
                    for month in range(1, 13):
                        value = values[month - 1] if month - 1 < len(values) else np.nan
                        all_data.append({
                            'year': year,
                            'month': month,
                            'temperature_celsius': value,
                            'region': 'AllIndia'
                        })
                
                if idx % 10 == 0 or idx == len(grd_files):
                    print(f"    Processed {idx}/{len(grd_files)} files...")
            
            except Exception as e:
                print(f"    ⚠️  Error reading {grd_file.name}: {str(e)}")
                continue
        
        # Convert to DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n✓ Loaded GRD data: {len(df)} records from {df['year'].nunique()} years")
        else:
            print("⚠️  GRD file parsing had issues, attempting CSV fallback...")
            use_csv_fallback = True

# Fallback to CSV if needed
if df is None or use_csv_fallback:
    print("  Attempting CSV fallback...")
    csv_files = [
        DATA_DIR / "temperature.csv",
        DATA_DIR / "temp_mean.csv",
        DATA_DIR / "TEMPERATURE.csv",
        DATA_DIR / "TEMP_ANNUAL_SEASONAL_MEAN.csv",
    ]
    
    csv_file = None
    for f in csv_files:
        if f.exists():
            csv_file = f
            break
    
    if csv_file:
        print(f"[OK] Loading CSV file: {csv_file.name}")
        df = pd.read_csv(csv_file)
        print(f"  Shape: {df.shape}")
    else:
        print(f"[ERROR] No temperature data found!")
        exit(1)

# ============================================================
# STEP 2: Handle different data formats
# ============================================================
print("\n[STEP 2] Processing data format...")

if 'YEAR' in df.columns:
    print("  Processing structured CSV format...")
    
    month_cols = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    month_map = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    
    available_months = [col for col in month_cols if col in df.columns]
    print(f"[OK] Found months: {available_months}")
    
    keep_cols = ['YEAR'] + available_months
    df_filtered = df[keep_cols].copy()
    
    df_long = df_filtered.melt(
        id_vars=['YEAR'],
        value_vars=available_months,
        var_name='month_str',
        value_name='temperature'
    )
    
    df_long['month'] = df_long['month_str'].map(month_map)
    df_long = df_long[['YEAR', 'month', 'temperature']]
    df_long['region'] = 'AllIndia'
    
    df_long.rename(columns={
        'YEAR': 'year',
        'temperature': 'temperature_celsius'
    }, inplace=True)
    
    df_long = df_long[['region', 'year', 'month', 'temperature_celsius']]
    print(f"[OK] Unpivoted format: {df_long.shape} records")

elif 'temperature_celsius' in df.columns:
    print("  Data already in long format")
    df_long = df[['region', 'year', 'month', 'temperature_celsius']].copy()

else:
    print(f"[ERROR] Unrecognized data format!")
    exit(1)

# ============================================================
# STEP 3: Clean data
# ============================================================
print("\n[STEP 3] Cleaning data...")

df_long['temperature_celsius'] = pd.to_numeric(df_long['temperature_celsius'], errors='coerce')
df_long['year'] = pd.to_numeric(df_long['year'], errors='coerce')
df_long['month'] = pd.to_numeric(df_long['month'], errors='coerce')

null_count = df_long.isnull().sum().sum()
print(f"[OK] Missing values: {null_count}")

df_clean = df_long.dropna(subset=['temperature_celsius', 'year', 'month'])
print(f"  After cleaning: {len(df_clean)} rows")

if len(df_clean) == 0:
    print(f"[ERROR] No valid data!")
    exit(1)

print(f"[OK] Data ranges:")
print(f"  Years: {df_clean['year'].min():.0f} - {df_clean['year'].max():.0f}")
print(f"  Temperature: {df_clean['temperature_celsius'].min():.2f}°C - {df_clean['temperature_celsius'].max():.2f}°C")

# ============================================================
# STEP 4: Final aggregation
# ============================================================
print("\n[STEP 4] Final data preparation...")

final_df = df_clean.sort_values(['region', 'year', 'month']).reset_index(drop=True)

print(f"[OK] Final dataset: {len(final_df)} records")
print(f"  Time range: {final_df['year'].min():.0f}-{final_df['year'].max():.0f}")

# ============================================================
# STEP 5: Save final dataset
# ============================================================
print("\n[STEP 5] Saving final dataset...")

output_file = OUTPUT_DIR / "temperature_final.csv"
final_df.to_csv(output_file, index=False)

print(f"[OK] Saved to: {output_file}")
print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")
print(f"  Records: {len(final_df)}")

print("\n  Sample data (first 10 rows):")
print(final_df.head(10).to_string(index=False))

print("\n  Summary Statistics:")
print(f"    Mean temperature: {final_df['temperature_celsius'].mean():.2f}°C")
print(f"    Std deviation: {final_df['temperature_celsius'].std():.2f}°C")
print(f"    Max temperature: {final_df['temperature_celsius'].max():.2f}°C")
print(f"    Min temperature: {final_df['temperature_celsius'].min():.2f}°C")

print("\n" + "=" * 70)
print("[SUCCESS] TEMPERATURE PROCESSING COMPLETE")
print("=" * 70)
print(f"\nOutput file ready for use:")
print(f"  {output_file}")
