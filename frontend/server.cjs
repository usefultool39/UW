const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// CORS 配置
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type']
}));

// 静态文件服务 - 在 public 目录
app.use(express.static(path.join(__dirname, 'public')));

// 主页
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// 所有未匹配的路由都返回 index.html（支持 SPA）
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// 启动服务器
app.listen(PORT, () => {
console.log(`
 ╔════════════════════════════════════════════════╗
 ║     边境回声 · 露茵村第一章 - 前端服务       ║
 ║                                                ║
 ║  🌐 前端服务: http://127.0.0.1:${PORT}       ║
 ║  🔌 后端 API: http://127.0.0.1:8765         ║
 ║  📁 静态文件: ./public/                       ║
 ║                                                ║
 ║  按 Ctrl+C 停止服务                           ║
 ╚════════════════════════════════════════════════╝
   `);
});

process.on('SIGINT', () => {
  console.log('\n✋ 服务已停止');
  process.exit(0);
});
