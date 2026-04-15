from app.services import ml_service_v2
from datetime import datetime

# Check what years get_forecast_data returns
forecast_result = ml_service_v2.get_forecast_data(
    city="Mumbai",
    month=6,
    day=15,
    latitude=19.0,
    longitude=72.9,
    years_ahead=5
)

print(f"Today: {datetime.now().year}")
print(f"\nForecast Results (get_forecast_data):")
for i, pred in enumerate(forecast_result['predicted']):
    print(f"  [{i}] Year {pred['year']}: {pred['temperature']:.2f}°C, {pred['rainfall']:.2f}mm")

# Now test single predictions
print(f"\nSingle Predictions (predict_statistical_*):")
for test_year in [2026, 2027, 2028]:
    temp = ml_service_v2.predict_statistical_temperature(
        year=test_year,
        month=6,
        day=15,
        city="Mumbai",
        latitude=19.0,
        longitude=72.9
    )
    rain = ml_service_v2.predict_statistical_rainfall(
        year=test_year,
        month=6,
        day=15,
        city="Mumbai",
        latitude=19.0,
        longitude=72.9
    )
    print(f"  Year {test_year}: {temp}°C, {rain}mm")
