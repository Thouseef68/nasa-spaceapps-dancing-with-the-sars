"""pipeline/export_web.py
Reprojects GeoTIFF water and change layers to EPSG:4326 RGBA PNGs for Leaflet.
Writes web/layers/layers.json with coordinate bounds and copies results/results.json to web/results.json.
"""
import json
import shutil
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.warp import Resampling, calculate_default_transform, reproject

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data/processed"
WEB = ROOT / "web"
LAYERS_DIR = WEB / "layers"
LAYERS_DIR.mkdir(parents=True, exist_ok=True)

LAYERS = {
    # Core open water layers (primary result: HH < -20 dB, HV < -23 dB)
    "core_flood_jul26_new":      ("core_flood_jul26_new.tif",      "#e31a1c"),
    "core_flood_jul26_receded":  ("core_flood_jul26_receded.tif",  "#ff7f00"),
    "core_baseline_jul02_water": ("core_baseline_jul02_water.tif", "#9ecae1"),
    "core_flood_jul26_water":    ("core_flood_jul26_water.tif",    "#3182bd"),
    # Headline layers (edge dynamics: HH < -15 dB, HV < -18 dB)
    "flood_jul26_new_flood":     ("flood_jul26_new_flood.tif",     "#e31a1c"),
    "flood_jul26_receded":       ("flood_jul26_receded.tif",       "#ff7f00"),
    "baseline_jul02_water":      ("baseline_jul02_water.tif",      "#9ecae1"),
    "flood_jul26_water":         ("flood_jul26_water.tif",         "#3182bd"),
}


def hex_rgb(h):
    return tuple(int(h[i : i + 2], 16) for i in (1, 3, 5))


def export_layers():
    meta = {}
    for key, (fname, color) in LAYERS.items():
        src_path = PROC / fname
        if not src_path.exists():
            print(f"Warning: {src_path} not found, skipping.")
            continue

        with rasterio.open(src_path) as src:
            t, w, h = calculate_default_transform(
                src.crs, "EPSG:4326", src.width, src.height, *src.bounds
            )
            out = np.zeros((h, w), np.uint8)
            reproject(
                source=rasterio.band(src, 1),
                destination=out,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=t,
                dst_crs="EPSG:4326",
                resampling=Resampling.nearest,
            )
            west, north = t.c, t.f
            east, south = west + t.a * w, north + t.e * h

        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[out == 1, :3] = hex_rgb(color)
        rgba[out == 1, 3] = 200  # Alpha opacity
        Image.fromarray(rgba).save(LAYERS_DIR / f"{key}.png")
        meta[key] = {"bounds": [[south, west], [north, east]]}

    # Also export grayscale SAR backscatter radar layers (L-band HH dB)
    radar_layers = {
        "flood_jul26_radar": "flood_jul26_HH_dB.tif",
        "baseline_jul02_radar": "baseline_jul02_HH_dB.tif",
    }
    for r_key, r_fname in radar_layers.items():
        r_path = PROC / r_fname
        if not r_path.exists():
            continue
        with rasterio.open(r_path) as src:
            t, w, h = calculate_default_transform(src.crs, "EPSG:4326", src.width // 2, src.height // 2, *src.bounds)
            out_db = np.full((h, w), np.nan, dtype=np.float32)
            reproject(
                source=rasterio.band(src, 1),
                destination=out_db,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=t,
                dst_crs="EPSG:4326",
                resampling=Resampling.bilinear,
            )
            west, north = t.c, t.f
            east, south = west + t.a * w, north + t.e * h

        valid = np.isfinite(out_db)
        norm = np.zeros_like(out_db)
        norm[valid] = np.clip((out_db[valid] - (-26.0)) / ((-4.0) - (-26.0)), 0.0, 1.0)
        gray = (norm * 255).astype(np.uint8)

        rgba_radar = np.zeros((h, w, 4), dtype=np.uint8)
        rgba_radar[valid, 0] = gray[valid]
        rgba_radar[valid, 1] = gray[valid]
        rgba_radar[valid, 2] = gray[valid]
        rgba_radar[valid, 3] = 215

        Image.fromarray(rgba_radar).save(LAYERS_DIR / f"{r_key}.png")
        meta[r_key] = {"bounds": [[south, west], [north, east]]}
        print(f"Exported radar imagery: {r_key}.png")

    layers_json_path = LAYERS_DIR / "layers.json"
    with open(layers_json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("Wrote", len(meta), "layers to", LAYERS_DIR.resolve())

    # Copy results.json into web/ directory for Leaflet panel
    results_src = ROOT / "results/results.json"
    if results_src.exists():
        shutil.copy(results_src, WEB / "results.json")
        print("Copied results.json to web/results.json")


if __name__ == "__main__":
    export_layers()
