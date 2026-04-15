import sys
sys.path.insert(0, '.')
from app.services.ml_service_v2 import get_unified_annual_temperature_trends, get_unified_annual_rainfall_trends

t = get_unified_annual_temperature_trends()
r = get_unified_annual_rainfall_trends()

print(f'Temp years: {len(t["years"])} (from {t["years"][0]} to {t["years"][-1]})')
print(f'Rain years: {len(r["years"])} (from {r["years"][0]} to {r["years"][-1]})')

missing = set(r["years"]) - set(t["years"])
if missing:
    print(f'Missing temp years: {sorted(missing)}')
else:
    print('All years match!')

# Show last few entries
print("\nLast 5 temp entries:")
for i in range(-5, 0):
    print(f"  {t['years'][i]}: {t['temperatures'][i]}")

print("\nLast 5 rain entries:")
for i in range(-5, 0):
    print(f"  {r['years'][i]}: {r['rainfall'][i]}")
