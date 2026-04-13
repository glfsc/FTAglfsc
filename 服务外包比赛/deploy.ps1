<#
.SYNOPSIS
故障树智能生成系统 - 一键环境配置与容器部署脚本

.DESCRIPTION
此脚本将自动检测并安装 WSL、Docker Desktop，并启动项目相关的所有容器。
请务必以【管理员身份】运行此脚本。
#>

# ==========================================
# 1. 权限检测 (必须以管理员身份运行)
# ==========================================
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "=======================================================" -ForegroundColor Red
    Write-Host "[错误] 权限不足！部署环境需要管理员权限。" -ForegroundColor Red
    Write-Host "请右键点击此脚本，选择【使用 PowerShell 运行】(可能需要先打开管理员终端)。" -ForegroundColor Red
    Write-Host "=======================================================" -ForegroundColor Red
    Read-Host "按回车键退出..."
    exit
}

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "    欢迎使用 故障树智能生成系统 一键部署向导" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "正在执行环境体检..."

# ==========================================
# 2. 检测并安装 WSL
# ==========================================
$wslInstalled = Get-Command wsl -ErrorAction SilentlyContinue
if ($wslInstalled) {
    Write-Host "[OK] WSL 已安装。" -ForegroundColor Green
} else {
    Write-Host "[!] 未检测到 WSL，正在自动安装底层 Linux 子系统..." -ForegroundColor Yellow
    wsl --install --no-distribution
    Write-Host "=======================================================" -ForegroundColor Magenta
    Write-Host "WSL 核心组件安装完成！" -ForegroundColor Magenta
    Write-Host "【重要提示】：Windows 需要重启才能使虚拟化生效。" -ForegroundColor Magenta
    Write-Host "请重启电脑后，再次运行此 deploy.ps1 脚本以继续安装 Docker。" -ForegroundColor Magenta
    Write-Host "=======================================================" -ForegroundColor Magenta
    Read-Host "按回车键退出并请手动重启电脑..."
    exit
}

# ==========================================
# 3. 检测并安装 Docker Desktop (使用 Winget)
# ==========================================
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerInstalled) {
    Write-Host "[OK] Docker 已安装。" -ForegroundColor Green
} else {
    Write-Host "[!] 未检测到 Docker，正在通过 Winget 官方源下载并安装 Docker Desktop..." -ForegroundColor Yellow
    Write-Host "这可能需要几分钟时间，具体取决于您的网络速度，请耐心等待..."
    winget install Docker.DockerDesktop -e --accept-package-agreements --accept-source-agreements
    
    Write-Host "=======================================================" -ForegroundColor Magenta
    Write-Host "Docker Desktop 安装已触发！" -ForegroundColor Magenta
    Write-Host "【重要提示】：安装完成后，您可能需要注销或重启电脑。" -ForegroundColor Magenta
    Write-Host "请在重启并确保桌面右下角出现 Docker 小鲸鱼图标后，再次运行此脚本。" -ForegroundColor Magenta
    Write-Host "=======================================================" -ForegroundColor Magenta
    Read-Host "按回车键退出..."
    exit
}

# ==========================================
# 4. 等待 Docker 引擎启动
# ==========================================
Write-Host "正在检查 Docker 引擎运行状态..." -ForegroundColor Yellow
$dockerReady = $false
$retryCount = 0

while (-not $dockerReady -and $retryCount -lt 12) { # 等待大约 1 分钟
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerReady = $true
        Write-Host "[OK] Docker 引擎已启动并连接成功！" -ForegroundColor Green
    } else {
        Write-Host "等待 Docker 引擎启动... (请确保已打开 Docker Desktop 软件) [$($retryCount)/12]"
        Start-Sleep -Seconds 5
        $retryCount++
    }
}

if (-not $dockerReady) {
    Write-Host "=======================================================" -ForegroundColor Red
    Write-Host "[错误] Docker 引擎未响应！" -ForegroundColor Red
    Write-Host "请手动从开始菜单打开 'Docker Desktop'，等待其启动变为绿灯后，再重新运行此脚本。" -ForegroundColor Red
    Write-Host "=======================================================" -ForegroundColor Red
    Read-Host "按回车键退出..."
    exit
}

# ==========================================
# 5. 部署并启动项目容器
# ==========================================
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "环境检查完毕，正在拉取镜像并构建故障树系统容器..." -ForegroundColor Cyan
Write-Host "首次构建可能需要较长时间，请耐心等待。" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# 强行拉取并后台构建运行
docker-compose up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host "部署成功！所有服务已在后台运行。" -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host "您现在可以通过浏览器访问以下地址进行体验："
    Write-Host " - 系统前端：http://localhost"
    Write-Host " - 知识图谱 (Neo4j)：http://localhost:7474"
    Write-Host " - 后端 API 文档：http://localhost:8000/docs"
    Write-Host "=======================================================" -ForegroundColor Green
} else {
    Write-Host "=======================================================" -ForegroundColor Red
    Write-Host "[警告] 容器启动时遇到问题。请往上翻阅红色报错日志进行排查。" -ForegroundColor Red
    Write-Host "常见问题：端口被占用，或磁盘空间不足。" -ForegroundColor Red
    Write-Host "=======================================================" -ForegroundColor Red
}

Read-Host "部署流程结束，按回车键退出..."