@echo off
REM Roda o Sinapesc em modo desenvolvimento (precisa Python instalado)
cd /d "%~dp0"
python -m pip install -r requirements.txt
python main.py
pause
