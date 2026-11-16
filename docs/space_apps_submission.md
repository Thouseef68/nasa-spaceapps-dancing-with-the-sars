# NASA International Space Apps Challenge 2026: Project Submission

**Challenge:** Dancing with the SARs  
**Team Name:** Black Hole Survivors  
**Project Title:** HydroWaltz — NISAR 3D Hydrological Digital Twin & Autonomous AI Intelligence for Brahmaputra Basin Flood Dynamics  
**Live Application URL:** https://nasa-hackathon-nisar.vercel.app  
**Repository:** https://github.com/Thouseef68/nasa-spaceapps-dancing-with-the-sars  
**Project Demonstration (Google Drive 7-Slide Presentation):** https://docs.google.com/presentation/d/1AZPC5wn49lXPZdQVYDR8RoVm-Ey7HoSZ/edit?usp=sharing  

---

## 1. High-Level Summary (The 30-Second Hook)
During the intense monsoon floods across the Brahmaputra River Valley in Assam, India, conventional optical satellites are blinded by perpetual cloud cover, obscuring the displacement of river communities across braided sandbars (*chars*). **HydroWaltz** leverages provisional Level-2 Ground Projected Copolarization / Crosspolarization Covariance (GCOV) data from the **NASA-ISRO Synthetic Aperture Radar (NISAR)** mission to pierce the cloud cover and measure hydrological change down to the centimeter scale.

Our platform couples rigorous radar remote sensing physics with a **hardware-accelerated WebGL 3D Digital Twin** and an **autonomous AI Hydro-Copilot powered by NVIDIA NIM**. By separating deep core channel stability from boundary vegetation speckle noise through a systematic 19-step sensitivity sweep and a 20-pixel spatial-shift null test, HydroWaltz provides flood responders, water resource engineers, and humanitarian agencies with ground-truth disaster intelligence they can trust.

---

## 2. Project Description & Challenge Alignment

### A. How does your project address "Dancing with the SARs"?
The challenge asks participants to track, visualize, and communicate complex Earth surface changes using radar remote sensing data, overcoming barriers such as speckle noise, polarization interpretation, and technical complexity.

Earth's surface does not move in simple lines; along the braided Brahmaputra, water expands, recedes, and shifts in a dynamic "waltz" with seasonal sandbanks and vegetation. **HydroWaltz** translates this radar dance into an intuitive, multi-dimensional decision platform:
1. **The Radar Physics:** Ingests descending-pass L-band dual-polarization (HH & HV) backscatter from Relative Orbit 91, Frame 76, comparing July 02, 2026 (baseline) and July 26, 2026 (flood observation).
2. **Solving the "Edge Flip" Illusion:** Standard thresholding maps often claim massive flood expansion or recession that is merely speckle noise along water-land boundaries. We introduce a **Dual-Pol Core vs. Transitional Edge Model**:
   - **Core Open Water** ($\text{HH} < -20.0\text{ dB}$, $\text{HV} < -23.0\text{ dB}$): Measures deep navigation channels, proving the river channel remained dynamically stable ($-0.62\text{ km}^2$ net change, which is indistinguishable from zero against our spatial-shift null spread $[-0.67, +0.02]\text{ km}^2$).
   - **Transitional Fringe** ($\text{HH} \in [-20, -15]\text{ dB}$): Proves that $99.8\%$ of new headline water and $99.5\%$ of receded water sits along dynamic boundary fringes.
3. **Space-to-Valley 3D Visualization:** Seamlessly transitions from an Apple Maps-style space orbit view down to a 3D terrain mesh with 1.8× elevation exaggeration, draping raw SAR backscatter and flood extents over real topography.
4. **NVIDIA-Powered Generative AI:** Integrates NVIDIA NIM (`nvidia/nemotron-3.5-bolt-e4b`) to provide sub-second natural language query resolution and automated UN-SPIDER / Central Water Commission (CWC) disaster Situation Report (SitRep) synthesis.

---

## 3. What Does It Do and How Was It Developed?

### Technical Architecture & Workflow
```
[ NASA/ISRO NISAR L2 GCOV HDF5 ]
               │
               ▼
   [ pipeline/step2_process.py ]
   - Power artifact rejection (< -40 dB, > +10 dB)
   - 2x2 linear spatial averaging (10m native -> 20m grid)
   - 5x5 boxcar speckle filtering (100m window)
   - Georeferenced GeoTIFFs (EPSG:32646)
               │
               ▼
     [ pipeline/analysis.py ]
   - Common Footprint Evaluation (1,480.43 km²)
   - Core vs. Headline dual-pol separation
   - 19-Step Sensitivity Sweep (-21.0 to -12.0 dB)
   - 20-pixel (+400m) Spatial-Shift Null Test
   - Single-denominator statistical accounting
               │
               ▼
   [ pipeline/export_web.py ]
   - Reprojects to EPSG:4326 Web Mercator
   - Exports 8 Flood Masks + 2 Grayscale Radar Backscatter PNGs
               │
               ▼
      [ web/ & server.py ]
   - WebGL 3D Globe & MapLibre Terrain Engine
   - 3D DEM Draping (AWS Terrarium 3D tiles)
   - River Transect Hydraulic Stage Profiler
   - Temporal Swipe Before/After Curtain
   - District Inundation Breakdown (Goalpara, Barpeta, Kamrup, Dhubri)
   - NVIDIA NIM AI Hydro-Intelligence Copilot & SitRep Engine
```

### Key Analytical Results (All Grounded from `results/results.json`)
- **Evaluation Denominator:** Single common dual-polarization footprint of **$1,480.43\text{ km}^2$** ($3.08\%$ of the $48,000\text{ km}^2$ regional study box).
- **Core Open Water:** Baseline = $28.42\text{ km}^2$ ($1.92\%$), Observed = $27.80\text{ km}^2$ ($1.88\%$). Net change = **$-0.62\text{ km}^2$** ($+2.29\text{ km}^2$ new, $-2.91\text{ km}^2$ receded). This $-0.62\text{ km}^2$ sits completely inside the 20-pixel shifted null spread of $[-0.67, +0.02]\text{ km}^2$, proving channel stability.
- **Headline Threshold:** Baseline = $64.90\text{ km}^2$ ($4.38\%$), Observed = $60.75\text{ km}^2$ ($4.10\%$). Net change = **$-4.15\text{ km}^2$** ($+4.68\text{ km}^2$ new, $-8.83\text{ km}^2$ receded). Over $99\%$ of this change is transitional edge noise.
- **Radiometric Stability:** Stable land median spread between passes was **$0.42\text{ dB}$** in HH and **$0.26\text{ dB}$** in HV, well within the $1.0\text{ dB}$ instrument stability threshold.

---

## 4. Space Agency Data & External Technologies

### Space Agency Data Used
1. **NASA / ISRO NISAR (Level-2 Provisional GCOV):**
   - Reference: `NISAR_L2_PR_GCOV_024_091_D_076_4005_DHDH_A_20260702T123423...` (July 02, 2026)
   - Observation: `NISAR_L2_PR_GCOV_026_091_D_076_4005_DHDH_A_20260726T123422...` (July 26, 2026)
   - Orbital Parameters: Relative Orbit 91, Frame 76, Descending Pass, L-band (1.257 GHz), dual-pol (DHDH).
2. **ESA / Copernicus Sentinel-1 (Level-1 GRD):**
   - Granule: `S1D_IW_GRDH_1SDV_20260725T120434_20260725T120459_003830_006E63_520C` (1.07 GB full product downloaded for proxy validation).
3. **NASA / USGS Shuttle Radar Topography Mission (SRTM):**
   - 1-Arcsecond (30 m) Global Elevation Model used for 3D digital twin terrain draping and hydraulic cross-sections.

### Software, Frameworks & AI Tools
- **NVIDIA NIM (Inference Microservice):** `nvidia/nemotron-3.5-bolt-e4b` providing sub-second hydrological reasoning grounded on verified data.
- **MapLibre GL JS v4:** WebGL/WebGPU hardware-accelerated 3D globe and terrain rendering engine.
- **Python Scientific Ecosystem:** `rasterio`, `numpy`, `scipy`, `h5py`, `matplotlib`, `pyproj`, `PIL`.
- **Chart.js:** Real-time hydraulic river transect and elevation profile visualization.
- **AWS Terrarium:** Global elevation RGB terrain tiles for real-time 3D topographic meshing.

---

## 5. Potential Impact & Future Evolution
Flooding in Assam affects millions annually across the Brahmaputra valley. By deploying an autonomous radar digital twin with embedded AI:
1. **Instant Actionable Relief:** Disaster management authorities (NDMA / ASDMA) can download district-by-district inundation metrics and generate formal SitReps in under 3 seconds.
2. **Island Community Evacuation:** Identifies cut-off river island (*char*) communities where navigation channels have shifted.
3. **Global Scalability:** The pipeline is sensor-agnostic and can be deployed across any global river basin, wetland, or coastal estuary monitored by NISAR, Sentinel-1, or ALOS-2.

---

## 6. Project Artifacts
- **Web Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Methodology Documentation:** [`docs/methods.md`](file:///c:/Users/thous/Desktop/NASA-HACKTHON/docs/methods.md)
- **Scientific Findings & Uncertainty Bounds:** [`docs/findings.md`](file:///c:/Users/thous/Desktop/NASA-HACKTHON/docs/findings.md)
- **Verification Composite:** [`results/map_check.png`](file:///c:/Users/thous/Desktop/NASA-HACKTHON/results/map_check.png)
- **Authoritative Verified Results:** [`results/results.json`](file:///c:/Users/thous/Desktop/NASA-HACKTHON/results/results.json)

