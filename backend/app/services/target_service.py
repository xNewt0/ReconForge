"""Target CRUD service."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Target, Scan


def create_target(db: Session, target_type: str, value: str, notes: str = "") -> Target:
    t = Target(type=target_type, value=value, notes=notes)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def get_targets(db: Session, skip: int = 0, limit: int = 100) -> list[Target]:
    return db.query(Target).order_by(Target.created_at.desc()).offset(skip).limit(limit).all()


def get_target(db: Session, target_id: int) -> Target | None:
    return db.query(Target).filter(Target.id == target_id).first()


def delete_target(db: Session, target_id: int) -> bool:
    t = db.query(Target).filter(Target.id == target_id).first()
    if t:
        db.delete(t)
        db.commit()
        return True
    return False


def get_target_with_scan_count(db: Session, target: Target) -> dict:
    count = db.query(func.count(Scan.id)).filter(Scan.target_id == target.id).scalar()
    return {
        "id": target.id,
        "type": target.type,
        "value": target.value,
        "notes": target.notes,
        "created_at": target.created_at,
        "scan_count": count or 0,
    }
