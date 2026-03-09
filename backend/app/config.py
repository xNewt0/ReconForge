"""Application configuration via pydantic-settings."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ReconForge"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./data/reconforge.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Directories
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "data"
    reports_dir: Path = data_dir / "reports"
    wordlists_dir: Path = Path("/usr/share/wordlists")

    # Default scan settings
    default_threads: int = 10
    max_concurrent_scans: int = 5

    class Config:
        env_prefix = "RECONFORGE_"


settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.reports_dir.mkdir(parents=True, exist_ok=True)
