from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .routers import (
    plans, hedis, cahps, members, campaigns,
    alerts, interventions, team_view, simulator, star_summary,
    market, hos, outreach,
)
from .services.voice_agent import handle_voice_agent

app = FastAPI(title="StarPulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(star_summary.router, prefix="/api")
app.include_router(plans.router, prefix="/api")
app.include_router(hedis.router, prefix="/api")
app.include_router(cahps.router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(interventions.router, prefix="/api")
app.include_router(team_view.router, prefix="/api")
app.include_router(simulator.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(hos.router, prefix="/api")
app.include_router(outreach.router, prefix="/api")


@app.on_event("startup")
async def warmup_warehouse():
    import asyncio, logging
    logger = logging.getLogger("startup")
    async def _warm():
        try:
            from .db import query
            from .config import settings
            if settings.databricks_host:
                query("SELECT 1")
                logger.info("Databricks warehouse warmed up")
        except Exception as e:
            logger.warning("Warehouse warmup failed (will retry on first request): %s", e)
    asyncio.create_task(_warm())


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/connection-status")
def connection_status():
    from .db import query
    from .config import settings
    has_config = bool(settings.databricks_host and settings.databricks_token and settings.databricks_http_path)
    from .services import message_ai
    ai_messaging = "live" if message_ai.is_live() else "fallback"
    if not has_config:
        return {"connected": False, "source": "fallback", "reason": "missing_secrets", "ai_messaging": ai_messaging}
    try:
        rows = query("SELECT COUNT(*) AS n FROM aiagenticdemo.stars_gold.gold_star_rating_summary WHERE measurement_year = 2025")
        count = rows[0]["n"] if rows else 0
        from .services import ml_propensity
        propensity_model = "live" if ml_propensity.is_live() else "fallback"
        return {"connected": True, "source": "live", "row_count": count, "propensity_model": propensity_model, "ai_messaging": ai_messaging}
    except Exception as exc:
        return {"connected": False, "source": "fallback", "reason": str(exc)[:120], "propensity_model": "fallback", "ai_messaging": ai_messaging}


# ── Twilio ConversationRelay WebSocket ────────────────────────────
@app.websocket("/ws/voice-agent")
async def ws_voice_agent(websocket: WebSocket):
    await handle_voice_agent(websocket)


# Serve compiled React frontend
_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(_dist):
    _assets = os.path.join(_dist, "assets")
    if os.path.isdir(_assets):
        app.mount("/assets", StaticFiles(directory=_assets), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        return FileResponse(
            os.path.join(_dist, "index.html"),
            headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"},
        )
