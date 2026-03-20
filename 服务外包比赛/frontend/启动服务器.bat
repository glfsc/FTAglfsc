@echo off
chcp 65001 >nul
echo ========================================
echo 启动前端开发服务器
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 jspdf 损坏的 .map 文件...
if exist "node_modules\jspdf\dist\*.map" (
    echo 发现损坏的文件，正在删除...
    del /q node_modules\jspdf\dist\*.map
    echo ✓ 已删除损坏的 .map 文件
) else (
    echo ✓ 未发现损坏的 .map 文件
)

echo.
echo [2/3] 检查依赖安装...
if not exist "node_modules" (
    echo 未安装依赖，正在安装...
    call npm install
    if errorlevel 1 (
        echo ✗ 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo ✓ 依赖已安装
)

echo.
echo [3/3] 启动开发服务器...
echo.
echo ========================================
echo 服务器将在 http://localhost:3000 启动
echo 按 Ctrl+C 可停止服务器
echo ========================================
echo.

call npm run dev
