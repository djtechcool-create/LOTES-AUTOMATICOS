@echo off
title LOTES AUTOMATICOS - KrezcoCargo
echo ========================================
echo   LOTES AUTOMATICOS - KrezcoCargo
echo   Iniciando servidor...
echo ========================================
echo.

pip install -r requirements.txt --quiet 2>nul

echo Iniciando en http://localhost:5000
echo Presiona Ctrl+C para detener
echo.
python app.py
pause
