"""Targets API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import TargetCreate, TargetResponse
from ..services import target_service

router = APIRouter(prefix="/api/targets", tags=["targets"])


@router.post("/", response_model=TargetResponse)
def create_target(data: TargetCreate, db: Session = Depends(get_db)):
    t = target_service.create_target(db, data.type, data.value, data.notes)
    return target_service.get_target_with_scan_count(db, t)


@router.get("/", response_model=list[TargetResponse])
def list_targets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    targets = target_service.get_targets(db, skip, limit)
    return [target_service.get_target_with_scan_count(db, t) for t in targets]


@router.get("/{target_id}", response_model=TargetResponse)
def get_target(target_id: int, db: Session = Depends(get_db)):
    t = target_service.get_target(db, target_id)
    if not t:
        raise HTTPException(status_code=404, detail="Target not found")
    return target_service.get_target_with_scan_count(db, t)


@router.delete("/{target_id}")
def delete_target(target_id: int, db: Session = Depends(get_db)):
    if not target_service.delete_target(db, target_id):
        raise HTTPException(status_code=404, detail="Target not found")
    return {"status": "deleted"}
