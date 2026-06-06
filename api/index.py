from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import numpy as np
import json, os

app = FastAPI()

DATA_PATH = os.path.join(os.path.dirname(__file__), "telemetry.json")
with open(DATA_PATH) as f:
    telemetry = json.load(f)

def compute(regions, threshold_ms):
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

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "*",
}

@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(content={}, headers=CORS_HEADERS)

@app.post("/")
async def root_post(request: Request):
    body = await request.json()
    result = compute(body.get("regions", []), body.get("threshold_ms", 200))
    return JSONResponse(content=result, headers=CORS_HEADERS)

@app.post("/api")
async def api_post(request: Request):
    body = await request.json()
    result = compute(body.get("regions", []), body.get("threshold_ms", 200))
    return JSONResponse(content=result, headers=CORS_HEADERS)

@app.get("/")
def root_get():
    return JSONResponse(content={"status": "ok"}, headers=CORS_HEADERS)
