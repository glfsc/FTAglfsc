@echo off
echo ========================================
echo 故障树智能生成系统 - 快速启动
echo ========================================

echo.
echo 正在启动后端服务（conda环境：fsy）...
start cmd /k "cd /d %~dp0 & call conda activate fsy & cd backend & python main.py"

timeout /t 3 /nobreak >nul

echo.
echo 正在启动前端服务...
start cmd /k "cd /d %~dp0frontend & npm run dev"

echo.
echo ========================================
echo 服务启动完成！
echo 前端地址：http://localhost:3000
echo 后端API：http://localhost:8000
echo API文档：http://localhost:8000/docs
echo ========================================
echo.
echo 按任意键关闭此窗口...
pause >nul
