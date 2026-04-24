#!/bin/bash
# 项目 · 前后端分离启动脚本 (Linux/Mac)

echo "╔════════════════════════════════════════════════════════╗"
echo "║   项目 · 前后端分离启动工具                        ║"
echo "║                                                        ║"
echo "║   🔧 启动步骤：                                       ║"
echo "║   1. 启动后端 API 服务 (8000)                        ║"
echo "║   2. 启动前端 Web 服务 (3000)                        ║"
echo "║                                                        ║"
echo "║   💡 提示：按 Ctrl+C 停止服务                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 启动后端 API
echo "[后端] 启动 FastAPI 服务器..."
cd /path/to/integrity/30小镇/backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

# 启动前端 Web
echo "[前端] 启动 Express 服务器..."
cd /path/to/integrity/30小镇/frontend
npm install >/dev/null 2>&1
npm start &
FRONTEND_PID=$!

sleep 2

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   ✅ 所有服务已启动！                                ║"
echo "║                                                        ║"
echo "║   🌐 前端: http://127.0.0.1:3000                     ║"
echo "║   🔌 API:  http://127.0.0.1:8000/api/health          ║"
echo "║                                                        ║"
echo "║   打开浏览器访问应用                                ║"
echo "║   按 Ctrl+C 停止所有服务                           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 等待中断
wait $BACKEND_PID $FRONTEND_PID
