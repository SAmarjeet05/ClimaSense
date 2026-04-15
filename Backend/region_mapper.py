"""
Region Mapping Utility
Maps to all 36 IMD subdivisions used in rainfall and temperature datasets
"""

# All 36 IMD subdivisions with their geographic bounds
REGIONS = {
    "HARYANA DELHI & CHANDIGARH": {
        "lat_min": 27.0, "lat_max": 30.5, "lon_min": 74.3, "lon_max": 77.9},
    "PUNJAB": {
        "lat_min": 30.7, "lat_max": 32.2, "lon_min": 73.5, "lon_max": 76.5},
    "HIMACHAL PRADESH": {
        "lat_min": 31.2, "lat_max": 33.3, "lon_min": 75.5, "lon_max": 78.8},
    "JAMMU & KASHMIR": {
        "lat_min": 32.2, "lat_max": 36.0, "lon_min": 74.0, "lon_max": 77.5},
    "UTTARAKHAND": {
        "lat_min": 28.7, "lat_max": 30.7, "lon_min": 78.8, "lon_max": 81.0},
    "EAST UTTAR PRADESH": {
        "lat_min": 25.0, "lat_max": 27.8, "lon_min": 79.0, "lon_max": 82.0},
    "WEST UTTAR PRADESH": {
        "lat_min": 27.0, "lat_max": 29.5, "lon_min": 76.5, "lon_max": 79.0},
    "BIHAR": {
        "lat_min": 24.2, "lat_max": 27.5, "lon_min": 82.3, "lon_max": 88.3},
    "JHARKHAND": {
        "lat_min": 22.0, "lat_max": 25.4, "lon_min": 83.3, "lon_max": 87.9},
    "GANGETIC WEST BENGAL": {
        "lat_min": 23.5, "lat_max": 25.5, "lon_min": 86.0, "lon_max": 88.4},
    "SUB HIMALAYAN WEST BENGAL & SIKKIM": {
        "lat_min": 25.5, "lat_max": 27.2, "lon_min": 86.0, "lon_max": 88.4},
    "ASSAM & MEGHALAYA": {
        "lat_min": 24.5, "lat_max": 28.3, "lon_min": 89.8, "lon_max": 97.4},
    "ARUNACHAL PRADESH": {
        "lat_min": 26.2, "lat_max": 29.0, "lon_min": 91.5, "lon_max": 97.5},
    "NAGA MANI MIZO TRIPURA": {
        "lat_min": 21.9, "lat_max": 27.0, "lon_min": 92.3, "lon_max": 95.4},
    "ORISSA": {
        "lat_min": 17.0, "lat_max": 22.5, "lon_min": 82.0, "lon_max": 87.5},
    "EAST MADHYA PRADESH": {
        "lat_min": 22.0, "lat_max": 24.5, "lon_min": 79.0, "lon_max": 82.0},
    "WEST MADHYA PRADESH": {
        "lat_min": 21.0, "lat_max": 23.5, "lon_min": 73.7, "lon_max": 78.5},
    "CHHATTISGARH": {
        "lat_min": 20.1, "lat_max": 24.1, "lon_min": 80.3, "lon_max": 83.4},
    "EAST RAJASTHAN": {
        "lat_min": 25.0, "lat_max": 27.5, "lon_min": 75.0, "lon_max": 78.0},
    "WEST RAJASTHAN": {
        "lat_min": 23.0, "lat_max": 27.0, "lon_min": 68.2, "lon_max": 75.0},
    "MADHYA MAHARASHTRA": {
        "lat_min": 17.0, "lat_max": 19.5, "lon_min": 73.0, "lon_max": 76.0},
    "MATATHWADA": {
        "lat_min": 17.5, "lat_max": 19.5, "lon_min": 74.5, "lon_max": 77.0},
    "VIDARBHA": {
        "lat_min": 20.5, "lat_max": 22.0, "lon_min": 77.0, "lon_max": 80.9},
    "KONKAN & GOA": {
        "lat_min": 14.8, "lat_max": 16.5, "lon_min": 72.6, "lon_max": 74.3},
    "GUJARAT REGION": {
        "lat_min": 20.1, "lat_max": 24.5, "lon_min": 68.2, "lon_max": 74.4},
    "SAURASHTRA & KUTCH": {
        "lat_min": 21.0, "lat_max": 23.5, "lon_min": 69.0, "lon_max": 72.0},
    "COASTAL KARNATAKA": {
        "lat_min": 13.0, "lat_max": 14.8, "lon_min": 74.1, "lon_max": 75.1},
    "NORTH INTERIOR KARNATAKA": {
        "lat_min": 14.8, "lat_max": 16.5, "lon_min": 74.5, "lon_max": 76.8},
    "SOUTH INTERIOR KARNATAKA": {
        "lat_min": 11.6, "lat_max": 14.8, "lon_min": 75.7, "lon_max": 78.6},
    "TELANGANA": {
        "lat_min": 15.5, "lat_max": 19.7, "lon_min": 77.3, "lon_max": 81.8},
    "COASTAL ANDHRA PRADESH": {
        "lat_min": 13.2, "lat_max": 15.0, "lon_min": 79.6, "lon_max": 84.0},
    "RAYALSEEMA": {
        "lat_min": 13.0, "lat_max": 15.5, "lon_min": 77.4, "lon_max": 79.6},
    "TAMIL NADU": {
        "lat_min": 8.0, "lat_max": 13.5, "lon_min": 77.0, "lon_max": 80.3},
    "KERALA": {
        "lat_min": 8.3, "lat_max": 12.8, "lon_min": 74.8, "lon_max": 77.8},
    "ANDAMAN & NICOBAR ISLANDS": {
        "lat_min": 6.0, "lat_max": 14.0, "lon_min": 91.4, "lon_max": 94.3},
    "LAKSHADWEEP": {
        "lat_min": 8.0, "lat_max": 12.3, "lon_min": 72.7, "lon_max": 74.3},
}


def map_coordinates_to_region(lat, lon):
    """
    Map latitude and longitude to IMD subdivision.
    Returns the subdivision name if coordinates fall within bounds, else "UNKNOWN"
    """
    for region, bounds in REGIONS.items():
        if (bounds["lat_min"] <= lat <= bounds["lat_max"] and 
            bounds["lon_min"] <= lon <= bounds["lon_max"]):
            return region
    return "UNKNOWN"


def get_all_regions():
    """Get list of all 36 IMD subdivisions"""
    return list(REGIONS.keys())


if __name__ == "__main__":
    print(f"Total IMD Subdivisions: {len(get_all_regions())}")
    for region in sorted(get_all_regions()):
        print(f"  • {region}")
