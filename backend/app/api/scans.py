"""Scans API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ScanCreate, ScanResponse, ScanDetailResponse, ScanLogResponse, DashboardStats
from ..services import scan_service, target_service
from ..tasks.scan_tasks import run_scan
from ..tool_adapters import get_adapter

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("/", response_model=ScanResponse)
def launch_scan(data: ScanCreate, db: Session = Depends(get_db)):
    # Verify target exists
    target = target_service.get_target(db, data.target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    # Verify tool exists
    adapter = get_adapter(data.tool_name)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {data.tool_name}")

    # Create scan record
    scan = scan_service.create_scan(db, data.target_id, data.tool_name, data.parameters, data.preset)

    # Dispatch Celery task
    task = run_scan.delay(scan.id, data.tool_name, target.value, data.parameters, data.preset)

    # Store celery task id
    scan_service.update_scan_status(db, scan.id, "queued", celery_task_id=task.id)
    db.refresh(scan)

    return scan


@router.get("/", response_model=list[ScanResponse])
def list_scans(
    target_id: int | None = None,
    status: str | None = None,
    tool_name: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return scan_service.get_scans(db, target_id, status, tool_name, skip, limit)


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    return scan_service.get_dashboard_stats(db)


@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = scan_service.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    logs = scan_service.get_scan_logs(db, scan_id)
    target = target_service.get_target(db, scan.target_id)

    return {
        **{c.name: getattr(scan, c.name) for c in scan.__table__.columns},
        "target": target_service.get_target_with_scan_count(db, target),
        "logs": [{"id": l.id, "output": l.output, "timestamp": l.timestamp} for l in logs],
    }


@router.get("/{scan_id}/logs", response_model=list[ScanLogResponse])
def get_scan_logs(scan_id: int, db: Session = Depends(get_db)):
    return scan_service.get_scan_logs(db, scan_id)
