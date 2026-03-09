"""Toolchain service (AutoPentest) – create and query toolchain runs/steps."""

from __future__ import annotations

import datetime
from typing import Any, List, Tuple, Optional

from sqlalchemy.orm import Session

from ..models import ToolchainRun, ToolchainStep, Target
from . import target_service


def _default_steps_for_target(target: Target) -> List[Tuple[str, str, dict[str, Any], str]]:
    """Return a list of steps.

    Each step tuple: (tool_name, preset, parameters, condition)
    condition can be "" or "wordpress".

    Notes:
    - Hydra excluded by design.
    - SQLMap excluded by default (can be added later as an advanced toggle).
    - For domain targets, URL-based tools will be given https://<domain> at runtime.
    """

    ttype = (target.type or "").lower()

    steps: List[Tuple[str, str, dict[str, Any], str]] = []

    # Recon / discovery
    if ttype == "domain":
        steps.append(("subfinder", "basic", {}, ""))
        steps.append(("amass", "enum", {}, ""))
        steps.append(("nmap", "service", {}, ""))
        steps.append(("katana", "basic", {"scope_domain": True}, ""))
        steps.append(("nuclei", "critical", {}, ""))
        steps.append(("nikto", "quick", {}, ""))
        # Conditional WordPress chain
        steps.append(("wpprobe", "detect", {}, ""))
        steps.append(("wpscan", "basic", {}, "wordpress"))

    elif ttype == "ip":
        steps.append(("nmap", "service", {}, ""))
        # Web-focused steps are best-effort on IP
        steps.append(("testssl", "standard", {}, ""))
        steps.append(("nikto", "quick", {}, ""))

    else:  # url
        steps.append(("katana", "basic", {"scope_domain": True}, ""))
        steps.append(("arjun", "get", {}, ""))
        steps.append(("ffuf", "common", {}, ""))
        steps.append(("nuclei", "critical", {}, ""))
        steps.append(("testssl", "standard", {}, ""))
        steps.append(("nikto", "quick", {}, ""))
        steps.append(("gobuster", "dir_common", {}, ""))
        steps.append(("trufflehog", "filesystem", {}, ""))
        steps.append(("wpprobe", "detect", {}, ""))
        steps.append(("wpscan", "basic", {}, "wordpress"))

    return steps


def create_toolchain_run(
    db: Session,
    target_type: str,
    target_value: str,
    notes: str = "",
    profile: str = "autopentest",
    tools: Optional[list[str]] = None,
) -> ToolchainRun:
    # Create target
    t = target_service.create_target(db, target_type, target_value, notes)

    run = ToolchainRun(
        target_id=t.id,
        profile=profile or "autopentest",
        status="queued",
        summary={},
        report_path="",
        created_at=datetime.datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Create steps
    default_steps = _default_steps_for_target(t)
    
    # Filter by user-selected tools if provided
    if tools:
        # Convert user tools to a set for faster lookup
        tool_set = set(tools)
        # We need to preserve the order from default_steps or user-defined list? 
        # Usually, order matters in toolchains (recon first). 
        # Let's keep the default order but only include what's selected.
        selected_steps = [s for s in default_steps if s[0] in tool_set]
        
        # If user explicitly asked for tools not in default_steps (like sqlmap or hydra),
        # they might want them added at the end with basic presets.
        existing_tools = set(s[0] for s in selected_steps)
        for tool_name in tools:
            if tool_name not in existing_tools:
                # Add it as a basic step at the end
                selected_steps.append((tool_name, "basic", {}, ""))
        
        steps = selected_steps
    else:
        steps = default_steps

    for idx, (tool, preset, params, condition) in enumerate(steps, start=1):
        s = ToolchainStep(
            run_id=run.id,
            step_index=idx,
            tool_name=tool,
            preset=preset or "",
            parameters=params or {},
            status="queued",
            notes="",
            condition=condition or "",
        )
        db.add(s)

    db.commit()
    db.refresh(run)
    return run


def get_runs(db: Session, skip: int = 0, limit: int = 50) -> list[ToolchainRun]:
    return db.query(ToolchainRun).order_by(ToolchainRun.created_at.desc()).offset(skip).limit(limit).all()


def get_run(db: Session, run_id: int) -> ToolchainRun | None:
    return db.query(ToolchainRun).filter(ToolchainRun.id == run_id).first()


def get_steps(db: Session, run_id: int) -> list[ToolchainStep]:
    return (
        db.query(ToolchainStep)
        .filter(ToolchainStep.run_id == run_id)
        .order_by(ToolchainStep.step_index.asc())
        .all()
    )
