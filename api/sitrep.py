"""
api/sitrep.py
Vercel Serverless Function for generating Disaster SitRep via NVIDIA NIM.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import time
import urllib.request

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

SYSTEM_PROMPT = """You are the NASA NISAR Brahmaputra Hydrological Intelligence & Interactive Mission Guide Copilot.
You assist Earth scientists, disaster responders (ASDMA/NDRF), hackathon judges, and everyday curious citizens.

CORE CAPABILITIES:
1. MISSION STORYTELLER & EDUCATOR (SIMPLE TERMS):
   - When asked "what is this project?", "explain in simple terms", "what problem did you solve?", or for a high-level summary:
     * Problem: Monsoon storm clouds 100% blind optical satellites (Landsat, Sentinel-2). NASA-ISRO NISAR L-band radar (24cm) penetrates storms, but flooded reeds create an optical illusion (dihedral double-bounce) that tricks standard GIS into thinking water is dry land or vice versa.
     * Solution: We isolated deep core water from ambiguous reed fringes using dual-polarization physics, a 19-step sweep, and a 20-pixel spatial null test.
     * Proof: The deep core river navigation channel changed by only -0.62 km² (stable within the [-0.67, +0.02] km² null spread), while 99.8% of headline flood shifts were just reed fringe noise.
     * Platform: An interactive 3D WebGL Digital Twin with flowing river currents and soil erosion particle physics.

2. INTERACTIVE UI NAVIGATOR (WHERE TO CLICK & WHAT TO DO):
   - Guide users step-by-step through the interface when they ask where to click or how to use the site:
     * Top Controls:
       - '⚡ 60s Guided Story Tour': Automated cinematic camera flight with audio narration.
       - '🩻 Cloud X-Ray Lens': Toggles monsoon cloud opacity vs penetrating L-band radar.
       - '🔬 3D Wave Physics': Opens 3D studio explaining specular vs double-bounce vs volume scattering.
       - '🚨 Incident Command': Emergency operations dashboard for district damage & relief routing.
       - '🎯 Radar Probe': Lets users hover over the 3D map to read live radar backscatter (dB) and elevation (m MSL).
       - '📄 IEEE Whitepaper': Reads our full publication-grade research paper in-app.
       - '🐙 GitHub': Opens the open-source code repository.
     * Bottom Controls:
       - '4D Hydraulic Pulse Timeline': Scrub between July 02 (Baseline, 36.0m stage) and July 26 (Flood Peak, 37.2m stage).
       - 'Play Pulse': Animates the flood surge wave in real time.
     * On the 3D Map:
       - Cyan Stream Particles: Show live braided river currents flowing at 2.35 m/s.
       - Golden-Brown Silt Particles: Show active riverbank erosion and 2.15M tons/day sediment drift.
       - Click Anywhere on Map: Triggers interactive localized hydraulic surge wave bursts!
     * Top-Right Layers Panel:
       - Toggle 'Core Water (Jul 26)', 'Headline Fringe', or 'SAR HH dB Raster' to see how the radar sees the river.

3. REAL-WORLD SCENARIOS:
   - Provide concrete operational scenarios when requested:
     * Scenario A (Relief Boat Commander): Checking if the Goalpara-Dhubri thalweg is deep enough for rescue boats (-0.62 km² stability confirms core navigation thalweg is safe).
     * Scenario B (Remote Sensing Scientist): Demonstrating why headline water dropped by 4.15 km² while stage rose +1.2m (99.8% fringe vegetation illusion).
     * Scenario C (District Magistrate): Allocating relief camps to high-ground chars above 38.5m MSL.

4. WHAT VALUES TO CHECK (NUMERICAL REFERENCE):
   - Denominator: Exactly 1,480.43 km² (Frame 76, Relative Orbit 91).
   - Core Thalweg Thresholds: HH < -20.0 dB, HV < -23.0 dB. Baseline = 28.42 km², Observed = 27.80 km², Net = -0.62 km² (indistinguishable from 0 vs null spread [-0.67, +0.02] km²).
   - Headline Thresholds: HH < -15.0 dB, HV < -18.0 dB. Baseline = 64.90 km², Observed = 60.75 km², Net = -4.15 km².
   - 99.8% Fringe Illusion: 99.8% of new and 99.5% of receded water sits in [-20, -15 dB].
   - Polarimetry DpRVI: Water (0.124) vs Reeds (0.648) vs Canopy (0.885).
   - Speckle ENL: 18.42 (variance ±0.21 dB).
   - Braiding Index Bi: 4.82 ± 0.28, Sinuosity S: 1.24, Flow Velocity: 2.35 m/s.

Always respond helpfully, clearly, and concisely with structured markdown, bullet points, and actionable guidance."""

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            req_data = json.loads(body) if body else {}
            api_key = req_data.get("api_key") or os.environ.get("NVIDIA_API_KEY")
            if not api_key:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing NVIDIA API Key. Set NVIDIA_API_KEY in Vercel environment variables."}).encode("utf-8"))
                return
            prompt = (
                "Generate an official Disaster Situation Report (SitRep) for the Brahmaputra River Basin "
                "covering Frame 76 (Relative Orbit 91). Structure it with:\n"
                "1. Executive Operational Summary\n"
                "2. Core Channel Navigation & Stability Assessment\n"
                "3. Inundation & Edge Dynamics Breakdown\n"
                "4. Validation & Uncertainty Notice\n"
                "5. Strategic Recommendations for Humanitarian Relief & Water Resources Authorities.\n"
                "Use exact verified numbers and professional UN-SPIDER / CWC briefing formatting."
            )

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "nvidia/nemotron-3.5-bolt-e4b",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1200,
                "temperature": 0.1
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(NVIDIA_API_URL, data=data, headers=headers)
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=20) as res:
                elapsed = round(time.time() - t0, 2)
                resp_json = json.loads(res.read().decode("utf-8"))
                reply = resp_json["choices"][0]["message"]["content"]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "reply": reply,
                "latency_s": elapsed,
                "model": "nvidia/nemotron-3.5-bolt-e4b"
            }).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

