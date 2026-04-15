import pandas as pd

df_temp = pd.read_csv('data/preprocessed/temperature_final.csv')
df_rain = pd.read_csv('data/preprocessed/rainfall_final.csv')

print('TEMPERATURE DATA RANGE:')
print(f'Years: {df_temp["year"].min()} - {df_temp["year"].max()}')
print(f'Unique regions: {df_temp["region"].unique().tolist()}')

print('\nRAINFALL DATA RANGE:')
print(f'Years: {df_rain["year"].min()} - {df_rain["year"].max()}')

max_year_rain = df_rain['year'].max()
print(f'\nSample rainfall data (year {max_year_rain}):')
print(df_rain[df_rain['year'] == max_year_rain].head(10))

max_year_temp = df_temp['year'].max()
print(f'\nSample temperature data (year {max_year_temp}):')
print(df_temp[df_temp['year'] == max_year_temp].head(10))
