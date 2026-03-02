@echo off
echo ========================================
echo 故障树智能生成系统 - 前端部署脚本
echo ========================================

echo.
echo [1/3] 检查Node.js环境...
node --version
if errorlevel 1 (
    echo 错误：未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo.
echo [2/3] 安装前端依赖...
cd frontend
call npm install

echo.
echo [3/3] 启动前端开发服务器...
echo 前端服务将在 http://localhost:3000 启动
call npm run dev

pause
