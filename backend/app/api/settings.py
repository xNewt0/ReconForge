"""Settings API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import SettingResponse, SettingUpdate
from ..services import settings_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/", response_model=list[SettingResponse])
def list_settings(db: Session = Depends(get_db)):
    return settings_service.get_all_settings(db)


@router.get("/{key}", response_model=SettingResponse)
def get_setting(key: str, db: Session = Depends(get_db)):
    s = settings_service.get_setting(db, key)
    if not s:
        raise HTTPException(status_code=404, detail="Setting not found")
    return s


@router.put("/{key}", response_model=SettingResponse)
def update_setting(key: str, data: SettingUpdate, db: Session = Depends(get_db)):
    s = settings_service.update_setting(db, key, data.value)
    return s
