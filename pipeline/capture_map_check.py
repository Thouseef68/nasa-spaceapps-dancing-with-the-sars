"""pipeline/capture_map_check.py
Captures a verification composite showing the core water change layers
overlaid on Esri World Imagery across the Brahmaputra river channels,
saved to results/map_check.png.
"""
import json
import math
import urllib.request
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
LAYERS_DIR = ROOT / "web/layers"


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


def capture_map():
    print("Generating results/map_check.png verification image...")
    # Regional view around Brahmaputra river at Goalpara (lon 90.25 to 90.75, lat 26.00 to 26.25)
    zoom = 12
    x0, y0 = deg2num(26.25, 90.25, zoom)
    x1, y1 = deg2num(26.00, 90.75, zoom)

    xmin, xmax = min(x0, x1), max(x0, x1)
    ymin, ymax = min(y0, y1), max(y0, y1)

    cols = xmax - xmin + 1
    rows = ymax - ymin + 1
    sat_img = Image.new("RGB", (cols * 256, rows * 256))
    headers = {"User-Agent": "Mozilla/5.0"}

    for r, y in enumerate(range(ymin, ymax + 1)):
        for c, x in enumerate(range(xmin, xmax + 1)):
            url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req) as resp:
                    tile = Image.open(resp)
                    sat_img.paste(tile, (c * 256, r * 256))
            except Exception as e:
                print(f"Error fetching tile {x}, {y}: {e}")

    north, west = num2deg(xmin, ymin, zoom)
    south, east = num2deg(xmax + 1, ymax + 1, zoom)
    sat_w, sat_h = sat_img.size

    with open(LAYERS_DIR / "layers.json") as f:
        meta = json.load(f)

    # Load core layers
    core_new_png = Image.open(LAYERS_DIR / "core_flood_jul26_new.png")
    core_rec_png = Image.open(LAYERS_DIR / "core_flood_jul26_receded.png")
    core_base_png = Image.open(LAYERS_DIR / "core_baseline_jul02_water.png")
    core_flood_png = Image.open(LAYERS_DIR / "core_flood_jul26_water.png")

    (ov_s, ov_w), (ov_n, ov_e) = meta["core_flood_jul26_new"]["bounds"]
    ow, oh = core_new_png.size

    # Affine transform parameters to project overlay PNG onto satellite image
    a = (east - west) / sat_w / (ov_e - ov_w) * ow
    c = (west - ov_w) / (ov_e - ov_w) * ow
    e = (south - north) / sat_h / (ov_s - ov_n) * oh
    f = (ov_n - north) / (ov_n - ov_s) * oh

    def apply_layer(base, img_pil):
        tf = img_pil.transform(
            (sat_w, sat_h), Image.AFFINE, (a, 0, c, 0, e, f), resample=Image.NEAREST
        )
        res = base.copy()
        res.paste(tf, (0, 0), tf)
        return res

    comp = sat_img.copy()
    # Apply baseline water in faint blue
    comp = apply_layer(comp, core_base_png)
    # Apply observed water in deeper blue
    comp = apply_layer(comp, core_flood_png)
    # Apply receded core in orange
    comp = apply_layer(comp, core_rec_png)
    # Apply new core in red
    comp = apply_layer(comp, core_new_png)

    # Add legend / label overlay
    draw = ImageDraw.Draw(comp)
    # Draw dark translucent banner at top
    banner_h = 42
    banner = Image.new("RGBA", (sat_w, banner_h), (0, 0, 0, 190))
    comp.paste(banner, (0, 0), banner)
    
    label_text = (
        "NISAR Frame 76 (Brahmaputra AOI) - Core Open Water Changes on Esri World Imagery\n"
        "Red: New Core Water | Orange: Receded Core Water | Blue: Persistent Core Water"
    )
    draw.text((10, 6), label_text, fill=(255, 255, 255))

    out_path = RESULTS_DIR / "map_check.png"
    comp.save(out_path)
    print(f"Saved verification map screenshot to {out_path.resolve()}")


if __name__ == "__main__":
    capture_map()

