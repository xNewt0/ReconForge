"""Report generation service – HTML and PDF reports."""

import datetime
from pathlib import Path
from jinja2 import Template
from sqlalchemy.orm import Session

from ..models import Report, Scan, ScanLog, Target
from ..config import settings

REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ReconForge Report – {{ scan.tool_name | upper }} Scan #{{ scan.id }}</title>
<style>
  :root { --bg: #0f172a; --card: #1e293b; --accent: #06b6d4; --text: #e2e8f0; --dim: #94a3b8; --border: #334155; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: 'Inter','Segoe UI',sans-serif; background:var(--bg); color:var(--text); padding:2rem; line-height:1.6; }
  .container { max-width:900px; margin:0 auto; }
  h1 { color:var(--accent); margin-bottom:.5rem; font-size:1.8rem; }
  h2 { color:var(--accent); margin-top:2rem; margin-bottom:.5rem; font-size:1.2rem; border-bottom:1px solid var(--border); padding-bottom:.3rem; }
  .meta { color:var(--dim); font-size:.9rem; margin-bottom:1.5rem; }
  .card { background:var(--card); border:1px solid var(--border); border-radius:8px; padding:1.2rem; margin-bottom:1rem; }
  table { width:100%; border-collapse:collapse; margin:.5rem 0; }
  th,td { text-align:left; padding:.4rem .8rem; border-bottom:1px solid var(--border); font-size:.9rem; }
  th { color:var(--accent); }
  .output { background:#0c1222; border:1px solid var(--border); border-radius:6px; padding:1rem; font-family:'Fira Code','Courier New',monospace; font-size:.82rem; white-space:pre-wrap; word-break:break-all; max-height:600px; overflow-y:auto; color:#a5f3fc; }
  .footer { margin-top:2rem; color:var(--dim); font-size:.8rem; text-align:center; }
  @media print { body { background:#fff; color:#111; } .output { background:#f8f8f8; color:#111; } h1,h2,th { color:#0891b2; } }
</style>
</head>
<body>
<div class="container">
  <h1>🛡️ ReconForge — Scan Report</h1>
  <p class="meta">Generated {{ now }}</p>

  <h2>Target</h2>
  <div class="card">
    <table>
      <tr><th>Type</th><td>{{ target.type | upper }}</td></tr>
      <tr><th>Value</th><td>{{ target.value }}</td></tr>
    </table>
  </div>

  <h2>Scan Details</h2>
  <div class="card">
    <table>
      <tr><th>Tool</th><td>{{ scan.tool_name }}</td></tr>
      <tr><th>Preset</th><td>{{ scan.preset or 'Custom' }}</td></tr>
      <tr><th>Status</th><td>{{ scan.status }}</td></tr>
      <tr><th>Started</th><td>{{ scan.started_at or '—' }}</td></tr>
      <tr><th>Finished</th><td>{{ scan.finished_at or '—' }}</td></tr>
    </table>
  </div>

  <h2>Parameters</h2>
  <div class="card">
    <table>
    {% for key, val in params.items() %}
      <tr><th>{{ key }}</th><td>{{ val }}</td></tr>
    {% endfor %}
    {% if not params %}
      <tr><td colspan="2">Default parameters</td></tr>
    {% endif %}
    </table>
  </div>

  <h2>Full Output</h2>
  <div class="output">{{ output }}</div>

  <p class="footer">ReconForge Pentesting Platform — {{ now }}</p>
</div>
</body>
</html>"""


def generate_report(db: Session, scan_id: int, fmt: str = "html") -> Report | None:
    """Generate a scan report.

    NOTE: PDF output intentionally not supported (HTML only).
    """

    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return None

    target = db.query(Target).filter(Target.id == scan.target_id).first()
    logs = db.query(ScanLog).filter(ScanLog.scan_id == scan_id).order_by(ScanLog.timestamp.asc()).all()
    output = "\n".join(log.output for log in logs)

    template = Template(REPORT_TEMPLATE)
    html_content = template.render(
        scan=scan,
        target=target,
        params=scan.parameters or {},
        output=output,
        now=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    )

    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    filename = f"report_scan{scan_id}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    html_path = settings.reports_dir / f"{filename}.html"
    html_path.write_text(html_content, encoding="utf-8")

    report = Report(scan_id=scan_id, format="html", file_path=str(html_path))
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
