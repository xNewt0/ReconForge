"""Scan service – create scans, query history, get logs."""

import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Scan, ScanLog, Target


def create_scan(db: Session, target_id: int, tool_name: str, parameters: dict, preset: str = "") -> Scan:
    scan = Scan(
        target_id=target_id,
        tool_name=tool_name,
        parameters=parameters,
        preset=preset,
        status="queued",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def update_scan_status(db: Session, scan_id: int, status: str, **kwargs) -> Scan | None:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return None
    scan.status = status
    if status == "running" and not scan.started_at:
        scan.started_at = datetime.datetime.utcnow()
    if status in ("completed", "failed"):
        scan.finished_at = datetime.datetime.utcnow()
    for k, v in kwargs.items():
        if hasattr(scan, k):
            setattr(scan, k, v)
    db.commit()
    db.refresh(scan)
    return scan


def add_scan_log(db: Session, scan_id: int, output: str) -> ScanLog:
    log = ScanLog(scan_id=scan_id, output=output)
    db.add(log)
    db.commit()
    return log


def get_scans(db: Session, target_id: int | None = None, status: str | None = None,
              tool_name: str | None = None, skip: int = 0, limit: int = 50) -> list[Scan]:
    q = db.query(Scan)
    if target_id:
        q = q.filter(Scan.target_id == target_id)
    if status:
        q = q.filter(Scan.status == status)
    if tool_name:
        q = q.filter(Scan.tool_name == tool_name)
    return q.order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()


def get_scan(db: Session, scan_id: int) -> Scan | None:
    return db.query(Scan).filter(Scan.id == scan_id).first()


def get_scan_logs(db: Session, scan_id: int) -> list[ScanLog]:
    return db.query(ScanLog).filter(ScanLog.scan_id == scan_id).order_by(ScanLog.timestamp.asc()).all()


def get_dashboard_stats(db: Session) -> dict:
    total = db.query(func.count(Scan.id)).scalar() or 0
    running = db.query(func.count(Scan.id)).filter(Scan.status == "running").scalar() or 0
    completed = db.query(func.count(Scan.id)).filter(Scan.status == "completed").scalar() or 0
    failed = db.query(func.count(Scan.id)).filter(Scan.status == "failed").scalar() or 0
    total_targets = db.query(func.count(Target.id)).scalar() or 0
    recent = db.query(Scan).order_by(Scan.created_at.desc()).limit(10).all()
    return {
        "total_scans": total,
        "running_scans": running,
        "completed_scans": completed,
        "failed_scans": failed,
        "total_targets": total_targets,
        "recent_scans": recent,
    }
