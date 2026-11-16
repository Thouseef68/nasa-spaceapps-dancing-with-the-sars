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

SYSTEM_PROMPT = """You are the NASA NISAR Brahmaputra Hydrological Intelligence Copilot.
VERIFIED CORE FACTS:
1. Denominator: 1,480.43 km² (Relative Orbit 91, Frame 76, descending).
2. Core Thalweg (HH < -20.0 dB, HV < -23.0 dB): Baseline = 28.42 km², Observed = 27.80 km², Net = -0.62 km². Indistinguishable from zero vs 20-pixel null spread [-0.67, +0.02] km². Navigation thalweg is STABLE.
3. Headline Water (HH < -15.0 dB, HV < -18.0 dB): Baseline = 64.90 km², Observed = 60.75 km², Net = -4.15 km².
4. 99.8% Fringe Illusion: 99.8% of new and 99.5% of receded water sits in transitional fringe band (-20 to -15 dB) due to double-bounce scattering on flooded reeds.
5. Deep Research Polarimetry: DpRVI = 0.124 (core open water specular) vs 0.648 (flooded reeds double-bounce) vs 0.885 (riparian canopy volume).
6. Speckle Statistics: Equivalent Number of Looks (ENL) = 18.42, suppressing speckle noise variance below ±0.21 dB.
7. River Braiding Invariance: Braiding Index Bi = 4.82 ± 0.28, Sinuosity S = 1.24 (invariant across flood peak).
Cite verified numbers concisely with bold markdown."""

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

