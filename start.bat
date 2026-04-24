@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title 30小镇 - Vue 试玩 + FastAPI

echo ========================================
echo   30小镇 · 后端框架 + Vue 试玩页
echo ========================================
echo.

set "BACKEND_CMD=python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765"

:: 优先使用 conda 环境
where conda >nul 2>&1
if not errorlevel 1 (
    conda run -n xiaozhen-mvp python --version >nul 2>&1
    if not errorlevel 1 (
        set "BACKEND_CMD=conda run -n xiaozhen-mvp python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765"
        echo [信息] 使用 conda 环境: xiaozhen-mvp
    ) else (
        echo [警告] 未找到 conda 环境 xiaozhen-mvp，回退使用系统 Python。
    )
)

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    where conda >nul 2>&1
    if errorlevel 1 (
        echo [错误] 未找到 Python/Conda，请先安装 Python 或 Anaconda。
        pause
        exit /b 1
    )
)

:: 启动后端
echo [1/2] 启动后端服务 (端口 8765)...
start "30小镇-后端" cmd /k "cd /d %~dp0backend && !BACKEND_CMD!"

timeout /t 2 /nobreak >nul

:: 启动前端
echo [2/2] 启动前端服务 (端口 3000)...
start "30小镇-前端" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   服务已启动！
echo   前端: http://127.0.0.1:3000
echo   后端: http://127.0.0.1:8765
echo ========================================
echo.
echo 按任意键打开浏览器...
pause >nul
start http://127.0.0.1:3000
