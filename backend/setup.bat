@echo off
echo 🚀 Setting up Legal Case Analyzer Backend...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found in PATH. Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo.
    echo ⚠️  Please edit .env file and add your OpenAI API key!
    echo.
) else (
    echo ✅ .env file already exists
)

REM Install requirements
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit .env file and add your OpenAI API key
echo 2. Run: python run_dev.py
echo.
pause
