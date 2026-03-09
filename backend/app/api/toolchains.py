"""AutoPentest Toolchain API router."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ToolchainLaunch, ToolchainRunResponse, ToolchainRunDetailResponse
from ..services import toolchain_service, target_service
from ..tasks.toolchain_tasks import run_toolchain

router = APIRouter(prefix="/api/toolchains", tags=["toolchains"])


@router.post("/launch", response_model=ToolchainRunResponse)
def launch_toolchain(data: ToolchainLaunch, db: Session = Depends(get_db)):
    run = toolchain_service.create_toolchain_run(
        db,
        target_type=data.target_type,
        target_value=data.target_value,
        notes=data.notes,
        profile=data.profile,
        tools=data.tools,
    )
    task = run_toolchain.delay(run.id)
    return run


@router.get("/", response_model=list[ToolchainRunResponse])
def list_toolchains(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return toolchain_service.get_runs(db, skip=skip, limit=limit)


@router.get("/{run_id}", response_model=ToolchainRunDetailResponse)
def get_toolchain(run_id: int, db: Session = Depends(get_db)):
    run = toolchain_service.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Toolchain run not found")

    steps = toolchain_service.get_steps(db, run_id)
    target = target_service.get_target(db, run.target_id)

    return {
        **{c.name: getattr(run, c.name) for c in run.__table__.columns},
        "target": target_service.get_target_with_scan_count(db, target),
        "steps": [{c.name: getattr(s, c.name) for c in s.__table__.columns} for s in steps],
    }


@router.get("/{run_id}/download")
def download_toolchain_report(run_id: int, db: Session = Depends(get_db)):
    run = toolchain_service.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Toolchain run not found")
    if not run.report_path:
        raise HTTPException(status_code=404, detail="Report not ready")

    file_path = Path(run.report_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(str(file_path), media_type="text/html", filename=file_path.name)
