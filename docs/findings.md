# NISAR Surface Water Change Pipeline: Findings

## 1. Radiometric Stability Check
Radiometric consistency on stable land across all three scenes (Relative Orbit 91, Frame 76) demonstrates calibration stability:
- July 02, 2026: Stable land HH median = -6.54 dB, HV median = -12.29 dB
- July 14, 2026: Stable land HH median = -6.12 dB, HV median = -12.03 dB
- July 26, 2026: Stable land HH median = -6.41 dB, HV median = -12.15 dB
- **Inter-scene Spread:** 0.42 dB in HH, 0.26 dB in HV (both well within nominal 1.0 dB radiometric stability limits).

## 2. Core Open Water Result and Uncertainty (Primary Metric)
Core open water is defined at HH < -20.0 dB and HV < -23.0 dB:
- **July 02 Baseline Core Water:** 28.42 km² (1.92% of common footprint)
- **July 26 Observed Core Water:** 27.8 km² (1.88% of common footprint)
- **New Core Water:** 2.29 km² (0.15%)
- **Receded Core Water:** 2.91 km² (0.2%)
- **Net Core Water Change:** -0.62 km² (-0.04%)
- **Uncertainty Assessment:** The net core water change of -0.62 km² falls inside the spread of the shifted nulls ([-0.67, +0.02] km²). Therefore, the core change is not distinguishable from zero at this resolution.
- **Sensitivity to HV Cutoff (HH -20.0 dB fixed):**
  - HV -22.0 dB: Baseline = 28.48 km², Observed = 27.83 km², Net = -0.66 km²
  - HV -23.0 dB: Baseline = 28.42 km², Observed = 27.8 km², Net = -0.62 km²
  - HV -24.0 dB: Baseline = 27.92 km², Observed = 27.58 km², Net = -0.34 km²

## 3. Headline Result and Edge-Pixel Composition
At the headline threshold (HH < -15.0 dB, HV < -18.0 dB):
- **July 02 Baseline Water:** 64.9 km² (4.38% of common footprint)
- **July 26 Observed Water:** 60.75 km² (4.1% of common footprint)
- **New Water:** 4.68 km² (0.32%)
- **Receded Water:** 8.83 km² (0.6%)
- **Net Change:** -4.15 km² (-0.28%)

### Transitional vs. Core Composition of Headline Change
- **New Water Pixels (11,709 px, 4.68 km²):**
  - Core Open Water (< -20 dB): 18 px (0.01 km², 0.2%)
  - Transitional Band ([-20, -15] dB): 11,691 px (4.68 km², 99.8%)
  - Observed HH backscatter: median = -15.58 dB [IQR: -16.14, -15.24] dB
- **Receded Water Pixels (22,086 px, 8.83 km²):**
  - Core Open Water (< -20 dB): 107 px (0.04 km², 0.5%)
  - Transitional Band ([-20, -15] dB): 21,979 px (8.79 km², 99.5%)
  - Baseline HH backscatter: median = -15.65 dB [IQR: -16.25, -15.28] dB

Over 99% of threshold-crossing change lies within 5 dB of the threshold (99.8% of new water and 99.5% of receded water). Its significance is tested against a spatial-shift null.

## 4. Systematic Sensitivity Sweep
In the sensitivity sweep from HH -21.0 dB to -12.0 dB (HV = HH - 3.0 dB, 19 increments, saved to `results/tables/sweep.csv`):
- Net change was negative at every tested threshold, ranging from -8.13 km² to -0.30 km².
- Pixels that receded at thresholds above -15 dB exhibit backscatter (median -11 to -13 dB) intermediate between the open-water floor (-23 dB) and stable land (-6.4 dB), reflecting transitional surfaces rather than open water.
- Within the -15.0 dB to -21.0 dB range, net change spans -0.30 km² to -4.15 km².
- Conservative row (HH -18.0 dB, HV -21.0 dB): Baseline = 38.51 km² (2.6%), Observed = 38.07 km² (2.57%), New = 3.24 km², Receded = 3.68 km², Net = -0.44 km² (-0.03%).

## 5. Spatial-Shift Null Outcome
Evaluated on the cropped common area (1438.39 km²):

| Shift (px / meters) | Headline New (km²) | Headline Receded (km²) | Headline Net (km²) | Core New (km²) | Core Receded (km²) | Core Net (km²) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 px (0 m) | 4.63 | 8.78 | -4.15 | 2.25 | 2.90 | -0.65 |
| 2 px (40 m) | 6.59 | 10.78 | -4.20 | 3.38 | 4.05 | -0.67 |
| 5 px (100 m) | 9.87 | 13.72 | -3.85 | 5.30 | 5.61 | -0.31 |
| 10 px (200 m) | 13.21 | 16.77 | -3.56 | 7.87 | 7.85 | +0.02 |
| 20 px (400 m) | 18.27 | 21.91 | -3.64 | 12.54 | 12.52 | +0.02 |

- As spatial displacement increases from 0 m to 400 m, apparent headline change increases from 4.63 km² / 8.78 km² to 18.27 km² / 21.91 km², confirming that the mapped features possess real spatial coherence.
- The net difference across all shifts remains anchored between -4.20 km² and -3.56 km² due to the marginal scene totals.

## 6. Independent Validation Status
- **Status:** BLOCKED
- **Framework:** Proxy comparison with Sentinel-1 acquired 2026-07-25 (one day before the NISAR observation).
- **Product ID:** `S1D_IW_GRDH_1SDV_20260725T120434_20260725T120459_003830_006E63_520C`
- **Step Outcome:** STEP 2: Calibrate, terrain-correct, and grid to the NISAR footprint: blocked: SNAP not available
- **Validation Assessment:** Independent validation against Sentinel-1 (acquired 2026-07-25, one day before the NISAR observation) was not completed. The Level-1 product was downloaded and verified; calibration and terrain correction were not performed, so no agreement metrics are reported. All classifications remain unvalidated.

## 7. Limitations
1. **Spatial Coverage:** The common dual-polarization footprint covers 1480.43 km², which is 3.08% of the 48,000 km² regional bounding box. Results do not represent basin-wide totals for Assam.
2. **Temporal Sampling:** Based on a single observation pair (July 02 and July 26, 2026), capturing change over a 24-day interval without intermediate temporal resolution.
3. **Threshold-Edge Sensitivity:** 99.8% of new water and 99.5% of receded water at the headline threshold sit within 5 dB of the threshold (-20 to -15 dB).
4. **Filter Window:** A 5x5 boxcar speckle filter (100 m effective window) smooths fine channel boundaries.
5. **Product Maturity:** NISAR Level-2 GCOV products are provisional and subject to ongoing calibration updates.
6. **Ground Truth:** No in-situ hydrologic gauge measurements or coincident high-resolution aerial surveys were available for direct validation.

## 8. Reporting Statement
Within the common 1480.43 km² dual-polarization footprint (Frame 76, Relative Orbit 91, covering 3.08% of the regional study box), core open water (HH < -20 dB, HV < -23 dB) remained stable between July 02, 2026 (28.42 km²) and July 26, 2026 (27.8 km²), with net change of -0.62 km² (2.29 km² new, 2.91 km² receded) which is not distinguishable from zero against a spatial-shift null spread of [-0.67, +0.02] km². At the headline threshold (HH < -15 dB, HV < -18 dB), detected water shifted from 64.9 km² to 60.75 km² (4.68 km² new, 8.83 km² receded; net: -4.15 km²), but over 99% of this change (99.8% of new, 99.5% of receded) sits in the transitional -20 to -15 dB band rather than core water. Across a sensitivity sweep from -21 to -12 dB, net change was negative at every threshold (-0.30 to -8.13 km²), spanning -0.30 to -4.15 km² across the -15 to -21 dB range. Visual overlay checks confirmed positioning consistent with the channel network at basemap resolution. Independent validation against Sentinel-1 (acquired 2026-07-25, one day before the NISAR observation) was not completed. The Level-1 product was downloaded and verified; calibration and terrain correction were not performed, so no agreement metrics are reported. All classifications remain unvalidated.
