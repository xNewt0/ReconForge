#!/usr/bin/env bash
# ReconForge – Local Startup Script
# Starts all services in the background without Docker.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT/data"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🛡️  ReconForge – Starting services…${NC}"
echo ""

# -- Data directory --
mkdir -p "$DATA_DIR/reports"

# ---- Check Redis ----
if ! command -v redis-server &>/dev/null; then
  echo -e "${RED}[✗] redis-server not found. Install Redis first.${NC}"
  exit 1
fi

if ! pgrep -x redis-server &>/dev/null; then
  echo -e "${GREEN}[+] Starting Redis…${NC}"
  redis-server --daemonize yes
else
  echo -e "${GREEN}[✓] Redis already running${NC}"
fi

# ---- Backend venv ----
if [ ! -d "$BACKEND_DIR/venv" ]; then
  echo -e "${CYAN}[+] Creating Python venv…${NC}"
  python3 -m venv "$BACKEND_DIR/venv"
fi

source "$BACKEND_DIR/venv/bin/activate"
pip install -q -r "$BACKEND_DIR/requirements.txt"

# ---- Environment ----
export RECONFORGE_REDIS_URL="redis://localhost:6379/0"
export RECONFORGE_DATABASE_URL="sqlite:///$DATA_DIR/reconforge.db"

# ---- Celery Worker ----
echo -e "${GREEN}[+] Starting Celery worker…${NC}"
cd "$BACKEND_DIR"
celery -A app.celery_app.celery worker --loglevel=info --concurrency=5 &
CELERY_PID=$!

# ---- Backend ----
echo -e "${GREEN}[+] Starting FastAPI backend on :8000…${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# ---- Frontend ----
echo -e "${GREEN}[+] Starting Next.js frontend on :3000…${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  ReconForge is running!${NC}"
echo -e "  Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Press Ctrl+C to stop all services."

# Trap cleanup
cleanup() {
  echo ""
  echo -e "${CYAN}Shutting down…${NC}"
  kill $CELERY_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null
  wait
  echo -e "${GREEN}Done.${NC}"
}
trap cleanup SIGINT SIGTERM

wait
