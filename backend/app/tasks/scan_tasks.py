"""Celery tasks for running scans as background jobs."""

from __future__ import annotations

import json
import subprocess
import time

import redis

from ..celery_app import celery
from ..config import settings
from ..database import SessionLocal
from ..models import ScanLog
from ..services.scan_service import update_scan_status
from ..tool_adapters import get_adapter


@celery.task(bind=True, name="run_scan")
def run_scan(self, scan_id: int, tool_name: str, target_value: str, parameters: dict, preset: str = ""):
    """Execute a tool scan as a Celery background task.

    Notes:
    - Uses shell=False and argument lists only.
    - Streams live output to Redis PubSub.
    - Buffers DB writes for performance.
    """

    db = SessionLocal()
    r = redis.Redis.from_url(settings.redis_url)
    channel = f"scan:{scan_id}"

    # Buffer for DB writes
    buffer: list[str] = []
    last_flush = time.monotonic()

    def flush(force: bool = False):
        nonlocal buffer, last_flush
        if not buffer:
            return
        # Flush every ~50 lines or at least every ~1s
        if not force and len(buffer) < 50 and (time.monotonic() - last_flush) < 1.0:
            return
        db.add_all([ScanLog(scan_id=scan_id, output=line) for line in buffer])
        db.commit()
        buffer = []
        last_flush = time.monotonic()

    try:
        adapter = get_adapter(tool_name)
        if not adapter:
            update_scan_status(db, scan_id, "failed", error=f"Unknown tool: {tool_name}")
            _publish(r, channel, f"[ERROR] Unknown tool: {tool_name}")
            _publish(r, channel, "__DONE__")
            return {"status": "failed", "error": "Unknown tool"}

        if not adapter.is_installed():
            hint = getattr(adapter, "install_hint", "") or ""
            update_scan_status(db, scan_id, "failed", error=f"{tool_name} not installed")
            _publish(r, channel, f"[ERROR] {tool_name} is not installed on this system")
            if hint:
                _publish(r, channel, f"[HINT] Install: {hint}")
            _publish(r, channel, "__DONE__")
            return {"status": "failed", "error": f"{tool_name} not installed"}

        # Build command safely
        cmd = adapter.build_command(target_value, parameters, preset)

        # Update status to running
        update_scan_status(db, scan_id, "running", celery_task_id=self.request.id, error="", return_code=None)
        _publish(r, channel, f"[*] Starting {tool_name} scan...")
        _publish(r, channel, f"[*] Command: {' '.join(cmd)}")
        _publish(r, channel, "")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        stdout = process.stdout
        if stdout is not None:
            for line in iter(stdout.readline, ""):
                line = line.rstrip("\n")
                buffer.append(line)
                _publish(r, channel, line)
                flush()

        process.wait()
        flush(force=True)

        rc = int(process.returncode or 0)
        if rc == 0:
            update_scan_status(db, scan_id, "completed", return_code=rc)
            _publish(r, channel, "")
            _publish(r, channel, "[✓] Scan completed successfully")
        else:
            update_scan_status(db, scan_id, "failed", return_code=rc, error=f"Return code {rc}")
            _publish(r, channel, "")
            _publish(r, channel, f"[!] Scan failed (return code {rc})")

        _publish(r, channel, "__DONE__")
        return {"status": "completed" if rc == 0 else "failed", "return_code": rc}

    except subprocess.CalledProcessError as e:
        flush(force=True)
        rc = e.returncode
        update_scan_status(db, scan_id, "failed", return_code=rc, error=f"Process error: {str(e)}")
        _publish(r, channel, f"[ERROR] Process failed with return code {rc}")
        _publish(r, channel, "__DONE__")
        return {"status": "failed", "return_code": rc, "error": str(e)}
    except Exception as e:
        flush(force=True)
        update_scan_status(db, scan_id, "failed", error=str(e))
        _publish(r, channel, f"[ERROR] Unexpected exception: {str(e)}")
        _publish(r, channel, "__DONE__")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


def _publish(r: redis.Redis, channel: str, message: str):
    """Publish a message to a Redis pubsub channel."""
    try:
        r.publish(channel, json.dumps({"output": message}))
    except Exception:
        pass
