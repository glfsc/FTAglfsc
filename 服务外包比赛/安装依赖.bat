@echo off
echo ========================================
echo 故障树智能生成系统 - 依赖安装
echo ========================================

echo.
echo [1/2] 安装后端依赖（conda 环境：csso）...
call conda activate csso
if errorlevel 1 (
    echo 错误：无法激活 conda 环境 csso
    echo 请先创建环境：conda create -n csso python=3.10
    pause
    exit /b 1
)

cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo 后端依赖安装失败
    pause
    exit /b 1
)

echo.
echo [2/2] 安装前端依赖...
cd ..\frontend
call npm install
if errorlevel 1 (
    echo 前端依赖安装失败，请检查Node.js是否已安装
    pause
    exit /b 1
)

cd ..
echo.
echo ========================================
echo 依赖安装完成！
echo 运行 快速启动.bat 启动系统
echo ========================================
pause
