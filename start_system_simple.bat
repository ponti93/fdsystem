@echo off
echo ========================================
echo  Advanced Fraud Detection System
echo ========================================
echo.
echo Starting system with your configuration:
echo - Database: new_fdsystem_db (PostgreSQL)
echo - Flutterwave API: Configured
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
echo.

REM Start backend
echo [1/2] Starting backend server...
cd backend
start "Backend - Fraud Detection API" cmd /k "python main_simple.py"
cd ..

REM Wait for backend to initialize
echo Waiting for backend to start...
timeout /t 8 /nobreak > nul

REM Start frontend
echo [2/2] Starting frontend dashboard...
cd frontend
start "Frontend - Admin Dashboard" cmd /k "npm start"
cd ..

echo.
echo ========================================
echo  System Started Successfully!
echo ========================================
echo.
echo Access your fraud detection system:
echo - Frontend Dashboard: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo.
echo Authentication:
echo - Admin Token: admin_token123
echo - Analyst Token: analyst_token123
echo.
echo Flutterwave Integration:
echo - Public Key: FLWPUBK_TEST-b6356446868a345e87f49853ca840527-X
echo - Secret Key: FLWSECK_TEST-29709f78d8dcc264a86c250cd0836bd8-X
echo - Encryption Key: FLWSECK_TEST39addd482452
echo.
echo Press any key to exit this window...
pause > nul
