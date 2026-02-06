@echo off
echo ==========================================
echo 🎬 Setting up AI Movie Night Planner...
echo ==========================================

:: 1. Install dependencies (only if needed)
echo 📦 Checking dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies. Please check your internet connection.
    pause
    exit /b
)
echo ✅ Dependencies are ready.

:: 2. Run the App
echo ==========================================
echo 🚀 Launching the UI...
echo ==========================================
streamlit run app.py