@echo off
echo 🚀 Starting Simple Fraud Detection System
echo ==========================================

echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install backend dependencies
    pause
    exit /b 1
)

echo Starting backend server...
start "Backend" cmd /k "python main.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Installing frontend dependencies...
cd ..\frontend
npm install
if %errorlevel% neq 0 (
    echo Failed to install frontend dependencies
    pause
    exit /b 1
)

echo Starting frontend server...
start "Frontend" cmd /k "npm start"

echo.
echo ==========================================
echo 🎉 System is starting up!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ==========================================
echo.
echo Press any key to stop all services...
pause >nul

echo Stopping services...
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1

echo All services stopped.
pause
