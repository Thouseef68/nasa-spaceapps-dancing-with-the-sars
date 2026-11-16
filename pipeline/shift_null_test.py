import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
import numpy as np
from pipeline.step2_process import aoi_bounds_utm, load_pol, align, SCENES, to_db, boxcar, RAW

CELL_KM2 = 0.0004  # 20 m x 20 m per pixel

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

def water(hh, hv, thr_hh, thr_hv, mask):
    return mask & (hh < thr_hh) & (hv < thr_hv)

# 1. Core water analysis
print("=== CORE WATER ANALYSIS (HH < -20.0 dB, HV < -23.0 dB) ===")
core_b = water(hh_base, hv_base, -20.0, -23.0, common)
core_o = water(hh_obs, hv_obs, -20.0, -23.0, common)
core_new = core_o & ~core_b
core_rec = core_b & ~core_o

print(f"Core water baseline (Jul 02): {core_b.sum() * CELL_KM2:.2f} km2 ({core_b.sum()} px)")
print(f"Core water observed (Jul 26): {core_o.sum() * CELL_KM2:.2f} km2 ({core_o.sum()} px)")
print(f"New core water:               {core_new.sum() * CELL_KM2:.2f} km2 ({core_new.sum()} px)")
print(f"Receded core water:           {core_rec.sum() * CELL_KM2:.2f} km2 ({core_rec.sum()} px)")
print(f"Net core change:              {(core_o.sum() - core_b.sum()) * CELL_KM2:+.2f} km2")
print()

# 2. Spatial Shift Null Test
# Create an inner common mask to strictly exclude edge effects from np.roll
margin = 25
inner_mask = np.zeros_like(common)
inner_mask[margin:-margin, margin:-margin] = True
common_inner = common & inner_mask

wb = water(hh_base, hv_base, -15.0, -18.0, common_inner)

print("=== SPATIAL SHIFT NULL TEST (HH -15 dB, HV -18 dB) ===")
print("k (shift px) | New (km2) | Receded (km2) | Net (km2) | Overlap (km2)")
print("-" * 65)

for k in [0, 1, 2, 5, 10, 20]:
    hh_s = np.roll(hh_obs, k, axis=1)
    hv_s = np.roll(hv_obs, k, axis=1)
    wo = water(hh_s, hv_s, -15.0, -18.0, common_inner)
    new = (wo & ~wb).sum() * CELL_KM2
    rec = (wb & ~wo).sum() * CELL_KM2
    overlap = (wo & wb).sum() * CELL_KM2
    net = (wo.sum() - wb.sum()) * CELL_KM2
    print(f"shift {k:2d} px ({k*20:3d}m): new {new:6.2f} km2 | receded {rec:6.2f} km2 | net {net:+6.2f} km2 | overlap {overlap:6.2f} km2")

print("\n(Note: Also running standard np.roll without margin erosion for exact comparison):")
wb_raw = water(hh_base, hv_base, -15.0, -18.0, common)
for k in [0, 2, 5, 10, 20]:
    hh_s = np.roll(hh_obs, k, axis=1)
    hv_s = np.roll(hv_obs, k, axis=1)
    wo = water(hh_s, hv_s, -15.0, -18.0, common)
    new = (wo & ~wb_raw).sum() * CELL_KM2
    rec = (wb_raw & ~wo).sum() * CELL_KM2
    print(f"raw shift {k:2d} px: new {new:6.2f} km2   receded {rec:6.2f} km2   net {wo.sum()*CELL_KM2 - wb_raw.sum()*CELL_KM2:+6.2f} km2")

