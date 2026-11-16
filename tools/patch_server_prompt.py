with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

target = """6. TERMINOLOGY: Always use "Frame 76" and "Relative Orbit 91". Never use "track 076", "slight", or "sub-pixel"."""

replacement = """6. TERMINOLOGY: Always use "Frame 76" and "Relative Orbit 91". Never use "track 076", "slight", or "sub-pixel".
7. CHALLENGE THEME: "DANCING WITH THE SARS" & RADAR SCATTERING PHYSICS:
   - Challenge Focus: Explaining dynamic Earth surface change while resolving radar scattering ambiguities and speckle noise.
   - Specular Reflection: Calm open water reflects microwaves away from the sensor, producing low backscatter (HH ~ -24 dB).
   - Double-Bounce Scattering: Water overtops vegetation or reed beds; microwave pulses reflect from water onto vertical stalks, bouncing 180° back to the radar antenna (HH ~ -10 dB). This explains why emergent flooded vegetation appears brighter than dry soil, confusing single-pol algorithms!
   - Bragg / Surface Roughness: Monsoon winds create capillary waves (~12 cm resonant with L-band) that scatter microwave energy directly back to the antenna (-15 to -13 dB), mimicking land.
   - Speckle & Edge Resolution: This physical mechanism explains why 99.8% of headline flood change sits in the transitional fringe band [-20, -15] dB! NISAR's dual-pol thresholding (HH < -20 dB, HV < -23 dB) separates true open water from wind roughness and flooded reeds.
   - Spatial-Shift Null Hypothesis: A 20-pixel horizontal shift test establishes the null noise spread [-0.67, +0.02] km², demonstrating that core channel change (-0.62 km²) is within random uncertainty and the braided thalweg is stable."""

assert target in code, "Target not found in server.py"
code = code.replace(target, replacement, 1)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)

print("server.py updated with Dancing with the SARs physics prompt!")

