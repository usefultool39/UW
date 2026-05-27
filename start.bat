@echo off
setlocal EnableExtensions EnableDelayedExpansion

chcp 65001 >nul
title Border Echo - start full project

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "SCRIPTS_DIR=%ROOT%scripts"
set "VENV_DIR=%ROOT%.venv"
set "CONDA_ENV_DIR=%ROOT%.conda\uw-runtime"
set "TOOLS_DIR=%ROOT%.tools"
set "MINIFORGE_DIR=%TOOLS_DIR%\miniforge"
set "MINIFORGE_CONDA=%MINIFORGE_DIR%\Scripts\conda.exe"
set "MINIFORGE_INSTALLER=%TOOLS_DIR%\installers\Miniforge3-Windows-x86_64.exe"
set "MINIFORGE_URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe"
set "BACKEND_PORT=8765"
set "FRONTEND_PORT=3000"

echo ========================================
echo   Border Echo full project launcher
echo ========================================
echo.

if not exist "%BACKEND_DIR%\app\main.py" (
    echo [ERROR] Backend entry not found:
    echo         %BACKEND_DIR%\app\main.py
    echo.
    echo Please run this file from the project root.
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo [ERROR] Frontend package.json not found:
    echo         %FRONTEND_DIR%\package.json
    echo.
    echo Please run this file from the project root.
    pause
    exit /b 1
)

set "PYTHON_CMD="

if exist "%VENV_DIR%\Scripts\python.exe" (
    set "PYTHON_CMD=""%VENV_DIR%\Scripts\python.exe"""
    echo [INFO] Using project venv: %VENV_DIR%
)

if not defined PYTHON_CMD if exist "%CONDA_ENV_DIR%\python.exe" (
    set "PYTHON_CMD=""%CONDA_ENV_DIR%\python.exe"""
    echo [INFO] Using project conda env: %CONDA_ENV_DIR%
)

set "CONDA_CMD="
if exist "%MINIFORGE_CONDA%" (
    set "CONDA_CMD=""%MINIFORGE_CONDA%"""
)

if not defined CONDA_CMD (
    where conda >nul 2>&1
    if not errorlevel 1 set "CONDA_CMD=conda"
)

if not defined CONDA_CMD if defined CONDA_EXE (
    if exist "%CONDA_EXE%" set "CONDA_CMD=""%CONDA_EXE%"""
)

if not defined CONDA_CMD if defined CONDA_PREFIX (
    if exist "%CONDA_PREFIX%\Scripts\conda.exe" set "CONDA_CMD=""%CONDA_PREFIX%\Scripts\conda.exe"""
)

if not defined CONDA_CMD (
    for %%C in (
        "%USERPROFILE%\anaconda3\Scripts\conda.exe"
        "%USERPROFILE%\miniconda3\Scripts\conda.exe"
        "%USERPROFILE%\miniforge3\Scripts\conda.exe"
        "%LOCALAPPDATA%\anaconda3\Scripts\conda.exe"
        "%LOCALAPPDATA%\miniconda3\Scripts\conda.exe"
        "%LOCALAPPDATA%\miniforge3\Scripts\conda.exe"
        "%ProgramData%\anaconda3\Scripts\conda.exe"
        "%ProgramData%\miniconda3\Scripts\conda.exe"
        "%ProgramData%\miniforge3\Scripts\conda.exe"
        "%ProgramFiles%\Anaconda3\Scripts\conda.exe"
        "%ProgramFiles%\Miniconda3\Scripts\conda.exe"
        "%ProgramFiles%\Miniforge3\Scripts\conda.exe"
    ) do (
        if not defined CONDA_CMD (
            if exist "%%~C" set "CONDA_CMD=""%%~C"""
        )
    )
)

if not defined CONDA_CMD (
    for %%D in (C D E F) do (
        for /d %%C in (
            "%%D:\Anaconda*"
            "%%D:\Miniconda*"
            "%%D:\Miniforge*"
        ) do (
            if not defined CONDA_CMD (
                if exist "%%~fC\Scripts\conda.exe" set "CONDA_CMD=""%%~fC\Scripts\conda.exe"""
            )
        )
    )
)

if defined CONDA_CMD (
    echo [INFO] Found Conda: %CONDA_CMD%
)

if not defined PYTHON_CMD if defined CONDA_CMD (
        echo [INFO] No local Python env found. Creating project conda env...
        %CONDA_CMD% create -y -p "%CONDA_ENV_DIR%" python=3.11 pip
        if errorlevel 1 (
            echo [WARN] Conda environment creation failed. Trying regular Python venv next...
        ) else (
            set "PYTHON_CMD=""%CONDA_ENV_DIR%\python.exe"""
            echo [INFO] Created project conda env: %CONDA_ENV_DIR%
        )
)

if not defined PYTHON_CMD (
    python -c "import sys" >nul 2>&1
    if not errorlevel 1 set "BOOTSTRAP_PYTHON=python"
)

if not defined PYTHON_CMD if not defined BOOTSTRAP_PYTHON (
    py -3 -c "import sys" >nul 2>&1
    if not errorlevel 1 set "BOOTSTRAP_PYTHON=py -3"
)

if not defined PYTHON_CMD if defined BOOTSTRAP_PYTHON (
    echo [INFO] No local Python env found. Creating project venv...
    %BOOTSTRAP_PYTHON% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Python venv creation failed.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=""%VENV_DIR%\Scripts\python.exe"""
    echo [INFO] Created project venv: %VENV_DIR%
)

if not defined PYTHON_CMD (
    echo [INFO] No usable Python or Conda found. Installing project-local Miniforge...
    echo [INFO] Downloading: %MINIFORGE_URL%
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; New-Item -ItemType Directory -Force '%TOOLS_DIR%\installers' | Out-Null; Invoke-WebRequest -Uri '%MINIFORGE_URL%' -OutFile '%MINIFORGE_INSTALLER%'"
    if errorlevel 1 (
        echo [ERROR] Miniforge download failed. Check your network, then run this file again.
        pause
        exit /b 1
    )

    echo [INFO] Installing Miniforge into project folder...
    start /wait "" "%MINIFORGE_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=%MINIFORGE_DIR%
    if errorlevel 1 (
        echo [ERROR] Miniforge install failed.
        pause
        exit /b 1
    )

    if not exist "%MINIFORGE_CONDA%" (
        echo [ERROR] Miniforge installed, but conda.exe was not found:
        echo         %MINIFORGE_CONDA%
        pause
        exit /b 1
    )

    echo [INFO] Creating project conda env...
    "%MINIFORGE_CONDA%" create -y -p "%CONDA_ENV_DIR%" python=3.11 pip
    if errorlevel 1 (
        echo [ERROR] Project conda env creation failed.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=""%CONDA_ENV_DIR%\python.exe"""
    echo [INFO] Created project conda env: %CONDA_ENV_DIR%
)

if not defined PYTHON_CMD (
    echo [ERROR] A usable Python runtime was not found.
    echo.
    echo The automatic runtime bootstrap did not finish.
    echo Install Miniconda/Anaconda or Python 3.11+, then run this file again.
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Backend dependencies are missing. Running pip install...
    pushd "%BACKEND_DIR%"
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        popd
        echo [ERROR] Backend dependency install failed.
        pause
        exit /b 1
    )
    popd
)

where npm.cmd >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm.cmd was not found. Install Node.js, then run this file again.
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [INFO] Frontend dependencies are missing. Running npm install...
    pushd "%FRONTEND_DIR%"
    call npm.cmd install
    if errorlevel 1 (
        popd
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
    popd
)

set "FRONTEND_CMD=npm.cmd run dev -- --host 127.0.0.1 --port %FRONTEND_PORT%"

netstat -ano | findstr /R /C:":%BACKEND_PORT% .*LISTENING" >nul
if errorlevel 1 (
    echo [1/2] Starting backend: http://127.0.0.1:%BACKEND_PORT%
    set "UW_PYTHON=%PYTHON_CMD%"
    set "UW_BACKEND_DIR=%BACKEND_DIR%"
    set "UW_BACKEND_PORT=%BACKEND_PORT%"
    start "Border Echo backend" "%SCRIPTS_DIR%\run-backend.bat"
) else (
    echo [1/2] Backend port %BACKEND_PORT% is already in use. Reusing the running service.
)

timeout /t 2 /nobreak >nul

netstat -ano | findstr /R /C:":%FRONTEND_PORT% .*LISTENING" >nul
if errorlevel 1 (
    echo [2/2] Starting frontend: http://127.0.0.1:%FRONTEND_PORT%
    set "UW_FRONTEND_DIR=%FRONTEND_DIR%"
    set "UW_FRONTEND_PORT=%FRONTEND_PORT%"
    start "Border Echo frontend" "%SCRIPTS_DIR%\run-frontend.bat"
) else (
    echo [2/2] Frontend port %FRONTEND_PORT% is already in use. Reusing the running service.
)

echo.
echo ========================================
echo   Border Echo is starting
echo   Frontend: http://127.0.0.1:%FRONTEND_PORT%
echo   Backend:  http://127.0.0.1:%BACKEND_PORT%/api/health
echo ========================================
echo.
echo Press any key to open the browser.
pause >nul
start "" "http://127.0.0.1:%FRONTEND_PORT%"
