@echo off
chcp 65001 >nul
title 30小镇 · 前后端启动

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   30小镇 · 前后端分离启动工具                        ║
echo ║                                                        ║
echo ║   启动步骤：                                           ║
echo ║   1. 启动后端 API 服务 (8765)                         ║
echo ║   2. 启动前端 Web 服务 (3000)                         ║
echo ║   3. 自动打开浏览器访问                                ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM 启动前检查后端端口是否可用
netstat -ano | findstr /R /C:":8765 .*LISTENING" >nul
if not errorlevel 1 (
	echo [错误] 端口 8765 已被占用，后端无法启动。
	echo [提示] 请先关闭占用进程，或改用其他端口（例如 8766）。
	echo [参考] 可执行: netstat -ano ^| findstr :8765
	echo.
	pause
	exit /b 1
)

REM 启动后端 API
echo [后端] 启动 FastAPI 服务器 (8765)...
start "30小镇-后端" cmd /k "cd /d %~dp0 && python -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --reload"

REM 等待后端启动
timeout /t 2 /nobreak >nul

REM 启动前端 Web
echo [前端] 启动 Vite 开发服务器 (3000)...
start "30小镇-前端" cmd /k "cd /d %~dp0..\frontend && npm run dev"

REM 等待前端启动
timeout /t 2 /nobreak >nul

REM 打开浏览器
echo [浏览器] 正在打开应用...
start http://127.0.0.1:3000

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   所有服务已启动！                                     ║
echo ║   前端: http://127.0.0.1:3000                         ║
echo ║   API:  http://127.0.0.1:8765                         ║
echo ╚════════════════════════════════════════════════════════╝
echo.
pause
