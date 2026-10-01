@echo off
title MCServerManager
echo ========================================
echo    MCServerManager - Servidor Minecraft
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH.
    echo Descárgalo desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Instalar dependencias si es necesario
if not exist ".venv" (
    echo [INFO] Creando entorno virtual...
    python -m venv .venv
    echo [INFO] Instalando dependencias...
    call .venv\Scripts\activate.bat
    python -m pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo [INFO] Iniciando MCServerManager...
echo.
python app.py

pause
