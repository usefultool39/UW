@echo off
setlocal EnableExtensions

if not defined UW_FRONTEND_DIR (
    echo [ERROR] UW_FRONTEND_DIR is not set.
    pause
    exit /b 1
)

if not defined UW_FRONTEND_PORT set "UW_FRONTEND_PORT=3000"

cd /d "%UW_FRONTEND_DIR%"
npm.cmd run dev -- --host 127.0.0.1 --port %UW_FRONTEND_PORT%

echo.
echo [ERROR] Frontend process exited.
pause
