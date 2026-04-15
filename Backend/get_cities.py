import pandas as pd

df = pd.read_csv('data/nasa_data/nasa_india_40cities.csv')

# Get unique cities with their coordinates
cities_coords = df[['city', 'latitude', 'longitude']].drop_duplicates().sort_values('city')

print("const availableCities = [")
for idx, row in cities_coords.iterrows():
    city = row['city']
    lat = round(row['latitude'], 2)
    lon = round(row['longitude'], 2)
    print(f"  {{ name: '{city}', lat: {lat}, lon: {lon} }},")
print("];")
print()
print(f"// Total cities: {len(cities_coords)}")
