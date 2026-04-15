import pandas as pd

print("\n=== TEMPERATURE FINAL ===")
df_temp = pd.read_csv('data/preprocessed/temperature_final.csv')
print(f"Shape: {df_temp.shape}")
print(f"Columns: {list(df_temp.columns)}")
print(f"Years: {df_temp['year'].min()} to {df_temp['year'].max()}")
print(f"Unique years: {df_temp['year'].nunique()}")
print(f"First 10 rows:\n{df_temp.head(10)}")

print("\n=== RAINFALL FINAL ===")
df_rain = pd.read_csv('data/preprocessed/rainfall_final.csv')
print(f"Shape: {df_rain.shape}")
print(f"Columns: {list(df_rain.columns)}")
print(f"Years: {df_rain['year'].min()} to {df_rain['year'].max()}")
print(f"Unique years: {df_rain['year'].nunique()}")
print(f"First 5 rows:\n{df_rain.head()}")
