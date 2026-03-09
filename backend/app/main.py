"""ReconForge FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, SessionLocal
from .services.settings_service import init_default_settings
from .tool_adapters import get_all_adapters

from .api import targets, scans, tools, reports, settings, toolchains
from .ws import scan_ws, toolchain_ws

logger = logging.getLogger("reconforge")


def check_tool_dependencies() -> dict[str, bool]:
    """Check which tools are installed."""
    adapters = get_all_adapters()
    status = {}
    for name, adapter in adapters.items():
        installed = adapter.is_installed()
        status[name] = installed
        if not installed:
            logger.warning(f"[!] Tool not found: {name} ({adapter.binary})")
    return status


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 ReconForge starting up…")
    init_db()
    db = SessionLocal()
    init_default_settings(db)
    db.close()
    tool_status = check_tool_dependencies()
    app.state.tool_status = tool_status
    installed = sum(1 for v in tool_status.values() if v)
    logger.info(f"  Tools: {installed}/{len(tool_status)} installed")
    yield
    # Shutdown
    logger.info("ReconForge shutting down.")


app = FastAPI(
    title="ReconForge",
    description="Pentesting orchestration platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(targets.router)
app.include_router(scans.router)
app.include_router(tools.router)
app.include_router(toolchains.router)
app.include_router(reports.router)
app.include_router(settings.router)
app.include_router(scan_ws.router)
app.include_router(toolchain_ws.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "ReconForge"}
