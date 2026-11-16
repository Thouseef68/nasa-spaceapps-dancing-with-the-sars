"""pipeline/run_validation.py
Independent validation module for NISAR vs Sentinel-1 proxy comparison.
Supports:
  - Route 1: ESA SNAP (gpt) calibration and terrain correction from raw GRD ZIP.
  - Route 2: On-demand ASF RTC GeoTIFF (--rtc <path> or placed in data/s1/rtc/).
  - Fallback: Records blocked status per protocol if neither tool/product is ready.

Outputs:
  - results/validation.json
  - results/tables/validation.csv
  - results/validation_overlay.png (when calibrated raster is available)
  - web/validation.json
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
WEB_DIR = ROOT / "web"
S1_DIR = ROOT / "data/s1"
PROCESSED_S1_DIR = S1_DIR / "processed"
NISAR_PROCESSED_DIR = ROOT / "data/processed"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)
WEB_DIR.mkdir(parents=True, exist_ok=True)
S1_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_S1_DIR.mkdir(parents=True, exist_ok=True)

SCENE_ID = "S1D_IW_GRDH_1SDV_20260725T120434_20260725T120459_003830_006E63_520C"
ZIP_PATH = S1_DIR / f"{SCENE_ID}.zip"
CELL_KM2 = 0.0004  # 20m x 20m = 0.0004 km2


def find_gpt(custom_path=None):
    """Finds ESA SNAP gpt executable from custom path, env var, PATH, or standard paths."""
    candidates = []
    if custom_path:
        candidates.append(custom_path)
    if os.environ.get("SNAP_GPT_PATH"):
        candidates.append(os.environ.get("SNAP_GPT_PATH"))
    
    # Check PATH
    which_gpt = shutil.which("gpt") or shutil.which("gpt.exe")
    if which_gpt:
        candidates.append(which_gpt)

    # Standard installation paths on Windows
    user_home = Path.home()
    candidates.extend([
        str(user_home / "snap/bin/gpt.exe"),
        r"C:\Program Files\esa-snap\bin\gpt.exe",
        r"C:\Program Files\snap\bin\gpt.exe",
        r"C:\Program Files (x86)\esa-snap\bin\gpt.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\snap\bin\gpt.exe"),
        r"C:\snap\bin\gpt.exe",
    ])

    for c in candidates:
        if c and Path(c).is_file():
            try:
                res = subprocess.run([c, "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
                if res.returncode == 0 or "Usage: gpt" in res.stdout or "Usage: gpt" in res.stderr:
                    return str(Path(c).resolve())
            except Exception:
                pass
    return None


def find_rtc_file(custom_path=None):
    """Finds an ASF RTC GeoTIFF file from custom path or standard directories."""
    if custom_path and Path(custom_path).is_file():
        return str(Path(custom_path).resolve())
    
    # Search in data/s1/ and data/s1/rtc/
    search_dirs = [S1_DIR / "rtc", S1_DIR]
    for d in search_dirs:
        if d.is_dir():
            for f in d.glob("*.tif"):
                fname = f.name.lower()
                if "rtc" in fname or ("vv" in fname and "water" not in fname and "calibrated" not in fname):
                    return str(f.resolve())
    return None


def otsu_threshold(data_db, n_bins=256):
    """Computes Otsu threshold for 1D float array of backscatter dB."""
    valid_data = data_db[np.isfinite(data_db)]
    if len(valid_data) == 0:
        return -16.0
    
    counts, bin_edges = np.histogram(valid_data, bins=n_bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    
    total = len(valid_data)
    current_max = 0.0
    threshold = bin_centers[0]
    
    weight_b = 0.0
    sum_b = 0.0
    total_sum = np.sum(counts * bin_centers)
    
    for i in range(len(counts)):
        weight_b += counts[i]
        if weight_b == 0:
            continue
        weight_f = total - weight_b
        if weight_f == 0:
            break
        
        sum_b += counts[i] * bin_centers[i]
        mean_b = sum_b / weight_b
        mean_f = (total_sum - sum_b) / weight_f
        
        var_between = weight_b * weight_f * ((mean_b - mean_f) ** 2)
        if var_between > current_max:
            current_max = var_between
            threshold = bin_centers[i]
            
    return float(threshold)


def generate_snap_graph_xml(zip_path, output_tif_path):
    """Creates a SNAP GPT XML graph for S1 GRD calibration and terrain correction."""
    xml_content = f"""<graph id="Graph">
  <version>1.0</version>
  <node id="Read">
    <operator>Read</operator>
    <sources/>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>{zip_path}</file>
    </parameters>
  </node>
  <node id="Apply-Orbit-File">
    <operator>Apply-Orbit-File</operator>
    <sources>
      <sourceProduct refid="Read"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <orbitType>Sentinel Precise (Auto Download)</orbitType>
      <polyDegree>3</polyDegree>
      <continueOnFail>true</continueOnFail>
    </parameters>
  </node>
  <node id="ThermalNoiseRemoval">
    <operator>ThermalNoiseRemoval</operator>
    <sources>
      <sourceProduct refid="Apply-Orbit-File"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <selectedPolarisations>VV,VH</selectedPolarisations>
      <removeThermalNoise>true</removeThermalNoise>
      <reIntroduceThermalNoise>false</reIntroduceThermalNoise>
    </parameters>
  </node>
  <node id="Calibration">
    <operator>Calibration</operator>
    <sources>
      <sourceProduct refid="ThermalNoiseRemoval"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <sourceBands/>
      <auxFile>Product Auxiliary</auxFile>
      <externalAuxFile/>
      <outputImageInComplex>false</outputImageInComplex>
      <outputImageScaleInDb>false</outputImageScaleInDb>
      <createGammaBand>false</createGammaBand>
      <createBetaBand>false</createBetaBand>
      <selectedPolarisations>VV,VH</selectedPolarisations>
      <outputSigmaBand>true</outputSigmaBand>
      <outputGammaBand>false</outputGammaBand>
      <outputBetaBand>false</outputBetaBand>
    </parameters>
  </node>
  <node id="Speckle-Filter">
    <operator>Speckle-Filter</operator>
    <sources>
      <sourceProduct refid="Calibration"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <sourceBands/>
      <filter>Refined Lee</filter>
      <filterSizeX>5</filterSizeX>
      <filterSizeY>5</filterSizeY>
      <dampingFactor>2</dampingFactor>
      <estimateENL>true</estimateENL>
      <enl>1.0</enl>
      <numLooksStr>1</numLooksStr>
      <windowSize>7x7</windowSize>
      <targetWindowSizeStr>3x3</targetWindowSizeStr>
      <sigmaStr>0.9</sigmaStr>
      <anSize>50</anSize>
    </parameters>
  </node>
  <node id="Terrain-Correction">
    <operator>Terrain-Correction</operator>
    <sources>
      <sourceProduct refid="Speckle-Filter"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <sourceBands/>
      <demName>SRTM 1Sec HGT</demName>
      <externalDEMFile/>
      <externalDEMNoDataValue>0.0</externalDEMNoDataValue>
      <externalDEMApplyEGM>true</externalDEMApplyEGM>
      <demResamplingMethod>BILINEAR_INTERPOLATION</demResamplingMethod>
      <imgResamplingMethod>BILINEAR_INTERPOLATION</imgResamplingMethod>
      <pixelSpacingInMeter>20.0</pixelSpacingInMeter>
      <pixelSpacingInDegree>1.796630568239043E-4</pixelSpacingInDegree>
      <mapProjection>EPSG:32646</mapProjection>
      <alignToStandardGrid>false</alignToStandardGrid>
      <standardGridOriginX>0.0</standardGridOriginX>
      <standardGridOriginY>0.0</standardGridOriginY>
      <nodataValueAtSea>false</nodataValueAtSea>
      <saveDEM>false</saveDEM>
      <saveLatLon>false</saveLatLon>
      <saveIncidenceAngleFromEllipsoid>false</saveIncidenceAngleFromEllipsoid>
      <saveLocalIncidenceAngle>false</saveLocalIncidenceAngle>
      <saveProjectedLocalIncidenceAngle>false</saveProjectedLocalIncidenceAngle>
      <saveSelectedSourceBand>true</saveSelectedSourceBand>
      <outputComplex>false</outputComplex>
      <applyRadiometricNormalization>false</applyRadiometricNormalization>
      <saveSigmaNought>false</saveSigmaNought>
      <saveGammaNought>false</saveGammaNought>
      <saveBetaNought>false</saveBetaNought>
      <incidenceAngleForSigma0>Use projected local incidence angle from DEM</incidenceAngleForSigma0>
      <incidenceAngleForGamma0>Use projected local incidence angle from DEM</incidenceAngleForGamma0>
      <auxFile>Latest Auxiliary File</auxFile>
      <externalAuxFile/>
    </parameters>
  </node>
  <node id="Write">
    <operator>Write</operator>
    <sources>
      <sourceProduct refid="Terrain-Correction"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>{output_tif_path}</file>
      <formatName>GeoTIFF-BigTIFF</formatName>
    </parameters>
  </node>
</graph>
"""
    xml_path = S1_DIR / "s1_process_graph.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    return xml_path


def compute_metrics(nisar_mask, s1_mask, eval_mask):
    """Computes IoU, F1, Precision, Recall, Accuracy over eval_mask."""
    n_w = nisar_mask & eval_mask
    s_w = s1_mask & eval_mask
    
    tp = int(np.logical_and(n_w, s_w).sum())
    fp = int(np.logical_and(n_w, ~s_w).sum())
    fn = int(np.logical_and(~n_w, s_w).sum())
    tn = int(np.logical_and(~n_w, ~s_w & eval_mask).sum())
    
    iou = round(tp / max(tp + fp + fn, 1), 4)
    precision = round(tp / max(tp + fp, 1), 4)
    recall = round(tp / max(tp + fn, 1), 4)
    f1 = round(2 * tp / max(2 * tp + fp + fn, 1), 4)
    accuracy = round((tp + tn) / max(tp + fp + fn + tn, 1), 4)
    
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "iou": iou,
        "f1": f1,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
    }


def generate_validation_overlay_plot(nisar_water, s1_water, eval_mask, s1_vv_db, s1_thr):
    """Generates results/validation_overlay.png comparing NISAR and Sentinel-1 water."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), dpi=200)

    # Left: S1 backscatter histogram and Otsu threshold
    ax_hist = axes[0]
    valid_db = s1_vv_db[eval_mask]
    counts, bins, _ = ax_hist.hist(valid_db, bins=100, range=(-35, 5), color="#4a7bb0", alpha=0.7, edgecolor="none", density=True)
    ax_hist.axvline(s1_thr, color="#d7191c", linestyle="--", linewidth=2, label=f"Otsu Threshold: {s1_thr:.2f} dB")
    ax_hist.set_title("Sentinel-1 VV Backscatter Histogram & Otsu Threshold", fontsize=12, fontweight="bold")
    ax_hist.set_xlabel("Backscatter (dB)", fontsize=11)
    ax_hist.set_ylabel("Probability Density", fontsize=11)
    ax_hist.legend(loc="upper right", frameon=True)
    ax_hist.grid(True, linestyle=":", alpha=0.5)

    # Right: Spatial overlay over Brahmaputra river reach
    # Crop to a representative Brahmaputra reach (e.g. columns 1000 to 5000, rows 600 to 1800)
    # Check where water is dense
    water_cols = np.where(nisar_water.any(axis=0))[0]
    water_rows = np.where(nisar_water.any(axis=1))[0]
    if len(water_cols) > 0 and len(water_rows) > 0:
        r0, r1 = max(0, water_rows[0] - 50), min(nisar_water.shape[0], water_rows[-1] + 50)
        c0, c1 = max(0, water_cols[0] - 50), min(nisar_water.shape[1], water_cols[-1] + 50)
        # Choose a central sub-window for high-resolution visual inspection
        mid_c = (c0 + c1) // 2
        w_sub = 3000
        c_sub0 = max(0, mid_c - w_sub // 2)
        c_sub1 = min(nisar_water.shape[1], mid_c + w_sub // 2)
    else:
        r0, r1 = 0, nisar_water.shape[0]
        c_sub0, c_sub1 = 0, nisar_water.shape[1]

    sub_eval = eval_mask[r0:r1, c_sub0:c_sub1]
    sub_nisar = nisar_water[r0:r1, c_sub0:c_sub1] & sub_eval
    sub_s1 = s1_water[r0:r1, c_sub0:c_sub1] & sub_eval

    # Color map:
    # 0 = Background / Invalid (dark gray)
    # 1 = Land in evaluation footprint (light gray)
    # 2 = Sentinel-1 only water (Magenta #d01c8b)
    # 3 = NISAR only water (Orange #fdae61)
    # 4 = Both agree water (Deep Blue #2b83ba)
    rgb = np.zeros((r1 - r0, c_sub1 - c_sub0, 3), dtype=np.uint8)
    rgb[:] = [240, 240, 240]  # default land
    rgb[~sub_eval] = [200, 200, 200]  # outside common footprint

    rgb[sub_s1 & ~sub_nisar] = [208, 28, 139]   # S1 only
    rgb[sub_nisar & ~sub_s1] = [253, 174, 97]   # NISAR only
    rgb[sub_nisar & sub_s1] = [43, 131, 186]    # Both agree

    ax_map = axes[1]
    ax_map.imshow(rgb)
    ax_map.set_title("Water Agreement Overlay (Sentinel-1 vs NISAR)", fontsize=12, fontweight="bold")
    ax_map.axis("off")

    # Custom legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2b83ba", label="Agreement (Both S1 & NISAR)"),
        Patch(facecolor="#fdae61", label="NISAR Water Only"),
        Patch(facecolor="#d01c8b", label="Sentinel-1 Water Only"),
        Patch(facecolor="#f0f0f0", edgecolor="#999999", label="Dry Land (Common Footprint)"),
    ]
    ax_map.legend(handles=legend_elements, loc="lower right", frameon=True, fontsize=9)

    plt.tight_layout()
    overlay_path = RESULTS_DIR / "validation_overlay.png"
    plt.savefig(overlay_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Generated validation overlay figure: {overlay_path.resolve()}")


def run_validation(gpt_path=None, rtc_path=None):
    print("=" * 70)
    print("TASK: Independent Validation of NISAR vs Sentinel-1 (Proxy)")
    print("=" * 70)

    rtc_file = find_rtc_file(rtc_path)
    gpt_exe = find_gpt(gpt_path)

    # Determine execution route:
    use_rtc = rtc_file is not None
    use_gpt = (not use_rtc) and (gpt_exe is not None)

    print(f"Route 1 (ESA SNAP gpt): {gpt_exe if gpt_exe else 'NOT INSTALLED'}")
    print(f"Route 2 (ASF RTC GeoTIFF): {rtc_file if rtc_file else 'NOT FOUND'}")

    if not (use_rtc or use_gpt):
        status = "blocked"
        step_blocked = "STEP 2: Calibrate, terrain-correct, and grid to the NISAR footprint"
        reason = "blocked: SNAP not available"
        print(f"Stopping at Step 2: {reason}")

        val_data = {
            "status": status,
            "step_blocked": step_blocked,
            "reason": reason,
            "product_id": SCENE_ID,
            "acquisition_date": "2026-07-25T12:04:34Z",
            "nisar_observation_date": "2026-07-26T12:34:22Z",
            "offset_days": 1,
            "comparison_type": "proxy comparison (one-day temporal offset)",
            "s1_threshold_dB": None,
            "s1_threshold_method": "blocked: pending SNAP terrain correction and calibration",
            "s1_water_km2": None,
            "metrics": {
                "headline_vs_s1": None,
                "core_vs_s1": None,
                "permanent_water_agreement": None,
                "shifted_null": None,
            },
            "pixel_counts": None,
            "footprint_km2": None,
            "warnings": [
                "Proxy comparison with Sentinel-1 acquired 2026-07-25 (one day before the NISAR observation).",
                "OPERA DSWx-S1 returned 0 products over the AOI for 2026-07-25 to 2026-07-27.",
                "Sentinel-1 Level-1 GRD product requires ESA SNAP gpt for calibration, thermal noise removal, Refined Lee speckle filtering, and SRTM 1-sec terrain correction to EPSG:32646 20 m grid.",
                "ESA SNAP gpt is not installed on this system. Validation stopped at STEP 2 per protocol.",
            ],
            "reporting_statement": (
                "Independent validation against Sentinel-1 (acquired 2026-07-25, one day before the NISAR observation) "
                "was not completed. The Level-1 product was downloaded and verified; calibration and terrain correction "
                "were not performed, so no agreement metrics are reported. All classifications remain unvalidated."
            ),
        }

        # Write results/validation.json
        val_json_path = RESULTS_DIR / "validation.json"
        with open(val_json_path, "w", encoding="utf-8") as f:
            json.dump(val_data, f, indent=2)
        print(f"Wrote {val_json_path.resolve()}")

        # Copy to web/validation.json
        shutil.copy(val_json_path, WEB_DIR / "validation.json")
        print(f"Copied to {WEB_DIR / 'validation.json'}")

        # Write results/tables/validation.csv
        csv_rows = [
            {
                "comparison": "Headline_vs_S1",
                "status": status,
                "product_id": SCENE_ID,
                "acquisition_date": "2026-07-25",
                "offset_days": 1,
                "s1_threshold_dB": "N/A",
                "s1_water_km2": "N/A",
                "iou": "N/A",
                "f1": "N/A",
                "precision": "N/A",
                "recall": "N/A",
                "accuracy": "N/A",
                "notes": reason,
            },
            {
                "comparison": "Core_vs_S1",
                "status": status,
                "product_id": SCENE_ID,
                "acquisition_date": "2026-07-25",
                "offset_days": 1,
                "s1_threshold_dB": "N/A",
                "s1_water_km2": "N/A",
                "iou": "N/A",
                "f1": "N/A",
                "precision": "N/A",
                "recall": "N/A",
                "accuracy": "N/A",
                "notes": reason,
            },
            {
                "comparison": "Permanent_Water",
                "status": status,
                "product_id": SCENE_ID,
                "acquisition_date": "2026-07-25",
                "offset_days": 1,
                "s1_threshold_dB": "N/A",
                "s1_water_km2": "N/A",
                "iou": "N/A",
                "f1": "N/A",
                "precision": "N/A",
                "recall": "N/A",
                "accuracy": "N/A",
                "notes": reason,
            },
            {
                "comparison": "Shifted_Null",
                "status": status,
                "product_id": SCENE_ID,
                "acquisition_date": "2026-07-25",
                "offset_days": 1,
                "s1_threshold_dB": "N/A",
                "s1_water_km2": "N/A",
                "iou": "N/A",
                "f1": "N/A",
                "precision": "N/A",
                "recall": "N/A",
                "accuracy": "N/A",
                "notes": reason,
            },
        ]

        csv_path = TABLES_DIR / "validation.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"Wrote {csv_path.resolve()}")

        # Update results/results.json validation block
        results_json_path = RESULTS_DIR / "results.json"
        if results_json_path.exists():
            with open(results_json_path, "r", encoding="utf-8") as f:
                res_all = json.load(f)
            res_all["validation"] = val_data
            with open(results_json_path, "w", encoding="utf-8") as f:
                json.dump(res_all, f, indent=2)
            shutil.copy(results_json_path, WEB_DIR / "results.json")
            print("Updated results/results.json with validation status.")

        return val_data

    # -------------------------------------------------------------
    # Route 1 or Route 2 Execution
    # -------------------------------------------------------------
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject

    nisar_water_path = NISAR_PROCESSED_DIR / "flood_jul26_water.tif"
    nisar_core_path = NISAR_PROCESSED_DIR / "core_flood_jul26_water.tif"
    nisar_base_path = NISAR_PROCESSED_DIR / "baseline_jul02_water.tif"

    with rasterio.open(nisar_water_path) as ref_ds:
        ref_profile = ref_ds.profile
        ref_shape = ref_ds.shape
        ref_transform = ref_ds.transform
        ref_crs = ref_ds.crs
        nisar_headline = (ref_ds.read(1) > 0)

    with rasterio.open(nisar_core_path) as ds:
        nisar_core = (ds.read(1) > 0)
    with rasterio.open(nisar_base_path) as ds:
        nisar_base = (ds.read(1) > 0)

    common_valid_path = NISAR_PROCESSED_DIR / "common_valid.tif"
    if common_valid_path.exists():
        with rasterio.open(common_valid_path) as ds:
            nisar_common = (ds.read(1) > 0)
    else:
        nisar_common = np.ones(ref_shape, dtype=bool)

    if use_rtc:
        print(f"Executing Route 2 using ASF RTC GeoTIFF: {rtc_file}")
        source_tif = rtc_file
        method_desc = "ASF On-Demand RTC Gamma-0 backscatter (reprojected to EPSG:32646 at 20 m)"
        radiometric_convention = "gamma0"
    else:
        print(f"Executing Route 1 using SNAP gpt: {gpt_exe}")
        out_calibrated_tif = PROCESSED_S1_DIR / "s1_calibrated.tif"
        graph_xml = generate_snap_graph_xml(ZIP_PATH.resolve(), out_calibrated_tif.resolve())
        print(f"Running SNAP graph: {graph_xml}...")
        cmd = [gpt_exe, str(graph_xml.resolve())]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print(f"SNAP processing failed: {res.stderr}")
            raise RuntimeError(f"SNAP processing failed: {res.stderr}")
        source_tif = str(out_calibrated_tif.resolve())
        method_desc = "ESA SNAP Level-1 GRD Sigma-0 backscatter (calibrated and terrain corrected to EPSG:32646 at 20 m)"
        radiometric_convention = "sigma0"

    print(f"Reprojecting {source_tif} to NISAR grid ({ref_shape[1]}x{ref_shape[0]} at 20 m)...")
    s1_raw_grid = np.full(ref_shape, np.nan, dtype=np.float32)
    with rasterio.open(source_tif) as s1_ds:
        reproject(
            source=rasterio.band(s1_ds, 1),
            destination=s1_raw_grid,
            src_transform=s1_ds.transform,
            src_crs=s1_ds.crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            resampling=Resampling.bilinear,
        )

    # Handle linear vs dB scaling
    finite_raw = s1_raw_grid[np.isfinite(s1_raw_grid)]
    if len(finite_raw) > 0 and np.nanmedian(finite_raw) > 0.0:
        # Linear amplitude / intensity -> convert to dB
        s1_vv_db = np.full(ref_shape, np.nan, dtype=np.float32)
        valid_pos = np.isfinite(s1_raw_grid) & (s1_raw_grid > 0.0)
        s1_vv_db[valid_pos] = 10.0 * np.log10(s1_raw_grid[valid_pos])
    else:
        # Already in dB
        s1_vv_db = s1_raw_grid

    s1_valid = np.isfinite(s1_vv_db)
    eval_mask = nisar_common & s1_valid
    eval_km2 = round(float(eval_mask.sum()) * CELL_KM2, 2)
    print(f"Valid evaluation footprint: {eval_km2} km2")

    # Otsu threshold on valid data in evaluation mask
    s1_thr = otsu_threshold(s1_vv_db[eval_mask])
    print(f"Derived Sentinel-1 Otsu threshold: {s1_thr:.2f} dB")

    warnings = [
        "Proxy comparison with Sentinel-1 acquired 2026-07-25 (one day before the NISAR observation).",
        "Differences reflect both sensor physics (C-band vs L-band) and potential 24-hour hydrodynamic change.",
    ]
    if use_rtc:
        warnings.append("Used ASF On-Demand RTC product (gamma-0 convention, native ~30 m resolution resampled to 20 m).")
    
    if not (-25.0 <= s1_thr <= -10.0):
        warnings.append(f"Derived threshold ({s1_thr:.2f} dB) sits outside standard [-25, -10] dB range. Check histogram.")

    s1_water = eval_mask & (s1_vv_db < s1_thr)
    s1_water_km2 = round(float(s1_water.sum()) * CELL_KM2, 2)

    # Save S1 water mask GeoTIFF
    s1_water_tif_path = PROCESSED_S1_DIR / "s1_water.tif"
    out_prof = ref_profile.copy()
    out_prof.update(dtype=rasterio.uint8, count=1, nodata=0)
    with rasterio.open(s1_water_tif_path, "w", **out_prof) as dst:
        dst.write(s1_water.astype(np.uint8), 1)
    print(f"Saved Sentinel-1 water mask: {s1_water_tif_path.resolve()}")

    # Compute comparison metrics
    headline_metrics = compute_metrics(nisar_headline, s1_water, eval_mask)
    core_metrics = compute_metrics(nisar_core, s1_water, eval_mask)

    # Permanent water agreement
    perm_nisar = nisar_base & nisar_headline & eval_mask
    perm_metrics = compute_metrics(perm_nisar, s1_water, eval_mask)

    # Shifted null: shift s1_water by 20 pixels horizontally (+400 m)
    s1_water_shifted = np.roll(s1_water, 20, axis=1)
    s1_water_shifted[:, :20] = False
    null_metrics = compute_metrics(nisar_headline, s1_water_shifted, eval_mask)

    # Generate overlay visualization figure
    generate_validation_overlay_plot(nisar_headline, s1_water, eval_mask, s1_vv_db, s1_thr)

    status = "completed"
    val_data = {
        "status": status,
        "step_blocked": None,
        "reason": None,
        "product_id": SCENE_ID,
        "acquisition_date": "2026-07-25T12:04:34Z",
        "nisar_observation_date": "2026-07-26T12:34:22Z",
        "offset_days": 1,
        "comparison_type": "proxy comparison (one-day temporal offset)",
        "processing_route": "Route 2 (ASF RTC)" if use_rtc else "Route 1 (ESA SNAP)",
        "radiometric_convention": radiometric_convention,
        "s1_threshold_dB": round(s1_thr, 2),
        "s1_threshold_method": f"Otsu bimodal threshold on C-band {radiometric_convention} backscatter",
        "s1_water_km2": s1_water_km2,
        "eval_footprint_km2": eval_km2,
        "metrics": {
            "headline_vs_s1": headline_metrics,
            "core_vs_s1": core_metrics,
            "permanent_water_agreement": perm_metrics,
            "shifted_null": null_metrics,
        },
        "warnings": warnings,
        "reporting_statement": (
            f"Independent proxy validation against Sentinel-1 (acquired July 25, 2026; 1-day temporal offset) "
            f"yielded an IoU of {headline_metrics['iou']:.3f} (F1: {headline_metrics['f1']:.3f}) against the headline water mask "
            f"and {core_metrics['iou']:.3f} against core water over the shared {eval_km2} km² evaluation footprint."
        ),
    }

    # Write results/validation.json
    val_json_path = RESULTS_DIR / "validation.json"
    with open(val_json_path, "w", encoding="utf-8") as f:
        json.dump(val_data, f, indent=2)
    shutil.copy(val_json_path, WEB_DIR / "validation.json")

    # Write results/tables/validation.csv
    csv_rows = [
        {
            "comparison": "Headline_vs_S1",
            "status": status,
            "product_id": SCENE_ID,
            "acquisition_date": "2026-07-25",
            "offset_days": 1,
            "s1_threshold_dB": round(s1_thr, 2),
            "s1_water_km2": s1_water_km2,
            "iou": headline_metrics["iou"],
            "f1": headline_metrics["f1"],
            "precision": headline_metrics["precision"],
            "recall": headline_metrics["recall"],
            "accuracy": headline_metrics["accuracy"],
            "notes": f"NISAR headline (-15/-18 dB) vs S1 {radiometric_convention} Otsu",
        },
        {
            "comparison": "Core_vs_S1",
            "status": status,
            "product_id": SCENE_ID,
            "acquisition_date": "2026-07-25",
            "offset_days": 1,
            "s1_threshold_dB": round(s1_thr, 2),
            "s1_water_km2": s1_water_km2,
            "iou": core_metrics["iou"],
            "f1": core_metrics["f1"],
            "precision": core_metrics["precision"],
            "recall": core_metrics["recall"],
            "accuracy": core_metrics["accuracy"],
            "notes": f"NISAR core (-20/-23 dB) vs S1 {radiometric_convention} Otsu",
        },
        {
            "comparison": "Permanent_Water",
            "status": status,
            "product_id": SCENE_ID,
            "acquisition_date": "2026-07-25",
            "offset_days": 1,
            "s1_threshold_dB": round(s1_thr, 2),
            "s1_water_km2": s1_water_km2,
            "iou": perm_metrics["iou"],
            "f1": perm_metrics["f1"],
            "precision": perm_metrics["precision"],
            "recall": perm_metrics["recall"],
            "accuracy": perm_metrics["accuracy"],
            "notes": "Agreement on permanent water channels",
        },
        {
            "comparison": "Shifted_Null",
            "status": status,
            "product_id": SCENE_ID,
            "acquisition_date": "2026-07-25",
            "offset_days": 1,
            "s1_threshold_dB": round(s1_thr, 2),
            "s1_water_km2": s1_water_km2,
            "iou": null_metrics["iou"],
            "f1": null_metrics["f1"],
            "precision": null_metrics["precision"],
            "recall": null_metrics["recall"],
            "accuracy": null_metrics["accuracy"],
            "notes": "20 px horizontal translation null test",
        },
    ]

    csv_path = TABLES_DIR / "validation.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
        writer.writeheader()
        writer.writerows(csv_rows)

    # Update results/results.json validation block
    results_json_path = RESULTS_DIR / "results.json"
    if results_json_path.exists():
        with open(results_json_path, "r", encoding="utf-8") as f:
            res_all = json.load(f)
        res_all["validation"] = val_data
        with open(results_json_path, "w", encoding="utf-8") as f:
            json.dump(res_all, f, indent=2)
        shutil.copy(results_json_path, WEB_DIR / "results.json")

    # Regenerate docs to incorporate new metrics
    from pipeline.generate_docs import generate_documentation
    generate_documentation()

    return val_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentinel-1 validation pipeline.")
    parser.add_argument("--gpt", type=str, default=None, help="Path to ESA SNAP gpt executable")
    parser.add_argument("--rtc", type=str, default=None, help="Path to ASF on-demand RTC GeoTIFF")
    args = parser.parse_args()
    run_validation(gpt_path=args.gpt, rtc_path=args.rtc)
