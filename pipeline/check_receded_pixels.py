import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
import numpy as np
from pipeline.step2_process import aoi_bounds_utm, load_pol, align, SCENES, to_db, boxcar, RAW

bounds = aoi_bounds_utm()
scenes = {}
for name in ["baseline_jul02", "flood_jul26"]:
    pattern = SCENES[name]
    path = next(RAW.glob(pattern))
    hh, west, north = load_pol(path, "HHHH", bounds)
    hv, _, _ = load_pol(path, "HVHV", bounds)
    scenes[name] = {
        "HH": to_db(boxcar(hh)),
        "HV": to_db(boxcar(hv)),
        "west": west,
        "north": north,
    }

W, N, H, Wd = align(scenes)

hh_base = scenes["baseline_jul02"]["HH"]
hv_base = scenes["baseline_jul02"]["HV"]
hh_obs = scenes["flood_jul26"]["HH"]
hv_obs = scenes["flood_jul26"]["HV"]

common = (
    np.isfinite(hh_base)
    & np.isfinite(hv_base)
    & np.isfinite(hh_obs)
    & np.isfinite(hv_obs)
)

# Compute stable land median (pixels above -12 dB in both scenes)
stable_land = common & (hh_base > -12.0) & (hh_obs > -12.0)
print(f"Stable land HH median: {np.nanmedian(hh_base[stable_land]):.2f} dB -> {np.nanmedian(hh_obs[stable_land]):.2f} dB")
print(f"Stable land HV median: {np.nanmedian(hv_base[stable_land]):.2f} dB -> {np.nanmedian(hv_obs[stable_land]):.2f} dB\n")

# Compute open water core (pixels below -18 dB in both scenes)
open_water = common & (hh_base < -18.0) & (hh_obs < -18.0)
print(f"Core open water HH median: {np.nanmedian(hh_base[open_water]):.2f} dB -> {np.nanmedian(hh_obs[open_water]):.2f} dB")
print(f"Core open water HV median: {np.nanmedian(hv_base[open_water]):.2f} dB -> {np.nanmedian(hv_obs[open_water]):.2f} dB\n")

for thr_hh, thr_hv, label in [
    (-12.0, -15.0, "High threshold (-12 dB HH / -15 dB HV)"),
    (-15.0, -18.0, "Primary Config A (-15 dB HH / -18 dB HV)"),
    (-18.0, -21.0, "Conservative sweep (-18 dB HH / -21 dB HV)")
]:
    wb = common & (hh_base < thr_hh) & (hv_base < thr_hv)
    wo = common & (hh_obs < thr_hh) & (hv_obs < thr_hv)
    rec = wb & ~wo
    new = wo & ~wb
    
    print(f"=== {label} ===")
    print(f"Receded pixel count: {rec.sum()} ({rec.sum() * 0.0004:.2f} km2)")
    print(f"  Receded HH median: {np.nanmedian(hh_base[rec]):.2f} dB -> {np.nanmedian(hh_obs[rec]):.2f} dB")
    print(f"  Receded HV median: {np.nanmedian(hv_base[rec]):.2f} dB -> {np.nanmedian(hv_obs[rec]):.2f} dB")
    print(f"New flood pixel count: {new.sum()} ({new.sum() * 0.0004:.2f} km2)")
    print(f"  New flood HH median: {np.nanmedian(hh_base[new]):.2f} dB -> {np.nanmedian(hh_obs[new]):.2f} dB")
    print(f"  New flood HV median: {np.nanmedian(hv_base[new]):.2f} dB -> {np.nanmedian(hv_obs[new]):.2f} dB")
    print()

