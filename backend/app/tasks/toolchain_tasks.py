"""Celery task: run a toolchain (AutoPentest) sequentially."""

from __future__ import annotations

import datetime
import json
import re
import subprocess
import time
from pathlib import Path

import redis
from jinja2 import Template

from ..celery_app import celery
from ..config import settings
from ..database import SessionLocal
from ..models import Scan, ScanLog, ToolchainRun, ToolchainStep, Target
from ..services.scan_service import create_scan, update_scan_status
from ..tool_adapters import get_adapter


TOOLCHAIN_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>ReconForge AutoPentest Report – Run #{{ run.id }}</title>
  <style>
    :root { --bg:#0b1220; --card:#0f172a; --border:#1f2a44; --text:#e5e7eb; --muted:#94a3b8; --accent:#22d3ee; --bad:#fb7185; --warn:#fbbf24; --ok:#34d399; }
    *{box-sizing:border-box}
    body{margin:0;padding:24px;background:var(--bg);color:var(--text);font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu}
    .container{max-width:1100px;margin:0 auto}
    .hero{border:1px solid var(--border);background:rgba(255,255,255,.03);border-radius:16px;padding:18px 20px}
    h1{margin:0;font-size:20px;letter-spacing:-.02em}
    .meta{margin-top:6px;color:var(--muted);font-size:13px}
    .grid{margin-top:14px;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}
    .stat{border:1px solid var(--border);background:rgba(255,255,255,.03);border-radius:14px;padding:12px 14px}
    .num{font-size:20px;font-weight:800}
    .lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.12em;margin-top:4px}
    .pill{display:inline-flex;padding:3px 8px;border-radius:999px;border:1px solid rgba(255,255,255,.12);font-size:11px;color:var(--muted)}
    .section{margin-top:18px}
    .card{border:1px solid var(--border);background:rgba(255,255,255,.03);border-radius:16px;padding:14px 16px;margin-top:10px}
    .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
    .badge{font-size:11px;font-weight:800;padding:4px 8px;border-radius:999px;border:1px solid rgba(255,255,255,.14)}
    .badge.completed{color:var(--ok);border-color:rgba(52,211,153,.35);background:rgba(52,211,153,.10)}
    .badge.failed{color:var(--bad);border-color:rgba(251,113,133,.35);background:rgba(251,113,133,.10)}
    .badge.skipped{color:var(--warn);border-color:rgba(251,191,36,.35);background:rgba(251,191,36,.10)}
    .badge.running{color:var(--accent);border-color:rgba(34,211,238,.35);background:rgba(34,211,238,.10)}
    pre{margin:10px 0 0;white-space:pre-wrap;word-break:break-word;max-height:420px;overflow:auto;background:#070b14;border:1px solid var(--border);padding:12px;border-radius:12px;color:#cbd5e1;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:12px}
    a{color:#7dd3fc;text-decoration:none}
    a:hover{text-decoration:underline}
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"hero\">
      <h1>ReconForge AutoPentest Report</h1>
      <div class=\"meta\">Run #{{ run.id }} • Target: <b>{{ target.value }}</b> ({{ target.type }}) • Generated: {{ now }}</div>
      <div class=\"grid\">
        <div class=\"stat\"><div class=\"num\">{{ summary.total_steps }}</div><div class=\"lbl\">Steps</div></div>
        <div class=\"stat\"><div class=\"num\">{{ summary.completed }}</div><div class=\"lbl\">Completed</div></div>
        <div class=\"stat\"><div class=\"num\">{{ summary.failed }}</div><div class=\"lbl\">Failed</div></div>
        <div class=\"stat\"><div class=\"num\">{{ summary.skipped }}</div><div class=\"lbl\">Skipped</div></div>
      </div>
    </div>

    <div class=\"section\">
      <h2 style=\"margin:16px 0 6px; font-size:14px; color: var(--muted); text-transform: uppercase; letter-spacing: .12em;\">Steps</h2>

      {% for s in steps %}
      <div class=\"card\">
        <div class=\"row\">
          <span class=\"pill\">#{{ s.step_index }}</span>
          <b>{{ s.tool_name }}</b>
          {% if s.preset %}<span class=\"pill\">preset: {{ s.preset }}</span>{% endif %}
          <span class=\"badge {{ s.status }}\">{{ s.status }}</span>
          {% if s.scan_id %}<span class=\"pill\">scan: {{ s.scan_id }}</span>{% endif %}
        </div>
        {% if s.notes %}<div class=\"meta\" style=\"margin-top:8px\">{{ s.notes }}</div>{% endif %}
        {% if s.output %}<pre>{{ s.output }}</pre>{% endif %}
      </div>
      {% endfor %}
    </div>
  </div>
</body>
</html>"""


def _publish(r: redis.Redis, channel: str, message: str):
    try:
        r.publish(channel, json.dumps({"output": message}))
    except Exception:
        pass


def _is_wordpress(text: str) -> bool:
    t = text.lower()
    return ("wordpress" in t) or ("wp-content" in t) or ("wp-includes" in t)


def _compute_target_value(tool_name: str, target: Target) -> str:
    """Compute best-effort target string for a given tool."""
    ttype = (target.type or "").lower()
    val = (target.value or "").strip()

    url_tools = {"katana", "wpscan", "sqlmap", "gobuster", "wpprobe"}

    if tool_name in url_tools:
        if ttype == "url":
            return val
        if ttype == "domain":
            return f"https://{val}"
        if ttype == "ip":
            return f"http://{val}"

    # default
    return val


@celery.task(bind=True, name="run_toolchain")
def run_toolchain(self, run_id: int):
    db = SessionLocal()
    r = redis.Redis.from_url(settings.redis_url)
    channel = f"toolchain:{run_id}"

    try:
        run = db.query(ToolchainRun).filter(ToolchainRun.id == run_id).first()
        if not run:
            _publish(r, channel, f"[ERROR] Toolchain run not found: {run_id}")
            _publish(r, channel, "__DONE__")
            return {"status": "failed", "error": "run not found"}

        target = db.query(Target).filter(Target.id == run.target_id).first()
        if not target:
            run.status = "failed"
            db.commit()
            _publish(r, channel, "[ERROR] Target not found")
            _publish(r, channel, "__DONE__")
            return {"status": "failed", "error": "target not found"}

        steps = (
            db.query(ToolchainStep)
            .filter(ToolchainStep.run_id == run_id)
            .order_by(ToolchainStep.step_index.asc())
            .all()
        )

        run.status = "running"
        run.started_at = datetime.datetime.utcnow()
        db.commit()

        wp_detected = False

        _publish(r, channel, f"[*] AutoPentest started (run #{run_id})")
        _publish(r, channel, f"[*] Target: {target.value} ({target.type})")
        _publish(r, channel, "")

        for step in steps:
            # condition check
            if step.condition == "wordpress" and not wp_detected:
                step.status = "skipped"
                step.notes = step.notes or "Skipped: WordPress not detected"
                db.commit()
                _publish(r, channel, f"[!] [{step.tool_name}] skipped (WordPress not detected)")
                continue

            adapter = get_adapter(step.tool_name)
            if not adapter:
                step.status = "skipped"
                step.notes = f"Unknown tool: {step.tool_name}"
                db.commit()
                _publish(r, channel, f"[!] [{step.tool_name}] skipped (unknown tool)")
                continue

            if not adapter.is_installed():
                hint = getattr(adapter, "install_hint", "") or ""
                step.status = "skipped"
                step.notes = f"Tool not installed. {('Install: ' + hint) if hint else ''}".strip()
                db.commit()
                _publish(r, channel, f"[!] [{step.tool_name}] skipped (not installed)")
                if hint:
                    _publish(r, channel, f"[HINT] {step.tool_name} install: {hint}")
                continue

            # Create scan
            scan = create_scan(db, target.id, step.tool_name, step.parameters or {}, preset=step.preset or "")
            step.scan_id = scan.id
            step.status = "running"
            step.started_at = datetime.datetime.utcnow()
            db.commit()

            tool_target = _compute_target_value(step.tool_name, target)
            cmd = adapter.build_command(tool_target, step.parameters or {}, step.preset or "")

            _publish(r, channel, f"[*] [{step.tool_name}] starting…")
            _publish(r, channel, f"[*] [{step.tool_name}] command: {' '.join(cmd)}")

            # Update scan running
            update_scan_status(db, scan.id, "running", celery_task_id=self.request.id, error="", return_code=None)

            # Buffer logs
            buf: list[str] = []
            last_flush = time.monotonic()

            def flush(force: bool = False):
                nonlocal buf, last_flush
                if not buf:
                    return
                if not force and len(buf) < 50 and (time.monotonic() - last_flush) < 1.0:
                    return
                db.add_all([ScanLog(scan_id=scan.id, output=line) for line in buf])
                db.commit()
                buf = []
                last_flush = time.monotonic()

            # Run process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            stdout = process.stdout
            output_for_condition = []
            if stdout is not None:
                for line in iter(stdout.readline, ""):
                    line = line.rstrip("\n")
                    buf.append(line)
                    # publish to scan channel and toolchain channel
                    _publish(r, f"scan:{scan.id}", line)
                    _publish(r, channel, f"[{step.tool_name}] {line}")
                    # keep small sample for WP detection
                    if len(output_for_condition) < 200:
                        output_for_condition.append(line)
                    flush()

            process.wait()
            flush(force=True)

            rc = int(process.returncode or 0)
            if rc == 0:
                update_scan_status(db, scan.id, "completed", return_code=rc)
                step.status = "completed"
            else:
                update_scan_status(db, scan.id, "failed", return_code=rc, error=f"Return code {rc}")
                step.status = "failed"

            step.finished_at = datetime.datetime.utcnow()

            # WordPress detection after wpprobe
            if step.tool_name == "wpprobe":
                joined = "\n".join(output_for_condition)
                wp_detected = _is_wordpress(joined)
                if wp_detected:
                    _publish(r, channel, "[*] WordPress detected → enabling WPScan step")
                else:
                    _publish(r, channel, "[*] WordPress not detected")

            db.commit()

            # mark scan done
            _publish(r, f"scan:{scan.id}", "__DONE__")

            _publish(r, channel, f"[{'✓' if rc == 0 else '!'}] [{step.tool_name}] finished (rc={rc})")
            _publish(r, channel, "")

        # Finalize run
        steps = (
            db.query(ToolchainStep)
            .filter(ToolchainStep.run_id == run_id)
            .order_by(ToolchainStep.step_index.asc())
            .all()
        )

        completed = sum(1 for s in steps if s.status == "completed")
        failed = sum(1 for s in steps if s.status == "failed")
        skipped = sum(1 for s in steps if s.status == "skipped")

        run.status = "completed" if failed == 0 else "failed"
        run.finished_at = datetime.datetime.utcnow()
        run.summary = {
            "total_steps": len(steps),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "wordpress_detected": wp_detected,
        }

        # Generate toolchain HTML report
        settings.reports_dir.mkdir(parents=True, exist_ok=True)
        fn = f"autopentest_run{run_id}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}.html"
        out_path = settings.reports_dir / fn

        # attach last N lines per scan
        step_views = []
        for s in steps:
            out = ""
            if s.scan_id:
                logs = (
                    db.query(ScanLog)
                    .filter(ScanLog.scan_id == s.scan_id)
                    .order_by(ScanLog.timestamp.asc())
                    .all()
                )
                # cap
                lines = [l.output for l in logs]
                if len(lines) > 600:
                    lines = lines[:200] + ["… (truncated) …"] + lines[-200:]
                out = "\n".join(lines)
            step_views.append({
                "step_index": s.step_index,
                "tool_name": s.tool_name,
                "preset": s.preset,
                "status": s.status,
                "scan_id": s.scan_id,
                "notes": s.notes,
                "output": out,
            })

        tpl = Template(TOOLCHAIN_REPORT_TEMPLATE)
        html = tpl.render(
            run=run,
            target=target,
            steps=step_views,
            summary=run.summary,
            now=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        )
        out_path.write_text(html, encoding="utf-8")
        run.report_path = str(out_path)
        db.commit()

        _publish(r, channel, "[✓] AutoPentest finished")
        _publish(r, channel, "__DONE__")
        return {"status": run.status, "report_path": run.report_path, "summary": run.summary}

    except Exception as e:
        _publish(r, channel, f"[ERROR] {str(e)}")
        _publish(r, channel, "__DONE__")
        try:
            run = db.query(ToolchainRun).filter(ToolchainRun.id == run_id).first()
            if run:
                run.status = "failed"
                run.finished_at = datetime.datetime.utcnow()
                run.summary = {"error": str(e)}
                db.commit()
        except Exception:
            pass
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
