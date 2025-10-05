import json
import statistics
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        regions = data.get("regions", [])
        threshold = data.get("threshold_ms", 180)

        # Load telemetry data from file
        with open("q-vercel-latency.json", "r") as f:
            telemetry = json.load(f)

        result = {}
        for region in regions:
            records = telemetry.get(region, [])
            latencies = [r["latency"] for r in records]
            uptimes = [r["uptime"] for r in records]
            breaches = sum(1 for l in latencies if l > threshold)

            result[region] = {
                "avg_latency": statistics.mean(latencies) if latencies else None,
                "p95_latency": statistics.quantiles(latencies, n=100)[94] if len(latencies) >= 2 else None,
                "avg_uptime": statistics.mean(uptimes) if uptimes else None,
                "breaches": breaches
            }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

