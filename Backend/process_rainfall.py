"""
Process Rainfall Data Pipeline - Memory Efficient
Loads NetCDF files one at a time, maps to regions, aggregates incrementally.

Output: data/preprocessed/rainfall_final.csv
"""

import pandas as pd
import numpy as np
import xarray as xr
from pathlib import Path
from region_mapper import map_coordinates_to_region

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAINFALL_FOLDER = DATA_DIR / "Rainfall Data 1900-2025 (trend) IMD"
OUTPUT_DIR = DATA_DIR / "preprocessed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("RAINFALL DATA PROCESSING PIPELINE")
print("=" * 70)

# ============================================================
# STEP 1: Find NetCDF files
# ============================================================
print("\n[STEP 1] Locating rainfall data files...")

if not RAINFALL_FOLDER.exists():
    print(f"[WARN] NetCDF folder not found, using CSV fallback")
    csv_file = DATA_DIR / "rainfall.csv"
    if not csv_file.exists():
        print(f"[ERROR] No rainfall data found!")
        exit(1)
    
    use_netcdf = False
else:
    nc_files = sorted(list(RAINFALL_FOLDER.glob("*.nc")))
    if len(nc_files) > 0:
        use_netcdf = True
        print(f"[OK] Found {len(nc_files)} NetCDF files")
        print("  Samples:")
        for f in nc_files[:5]:
            print(f"    - {f.name}")
        if len(nc_files) > 5:
            print(f"    ... and {len(nc_files) - 5} more")
    else:
        print(f"[WARN] No .nc files in folder, using CSV fallback")
        use_netcdf = False

# ============================================================
# STEP 2: Load and aggregate data
# ============================================================
print("\n[STEP 2] Loading and processing data...")

all_data = []

if use_netcdf:
    print("  Processing NetCDF files...")
    for idx, nc_file in enumerate(nc_files, 1):
        try:
            year_str = nc_file.stem.split('_')[1].replace('ind', '')
            year = int(year_str) if year_str.isdigit() else None
            
            ds = xr.open_dataset(nc_file)
            df_temp = ds.to_dataframe().reset_index()
            ds.close()
            
            # Find columns
            lat_col = next((c for c in df_temp.columns if 'lat' in c.lower()), None)
            lon_col = next((c for c in df_temp.columns if 'lon' in c.lower()), None)
            data_col = next((c for c in df_temp.columns if 'rain' in c.lower() or 'precip' in c.lower()), None)
            
            if lat_col and lon_col and data_col and year:
                df_temp['region'] = df_temp.apply(
                    lambda r: map_coordinates_to_region(r[lat_col], r[lon_col]), axis=1
                )
                df_temp['rainfall'] = pd.to_numeric(df_temp[data_col], errors='coerce')
                
                if 'time' in df_temp.columns:
                    df_temp['month'] = pd.to_datetime(df_temp['time'], errors='coerce').dt.month
                else:
                    df_temp['month'] = (df_temp.groupby([lat_col, lon_col]).cumcount() % 12) + 1
                
                df_temp = df_temp[df_temp['region'] != 'UNKNOWN'].dropna(subset=['rainfall'])
                
                if len(df_temp) > 0:
                    agg = df_temp.groupby(['region', 'month']).agg({'rainfall': 'mean'}).reset_index()
                    agg['year'] = year
                    agg = agg[['region', 'year', 'month', 'rainfall']]
                    all_data.extend(agg.to_dict('records'))
            
            if idx % 25 == 0:
                print(f"    Processed {idx}/{len(nc_files)}...")
        
        except Exception as e:
            print(f"    [WARN] Error {idx}: {str(e)[:40]}")
            continue
else:
    print("  Processing CSV...")
    csv_file = DATA_DIR / "rainfall.csv"
    df_csv = pd.read_csv(csv_file)
    
    month_cols = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    month_map = {col: i + 1 for i, col in enumerate(month_cols)}
    
    for _, row in df_csv.iterrows():
        region = row.get('SUBDIVISION', 'AllIndia')
        year = row.get('YEAR')
        for month_str, month_num in month_map.items():
            if month_str in df_csv.columns and month_str in row.index:
                val = row[month_str]
                if pd.notna(val) and val != 'NA':
                    try:
                        all_data.append({
                            'region': region,
                            'year': year,
                            'month': month_num,
                            'rainfall': float(val)
                        })
                    except:
                        pass

if all_data:
    aggregated_df = pd.DataFrame(all_data)
    aggregated_df.rename(columns={'rainfall': 'rainfall_mm'}, inplace=True)
    print(f"[OK] Loaded {len(aggregated_df)} records")
else:
    print("[ERROR] No data loaded!")
    exit(1)

# ============================================================
# STEP 3: Clean and finalize
# ============================================================
print("\n[STEP 3] Cleaning data...")

aggregated_df = aggregated_df.dropna(subset=['rainfall_mm'])
aggregated_df = aggregated_df.sort_values(['region', 'year', 'month']).reset_index(drop=True)

print(f"[OK] Final dataset: {len(aggregated_df)} records")
print(f"  Regions: {aggregated_df['region'].nunique()}")
print(f"  Years: {aggregated_df['year'].min():.0f}-{aggregated_df['year'].max():.0f}")

# ============================================================
# STEP 4: Save
# ============================================================
print("\n[STEP 4] Saving dataset...")

output_file = OUTPUT_DIR / "rainfall_final.csv"
aggregated_df.to_csv(output_file, index=False)

print(f"[OK] Saved to: {output_file}")
print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")
print(f"  Records: {len(aggregated_df)}")
print("\n  Sample (first 10 rows):")
print(aggregated_df.head(10).to_string(index=False))

print("\n" + "=" * 70)
print("[SUCCESS] RAINFALL PROCESSING COMPLETE")
print("=" * 70)
