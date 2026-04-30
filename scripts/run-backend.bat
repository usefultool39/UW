@echo off
setlocal EnableExtensions

if not defined UW_PYTHON (
    echo [ERROR] UW_PYTHON is not set.
    pause
    exit /b 1
)

if not defined UW_BACKEND_DIR (
    echo [ERROR] UW_BACKEND_DIR is not set.
    pause
    exit /b 1
)

if not defined UW_BACKEND_PORT set "UW_BACKEND_PORT=8765"

cd /d "%UW_BACKEND_DIR%"
%UW_PYTHON% -m uvicorn app.main:app --reload --host 127.0.0.1 --port %UW_BACKEND_PORT%

echo.
echo [ERROR] Backend process exited.
pause
