@echo off
SETLOCAL

:: Health & Wellness Planner - Windows Launcher

:: Set environment variables
set API_BASE_URL=http://localhost:8000

if "%1"=="install" (
    echo 🚀 Installing dependencies...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    echo ✅ Done!
    goto :EOF
)

if "%1"=="backend" (
    echo 🏗️  Starting FastAPI backend...
    call venv\Scripts\activate
    uvicorn src.backend_main:app --reload --host 0.0.0.0 --port 8000
    goto :EOF
)

if "%1"=="frontend" (
    echo 💻 Starting Streamlit UI...
    call venv\Scripts\activate
    set API_BASE_URL=http://localhost:8000
    streamlit run ui/streamlit_app.py
    goto :EOF
)

if "%1"=="full" (
    echo 🚀 Starting full application...
    start "Backend" cmd /k "call launch.bat backend"
    timeout /t 5
    start "Frontend" cmd /k "call launch.bat frontend"
    goto :EOF
)

:: Show help if no or invalid command
echo Health & Wellness Planner Launcher:
echo   launch.bat install    - Install dependencies
echo   launch.bat backend    - Run FastAPI backend only
echo   launch.bat frontend   - Run Streamlit frontend only
echo   launch.bat full       - Run both backend and frontend
echo   launch.bat help       - Show this help

ENDLOCAL