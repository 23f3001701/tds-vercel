from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry data
DATA_PATH = os.path.join(os.path.dirname(__file__), "telemetry.json")
with open(DATA_PATH) as f:
    telemetry = json.load(f)

@app.post("/api")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 200)

    result = {}
    for region in regions:
        records = [r for r in telemetry if r["region"] == region]
        if not records:
            result[region] = {}
            continue
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]
        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 4),
            "p95_latency": round(float(np.percentile(latencies, 95)), 4),
            "avg_uptime": round(float(np.mean(uptimes)), 4),
            "breaches": int(sum(1 for l in latencies if l > threshold_ms))
        }
    return result

@app.get("/")
def root():
    return {"status": "ok"}
