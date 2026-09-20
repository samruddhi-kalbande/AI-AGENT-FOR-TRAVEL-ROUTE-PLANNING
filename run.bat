@echo off
echo =========================================================
echo    Starting Atlas AI Travel Route Planning Agent
echo =========================================================

echo [1/3] Starting FastAPI Backend on http://localhost:8000...
start cmd /k "python -m uvicorn backend.main:app --port 8000 --reload"

echo [2/3] Starting Gradio Conversational Agent on http://localhost:7860...
start cmd /k "python gradio/app.py"

echo [3/3] Starting React Frontend on http://localhost:5173...
cd frontend
start cmd /k "npm run dev -- --port 5173"
cd ..

echo.
echo All services launched!
echo - Main React UI:   http://localhost:5173/
echo - Gradio Agent:    http://localhost:7860/
echo - Backend API:     http://localhost:8000/docs
echo =========================================================
pause
