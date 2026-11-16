"""run_all.py
Master execution pipeline for the NISAR Brahmaputra surface-water change project.
Executes, in order:
  1. pipeline/step2_process.py  (calibrates, speckle-filters, downsamples, exports GeoTIFFs)
  2. pipeline/analysis.py       (runs headline, core, sweep, null test, writes results.json & tables)
  3. pipeline/export_web.py     (reprojects layers to EPSG:4326 PNGs, syncs web/results.json)
  4. pipeline/capture_map_check.py (generates verification screenshot results/map_check.png)
  5. pipeline/generate_docs.py  (generates docs/methods.md and docs/findings.md from results.json)

Stops immediately on the first error.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable


def run_pipeline(gpt_path=None, rtc_path=None):
    start_total = time.time()
    print("=" * 70)
    print("STARTING COMPLETE END-TO-END NISAR PROCESSING PIPELINE")
    print(f"Project root: {ROOT}")
    print("=" * 70)

    val_cmd = [PYTHON, "pipeline/run_validation.py"]
    if gpt_path:
        val_cmd.extend(["--gpt", gpt_path])
    if rtc_path:
        val_cmd.extend(["--rtc", rtc_path])

    pipeline_steps = [
        ("Step 1: SAR Processing & GeoTIFF Export", [PYTHON, "pipeline/step2_process.py"]),
        ("Step 2: Consolidated Analysis & Statistics", [PYTHON, "pipeline/analysis.py"]),
        ("Step 3: Sentinel-1 Proxy Validation Check", val_cmd),
        ("Step 4: Web Layer Reprojection & Sync", [PYTHON, "pipeline/export_web.py"]),
        ("Step 5: Map Check Verification Capture", [PYTHON, "pipeline/capture_map_check.py"]),
        ("Step 6: Documentation Generation", [PYTHON, "pipeline/generate_docs.py"]),
    ]

    for step_name, cmd in pipeline_steps:
        print(f"\n>>> Running: {step_name}")
        print(f"    Command: {' '.join(cmd)}")
        step_start = time.time()
        res = subprocess.run(cmd, cwd=ROOT)
        elapsed = time.time() - step_start

        if res.returncode != 0:
            print(f"\n[ERROR] Pipeline failed during: {step_name} (exit code {res.returncode})")
            sys.exit(res.returncode)

        print(f"    Completed in {elapsed:.1f}s")

    total_elapsed = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {total_elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run NISAR end-to-end pipeline.")
    parser.add_argument("--gpt", type=str, default=None, help="Path to ESA SNAP gpt executable")
    parser.add_argument("--rtc", type=str, default=None, help="Path to ASF on-demand RTC GeoTIFF")
    args = parser.parse_args()
    run_pipeline(gpt_path=args.gpt, rtc_path=args.rtc)

