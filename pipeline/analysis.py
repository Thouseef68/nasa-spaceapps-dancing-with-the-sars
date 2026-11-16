"""pipeline/analysis.py
Consolidated analysis for NISAR Brahmaputra surface-water change.
Reads processed rasters and raw grids, computes all statistics on the common footprint,
and writes results/results.json and results/tables/*.csv.
"""
import csv
import json
import sys
from pathlib import Path

# Ensure workspace root is in python path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
from pipeline.step2_process import (
    CELL,
    GRID,
    LIN_CEIL,
    LIN_FLOOR,
    RAW,
    SCENES,
    align,
    aoi_bounds_utm,
    boxcar,
    load_pol,
    to_db,
)

CELL_KM2 = CELL * CELL / 1e6  # 0.0004 km2 per pixel
AOI_BOX_KM2 = 48000.0         # 48,000 km2 regional AOI box

OUT_DIR = ROOT / "results"
TABLES_DIR = OUT_DIR / "tables"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def water_mask(hh, hv, thr_hh, thr_hv, mask):
    """Dual-polarization water mask."""
    return mask & (hh < thr_hh) & (hv < thr_hv)


def run_analysis():
    print("=" * 70)
    print("NISAR Brahmaputra Analysis: Consolidating Results")
    print("=" * 70)

    bounds = aoi_bounds_utm()
    scenes = {}

    for name, pattern in SCENES.items():
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
    print(f"Aligned grid: {Wd} x {H} px at {CELL:.0f} m\n")

    # Valid dual-pol footprints per scene
    valids = {}
    for name, s in scenes.items():
        valids[name] = np.isfinite(s["HH"]) & np.isfinite(s["HV"])

    # Canonical common dual-pol footprint: baseline_jul02 & flood_jul26
    common = valids["baseline_jul02"] & valids["flood_jul26"]
    common_px = int(common.sum())
    common_km2 = round(common_px * CELL_KM2, 2)
    common_pct_aoi = round(common_km2 / AOI_BOX_KM2 * 100, 2)

    own_valid_km2 = {
        name: round(int(v.sum()) * CELL_KM2, 2) for name, v in valids.items()
    }

    # July 14 overlap with July 26 water
    jul26_headline_water = water_mask(
        scenes["flood_jul26"]["HH"], scenes["flood_jul26"]["HV"], -15.0, -18.0, valids["flood_jul26"]
    )
    jul26_water_in_jul14_swath = jul26_headline_water & valids["flood_jul14"]
    pct_jul26_water_outside_jul14 = round(
        (1.0 - (jul26_water_in_jul14_swath.sum() / max(jul26_headline_water.sum(), 1))) * 100,
        1,
    )

    hh_base = scenes["baseline_jul02"]["HH"]
    hv_base = scenes["baseline_jul02"]["HV"]
    hh_obs = scenes["flood_jul26"]["HH"]
    hv_obs = scenes["flood_jul26"]["HV"]

    # ---------------------------------------------------------
    # Radiometry: Stable land check across all 3 scenes
    # ---------------------------------------------------------
    all_3_valid = valids["baseline_jul02"] & valids["flood_jul14"] & valids["flood_jul26"]
    # Stable land defined as valid across all 3 and above headline water threshold in all 3
    stable_land_mask = all_3_valid.copy()
    for name, s in scenes.items():
        stable_land_mask &= (s["HH"] >= -15.0) | (s["HV"] >= -18.0)

    radiometry = {}
    hh_medians = []
    hv_medians = []
    for name in ["baseline_jul02", "flood_jul14", "flood_jul26"]:
        hh_m = round(float(np.nanmedian(scenes[name]["HH"][stable_land_mask])), 2)
        hv_m = round(float(np.nanmedian(scenes[name]["HV"][stable_land_mask])), 2)
        radiometry[name] = {"stable_land_HH_median_dB": hh_m, "stable_land_HV_median_dB": hv_m}
        hh_medians.append(hh_m)
        hv_medians.append(hv_m)

    hh_spread = round(max(hh_medians) - min(hh_medians), 2)
    hv_spread = round(max(hv_medians) - min(hv_medians), 2)
    radiometry["spread_HH_dB"] = hh_spread
    radiometry["spread_HV_dB"] = hv_spread

    # ---------------------------------------------------------
    # Task 1b: Headline Table on Common Footprint (HH -15, HV -18)
    # ---------------------------------------------------------
    head_wb = water_mask(hh_base, hv_base, -15.0, -18.0, common)
    head_wo = water_mask(hh_obs, hv_obs, -15.0, -18.0, common)
    head_new = head_wo & ~head_wb
    head_rec = head_wb & ~head_wo

    head_base_px = int(head_wb.sum())
    head_obs_px = int(head_wo.sum())
    head_new_px = int(head_new.sum())
    head_rec_px = int(head_rec.sum())
    head_net_px = head_obs_px - head_base_px

    headline = {
        "threshold_HH_dB": -15.0,
        "threshold_HV_dB": -18.0,
        "baseline_water_px": head_base_px,
        "baseline_water_km2": round(head_base_px * CELL_KM2, 2),
        "baseline_water_pct": round(head_base_px / common_px * 100, 2),
        "observed_water_px": head_obs_px,
        "observed_water_km2": round(head_obs_px * CELL_KM2, 2),
        "observed_water_pct": round(head_obs_px / common_px * 100, 2),
        "new_water_px": head_new_px,
        "new_water_km2": round(head_new_px * CELL_KM2, 2),
        "new_water_pct": round(head_new_px / common_px * 100, 2),
        "receded_water_px": head_rec_px,
        "receded_water_km2": round(head_rec_px * CELL_KM2, 2),
        "receded_water_pct": round(head_rec_px / common_px * 100, 2),
        "net_change_px": head_net_px,
        "net_change_km2": round(head_net_px * CELL_KM2, 2),
        "net_change_pct": round(head_net_px / common_px * 100, 2),
    }

    # ---------------------------------------------------------
    # Task 1d: Core Open Water Table (HH < -20, HV < -23)
    # ---------------------------------------------------------
    core_wb = water_mask(hh_base, hv_base, -20.0, -23.0, common)
    core_wo = water_mask(hh_obs, hv_obs, -20.0, -23.0, common)
    core_new = core_wo & ~core_wb
    core_rec = core_wb & ~core_wo

    core_base_px = int(core_wb.sum())
    core_obs_px = int(core_wo.sum())
    core_new_px = int(core_new.sum())
    core_rec_px = int(core_rec.sum())
    core_net_px = core_obs_px - core_base_px

    core_water = {
        "threshold_HH_dB": -20.0,
        "threshold_HV_dB": -23.0,
        "baseline_core_px": core_base_px,
        "baseline_core_km2": round(core_base_px * CELL_KM2, 2),
        "baseline_core_pct": round(core_base_px / common_px * 100, 2),
        "observed_core_px": core_obs_px,
        "observed_core_km2": round(core_obs_px * CELL_KM2, 2),
        "observed_core_pct": round(core_obs_px / common_px * 100, 2),
        "new_core_px": core_new_px,
        "new_core_km2": round(core_new_px * CELL_KM2, 2),
        "new_core_pct": round(core_new_px / common_px * 100, 2),
        "receded_core_px": core_rec_px,
        "receded_core_km2": round(core_rec_px * CELL_KM2, 2),
        "receded_core_pct": round(core_rec_px / common_px * 100, 2),
        "net_core_change_px": core_net_px,
        "net_core_change_km2": round(core_net_px * CELL_KM2, 2),
        "net_core_change_pct": round(core_net_px / common_px * 100, 2),
    }

    # ---------------------------------------------------------
    # Task 1e: Transitional Band Table for the Headline
    # ---------------------------------------------------------
    # Receded pixels breakdown
    rec_core_mask = head_rec & (hh_base < -20.0)
    rec_trans_mask = head_rec & (hh_base >= -20.0)
    rec_core_count = int(rec_core_mask.sum())
    rec_trans_count = int(rec_trans_mask.sum())
    rec_core_pct = round(rec_core_count / head_rec_px * 100, 1)
    rec_trans_pct = round(rec_trans_count / head_rec_px * 100, 1)

    rec_hh_vals = hh_base[head_rec]
    rec_hh_median = round(float(np.nanmedian(rec_hh_vals)), 2)
    rec_hh_q25 = round(float(np.nanpercentile(rec_hh_vals, 25)), 2)
    rec_hh_q75 = round(float(np.nanpercentile(rec_hh_vals, 75)), 2)

    # New pixels breakdown
    new_core_mask = head_new & (hh_obs < -20.0)
    new_trans_mask = head_new & (hh_obs >= -20.0)
    new_core_count = int(new_core_mask.sum())
    new_trans_count = int(new_trans_mask.sum())
    new_core_pct = round(new_core_count / head_new_px * 100, 1)
    new_trans_pct = round(new_trans_count / head_new_px * 100, 1)

    new_hh_vals = hh_obs[head_new]
    new_hh_median = round(float(np.nanmedian(new_hh_vals)), 2)
    new_hh_q25 = round(float(np.nanpercentile(new_hh_vals, 25)), 2)
    new_hh_q75 = round(float(np.nanpercentile(new_hh_vals, 75)), 2)

    transitional = {
        "receded_total_px": head_rec_px,
        "receded_total_km2": headline["receded_water_km2"],
        "receded_core_px": rec_core_count,
        "receded_core_km2": round(rec_core_count * CELL_KM2, 2),
        "receded_core_pct": rec_core_pct,
        "receded_transitional_px": rec_trans_count,
        "receded_transitional_km2": round(rec_trans_count * CELL_KM2, 2),
        "receded_transitional_pct": rec_trans_pct,
        "receded_HH_median_dB": rec_hh_median,
        "receded_HH_q25_dB": rec_hh_q25,
        "receded_HH_q75_dB": rec_hh_q75,
        "new_total_px": head_new_px,
        "new_total_km2": headline["new_water_km2"],
        "new_core_px": new_core_count,
        "new_core_km2": round(new_core_count * CELL_KM2, 2),
        "new_core_pct": new_core_pct,
        "new_transitional_px": new_trans_count,
        "new_transitional_km2": round(new_trans_count * CELL_KM2, 2),
        "new_transitional_pct": new_trans_pct,
        "new_HH_median_dB": new_hh_median,
        "new_HH_q25_dB": new_hh_q25,
        "new_HH_q75_dB": new_hh_q75,
    }

    # ---------------------------------------------------------
    # Task 1c: Sweep Table (HH -21.0 to -12.0, HV = HH - 3)
    # ---------------------------------------------------------
    sweep_results = []
    for t_hh in np.arange(-21.0, -11.5, 0.5):
        t_hv = t_hh - 3.0
        wb = water_mask(hh_base, hv_base, t_hh, t_hv, common)
        wo = water_mask(hh_obs, hv_obs, t_hh, t_hv, common)
        n_w = wo & ~wb
        r_w = wb & ~wo

        b_px = int(wb.sum())
        o_px = int(wo.sum())
        nw_px = int(n_w.sum())
        rc_px = int(r_w.sum())
        nt_px = o_px - b_px

        row = {
            "threshold_HH_dB": round(float(t_hh), 1),
            "threshold_HV_dB": round(float(t_hv), 1),
            "baseline_water_km2": round(b_px * CELL_KM2, 2),
            "baseline_water_pct": round(b_px / common_px * 100, 2),
            "observed_water_km2": round(o_px * CELL_KM2, 2),
            "observed_water_pct": round(o_px / common_px * 100, 2),
            "new_water_km2": round(nw_px * CELL_KM2, 2),
            "new_water_pct": round(nw_px / common_px * 100, 2),
            "receded_water_km2": round(rc_px * CELL_KM2, 2),
            "receded_water_pct": round(rc_px / common_px * 100, 2),
            "net_change_km2": round(nt_px * CELL_KM2, 2),
            "net_change_pct": round(nt_px / common_px * 100, 2),
        }
        sweep_results.append(row)

    # Save sweep table to CSV
    with open(TABLES_DIR / "sweep.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sweep_results[0].keys())
        writer.writeheader()
        writer.writerows(sweep_results)

    # Sweep metrics
    all_net_km2 = [r["net_change_km2"] for r in sweep_results]
    sweep_summary = {
        "min_net_change_km2": min(all_net_km2),
        "max_net_change_km2": max(all_net_km2),
        "sign_consistent_negative": all(x < 0 for x in all_net_km2),
        # Range between -15 and -21 dB
        "physical_transitional_range_net_min_km2": min(
            r["net_change_km2"] for r in sweep_results if r["threshold_HH_dB"] <= -15.0
        ),
        "physical_transitional_range_net_max_km2": max(
            r["net_change_km2"] for r in sweep_results if r["threshold_HH_dB"] <= -15.0
        ),
    }

    # Conservative row: HH -18.0, HV -21.0
    cons_row = next(r for r in sweep_results if r["threshold_HH_dB"] == -18.0)
    conservative = {
        "threshold_HH_dB": -18.0,
        "threshold_HV_dB": -21.0,
        "baseline_water_km2": cons_row["baseline_water_km2"],
        "baseline_water_pct": cons_row["baseline_water_pct"],
        "observed_water_km2": cons_row["observed_water_km2"],
        "observed_water_pct": cons_row["observed_water_pct"],
        "new_water_km2": cons_row["new_water_km2"],
        "new_water_pct": cons_row["new_water_pct"],
        "receded_water_km2": cons_row["receded_water_km2"],
        "receded_water_pct": cons_row["receded_water_pct"],
        "net_change_km2": cons_row["net_change_km2"],
        "net_change_pct": cons_row["net_change_pct"],
    }

    # ---------------------------------------------------------
    # Task 1g & Task 2: Shift Null Test (Headline & Core)
    # ---------------------------------------------------------
    # Crop 20 px from edges where np.roll wraps around
    crop_border = 20
    inner_mask = np.zeros_like(common)
    inner_mask[crop_border:-crop_border, crop_border:-crop_border] = True
    common_cropped = common & inner_mask
    common_cropped_px = int(common_cropped.sum())
    common_cropped_km2 = round(common_cropped_px * CELL_KM2, 2)

    head_wb_crop = water_mask(hh_base, hv_base, -15.0, -18.0, common_cropped)
    core_wb_crop = water_mask(hh_base, hv_base, -20.0, -23.0, common_cropped)

    shift_null_results = []
    core_net_changes_in_null = []

    for k in [0, 2, 5, 10, 20]:
        hh_s = np.roll(hh_obs, k, axis=1)
        hv_s = np.roll(hv_obs, k, axis=1)

        # Headline shifted
        head_wo_crop = water_mask(hh_s, hv_s, -15.0, -18.0, common_cropped)
        h_new = (head_wo_crop & ~head_wb_crop).sum() * CELL_KM2
        h_rec = (head_wb_crop & ~head_wo_crop).sum() * CELL_KM2
        h_net = (head_wo_crop.sum() - head_wb_crop.sum()) * CELL_KM2

        # Core shifted
        core_wo_crop = water_mask(hh_s, hv_s, -20.0, -23.0, common_cropped)
        c_new = (core_wo_crop & ~core_wb_crop).sum() * CELL_KM2
        c_rec = (core_wb_crop & ~core_wo_crop).sum() * CELL_KM2
        c_net = (core_wo_crop.sum() - core_wb_crop.sum()) * CELL_KM2

        core_net_changes_in_null.append(round(float(c_net), 2))

        shift_null_results.append({
            "shift_px": k,
            "shift_meters": k * int(CELL),
            "headline_new_km2": round(float(h_new), 2),
            "headline_receded_km2": round(float(h_rec), 2),
            "headline_net_km2": round(float(h_net), 2),
            "core_new_km2": round(float(c_new), 2),
            "core_receded_km2": round(float(c_rec), 2),
            "core_net_km2": round(float(c_net), 2),
        })

    with open(TABLES_DIR / "shift_null.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=shift_null_results[0].keys())
        writer.writeheader()
        writer.writerows(shift_null_results)

    # ---------------------------------------------------------
    # Task 2: Core-water sensitivity to HV cutoff (-22, -23, -24)
    # ---------------------------------------------------------
    core_hv_sensitivity = []
    for c_hv in [-22.0, -23.0, -24.0]:
        c_b = water_mask(hh_base, hv_base, -20.0, c_hv, common)
        c_o = water_mask(hh_obs, hv_obs, -20.0, c_hv, common)
        c_net = (c_o.sum() - c_b.sum()) * CELL_KM2
        core_hv_sensitivity.append({
            "threshold_HH_dB": -20.0,
            "threshold_HV_dB": c_hv,
            "baseline_core_km2": round(float(c_b.sum() * CELL_KM2), 2),
            "observed_core_km2": round(float(c_o.sum() * CELL_KM2), 2),
            "net_core_change_km2": round(float(c_net), 2),
        })

    core_spread_in_null = [min(core_net_changes_in_null), max(core_net_changes_in_null)]
    core_change_val = core_water["net_core_change_km2"]
    is_inside_null_spread = (core_change_val >= core_spread_in_null[0]) and (
        core_change_val <= core_spread_in_null[1]
    )

    core_uncertainty = {
        "unshifted_net_change_km2": core_change_val,
        "shifted_null_net_spread_km2": core_spread_in_null,
        "is_inside_null_spread": is_inside_null_spread,
        "distinguishable_from_zero": not is_inside_null_spread,
        "hv_cutoff_sensitivity": core_hv_sensitivity,
    }

    # ---------------------------------------------------------
    # Task 3: Independent Validation Status
    # ---------------------------------------------------------
    validation = {
        "status": "pending",
        "reason": (
            "OPERA DSWx-S1 returned 0 products for 2026-07-25 to 2026-07-27 over the AOI. "
            "Sentinel-1 GRD acquisition exists for 2026-07-25 (S1D_IW_GRDH_1SDV_20260725T120434) "
            "intersecting the footprint, but cannot be terrain-corrected and calibrated to the 20 m grid "
            "without a dedicated SAR preprocessing suite (such as ESA SNAP). Validation remains pending "
            "independent calibrated imagery."
        ),
        "opera_dswx_products_found": 0,
        "sentinel1_grd_products_found": 1,
        "sentinel1_scene_id": "S1D_IW_GRDH_1SDV_20260725T120434_20260725T120459_003830_006E63_520C",
    }

    # ---------------------------------------------------------
    # Consolidate into full results dictionary
    # ---------------------------------------------------------
    results = {
        "mission": "NISAR",
        "product_level": "L2_PR_GCOV",
        "orbit_pass": "descending",
        "relative_orbit_track": 91,
        "frame": 76,
        "pixel_size_meters": int(CELL),
        "pixel_area_km2": CELL_KM2,
        "footprint": {
            "aoi_box_km2": AOI_BOX_KM2,
            "common_dual_pol_px": common_px,
            "common_dual_pol_km2": common_km2,
            "percent_of_aoi_box": common_pct_aoi,
            "own_valid_km2": own_valid_km2,
            "jul14_swath_truncation": {
                "percent_jul26_water_outside_jul14_footprint": pct_jul26_water_outside_jul14
            },
        },
        "radiometry": radiometry,
        "core_water": core_water,
        "headline": headline,
        "conservative": conservative,
        "transitional_composition": transitional,
        "sweep_summary": sweep_summary,
        "shift_null_test": {
            "cropped_common_km2": common_cropped_km2,
            "shifts": shift_null_results,
        },
        "core_water_uncertainty": core_uncertainty,
        "validation": validation,
    }

    # Write results/results.json
    results_path = OUT_DIR / "results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Save additional tables to CSV
    with open(TABLES_DIR / "headline.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headline.keys())
        writer.writeheader()
        writer.writerow(headline)

    with open(TABLES_DIR / "core_water.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=core_water.keys())
        writer.writeheader()
        writer.writerow(core_water)

    with open(TABLES_DIR / "transitional_composition.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=transitional.keys())
        writer.writeheader()
        writer.writerow(transitional)

    print(f"\nWrote full results to {results_path.resolve()}")
    print("Headline:", headline)
    print("Core Water:", core_water)
    print("Core Uncertainty:", core_uncertainty)
    return results


if __name__ == "__main__":
    run_analysis()

