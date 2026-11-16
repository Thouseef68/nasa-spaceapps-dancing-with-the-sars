import urllib.request
import json
import rasterio
from pyproj import Transformer
import numpy as np
from PIL import Image

# 1. Reverse geocode sample points
coords = [(26.18, 90.62), (26.12, 90.58), (26.07, 90.55), (26.00, 90.50), (25.92, 90.40)]
for lat, lon in coords:
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14"
    req = urllib.request.Request(url, headers={"User-Agent": "NisarVerification/1.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
            name = data.get("display_name", "")
            print(f"({lat}, {lon}) -> {name}")
    except Exception as e:
        print(f"({lat}, {lon}) -> {e}")

