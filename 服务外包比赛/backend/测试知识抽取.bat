@echo off
chcp 65001 >nul
echo ================================================
echo Knowledge Extraction Module - Quick Test
echo ================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 已安装
echo.

REM 检查 .env 文件是否存在
if not exist ".env" (
    echo Note: Make sure .env file is configured with:
    echo   - DASHSCOPE_API_KEY
    echo   - NEO4J_URI
    echo   - NEO4J_USER
    echo   - NEO4J_PASSWORD
    echo.
) else (
    echo ✅ .env file found
)

echo.
echo ================================================
echo Step 1: Create necessary directories
echo ================================================
if not exist "uploads" mkdir uploads
if not exist "data\output" mkdir data\output
if not exist "exports" mkdir exports
echo ✅ Directories created
echo.

echo ================================================
echo Step 2: Run test script
echo ================================================
echo.
python test_knowledge_extraction.py

echo.
echo ================================================
echo Step 3: Check generated files
echo ================================================
echo.
if exist "data\output" (
    echo Generated triplet files:
    dir /b data\output\*_triplets.json 2>nul || echo No files generated yet
)

echo.
echo ================================================
echo Test Complete!
echo ================================================
echo.
echo Next steps:
echo   1. Start backend: python main.py
echo   2. Start frontend: cd ..\frontend ^&^& npm run dev
echo   3. Visit http://localhost:5173
echo   4. Or test API with Postman/Curl
echo.
echo API Endpoints:
echo   POST /api/v1/fault-tree/upload      - Upload file
echo   POST /api/v1/fault-tree/extract     - Extract knowledge
echo   GET  /api/v1/fault-tree/generate_tree?top_event=xxx - Generate tree
echo.

pause
