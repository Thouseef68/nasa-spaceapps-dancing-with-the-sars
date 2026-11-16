import math
import urllib.request
from PIL import Image

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 1 << zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

zoom = 13
x0, y0 = deg2num(26.10, 90.33, zoom)
x1, y1 = deg2num(26.03, 90.43, zoom)
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

sat_img.save('web/verification_base_satellite.png')
print('Saved base satellite image.')

