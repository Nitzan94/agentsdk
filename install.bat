@echo off
REM ABOUTME: Installation script for Windows
REM ABOUTME: Sets up virtual environment and dependencies

echo [INFO] Personal Assistant Agent - Setup
echo ======================================

REM Check Python
python --version
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.8+ first.
    exit /b 1
)

REM Create virtual environment
echo [INFO] Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [INFO] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Run tests
echo [INFO] Running setup tests...
python test_setup.py

if errorlevel 1 (
    echo [ERROR] Installation failed. Check errors above.
    exit /b 1
)

echo.
echo [OK] Installation complete!
echo.
echo Next steps:
echo 1. Set your API key: set ANTHROPIC_API_KEY=your_key_here
echo 2. Activate venv: venv\Scripts\activate.bat
echo 3. Run assistant: python main.py
echo 4. See USAGE.md for detailed guide
