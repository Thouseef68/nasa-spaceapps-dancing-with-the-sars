"""Step 2: load HH/HV, remove processing artifacts, align to a common 20 m grid,
speckle filter, convert to dB, build water masks, and compute change vs. the baseline."""
import csv
import warnings
from pathlib import Path

import h5py
import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.transform import from_origin
from scipy.ndimage import uniform_filter
from skimage.filters import threshold_otsu

warnings.filterwarnings("ignore", category=RuntimeWarning)

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

GRID = "science/LSAR/GCOV/grids/frequencyA"
EPSG = 32646
CELL = 20.0                              # common output resolution (m)
AOI_LONLAT = (89.8, 25.9, 94.2, 26.9)    # west, south, east, north
SPECKLE = 5                              # boxcar window (pixels)

LIN_FLOOR = 1e-4     # -40 dB: below this is a processing artifact, not backscatter
LIN_CEIL = 10.0      # +10 dB: above this is not physical for land
DB_LAND_MIN = -40.0  # Otsu is computed only on this range
DB_LAND_MAX = 5.0

FIXED_HH_DB = -15.0  # test values: -15, -18
FIXED_HV_DB = -18.0  # test values: -18, -20

SCENES = {
    "baseline_jul02": "*_024_091_D_076_*.h5",
    "flood_jul14":    "*_025_091_D_076_*.h5",
    "flood_jul26":    "*_026_091_D_076_*.h5",
}


def aoi_bounds_utm():
    to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{EPSG}", always_xy=True)
    w, s, e, n = AOI_LONLAT
    pts = [to_utm.transform(lon, lat) for lon in (w, e) for lat in (s, n)]
    xs, ys = zip(*pts)
    return min(xs), min(ys), max(xs), max(ys)


def index_range(coords, lo, hi):
    idx = np.where((coords >= lo) & (coords <= hi))[0]
    return idx.min(), idx.max() + 1


def load_pol(path, pol, bounds):
    """Crop one polarization to the AOI, remove artifacts, and resample to CELL metres."""
    xmin, ymin, xmax, ymax = bounds
    with h5py.File(path, "r") as h5:
        g = h5[GRID]
        x = g["xCoordinates"][:]
        y = g["yCoordinates"][:]
        dx = float(g["xCoordinateSpacing"][()])
        dy = float(g["yCoordinateSpacing"][()])
        c0, c1 = index_range(x, xmin, xmax)
        r0, r1 = index_range(y, ymin, ymax)
        arr = g[pol][r0:r1, c0:c1].astype(np.float64)

    # Remove non-finite values and unphysical artifacts before anything else
    arr[~np.isfinite(arr) | (arr < LIN_FLOOR) | (arr > LIN_CEIL)] = np.nan

    west = x[c0] - dx / 2
    north = y[r0] - dy / 2

    if abs(dx) < CELL:  # 10 m -> 20 m: average 2x2 blocks in linear power
        r = (arr.shape[0] // 2) * 2
        c = (arr.shape[1] // 2) * 2
        arr = np.nanmean(arr[:r, :c].reshape(r // 2, 2, c // 2, 2), axis=(1, 3))

    return arr, west, north


def boxcar(lin):
    """Speckle reduction in linear power that ignores no-data pixels."""
    valid = np.isfinite(lin).astype(float)
    total = uniform_filter(np.nan_to_num(lin), SPECKLE, mode="nearest")
    count = uniform_filter(valid, SPECKLE, mode="nearest")
    out = total / np.maximum(count, 1e-9)
    out[valid == 0] = np.nan
    return out


def to_db(lin):
    with np.errstate(divide="ignore", invalid="ignore"):
        return 10 * np.log10(lin)


def land_threshold(db):
    """Otsu on the physically plausible land/water range only."""
    vals = db[np.isfinite(db) & (db > DB_LAND_MIN) & (db < DB_LAND_MAX)]
    return threshold_otsu(vals)


def align(scenes):
    """Crop all scenes to the same top-left corner and common size."""
    W = max(s["west"] for s in scenes.values())
    N = min(s["north"] for s in scenes.values())
    for s in scenes.values():
        cr = round((s["north"] - N) / CELL)
        cc = round((W - s["west"]) / CELL)
        for k in ("HH", "HV"):
            s[k] = s[k][cr:, cc:]
    H = min(s["HH"].shape[0] for s in scenes.values())
    Wd = min(s["HH"].shape[1] for s in scenes.values())
    for s in scenes.values():
        for k in ("HH", "HV"):
            s[k] = s[k][:H, :Wd]
    return W, N, H, Wd


def save_tif(path, arr, W, N, dtype, nodata=None):
    h, w = arr.shape
    with rasterio.open(
        path, "w", driver="GTiff", height=h, width=w, count=1,
        dtype=dtype, crs=f"EPSG:{EPSG}",
        transform=from_origin(W, N, CELL, CELL), nodata=nodata,
    ) as dst:
        dst.write(arr.astype(dtype), 1)


def main():
    bounds = aoi_bounds_utm()
    scenes = {}

    for name, pattern in SCENES.items():
        path = next(RAW.glob(pattern))
        print(f"Loading {path.name}")
        hh, west, north = load_pol(path, "HHHH", bounds)
        hv, _, _ = load_pol(path, "HVHV", bounds)
        scenes[name] = {
            "HH": to_db(boxcar(hh)),
            "HV": to_db(boxcar(hv)),
            "west": west,
            "north": north,
        }

    W, N, H, Wd = align(scenes)
    print(f"Common grid: {Wd} x {H} px at {CELL:.0f} m")

    cell_km2 = CELL * CELL / 1e6
    masks, valids = {}, {}

    for name, s in scenes.items():
        hh, hv = s["HH"], s["HV"]
        valid = np.isfinite(hh) & np.isfinite(hv)
        t_hh = FIXED_HH_DB
        t_hv = FIXED_HV_DB
        water = valid & (hh < t_hh) & (hv < t_hv)
        print(
            f"{name}: Fixed Threshold HH = {t_hh:.2f} dB, HV = {t_hv:.2f} dB | "
            f"valid = {valid.mean() * 100:.1f}% | "
            f"water = {water.sum() / max(valid.sum(), 1) * 100:.2f}% of valid"
        )
        masks[name] = water
        valids[name] = valid
        save_tif(OUT / f"{name}_HH_dB.tif", hh, W, N, "float32", nodata=np.nan)
        save_tif(OUT / f"{name}_water.tif", water.astype(np.uint8), W, N, "uint8")

    # Change is computed only where both the baseline and the flood scene have valid data
    base_name = "baseline_jul02"
    base_water = masks[base_name]
    base_valid = valids[base_name]

    common_all = np.logical_and.reduce(list(valids.values()))
    common_dual = base_valid & valids["flood_jul26"]
    print(f"Intersection of all 3 scenes: {common_all.sum() * cell_km2:.2f} km2")
    print(f"Common footprint (Jul 02 & Jul 26): {common_dual.sum() * cell_km2:.2f} km2")
    save_tif(OUT / "common_valid.tif", common_dual.astype(np.uint8), W, N, "uint8")

    stable = np.ones_like(base_valid)
    for n in scenes:
        stable &= valids[n] & ~masks[n]
    for n in scenes:
        print(n, "stable-land median HH:", round(np.nanmedian(scenes[n]["HH"][stable]), 2),
              "HV:", round(np.nanmedian(scenes[n]["HV"][stable]), 2))

    # Core water masks (HH < -20.0 dB, HV < -23.0 dB)
    core_masks = {}
    for name, s in scenes.items():
        c_water = valids[name] & (s["HH"] < -20.0) & (s["HV"] < -23.0)
        core_masks[name] = c_water
        save_tif(OUT / f"core_{name}_water.tif", c_water.astype(np.uint8), W, N, "uint8")

    core_base_water = core_masks[base_name]
    core_new = core_masks["flood_jul26"] & ~core_base_water & common_dual
    core_rec = core_base_water & ~core_masks["flood_jul26"] & common_dual
    save_tif(OUT / "core_flood_jul26_new.tif", core_new.astype(np.uint8), W, N, "uint8")
    save_tif(OUT / "core_flood_jul26_receded.tif", core_rec.astype(np.uint8), W, N, "uint8")

    summary = []
    for name, water in masks.items():
        common = base_valid & valids[name]
        water_common_all = water & common_all
        water_common_dual = water & common_dual
        if name == base_name:
            new = np.zeros_like(water)
            receded = np.zeros_like(water)
        else:
            new = water & ~base_water & common
            receded = base_water & ~water & common
            save_tif(OUT / f"{name}_new_flood.tif", new.astype(np.uint8), W, N, "uint8")
            save_tif(OUT / f"{name}_receded.tif", receded.astype(np.uint8), W, N, "uint8")

        row = {
            "scene": name,
            "valid_km2": round(valids[name].sum() * cell_km2, 2),
            "water_km2": round(water.sum() * cell_km2, 2),
            "water_pct_of_valid": round(water.sum() / max(valids[name].sum(), 1) * 100, 3),
            "water_km2_common_3scenes": round(water_common_all.sum() * cell_km2, 2),
            "water_pct_common_3scenes": round(water_common_all.sum() / max(common_all.sum(), 1) * 100, 3),
            "water_km2_common_dual": round(water_common_dual.sum() * cell_km2, 2),
            "water_pct_common_dual": round(water_common_dual.sum() / max(common_dual.sum(), 1) * 100, 3),
            "new_water_vs_baseline_km2": round(new.sum() * cell_km2, 2),
            "receded_vs_baseline_km2": round(receded.sum() * cell_km2, 2),
        }
        summary.append(row)

    with open(OUT / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)

    print("\nSummary:")
    for row in summary:
        print(row)
    print(f"\nOutputs written to {OUT.resolve()}")


if __name__ == "__main__":
    main()
