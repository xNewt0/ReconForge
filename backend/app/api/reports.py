"""Reports API router."""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ReportCreate, ReportResponse
from ..models import Report
from ..services import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse)
def generate_report(data: ReportCreate, db: Session = Depends(get_db)):
    report = report_service.generate_report(db, data.scan_id, data.format)
    if not report:
        raise HTTPException(status_code=404, detail="Scan not found")
    return report


@router.get("/", response_model=list[ReportResponse])
def list_reports(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.created_at.desc()).all()


@router.get("/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    file_path = Path(report.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    media = "application/pdf" if report.format == "pdf" else "text/html"
    return FileResponse(str(file_path), media_type=media, filename=file_path.name)
