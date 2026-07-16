@echo off
REM Quick test runner for Windows

echo ========================================
echo AI SRE Stack - Quick Tests
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file with ANTHROPIC_API_KEY
    echo.
    pause
)

REM Run quick tests
echo Running quick tests...
echo.
cd tests
python run_quick_tests.py

echo.
echo ========================================
echo Tests complete!
echo ========================================
pause
