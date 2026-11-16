# NISAR Surface Water Change Pipeline: Methods

## 1. Input Datasets & Orbital Geometry
- **Mission:** NISAR Provisional Level-2 Ground Projected Copolarization / Crosspolarization Covariance (L2_PR_GCOV).
- **Orbit Parameters:** Descending pass, Relative Orbit (Track) 91, Frame 76.
- **Input Scenes (`data/raw/`):**
  - `NISAR_L2_PR_GCOV_024_091_D_076_4005_DHDH_A_20260702T123423_20260702T123458_P05023_N_F_J_001.h5` (July 02, 2026; DHDH dual-pol, 10 m native posting; reference scene).
  - `NISAR_L2_PR_GCOV_025_091_D_076_2005_QPDH_A_20260714T123423_20260714T123457_P05023_F_F_J_001.h5` (July 14, 2026; QPDH quad-pol, 20 m native posting; excluded from spatial change analysis).
  - `NISAR_L2_PR_GCOV_026_091_D_076_4005_DHDH_A_20260726T123422_20260726T123457_P05023_N_F_J_001.h5` (July 26, 2026; DHDH dual-pol, 10 m native posting; observation scene).

## 2. Common Footprint Definition
- All spatial change detection and statistical comparisons are evaluated strictly over the **common dual-polarization footprint** (1480.43 km², 3701070 pixels).
- The common footprint is defined as pixels where both HH and HV polarizations are finite in both the July 02 reference and July 26 observation scenes.
- The common footprint covers 3.08% of the 48,000 km² regional bounding box (89.8°E–94.2°E, 25.9°N–26.9°N).
- Individual scene valid footprints:
  - July 02, 2026 (DHDH): 1590.01 km²
  - July 14, 2026 (QPDH): 1080.63 km²
  - July 26, 2026 (DHDH): 1481.32 km²
- **Reason for July 14 Exclusion:** The July 14 QPDH acquisition swath is narrower than the DHDH swaths; 96.6% of July 26's detected water lies outside the July 14 footprint, preventing like-for-like spatial change comparison.

## 3. Data Processing & Artifact Correction
1. **Coordinate Subsetting & Artifact Filtering:** Raw linear power rasters from `science/LSAR/GCOV/grids/frequencyA` (HHHH and HVHV) are subset to the AOI. Processing artifacts and non-physical values—specifically linear power values below 1e-4 (-40 dB, unphysical near-zero noise floor) and above 10.0 (+10 dB, unphysical for natural terrain)—are set to no-data before any filtering.
2. **Spatial Resampling:** DHDH scenes (10 m spacing) are block-averaged 2x2 in linear power to align to the common 20 m grid (0.0004 km² per pixel, EPSG:32646).
3. **Speckle Reduction:** A 5x5 boxcar uniform filter is applied to linear power ignoring no-data pixels, after which values are converted to decibels (dB): $\sigma^0_\text{dB} = 10 \log_{10}(\sigma^0)$.
4. **Spatial Alignment:** All scenes are aligned to a common upper-left corner and cropped to identical dimensions.

## 4. Threshold Families
To prevent threshold-split artifacts, fixed dual-polarization thresholding ($HH < T_\text{HH}$ and $HV < T_\text{HV}$) is applied across all scenes using consistent threshold families:
- **Core Open Water:** HH < -20.0 dB and HV < -23.0 dB. Captures unambiguous deep water bodies free of threshold boundary sensitivity.
- **Transitional Band:** Pixels meeting the headline threshold but having HH between -20.0 dB and -15.0 dB (headline mask minus core mask).
- **Headline Threshold:** HH < -15.0 dB and HV < -18.0 dB (holding HV = HH - 3.0 dB).
- **Conservative Sweep Row:** HH < -18.0 dB and HV < -21.0 dB (a specific row of the systematic sweep; HV = HH - 3.0 dB).
- **Systematic Sensitivity Sweep:** HH from -21.0 dB to -12.0 dB in 0.5 dB increments with HV = HH - 3.0 dB.

## 5. Statistical Definitions & Change Accounting
- Every percentage and area statistic uses the single common footprint denominator (1480.43 km²).
- For baseline water mask $W_\text{base}$ and observed water mask $W_\text{obs}$ on the common footprint:
  - $\text{New Water} = W_\text{obs} \land \neg W_\text{base}$
  - $\text{Receded Water} = W_\text{base} \land \neg W_\text{obs}$
  - $\text{Net Change} = \text{New Water} - \text{Receded Water} = |W_\text{obs}| - |W_\text{base}|$ by definition.

## 6. Spatial-Shift Null Test
To evaluate whether threshold-crossing change represents spatially coherent signal versus random measurement noise/threshold-edge flipping, the July 26 observation arrays are shifted in east-west column steps ($k \in \{0, 2, 5, 10, 20\}$ pixels, where 1 pixel = 20 m). A 20-pixel border is cropped from the common footprint to prevent wrap-around edge effects from `np.roll`. New water, receded water, and net change are recomputed on this cropped common mask (1438.39 km²).

## 7. Independent Validation Methodology (Sentinel-1 Proxy)
- **Target Comparison Granule:** `S1D_IW_GRDH_1SDV_20260725T120434_20260725T120459_003830_006E63_520C` (acquired July 25, 2026; 1-day temporal proxy for NISAR July 26).
- **Temporal Proxy Caveat:** Differences reflect both physical sensor differences (C-band 5.405 GHz vs L-band 1.257 GHz) and potential 24-hour hydrologic stage dynamics.
- **Preprocessing Routes:**
  - *Route 1 (ESA SNAP Graph):* Ingestion of raw Level-1 GRD ZIP, precise orbit application, thermal noise removal, calibration to $\sigma^0$ (VV, VH), Refined Lee speckle filtering (5x5), and SRTM 1-sec terrain correction to EPSG:32646 at 20 m.
  - *Route 2 (ASF On-Demand RTC):* Ingestion of radiometrically terrain-corrected backscatter processed via ASF Vertex/HyP3. Caveats: RTC uses gamma-0 ($\gamma^0$) rather than sigma-0 ($\sigma^0$), and native resolution is 30 m resampled to the 20 m EPSG:32646 grid. Because the C-band threshold is derived empirically from the scene histogram, the radiometric difference between $\gamma^0$ and $\sigma^0$ does not affect the thresholding methodology.
- **Thresholding:** Otsu bimodal threshold derived dynamically on valid VV backscatter within the intersection of the Sentinel-1 footprint and NISAR common dual-polarization footprint.
- **Evaluation Metrics:** Evaluated exclusively on the shared valid footprint intersection:
  - Intersection-over-Union (IoU) / Jaccard index
  - F1-Score (Dice coefficient)
  - Precision, Recall, and Overall Accuracy
  - Spatial-shift null control (20-pixel displacement).
