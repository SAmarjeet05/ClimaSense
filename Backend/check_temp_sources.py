import pandas as pd

print("\n=== temp_mean.csv ===")
try:
    df = pd.read_csv('data/temp_mean.csv')
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")

print("\n=== TEMP_ANNUAL_SEASONAL_MEAN.csv ===")
try:
    df = pd.read_csv('data/TEMP_ANNUAL_SEASONAL_MEAN.csv')
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")

print("\n=== Check NASA data temperature values ===")
try:
    df = pd.read_csv('data/nasa_data/nasa_india_40cities.csv')
    print(f"Columns: {list(df.columns)}")
    print(f"Temperature (T2M) stats:")
    print(df['T2M'].describe())
    print(f"\nSample rows:")
    print(df[['date', 'city', 'T2M']].head())
except Exception as e:
    print(f"Error: {e}")
