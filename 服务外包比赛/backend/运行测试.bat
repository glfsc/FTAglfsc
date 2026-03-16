@echo off
chcp 65001 >nul
REM ========================================
REM  后端测试运行脚本
REM  用于快速运行各类测试
REM ========================================

echo.
echo ======================================
echo   后端测试运行工具
echo ======================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python
    pause
    exit /b 1
)

echo [信息] 当前 Python 版本:
python --version
echo.

REM 切换到 backend 目录
cd /d "%~dp0"

REM 显示菜单
:menu
echo 请选择要运行的测试类型:
echo.
echo 1. 运行所有测试
echo 2. API接口测试
echo 3. 服务层测试
echo 4. 数据模型测试
echo 5. 集成测试
echo 6. AI 聊天测试
echo 7. 故障树 API 测试
echo 8. 知识抽取测试
echo 9. 带覆盖率报告的测试
echo 10. 清理测试缓存
echo 0. 退出
echo.

set /p choice=请输入选项 (0-10): 

if "%choice%"=="1" goto run_all
if "%choice%"=="2" goto run_api
if "%choice%"=="3" goto run_service
if "%choice%"=="4" goto run_model
if "%choice%"=="5" goto run_integration
if "%choice%"=="6" goto run_ai_chat
if "%choice%"=="7" goto run_fault_tree
if "%choice%"=="8" goto run_knowledge
if "%choice%"=="9" goto run_coverage
if "%choice%"=="10" goto clean_cache
if "%choice%"=="0" goto end

echo [错误] 无效的选项！
echo.
goto menu

:run_all
echo.
echo ======================================
echo   运行所有测试
echo ======================================
echo.
pytest test/ -v --tb=short
goto menu

:run_api
echo.
echo ======================================
echo   运行 API接口测试
echo ======================================
echo.
pytest test/api_tests/ -v --tb=short
goto menu

:run_service
echo.
echo ======================================
echo   运行服务层测试
echo ======================================
echo.
pytest test/service_tests/ -v --tb=short
goto menu

:run_model
echo.
echo ======================================
echo   运行数据模型测试
echo ======================================
echo.
pytest test/model_tests/ -v --tb=short
goto menu

:run_integration
echo.
echo ======================================
echo   运行集成测试
echo ======================================
echo.
pytest test/integration_tests/ -v --tb=short
goto menu

:run_ai_chat
echo.
echo ======================================
echo   运行 AI 聊天测试
echo ======================================
echo.
pytest test/api_tests/test_ai_chat.py -v -s --tb=short
goto menu

:run_fault_tree
echo.
echo ======================================
echo   运行故障树 API 测试
echo ======================================
echo.
pytest test/api_tests/test_fault_tree.py -v -s --tb=short
goto menu

:run_knowledge
echo.
echo ======================================
echo   运行知识抽取测试
echo ======================================
echo.
pytest test/service_tests/test_knowledge_extraction.py -v -s --tb=short
goto menu

:run_coverage
echo.
echo ======================================
echo   运行测试并生成覆盖率报告
echo ======================================
echo.
pytest --cov=app --cov-report=html --cov-report=term-missing
echo.
echo [提示] HTML 报告已生成在 htmlcov/ 目录
echo [提示] 使用以下命令查看:
echo        start htmlcov\index.html
echo.
goto menu

:clean_cache
echo.
echo ======================================
echo   清理测试缓存
echo ======================================
echo.
echo [信息] 正在清理 __pycache__ 目录...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo [信息] 正在清理 .pytest_cache 目录...
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"
echo [信息] 正在清理 htmlcov 目录...
if exist "htmlcov" rd /s /q "htmlcov"
echo [完成] 清理完成!
echo.
goto menu

:end
echo.
echo 感谢使用，再见！
echo.
exit /b 0
