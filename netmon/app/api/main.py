import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from .routers import health, devices, checks, topology, alerts, silences, admin
from ..exporters.prometheus import metrics_app
from starlette.responses import Response

app = FastAPI(title="NetMon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(checks.router, prefix="/checks", tags=["checks"])
app.include_router(topology.router, prefix="/topology", tags=["topology"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(silences.router, prefix="/silences", tags=["silences"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Static UI (D3 topology)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
app.mount("/ui", StaticFiles(directory=os.path.join(ROOT, "webui"), html=True), name="ui")

# Prometheus endpoint
@app.get("/metrics")
def metrics():
    def _start(status, headers):
        pass
    body = b"".join(metrics_app({}, _start))
    return Response(content=body, media_type="text/plain; version=0.0.4")