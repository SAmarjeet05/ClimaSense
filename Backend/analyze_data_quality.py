import pandas as pd
import numpy as np

print("\n" + "="*80)
print("DATA QUALITY ANALYSIS")
print("="*80)

# ============================================================
# EXAMINE TEMPERATURE DATA
# ============================================================
print("\n📊 TEMPERATURE DATA ANALYSIS")
print("-" * 80)
df_temp = pd.read_csv('data/preprocessed/temperature_final.csv')
print(f"Shape: {df_temp.shape}")
print(f"Columns: {list(df_temp.columns)}")
print(f"\nUnique regions: {df_temp['region'].nunique()}")
print(f"Region: {df_temp['region'].unique()}")
print(f"\nTemperature value range: {df_temp['temperature_celsius'].min()} to {df_temp['temperature_celsius'].max()}")
print(f"Unique temperature values: {df_temp['temperature_celsius'].nunique()}")
print(f"\nValue counts (top 10):")
print(df_temp['temperature_celsius'].value_counts().head(10))

# Check for problematic values
bad_temps = df_temp[df_temp['temperature_celsius'] > 50]
print(f"\n⚠️  Values > 50°C: {len(bad_temps)} records")
if len(bad_temps) > 0:
    print(bad_temps.head(10))

# ============================================================
# EXAMINE RAINFALL DATA
# ============================================================
print("\n\n📊 RAINFALL DATA ANALYSIS")
print("-" * 80)
df_rain = pd.read_csv('data/preprocessed/rainfall_final.csv')
print(f"Shape: {df_rain.shape}")
print(f"\nUnique regions: {df_rain['region'].nunique()}")
print(f"Rainfall value range: {df_rain['rainfall_mm'].min()} to {df_rain['rainfall_mm'].max()}")
print(f"Unique rainfall values: {df_rain['rainfall_mm'].nunique()}")
print(f"\nRainfall statistics:")
print(df_rain['rainfall_mm'].describe())

# Check for negative or extreme values
bad_rain = df_rain[df_rain['rainfall_mm'] < 0]
print(f"\n⚠️  Negative rainfall values: {len(bad_rain)}")

print("\n" + "="*80)
