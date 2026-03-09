"""SQLAlchemy ORM models."""

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .database import Base


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # ip, domain, url
    value = Column(String(500), nullable=False)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scans = relationship("Scan", back_populates="target", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    tool_name = Column(String(50), nullable=False)
    parameters = Column(JSON, default=dict)
    preset = Column(String(100), default="")
    status = Column(String(20), default="queued")  # queued, running, completed, failed
    celery_task_id = Column(String(255), default="")

    # Execution info
    return_code = Column(Integer, nullable=True)
    error = Column(Text, default="")

    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    target = relationship("Target", back_populates="scans")
    logs = relationship("ScanLog", back_populates="scan", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="scan", cascade="all, delete-orphan")


class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    output = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    scan = relationship("Scan", back_populates="logs")


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, default="")
    description = Column(String(500), default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    format = Column(String(10), default="html")  # html
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scan = relationship("Scan", back_populates="reports")


class ToolchainRun(Base):
    __tablename__ = "toolchain_runs"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)

    profile = Column(String(100), default="autopentest")
    status = Column(String(20), default="queued")  # queued, running, completed, failed

    # optional: aggregated report for the whole run
    report_path = Column(String(500), default="")
    summary = Column(JSON, default=dict)

    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    target = relationship("Target")
    steps = relationship("ToolchainStep", back_populates="run", cascade="all, delete-orphan")


class ToolchainStep(Base):
    __tablename__ = "toolchain_steps"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("toolchain_runs.id"), nullable=False)
    step_index = Column(Integer, nullable=False)

    tool_name = Column(String(50), nullable=False)
    preset = Column(String(100), default="")
    parameters = Column(JSON, default=dict)

    # link to Scan (optional)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=True)

    status = Column(String(20), default="queued")  # queued, running, completed, failed, skipped
    notes = Column(Text, default="")

    # conditional execution
    condition = Column(String(50), default="")  # e.g. "wordpress"

    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    run = relationship("ToolchainRun", back_populates="steps")
    scan = relationship("Scan")
