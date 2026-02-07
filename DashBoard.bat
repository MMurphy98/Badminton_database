@echo off
cd /d "%~dp0"
echo "Starting Badminton Dashboard..."
streamlit run badminton_app.py
pause