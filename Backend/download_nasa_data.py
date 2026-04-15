"""
NASA POWER API Data Download Script
Downloads climate data for 40 Indian cities (1981-2025)

Parameters downloaded:
- T2M: Temperature at 2m (°C)
- PRECTOTCORR: Total corrected precipitation (mm/day)
- QV2M: Specific humidity at 2m (g/kg)
- WS2M: Wind speed at 2m (m/s)
- ALLSKY_SFC_SW_DWN: All sky insolation incident on surface (MJ/m²/day)

Output: data/nasa_data/nasa_india_40cities.csv
Expected: ~40 cities × ~45 years × 365 days ≈ 657,000 rows
"""

import requests
import pandas as pd
import time
from pathlib import Path
from datetime import datetime

# ============================================================
# COORDINATES OF 40 INDIAN CITIES
# ============================================================
cities = {
    "Delhi": (28.6, 77.2),
    "Noida": (28.53, 77.39),
    "Greater Noida": (28.47, 77.50),
    "Ghaziabad": (28.67, 77.45),
    "Lucknow": (26.85, 80.95),
    "Kanpur": (26.44, 80.33),
    "Varanasi": (25.32, 82.97),
    "Agra": (27.18, 78.01),
    "Meerut": (28.98, 77.70),
    "Prayagraj": (25.45, 81.84),
    "Chandigarh": (30.73, 76.78),
    "Dehradun": (30.32, 78.03),
    "Srinagar": (34.08, 74.79),

    "Mumbai": (19.07, 72.87),
    "Pune": (18.52, 73.85),
    "Ahmedabad": (23.02, 72.57),
    "Surat": (21.17, 72.83),
    "Jaipur": (26.91, 75.78),
    "Jodhpur": (26.24, 73.02),
    "Udaipur": (24.58, 73.68),

    "Bangalore": (12.97, 77.59),
    "Chennai": (13.08, 80.27),
    "Hyderabad": (17.38, 78.48),
    "Kochi": (9.93, 76.26),
    "Trivandrum": (8.52, 76.93),
    "Coimbatore": (11.01, 76.96),
    "Mysore": (12.30, 76.65),
    "Visakhapatnam": (17.68, 83.22),

    "Kolkata": (22.57, 88.36),
    "Bhubaneswar": (20.30, 85.82),
    "Ranchi": (23.34, 85.31),
    "Patna": (25.59, 85.13),
    "Raipur": (21.25, 81.63),
    "Bhopal": (23.25, 77.41),
    "Indore": (22.72, 75.86),

    "Guwahati": (26.14, 91.73),
    "Shillong": (25.57, 91.88),
    "Imphal": (24.81, 93.94),
    "Agartala": (23.83, 91.28)
}

# ============================================================
# CONFIGURATION
# ============================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "nasa_data"
OUTPUT_FILE = OUTPUT_DIR / "nasa_india_40cities.csv"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# NASA POWER API endpoints and parameters
NASA_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS = "T2M,PRECTOTCORR,QV2M,WS2M,ALLSKY_SFC_SW_DWN"  # PRECTOTCORR = corrected precipitation
START_DATE = "19810101"  # January 1, 1981
END_DATE = "20251231"    # December 31, 2025
COMMUNITY = "RE"         # Renewable Energy community
DATA_FORMAT = "JSON"

# Rate limiting
API_RATE_LIMIT = 1  # seconds between API calls

print("=" * 70)
print("NASA POWER API DATA DOWNLOADER")
print("=" * 70)
print(f"\n📍 Configuration:")
print(f"  Output folder: {OUTPUT_DIR}")
print(f"  Output file: {OUTPUT_FILE}")
print(f"  Cities: {len(cities)}")
print(f"  Date range: {START_DATE} to {END_DATE}")
print(f"  Parameters: T2M, PRECTOTCORR, QV2M, WS2M, ALLSKY_SFC_SW_DWN")
print(f"  API rate limit: {API_RATE_LIMIT}s between requests")

print(f"\n🔄 STEP 1: Verifying API connectivity...")
try:
    test_city = list(cities.items())[0]
    test_lat, test_lon = test_city[1]
    test_url = f"{NASA_API_URL}?parameters=T2M&community={COMMUNITY}&longitude={test_lon}&latitude={test_lat}&start=20250101&end=20250131&format={DATA_FORMAT}"
    response = requests.get(test_url, timeout=10)
    if response.status_code == 200:
        print(f"✅ API is accessible")
    else:
        print(f"⚠️  API returned status: {response.status_code}")
except Exception as e:
    print(f"❌ API connectivity error: {e}")
    print(f"Make sure you have internet connection")
    exit(1)

# ============================================================
# DOWNLOAD DATA FOR ALL CITIES
# ============================================================
print(f"\n🚀 STEP 2: Downloading data for {len(cities)} cities...\n")

all_data = []
successful = 0
failed = 0
failed_cities = []

for idx, (city, (lat, lon)) in enumerate(cities.items(), 1):
    print(f"[{idx:2d}/{len(cities)}] Downloading {city:20s} ({lat:7.2f}, {lon:7.2f})... ", end="", flush=True)
    
    try:
        # Build API URL
        url = f"{NASA_API_URL}?parameters={PARAMETERS}&community={COMMUNITY}&longitude={lon}&latitude={lat}&start={START_DATE}&end={END_DATE}&format={DATA_FORMAT}"
        
        # Make request with timeout
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        if "properties" not in data or "parameter" not in data["properties"]:
            print(f"❌ Invalid response format")
            failed += 1
            failed_cities.append(city)
            time.sleep(API_RATE_LIMIT)
            continue
        
        params = data["properties"]["parameter"]
        
        # Check for required parameters
        required_params = ["T2M", "PRECTOTCORR", "QV2M", "WS2M", "ALLSKY_SFC_SW_DWN"]
        missing_params = [p for p in required_params if p not in params]
        if missing_params:
            print(f"❌ Missing parameters: {missing_params}")
            failed += 1
            failed_cities.append(city)
            time.sleep(API_RATE_LIMIT)
            continue
        
        # Extract data into DataFrame
        df = pd.DataFrame({
            "date": params["T2M"].keys(),
            "temperature": params["T2M"].values(),
            "rainfall": params["PRECTOTCORR"].values(),  # Corrected precipitation
            "humidity": params["QV2M"].values(),
            "wind": params["WS2M"].values(),
            "solar": params["ALLSKY_SFC_SW_DWN"].values()
        })
        
        # Add metadata
        df["city"] = city
        df["latitude"] = lat
        df["longitude"] = lon
        
        # Convert date and extract year/month
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        
        # Reorder columns
        df = df[["date", "year", "month", "day", "city", "latitude", "longitude", 
                 "temperature", "rainfall", "humidity", "wind", "solar"]]
        
        all_data.append(df)
        successful += 1
        
        print(f"✅ ({len(df)} records)")
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout")
        failed += 1
        failed_cities.append(city)
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error")
        failed += 1
        failed_cities.append(city)
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        failed += 1
        failed_cities.append(city)
    
    # Rate limiting - be respectful to NASA API
    time.sleep(API_RATE_LIMIT)

# ============================================================
# COMBINE AND SAVE DATA
# ============================================================
print(f"\n📊 STEP 3: Processing and saving data...")

if all_data:
    # Concatenate all data
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Convert numeric columns
    numeric_cols = ["temperature", "rainfall", "humidity", "wind", "solar"]
    for col in numeric_cols:
        final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
    
    # Sort by city, date
    final_df = final_df.sort_values(["city", "date"]).reset_index(drop=True)
    
    # Save to CSV
    final_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"✅ Data saved to: {OUTPUT_FILE}")
    print(f"\n📈 Dataset Statistics:")
    print(f"  Total rows: {len(final_df):,}")
    print(f"  Cities: {final_df['city'].nunique()}")
    print(f"  Date range: {final_df['date'].min().date()} to {final_df['date'].max().date()}")
    print(f"  File size: {OUTPUT_FILE.stat().st_size / (1024**2):.2f} MB")
    
    print(f"\n  Data by city:")
    city_counts = final_df['city'].value_counts().sort_values(ascending=False)
    for city, count in city_counts.head(5).items():
        print(f"    - {city}: {count:,} records")
    if len(city_counts) > 5:
        print(f"    ... and {len(city_counts) - 5} more cities")
    
    print(f"\n  Data quality:")
    print(f"    Temperature: {final_df['temperature'].notna().sum():,} valid values ({final_df['temperature'].notna().sum()/len(final_df)*100:.1f}%)")
    print(f"    Rainfall: {final_df['rainfall'].notna().sum():,} valid values ({final_df['rainfall'].notna().sum()/len(final_df)*100:.1f}%)")
    print(f"    Humidity: {final_df['humidity'].notna().sum():,} valid values ({final_df['humidity'].notna().sum()/len(final_df)*100:.1f}%)")
    print(f"    Wind: {final_df['wind'].notna().sum():,} valid values ({final_df['wind'].notna().sum()/len(final_df)*100:.1f}%)")
    print(f"    Solar: {final_df['solar'].notna().sum():,} valid values ({final_df['solar'].notna().sum()/len(final_df)*100:.1f}%)")
    
    print(f"\n  Sample data (first 5 rows):")
    print(final_df.head(5).to_string(index=False))
    
else:
    print(f"❌ No data downloaded!")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n" + "=" * 70)
print(f"DOWNLOAD SUMMARY")
print(f"=" * 70)
print(f"✅ Successful: {successful}/{len(cities)}")
print(f"❌ Failed: {failed}/{len(cities)}")
if failed_cities:
    print(f"   Failed cities: {', '.join(failed_cities[:5])}" + 
          (f" ... and {len(failed_cities)-5} more" if len(failed_cities) > 5 else ""))
print(f"\n🎉 Download complete!")
print(f"📂 Output: {OUTPUT_FILE}")
