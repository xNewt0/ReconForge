# 🛡️ ReconForge

**Pentesting Orchestration Platform** — A localhost web application to launch and manage common cybersecurity tools through a modern web UI.

![Stack](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square)
![Stack](https://img.shields.io/badge/Next.js-15-000000?style=flat-square)
![Stack](https://img.shields.io/badge/Celery-5.4-37814A?style=flat-square)
![Stack](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square)

---

## Features

- **9 Integrated Tools**: Nmap, Gobuster, Hydra, WPScan, Nikto, SQLMap, Subfinder, Katana, WPProbe
- **Preset & Custom Scans**: Quick-launch presets + full advanced parameter control
- **Live Terminal Output**: WebSocket-powered real-time scan output streaming
- **Concurrent Scans**: Run multiple scans simultaneously via Celery workers
- **Report Generation**: Export pentest reports as HTML or PDF
- **Dependency Checker**: Dashboard warnings for missing tools
- **Dark UI**: Professional cybersecurity dashboard with animations

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis
- At least one pentesting tool installed (nmap, gobuster, etc.)

### Option 1: Startup Script

```bash
# Clone & enter the project
cd reconforge

# Run everything
./scripts/start.sh
```

This starts Redis, the FastAPI backend (:8000), Celery worker, and Next.js frontend (:3000).

### Option 2: Manual Start

**1. Redis**
```bash
redis-server
```

**2. Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment
export RECONFORGE_REDIS_URL="redis://localhost:6379/0"
export RECONFORGE_DATABASE_URL="sqlite:///./data/reconforge.db"

# Start API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**3. Celery Worker** (new terminal)
```bash
cd backend
source venv/bin/activate
export RECONFORGE_REDIS_URL="redis://localhost:6379/0"
export RECONFORGE_DATABASE_URL="sqlite:///./data/reconforge.db"

celery -A app.celery_app.celery worker --loglevel=info --concurrency=5
```

**4. Frontend** (new terminal)
```bash
cd frontend
npm install
npm run dev
```

### Option 3: Docker Compose

```bash
cd docker
docker-compose up --build
```

---

## Usage

1. Open **http://localhost:3000**
2. Add a target (IP, domain, or URL) on the **Targets** page
3. Go to **Tools**, select a tool, pick a preset or configure params
4. Click **Launch Scan** — watch live output in the terminal panel
5. When done, generate an **HTML or PDF report** from the scan detail page

---

## Architecture

```
reconforge/
├── backend/            # FastAPI + Celery
│   └── app/
│       ├── api/        # REST endpoints
│       ├── services/   # Business logic
│       ├── tool_adapters/  # 9 tool integrations
│       ├── tasks/      # Celery background tasks
│       ├── ws/         # WebSocket streaming
│       ├── models.py   # SQLAlchemy ORM
│       └── main.py     # App entry point
├── frontend/           # Next.js + TailwindCSS
│   └── src/
│       ├── app/        # Page routes
│       ├── components/ # React components
│       └── lib/        # API client & hooks
├── docker/             # Docker Compose
└── scripts/            # Startup scripts
```

---

## Supported Tools

| Tool | Category | Features |
|------|----------|----------|
| **Nmap** | Recon | Port scan, service/OS detection, scripts |
| **Gobuster** | Scanner | Directory, DNS, VHost brute-force |
| **Hydra** | Brute-Force | SSH, FTP, HTTP, form login |
| **WPScan** | Web | WordPress vuln scanner |
| **Nikto** | Web | Web server vulnerability scanner |
| **SQLMap** | Web | SQL injection detection |
| **Subfinder** | Recon | Passive subdomain discovery |
| **Katana** | Crawl | Web endpoint crawling |
| **WPProbe** | Web | WordPress detection |

---

## API Docs

FastAPI auto-generates interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Security

- All tool commands are built as **argument lists** — never shell-interpolated
- Parameters are **whitelisted** per tool adapter
- User input is **validated** before command construction
- `subprocess.Popen` is used with `shell=False`

---

## License

MIT
# ReconForge
