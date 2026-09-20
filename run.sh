#!/usr/bin/env bash
set -e

echo "========================================================="
echo "   Starting Atlas AI Travel Route Planning Agent"
echo "========================================================="

# 1. Start FastAPI Backend in background
echo "[1/3] Launching FastAPI Backend on http://localhost:8000..."
python -m uvicorn backend.main:app --port 8000 --reload &
BACKEND_PID=$!

# 2. Start Gradio Conversational Agent in background
echo "[2/3] Launching Gradio Conversational Agent on http://localhost:7860..."
python gradio/app.py &
GRADIO_PID=$!

# 3. Start React Frontend
echo "[3/3] Launching React Frontend on http://localhost:5173..."
cd frontend
npm run dev -- --port 5173 &
FRONTEND_PID=$!
cd ..

echo "All services running in background:"
echo " - React UI:    http://localhost:5173/"
echo " - Gradio Chat: http://localhost:7860/"
echo " - REST API:    http://localhost:8000/docs"
echo "Press Ctrl+C to terminate all services."

trap "kill $BACKEND_PID $GRADIO_PID $FRONTEND_PID" EXIT
wait
