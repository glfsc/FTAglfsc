@echo off
chcp 65001 >nul
echo ========================================
echo    前端界面风格测试 - 启动程序
echo ========================================
echo.
echo 正在启动测试服务器...
echo 端口：3001
echo 测试页面：http://localhost:3001/test-theme
echo.
echo 提示：
echo - 按 Ctrl+C 可停止服务器
echo - 主应用运行在端口 3000，不受影响
echo ========================================
echo.

cd /d "%~dp0"
npm run test:theme

pause
