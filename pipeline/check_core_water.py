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

thr_hh, thr_hv = -15.0, -18.0
wb = common & (hh_base < thr_hh) & (hv_base < thr_hv)
wo = common & (hh_obs < thr_hh) & (hv_obs < thr_hv)
rec = wb & ~wo
new = wo & ~wb
core = -20.0  # well inside the open-water range

rec_total = rec.sum()
rec_core = (rec & (hh_base < core)).sum()
rec_edge = rec_total - rec_core

new_total = new.sum()
new_core = (new & (hh_obs < core)).sum()
new_edge = new_total - new_core

print(f"Receded total pixels: {rec_total} ({rec_total * 0.0004:.2f} km2)")
print(f"  Receded with baseline HH < -20 dB (core): {rec_core} ({rec_core * 0.0004:.2f} km2, {rec_core / rec_total * 100:.1f}%)")
print(f"  Receded with baseline HH in [-20, -15] dB (edge): {rec_edge} ({rec_edge * 0.0004:.2f} km2, {rec_edge / rec_total * 100:.1f}%)")
print(f"  Receded baseline HH median: {np.nanmedian(hh_base[rec]):.2f} dB, 25th-75th percentile: [{np.nanpercentile(hh_base[rec], 25):.2f}, {np.nanpercentile(hh_base[rec], 75):.2f}] dB")

print(f"\nNew flood total pixels: {new_total} ({new_total * 0.0004:.2f} km2)")
print(f"  New flood with obs HH < -20 dB (core): {new_core} ({new_core * 0.0004:.2f} km2, {new_core / new_total * 100:.1f}%)")
print(f"  New flood with obs HH in [-20, -15] dB (edge): {new_edge} ({new_edge * 0.0004:.2f} km2, {new_edge / new_total * 100:.1f}%)")
print(f"  New flood obs HH median: {np.nanmedian(hh_obs[new]):.2f} dB, 25th-75th percentile: [{np.nanpercentile(hh_obs[new], 25):.2f}, {np.nanpercentile(hh_obs[new], 75):.2f}] dB")

