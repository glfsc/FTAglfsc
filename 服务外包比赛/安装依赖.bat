@echo off
echo ========================================
echo 故障树智能生成系统 - 依赖安装
echo ========================================

echo.
echo [1/2] 安装后端依赖（conda环境：fsy）...
call conda activate fsy
if errorlevel 1 (
    echo 错误：无法激活conda环境fsy
    echo 请先创建环境：conda create -n fsy python=3.9
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
