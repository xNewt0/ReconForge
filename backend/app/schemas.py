"""Pydantic schemas for API request/response validation."""

from __future__ import annotations

import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Targets ──────────────────────────────────────────────────────────────────

class TargetCreate(BaseModel):
    type: str = Field(..., pattern=r"^(ip|domain|url)$")
    value: str = Field(..., min_length=1, max_length=500)
    notes: str = ""


class TargetResponse(BaseModel):
    id: int
    type: str
    value: str
    notes: str
    created_at: datetime.datetime
    scan_count: int = 0

    class Config:
        from_attributes = True


# ── Scans ────────────────────────────────────────────────────────────────────

class ScanCreate(BaseModel):
    target_id: int
    tool_name: str
    parameters: dict[str, Any] = {}
    preset: str = ""


class ScanResponse(BaseModel):
    id: int
    target_id: int
    tool_name: str
    parameters: dict[str, Any]
    preset: str
    status: str
    celery_task_id: str
    return_code: Optional[int] = None
    error: str = ""
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ScanDetailResponse(ScanResponse):
    target: TargetResponse
    logs: list[ScanLogResponse] = []


class ScanLogResponse(BaseModel):
    id: int
    output: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


# ── Tools ────────────────────────────────────────────────────────────────────

class ToolPreset(BaseModel):
    name: str
    label: str
    description: str


class ToolParameter(BaseModel):
    name: str
    label: str
    type: str  # text, number, boolean, select, file
    required: bool = False
    default: Any = None
    options: list[str] = []
    description: str = ""


class ToolInfo(BaseModel):
    name: str
    label: str
    description: str
    category: str
    installed: bool
    enabled: bool = True
    install_hint: str = ""
    presets: list[ToolPreset]
    parameters: list[ToolParameter]


# ── Reports ──────────────────────────────────────────────────────────────────

class ReportCreate(BaseModel):
    scan_id: int
    format: str = Field("html", pattern=r"^(html)$")


class ReportResponse(BaseModel):
    id: int
    scan_id: int
    format: str
    file_path: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ── Settings ─────────────────────────────────────────────────────────────────

class SettingUpdate(BaseModel):
    value: str


class SettingResponse(BaseModel):
    id: int
    key: str
    value: str
    description: str
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


# ── Dashboard ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_scans: int
    running_scans: int
    completed_scans: int
    failed_scans: int
    total_targets: int
    recent_scans: list[ScanResponse]


# ── Toolchains (AutoPentest) ───────────────────────────────────────────────

class ToolchainLaunch(BaseModel):
    target_type: str = Field(..., pattern=r"^(ip|domain|url)$")
    target_value: str = Field(..., min_length=1, max_length=500)
    notes: str = ""
    profile: str = "autopentest"
    tools: Optional[list[str]] = None


class ToolchainStepResponse(BaseModel):
    id: int
    run_id: int
    step_index: int
    tool_name: str
    preset: str
    parameters: dict[str, Any] = {}
    scan_id: Optional[int] = None
    status: str
    notes: str = ""
    condition: str = ""
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ToolchainRunResponse(BaseModel):
    id: int
    target_id: int
    profile: str
    status: str
    report_path: str = ""
    summary: dict[str, Any] = {}
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ToolchainRunDetailResponse(ToolchainRunResponse):
    target: TargetResponse
    steps: list[ToolchainStepResponse] = []


# Fix forward reference
ScanDetailResponse.model_rebuild()
