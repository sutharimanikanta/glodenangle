#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  Gold Buy Advisor — start both services
#  Usage: bash start.sh
# ─────────────────────────────────────────────────────────────────

set -e

# Check .env exists
if [ ! -f .env ]; then
  echo "⚠️  No .env file found. Copying from .env.example..."
  cp .env.example .env
  echo "✅  Created .env — edit it to add your GROQ_API_KEY (optional but recommended)"
fi

# Kill anything on our ports
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 8501/tcp 2>/dev/null || true

echo ""
echo "✦  Starting Gold Buy Advisor"
echo "   Backend  → http://localhost:8000"
echo "   Frontend → http://localhost:8501"
echo ""

# Start FastAPI backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 2  # Give backend time to initialize DB

# Start Streamlit frontend
streamlit run app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --browser.gatherUsageStats false \
  --theme.base dark \
  --theme.backgroundColor "#0F0E0A" \
  --theme.secondaryBackgroundColor "#1A1812" \
  --theme.textColor "#F0E6C8" \
  --theme.primaryColor "#C8942A" &
FRONTEND_PID=$!

echo "Press Ctrl+C to stop both services"
wait $BACKEND_PID $FRONTEND_PID
