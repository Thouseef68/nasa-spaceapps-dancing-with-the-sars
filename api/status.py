"""
api/status.py
Status endpoint for NASA NISAR Hydro Copilot API.
"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        status_data = {
            "service": "NASA NISAR Hydro Copilot API",
            "status": "online",
            "default_model": "nvidia/nemotron-3.5-bolt-e4b",
            "provider": "NVIDIA NIM",
            "common_footprint_km2": 1480.43,
        }
        self.wfile.write(json.dumps(status_data).encode("utf-8"))

