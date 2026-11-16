# 🛰️ HydroWaltz: NASA NISAR 3D Hydrological Digital Twin & Deep Polarimetric Intelligence

<div align="center">

[![Live Demo on Vercel](https://img.shields.io/badge/Live%20Demo-nasa--hackathon--nisar.vercel.app-brightgreen.svg?style=for-the-badge&logo=vercel)](https://nasa-hackathon-nisar.vercel.app)
[![NASA Space Apps Challenge 2026](https://img.shields.io/badge/NASA%20Space%20Apps-2026%20Global%20Challenge-blue.svg?style=for-the-badge&logo=nasa)](https://www.spaceappschallenge.org/2026/find-a-team/black-hole-survivors/?tab=details)
[![Challenge: Dancing with the SARs](https://img.shields.io/badge/Challenge-Dancing%20with%20the%20SARs-purple.svg?style=for-the-badge)](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/)
[![Team: Black Hole Survivors](https://img.shields.io/badge/Team-Black%20Hole%20Survivors-orange.svg?style=for-the-badge)](#team--challenge-context)
[![NISAR L-Band GCOV](https://img.shields.io/badge/NISAR%20Radar-L--Band%20(24cm)%20Level--2%20GCOV-red.svg?style=for-the-badge)](#data-products)
[![NVIDIA NIM Autonomous Copilot](https://img.shields.io/badge/AI%20Copilot-NVIDIA%20NIM%20(nemotron--3.5)-green.svg?style=for-the-badge)](https://build.nvidia.com)
[![IEEE Whitepaper](https://img.shields.io/badge/Research-IEEE%20Whitepaper-blueviolet.svg?style=for-the-badge)](docs/research_whitepaper.md)

**A spaceborne 3D digital twin and autonomous AI intelligence copilot resolving microwave radar speckle ambiguity, dihedral double-bounce scattering, and geomorphic river stability during the 2026 Brahmaputra mega-flood in Assam, India.**

[🚀 Launch Live 3D Twin (Vercel)](https://nasa-hackathon-nisar.vercel.app) • [📄 Read IEEE Research Paper](docs/research_whitepaper.md) • [📊 Verified Results](#-key-scientific-discoveries) • [⚡ Quickstart](#-quickstart-reproduction)

</div>

---

## 🌟 Executive Summary: Resolving the "Dancing with the SARs" Paradox

During peak monsoon surges along the mighty **Brahmaputra River** in Assam, India, optical Earth-observation satellites (Landsat-8/9, Sentinel-2 MSI) are rendered completely blind by perpetual monsoon storm clouds ($100\%$ cloud cover). The joint **NASA-ISRO Synthetic Aperture Radar (NISAR)** mission cuts through these storms with penetrating **L-band ($24.0\text{ cm}$) microwave radar**.

However, interpreting raw SAR backscatter presents a notorious physical paradox:
1. **The Dihedral Double-Bounce Illusion:** Calm open water reflects microwaves away (specular Fresnel bounce, $\text{HH} \approx -25\text{ dB}$, dark). But when floodwaters overtop emergent reeds, crops, or rural char communities, the radar pulse reflects off the water onto vertical stalks and bounces $180^\circ$ directly back to the antenna ($\text{HH} \approx -10\text{ dB}$, bright). Naive single-polarization algorithms mistake flooded vegetation for dry land!
2. **Capillary Bragg Roughness:** Monsoon winds whip up capillary ripples matching half the radar wavelength ($\sim 12\text{ cm}$), elevating water returns ($-15$ to $-13\text{ dB}$) and mimicking land.

### 🏆 The Discovery by Team Black Hole Survivors:
Across the common dual-pol valid footprint of **$1,480.43\text{ km}^2$** (Relative Orbit 91, Frame 76):
* **Core Navigation Thalweg Stability:** Applying strict dual-polarization thresholding ($\text{HH} < -20.0\text{ dB}$, $\text{HV} < -23.0\text{ dB}$) proves the deep braided river channel encompassed $28.42\text{ km}^2$ at baseline and $27.80\text{ km}^2$ at flood peak—a net drift of **$-0.62\text{ km}^2$**. Monte Carlo 20-pixel spatial translation null testing yields a baseline noise spread of $[-0.67, +0.02]\text{ km}^2$, proving channel change is **statistically indistinguishable from zero ($p > 0.05$)**. The main navigation thalweg is stable!
* **The 99.8% Fringe Paradox:** While headline water appeared to drop by $-4.15\text{ km}^2$ ($64.90 \rightarrow 60.75\text{ km}^2$), pixel decomposition proves that **$99.8\%$ of newly flooded pixels ($4.67\text{ km}^2$)** and **$99.5\%$ of receded pixels ($8.79\text{ km}^2$)** reside strictly in the transitional reed fringe band $[-20, -15]\text{ dB}$.

---

## 📊 Key Scientific Discoveries

| Metric / Parameter | Value | Scientific & Hydrological Significance |
| :--- | :--- | :--- |
| **Common Observation Swath** | **$1,480.43\text{ km}^2$** | Valid dual-pol intersection of Relative Orbit 91, Frame 76 (Assam) |
| **Core Open Water Baseline (Jul 02)** | **$28.42\text{ km}^2$** ($1.92\%$) | Deep, unobstructed braided navigation channels at $36.0\text{ m MSL}$ stage |
| **Core Open Water Flood Peak (Jul 26)** | **$27.80\text{ km}^2$** ($1.88\%$) | Deep channel extent at $37.2\text{ m MSL}$ flood crest |
| **Core Net Thalweg Change** | **$-0.62\text{ km}^2$** | Within spatial null spread $[-0.67, +0.02]\text{ km}^2$ $\rightarrow$ **Channel is Stable** |
| **Headline Water Extent (Jul 02 $\rightarrow$ 26)** | **$64.90 \rightarrow 60.75\text{ km}^2$** | Net $-4.15\text{ km}^2$ ($+4.68\text{ km}^2$ new, $-8.83\text{ km}^2$ receded) |
| **Fringe Band Concentration** | **$99.8\%$ new / $99.5\%$ receded** | Confined to $[-20, -15]\text{ dB}$ emergent reed double-bounce |
| **Dual-Pol Radar Vegetation Index (DpRVI)** | **$0.124$ (Water) vs $0.648$ (Reeds)** | Confirms dihedral corner reflector scattering on flooded char fringes |
| **Equivalent Number of Looks (ENL)** | **$18.42$** (Suppression: $18\times$) | Suppresses multiplicative speckle noise variance to $\pm 0.21\text{ dB}$ |
| **River Braiding Index ($B_i$)** | **$4.82 \pm 0.28$** | Invariant channel bifurcation despite $+1.2\text{ m}$ flood surge |
| **Mean Surface Flow Velocity** | **$2.35\text{ m/s}$** | Bedload & suspended sediment discharge of $\sim 2.15\text{M tons/day}$ |

---

## 🚀 Live Web Application & Features

Our interactive 3D digital twin is designed for emergency dispatchers (ASDMA), hydrologists, and NASA judges:

```
+---------------------------------------------------------------------------------------------------------------+
|  🛰️ 1,480.43 km² Swath         |  🌊 -0.62 km² Core Thalweg       |  🔬 DpRVI: 0.12 vs 0.65 (Reeds)         |
|  Rel Orbit 91 • Frame 76 (Assam) |  Baseline: 28.42 → Flood: 27.80  |  Speckle ENL: 18.42 • Braiding: 4.82   |
+---------------------------------------------------------------------------------------------------------------+
|                                                                                                               |
|          ✨ FULL-SCREEN 3D GLOBE • REAL-TIME RIVER FLOW & SEDIMENT PARTICLES • GEOGRAPHIC LABELS ✨           |
|                                                                                                               |
|   +------------------------------+                                     +----------------------------------+   |
|   | ⚡ 60s Guided Story Tour     |                                     | 🤖 AI Hydro-Copilot (NVIDIA NIM) |   |
|   | 🩻 Cloud-Penetrating X-Ray   |                                     | 🎙️ Voice SitRep Audio Briefing   |   |
|   | 🌊 4D Space-Time Scrubber    |                                     | 🚨 Incident Command (ASDMA)      |   |
|   | 🔬 3D Wave Physics Studio    |                                     | 📄 Official IEEE Whitepaper      |   |
|   +------------------------------+                                     +----------------------------------+   |
+---------------------------------------------------------------------------------------------------------------+
```

### Key Interactive Features:
1. **🌊 Live River Flow & Soil Erosion Simulation:**
   * **240+ animated flowing water vectors** stream down the braided channels from Guwahati to Dhubri at $2.35\text{ m/s}$.
   * **100+ golden-brown silt drift particles** billow from active riverbank erosion zones, visually modeling riverbank slumping and alluvial sediment dispersion ($\sim 2.15\text{M tons/day}$).
   * **Interactive Click-to-Spawn:** Click anywhere on the river to drop a localized hydrodynamic surge burst and sediment plume!
2. **🩻 Cloud-Penetrating SAR X-Ray Lens:**
   * Draggable radar loupe: outside is $100\%$ opaque monsoon storm cloud cover; inside the lens, L-band microwave radar pierces $100\%$ of the storm clouds to reveal the crisp surface water mask.
3. **🌊 4D Space-Time River Pulse Scrubber:**
   * Interactive slider cycling through Epoch 1 (July 02 Baseline, $36.0\text{ m}$), Epoch 2 (July 14 Monsoon Crest, $38.5\text{ m}$), and Epoch 3 (July 26 Flood Peak, $37.2\text{ m}$) with dynamic stage gauges.
4. **🔬 3D Microwave Wavefront Physics Studio:**
   * WebGL/Canvas simulation of electromagnetic wave oscillations, specular surface reflection, dihedral double-bounce, and volume depolarization.
5. **🚨 Disaster Emergency Command Room (ASDMA / NDRF Mode):**
   * Tactical operational overlay with population exposure counts ($\sim 111,700$ people across Goalpara, Barpeta, Kamrup, and Dhubri) and 1-click field evacuation order PDF generator.
6. **🤖 Autonomous AI Hydro-Copilot with Voice Briefing:**
   * Powered by **NVIDIA NIM** (`nvidia/nemotron-3.5-bolt-e4b`) with sub-second verified latency, prompt chips, and Web Speech API Flight Director audio synthesis with real-time audio waveform visualizers.

---

## 🛠️ Tech Stack & Architecture

* **Frontend Engine:** MapLibre GL v4 (3D AWS Terrarium DEM terrain, 1.8× exaggeration), Chart.js, HTML5 Canvas Particle Engine, Web Audio API, Web Speech API.
* **Cartographic Layers:** Esri World Imagery (Satellite) + Esri World Boundaries and Places Reference Layer (Labels, Borders, Cities, Rivers).
* **AI Copilot Backend:** NVIDIA NIM API (`nvidia/nemotron-3.5-bolt-e4b`), Python HTTP server (`server.py`).
* **Radar Processing Pipeline:** Python 3.10+, GDAL, Rasterio, NumPy, H5py, SciPy (Spatial-Shift Null Tests & DpRVI decomposition).

---

## ⚡ Quickstart: Reproduction

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

### 2. Launch Local Mission Control & AI Copilot (1 Command)
```bash
python server.py 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

### 3. (Optional) Re-Run Complete End-to-End Data Pipeline from Scratch
To verify and reproduce all calculations, sensitivity sweeps, null hypothesis tests, and polarimetry:
```bash
python run_all.py
```

---

## 📁 Repository Directory Structure

```
├── data/
│   ├── processed/          # Summary CSVs, sensitivity sweeps, and thresholds
│   └── raw/                # NASA NISAR Level-2 GCOV granules (git-ignored, 20GB)
├── docs/
│   ├── research_whitepaper.md  # Formal IEEE/AGU publication-grade scientific paper
│   ├── space_apps_submission.md# Official NASA Space Apps challenge submission text
│   ├── presentation_deck.md    # 2-minute elevator pitch & video walkthrough script
│   ├── findings.md             # Authoritative verified scientific metrics
│   └── methods.md              # Complete technical methodology
├── pipeline/
│   ├── download_nisar.py       # NASA ASF/DAAC granule fetcher
│   ├── step2_process.py        # Radiometric calibration & UTM geocoding
│   ├── threshold_sweep.py      # 19-threshold sensitivity analysis
│   ├── shift_null_test.py      # Monte Carlo 20-pixel spatial translation null test
│   ├── deep_research_polarimetry.py # DpRVI, ENL speckle & Braiding Index
│   └── export_web.py           # Web raster & JSON asset generation
├── results/
│   ├── results.json            # Authoritative project metrics database
│   ├── deep_research.json      # DpRVI, ENL, and river morphodynamics
│   └── validation.json         # Sentinel-1 proxy cross-validation status
├── web/
│   ├── index.html              # 3D Digital Twin Viewer & Mission Control Suite
│   ├── layers/                 # Web-optimized georeferenced radar rasters
│   ├── results.json            # Ground-truth analytics for AI copilot
│   └── sweep.json              # 19-row sensitivity sweep data
├── run_all.py                  # Master automated pipeline orchestrator
├── server.py                   # Unified HTTP server & NVIDIA NIM AI backend
└── vercel.json                 # Vercel Edge deployment configuration
```

---

## 🏆 Team & Challenge Context

* **Event:** NASA International Space Apps Challenge 2026
* **Team:** **Black Hole Survivors**
* **Project Team Page:** [https://www.spaceappschallenge.org/2026/find-a-team/black-hole-survivors/?tab=details](https://www.spaceappschallenge.org/2026/find-a-team/black-hole-survivors/?tab=details)
* **Challenge:** *"Dancing with the SARs"* — Developing novel algorithms and scientific frameworks to track dynamic surface changes with multi-temporal SAR remote sensing.

---

## 📜 Citations & Data Attributions

* **NASA / ISRO:** NISAR Level-2 Geocoded Polarimetric Covariance (GCOV) L-band products, Relative Orbit 91, Frame 76.
* **ESA Copernicus:** Sentinel-1 C-band synthetic aperture radar ground range detected (GRD) products.
* **NASA / USGS:** Shuttle Radar Topography Mission (SRTM) 30m Global Digital Elevation Model.
* **Esri & Contributors:** World Imagery & World Boundaries Reference Map Services.
* **NVIDIA:** NVIDIA NIM Cloud Inference (`nvidia/nemotron-3.5-bolt-e4b`).

*Open-source under the MIT License.*
