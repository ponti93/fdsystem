#!/usr/bin/env python3
"""
Fraud Detection System Setup Script
Comprehensive setup for the advanced fraud detection system
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_requirements():
    """Check if required software is installed"""
    logger.info("Checking system requirements...")
    
    requirements = {
        'python': 'python --version',
        'pip': 'pip --version',
        'node': 'node --version',
        'npm': 'npm --version',
        'psql': 'psql --version'
    }
    
    missing = []
    for req, cmd in requirements.items():
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                logger.info(f"✓ {req}: {version}")
            else:
                missing.append(req)
        except FileNotFoundError:
            missing.append(req)
    
    if missing:
        logger.error(f"Missing requirements: {', '.join(missing)}")
        logger.error("Please install the missing software and try again.")
        return False
    
    return True

def setup_backend():
    """Set up the backend environment"""
    logger.info("Setting up backend environment...")
    
    backend_dir = Path("backend")
    
    # Create virtual environment if it doesn't exist
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        logger.info("Creating Python virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = venv_dir / "Scripts" / "pip.exe"
        python_path = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        pip_path = venv_dir / "bin" / "pip"
        python_path = venv_dir / "bin" / "python"
    
    # Install requirements
    logger.info("Installing Python dependencies...")
    requirements_file = backend_dir / "requirements.txt"
    subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
    
    # Create .env file from example if it doesn't exist
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        logger.info("Creating .env file from example...")
        shutil.copy(env_example, env_file)
        logger.warning("Please edit backend/.env with your actual database and API credentials!")
    
    # Create necessary directories
    dirs_to_create = [
        backend_dir / "models",
        backend_dir / "data",
        backend_dir / "logs"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(exist_ok=True)
        logger.info(f"Created directory: {dir_path}")
    
    return python_path

def setup_frontend():
    """Set up the frontend environment"""
    logger.info("Setting up frontend environment...")
    
    frontend_dir = Path("frontend")
    
    # Install npm dependencies
    logger.info("Installing Node.js dependencies...")
    subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    return True

def setup_database(python_path):
    """Set up the database"""
    logger.info("Setting up database...")
    
    backend_dir = Path("backend")
    setup_script = backend_dir / "setup_database.py"
    
    if setup_script.exists():
        logger.info("Running database setup script...")
        try:
            subprocess.run([str(python_path), str(setup_script)], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Database setup failed: {e}")
            logger.error("Please ensure PostgreSQL is running and your .env file is configured correctly.")
            return False
    else:
        logger.warning("Database setup script not found. You may need to set up the database manually.")
        return False

def create_startup_scripts():
    """Create convenient startup scripts"""
    logger.info("Creating startup scripts...")
    
    # Windows batch file
    batch_content = """@echo off
echo Starting Advanced Fraud Detection System...
echo.

REM Start backend
echo Starting backend...
cd backend
call venv\\Scripts\\activate.bat
start "Backend" cmd /k "python main.py"
cd ..

REM Wait a moment for backend to start
timeout /t 5 /nobreak

REM Start frontend  
echo Starting frontend...
cd frontend
start "Frontend" cmd /k "npm start"
cd ..

echo.
echo System is starting up...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause
"""
    
    with open("start_system.bat", "w") as f:
        f.write(batch_content)
    
    # Unix shell script
    shell_content = """#!/bin/bash
echo "Starting Advanced Fraud Detection System..."
echo

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo
echo "System is starting up..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000" 
echo "API Docs: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
"""
    
    with open("start_system.sh", "w") as f:
        f.write(shell_content)
    
    # Make shell script executable on Unix systems
    if os.name != 'nt':
        os.chmod("start_system.sh", 0o755)
    
    logger.info("Created startup scripts: start_system.bat and start_system.sh")

def main():
    """Main setup function"""
    logger.info("=== Advanced Fraud Detection System Setup ===")
    logger.info("This script will set up the complete fraud detection system.")
    logger.info("")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    try:
        # Setup backend
        python_path = setup_backend()
        logger.info("✓ Backend setup completed")
        
        # Setup frontend
        setup_frontend()
        logger.info("✓ Frontend setup completed")
        
        # Setup database
        db_success = setup_database(python_path)
        if db_success:
            logger.info("✓ Database setup completed")
        else:
            logger.warning("⚠ Database setup had issues - you may need to configure it manually")
        
        # Create startup scripts
        create_startup_scripts()
        logger.info("✓ Startup scripts created")
        
        logger.info("")
        logger.info("=== Setup Complete! ===")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Configure your database settings in backend/.env")
        logger.info("2. Add your Paystack and Flutterwave API keys to backend/.env")
        logger.info("3. Start the system using:")
        logger.info("   - Windows: start_system.bat")
        logger.info("   - Unix/Linux/macOS: ./start_system.sh")
        logger.info("")
        logger.info("System URLs:")
        logger.info("- Frontend: http://localhost:3000")
        logger.info("- Backend API: http://localhost:8000")
        logger.info("- API Documentation: http://localhost:8000/docs")
        logger.info("")
        logger.info("Authentication tokens for testing:")
        logger.info("- Admin access: admin_token123")
        logger.info("- Analyst access: analyst_token123")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
