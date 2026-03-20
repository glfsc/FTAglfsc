@echo off
echo ========================================
echo 故障树智能生成系统 - 本地部署脚本
echo ========================================

echo.
echo [1/4] 激活conda环境 csso(经过更改）...
call conda activate csso
if errorlevel 1 (
    echo 错误：无法激活 conda 环境 csso，请确认环境已创建
    pause
    exit /b 1
)

echo.
echo [2/4] 安装后端依赖...
cd backend
pip install -r requirements.txt

echo.
echo [3/4] 配置环境变量...
if not exist .env (
    copy .env.example .env
    echo 已创建.env配置文件，如需修改数据库配置请编辑 backend\.env
)

echo.
echo [4/4] 启动后端服务...
echo 后端服务将在 http://localhost:8000 启动
echo API文档地址：http://localhost:8000/docs
python main.py

pause
