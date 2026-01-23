import requests
from math import radians, sin, cos, sqrt, atan2

STORE_LOCATIONS = [
    {"key": "wigan", "name": "Wigan", "lat": 53.552925, "lon": -2.627962},
    {"key": "southport", "name": "Southport", "lat": 53.639413, "lon": -3.004943},
]

def haversine(lat1, lon1, lat2, lon2):
    R = 3959  # miles
    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2*atan2(sqrt(a), sqrt(1-a))
    return R * c

def get_store_for_postcode(postcode):
    """Returns (store_dict, distance_miles) or (None, None) if not deliverable."""
    postcode = postcode.replace(" ", "").upper()
    resp = requests.get(f"https://api.postcodes.io/postcodes/{postcode}")
    data = resp.json()
    if data.get('status') != 200:
        return None, None
    lat, lon = data['result']['latitude'], data['result']['longitude']
    for store in STORE_LOCATIONS:
        dist = haversine(lat, lon, store['lat'], store['lon'])
        if dist <= 5:
            return store, dist
    return None, None
