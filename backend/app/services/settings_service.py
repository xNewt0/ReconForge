"""Settings key-value service."""

import datetime
from sqlalchemy.orm import Session
from ..models import Setting

DEFAULT_SETTINGS = {
    "wpscan_api_token": {"value": "", "description": "WPScan API token for vulnerability data"},
    "default_wordlist": {"value": "/usr/share/wordlists/dirb/common.txt", "description": "Default wordlist path"},
    "wordlist_directory": {"value": "/usr/share/wordlists", "description": "Directory containing wordlists"},
    "default_threads": {"value": "10", "description": "Default number of threads for scans"},
    "max_concurrent_scans": {"value": "5", "description": "Maximum concurrent scan tasks"},
}


def init_default_settings(db: Session):
    """Insert default settings if they don't exist."""
    for key, meta in DEFAULT_SETTINGS.items():
        existing = db.query(Setting).filter(Setting.key == key).first()
        if not existing:
            db.add(Setting(key=key, value=meta["value"], description=meta["description"]))
    db.commit()


def get_all_settings(db: Session) -> list[Setting]:
    return db.query(Setting).order_by(Setting.key).all()


def get_setting(db: Session, key: str) -> Setting | None:
    return db.query(Setting).filter(Setting.key == key).first()


def update_setting(db: Session, key: str, value: str) -> Setting | None:
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = value
        setting.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(setting)
        return setting
    # Auto-create if missing
    setting = Setting(key=key, value=value)
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting
