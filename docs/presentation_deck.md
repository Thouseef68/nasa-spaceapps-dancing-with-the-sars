# NASA Space Apps Challenge 2026: Presentation Script & Slide Deck

**Team:** Black Hole Survivors  
**Challenge:** Dancing with the SARs  
**Project:** HydroWaltz — NISAR 3D Hydrological Digital Twin & AI Intelligence Platform  

---

## Part 1: The 30-Second Elevator Pitch (For Quick Judging Round)

> *"Every monsoon, the Brahmaputra River in India swells into an inland sea, displacing millions. Optical satellites are blinded by perpetual storm clouds, leaving disaster relief teams in the dark.*
> 
> *We built **HydroWaltz** — an interactive 3D digital twin and AI copilot powered by NASA-ISRO's new **NISAR** radar satellite and **NVIDIA NIM**.*
> 
> *By solving the classic radar 'edge noise' illusion with dual-pol thresholding and a 20-pixel spatial-shift null test, we prove that while surface fringes fluctuate, the core navigation channel remained rock-solid. With real-time 3D elevation profiling, temporal swipe comparison, and instant UN-SPIDER disaster SitRep generation in under 2 seconds, HydroWaltz turns raw radar pulses into lifesaving humanitarian intelligence."*

---

## Part 2: The 2-Minute Video Presentation Script (Slide-by-Slide)

### Slide 1: Title & The Problem (0:00 – 0:20)
- **Visual:** Split screen: Cloud-covered optical satellite image of Assam vs. raw L-band NISAR radar penetrating through.
- **Voiceover:**
  > *"Welcome. We are Team **Black Hole Survivors**, presenting **HydroWaltz** for the NASA Space Apps Challenge: 'Dancing with the SARs'.*
  > 
  > *During South Asia's monsoon, floods swallow islands and embankments. But traditional optical cameras see only clouds. Synthetic Aperture Radar can pierce the storm, but raw radar data is plagued by speckle noise, complex scattering, and false boundary alarms."*

### Slide 2: The Space-to-Valley 3D Digital Twin (0:20 – 0:45)
- **Visual:** Video capture zooming from the 3D globe in space down through the atmosphere into the Brahmaputra braided reach at Goalpara with 3D elevation terrain.
- **Voiceover:**
  > *"To solve this, we built a hardware-accelerated 3D Digital Twin using MapLibre GL and global elevation tiles.*
  > 
  > *Starting from NISAR's orbit 747 kilometers in space, users dive directly into the river valley. We process Level-2 dual-polarization GCOV radar swaths from Frame 76, draping calibrated radar backscatter and flood layers directly over 3D topography."*

### Slide 3: The Radar Physics & The Scientific Breakthrough (0:45 – 1:15)
- **Visual:** The 19-step sensitivity curve, the spatial-shift null test table, and the red/orange core water layer overlay.
- **Voiceover:**
  > *"When standard tools detect 4.7 square kilometers of new water, is it a real flood, or just speckle noise?*
  > 
  > *Our pipeline tested this with a 19-step sensitivity sweep and a 20-pixel spatial-shift null test. We discovered that over 99% of detected change occurs in boundary fringes. By isolating Core Open Water below minus 20 dB HH and minus 23 dB HV, we proved the river's main channel had a net change of only minus 0.62 square kilometers — completely indistinguishable from zero against measurement noise. This prevents false alarms for maritime authorities."*

### Slide 4: Interactive Tools & NVIDIA AI Hydro-Copilot (1:15 – 1:45)
- **Visual:** User drawing a river transect, swiping the before/after curtain, and clicking "Generate SitRep" in the AI drawer.
- **Voiceover:**
  > *"HydroWaltz puts professional hydraulic tools at anyone's fingertips:*
  > 
  > *- With our **River Transect tool**, click anywhere to profile water stage height against embankment crests.*
  > *- With **Swipe Compare**, interactively peel back time between July 02 baseline and July 26 flood.*
  > *- And powered by **NVIDIA NIM**, our embedded AI Hydro-Copilot delivers sub-second answers to emergency queries and generates official UN-SPIDER Disaster Situation Reports at the click of a button."*

### Slide 5: Real-World Impact & Conclusion (1:45 – 2:00)
- **Visual:** District breakdown table showing Goalpara and Barpeta exposure, ending on the Team Black Hole Survivors logo.
- **Voiceover:**
  > *"By uniting NISAR radar physics, 3D spatial twins, and autonomous AI, HydroWaltz transforms raw satellite data into actionable decisions for flood defense.*
  > 
  > *Thank you. We are Black Hole Survivors, dancing with the SARs to protect vulnerable communities worldwide."*

