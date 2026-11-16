import csv
import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
import numpy as np
from pipeline.step2_process import aoi_bounds_utm, load_pol, align, SCENES, to_db, boxcar, RAW, OUT

print("Loading raw scenes for sensitivity sweep...")
bounds = aoi_bounds_utm()
scenes = {}
for name in ["baseline_jul02", "flood_jul26"]:
    pattern = SCENES[name]
    path = next(RAW.glob(pattern))
    print(f"Loading {name} ({path.name})...")
    hh, west, north = load_pol(path, "HHHH", bounds)
    hv, _, _ = load_pol(path, "HVHV", bounds)
    scenes[name] = {
        "HH": to_db(boxcar(hh)),
        "HV": to_db(boxcar(hv)),
        "west": west,
        "north": north,
    }

W, N, H, Wd = align(scenes)
print(f"Aligned grid: {Wd} x {H} px")

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
common_km2 = common.sum() * 0.0004
print(f"Common footprint: {common_km2:.2f} km2\n")

results = []
for t_hh in np.arange(-21.0, -11.5, 0.5):
    t_hv = t_hh - 3.0
    wb = common & (hh_base < t_hh) & (hv_base < t_hv)
    wo = common & (hh_obs < t_hh) & (hv_obs < t_hv)
    new = wo & ~wb
    rec = wb & ~wo
    base_km2 = wb.sum() * 0.0004
    obs_km2 = wo.sum() * 0.0004
    new_km2 = new.sum() * 0.0004
    rec_km2 = rec.sum() * 0.0004
    net_km2 = (wo.sum() - wb.sum()) * 0.0004
    results.append({
        "t_hh": round(t_hh, 1),
        "t_hv": round(t_hv, 1),
        "baseline_km2": round(base_km2, 2),
        "jul26_km2": round(obs_km2, 2),
        "new_km2": round(new_km2, 2),
        "receded_km2": round(rec_km2, 2),
        "net_km2": round(net_km2, 2),
    })

print(f"{'HH (dB)':>8} {'HV (dB)':>8} {'Base (km2)':>12} {'Jul26 (km2)':>12} {'New (km2)':>10} {'Receded (km2)':>14} {'Net (km2)':>10}")
print("-" * 80)
for r in results:
    print(
        f"{r['t_hh']:8.1f} {r['t_hv']:8.1f} {r['baseline_km2']:12.2f} {r['jul26_km2']:12.2f} "
        f"{r['new_km2']:10.2f} {r['receded_km2']:14.2f} {r['net_km2']:+10.2f} km²"
    )

with open(OUT / "sensitivity_sweep.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"\nSaved sweep results to {OUT / 'sensitivity_sweep.csv'}")
