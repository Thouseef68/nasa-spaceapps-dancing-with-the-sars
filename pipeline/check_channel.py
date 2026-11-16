import math
import urllib.request
from PIL import Image
import numpy as np
import rasterio
from pyproj import Transformer

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 1 << zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    n = 1 << zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

zoom = 14
# Focus on northernmost water: 26.1333, 90.3597
center_lat, center_lon = 26.1333, 90.3597
x0, y0 = deg2num(center_lat + 0.02, center_lon - 0.02, zoom)
x1, y1 = deg2num(center_lat - 0.02, center_lon + 0.02, zoom)
xmin, xmax = min(x0, x1), max(x0, x1)
ymin, ymax = min(y0, y1), max(y0, y1)

cols = xmax - xmin + 1
rows = ymax - ymin + 1
sat_img = Image.new('RGB', (cols * 256, rows * 256))
headers = {'User-Agent': 'Mozilla/5.0'}

for r, y in enumerate(range(ymin, ymax + 1)):
    for c, x in enumerate(range(xmin, xmax + 1)):
        url = f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            tile = Image.open(resp)
            sat_img.paste(tile, (c * 256, r * 256))

north, west = num2deg(xmin, ymin, zoom)
south, east = num2deg(xmax + 1, ymax + 1, zoom)
sat_w, sat_h = sat_img.size

# Read raster water layer directly
with rasterio.open('data/processed/flood_jul26_water.tif') as src:
    to_utm = Transformer.from_crs('EPSG:4326', src.crs, always_xy=True)
    # For every pixel in sat_img, compute lat, lon -> utm -> src row, col
    out_mask = np.zeros((sat_h, sat_w), dtype=np.uint8)
    
    # Generate meshgrid of lat/lon
    lons = np.linspace(west, east, sat_w)
    lats = np.linspace(north, south, sat_h) # north is top
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    
    x_utm, y_utm = to_utm.transform(lon_grid, lat_grid)
    
    # Transform to pixel coords in src
    # inv transform: (c, r) = ~transform * (x, y)
    inv_tf = ~src.transform
    cols = inv_tf.a * x_utm + inv_tf.b * y_utm + inv_tf.c
    rows = inv_tf.d * x_utm + inv_tf.e * y_utm + inv_tf.f
    
    cols = np.round(cols).astype(int)
    rows = np.round(rows).astype(int)
    
    valid_px = (cols >= 0) & (cols < src.width) & (rows >= 0) & (rows < src.height)
    arr = src.read(1)
    
    out_mask[valid_px] = arr[rows[valid_px], cols[valid_px]]

# Save composite: overlay cyan (#3182bd) water on sat_img
comp = sat_img.copy()
rgba = np.zeros((sat_h, sat_w, 4), dtype=np.uint8)
rgba[out_mask == 1, 0] = 49
rgba[out_mask == 1, 1] = 130
rgba[out_mask == 1, 2] = 189
rgba[out_mask == 1, 3] = 180
overlay_pil = Image.fromarray(rgba)
comp.paste(overlay_pil, (0, 0), overlay_pil)

comp.save('web/verification_direct_sat.png')
sat_img.save('web/verification_sat_only.png')
print('Saved web/verification_direct_sat.png')

