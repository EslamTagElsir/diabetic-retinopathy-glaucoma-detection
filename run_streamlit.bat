@echo off
echo =========================================================
echo  Starting Diabetic Retinopathy Detection (Streamlit)
echo =========================================================

REM Check if virtual environment exists, if so activate it
if exist venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo [INFO] Installing requirements...
pip install -r requirements.txt

echo [INFO] Launching Streamlit Server...
python -m streamlit run app_streamlit.py --server.port 8507

pause
