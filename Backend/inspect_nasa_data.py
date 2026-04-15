import pandas as pd

# Load NASA data
nasa = pd.read_csv('data/nasa_data/nasa_india_40cities.csv')
print(f'NASA data shape: {nasa.shape}')
print(f'Date range: {nasa["date"].min()} to {nasa["date"].max()}')
print(f'Delhi records: {len(nasa[nasa["city"] == "Delhi"])}')

# Show last few Delhi records
delhi = nasa[nasa['city'] == 'Delhi'].sort_values('date').tail(10)
print(f'\nLast 10 Delhi records:')
for idx, row in delhi.iterrows():
    print(f'  {row["date"]}: Temp={row["temperature"]:.1f}C, Rain={row["rainfall"]:.1f}mm')

# Check if humidity and wind columns exist
print(f'\nColumns: {list(nasa.columns)}')
