@echo off
:: 1. 环境编码适配 (防止中文乱码)
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 2. 路径锁定 (确保在任何位置双击都能找对文件夹)
cd /d "%~dp0"

:: --- 配置区 ---
set APP_NAME=177 重炮手竞技座舱
set BACKUP_DIR=backups
set KEEP_DAYS=7
set PORT=8501
:: --------------

echo ==========================================
echo    %APP_NAME% - 系统启动中
echo ==========================================

:: 3. 自动化数据备份逻辑
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

:: 生成兼容的时间戳 (YYYYMMDD_HHMMSS)
set t=%time: =0%
set DAILY_TAG=%date:~0,4%%date:~5,2%%date:~8,2%

echo [1/3] 🛡️ 检查每日备份状态...

:: 检查今天是否已经备份过了
if exist "%BACKUP_DIR%\sessions_daily_%DAILY_TAG%.csv" (
    echo [提示] 今日数据已备份，跳过重复操作。
) else (
    echo [备份] 正在创建今日快照...
    if exist sessions_cleaned.csv copy sessions_cleaned.csv "%BACKUP_DIR%\sessions_daily_%DAILY_TAG%.csv" >nul
    if exist equipment_cleaned.csv copy equipment_cleaned.csv "%BACKUP_DIR%\equipment_daily_%DAILY_TAG%.csv" >nul
    echo [完成] 已建立今日备份: %DAILY_TAG%
)

:: 4. 自动清理过期备份
echo [2/3] 🧹 正在清理 %KEEP_DAYS% 天前的旧数据...
forfiles /p "%BACKUP_DIR%" /m *.csv /d -%KEEP_DAYS% /c "cmd /c del /f @path" 2>nul

:: 5. 启动座舱并强制弹出浏览器
echo [3/3] 🚀 正在唤醒座舱界面...
echo.
echo 系统地址: http://localhost:%PORT%
echo ------------------------------------------

:: 双重保险：先启动浏览器地址，再开启后台
:: start http://localhost:%PORT%

:: 运行嵌入式 Python 
:: 取消 --server.headless=true 以确保本地运行模式正常
.\python.exe -m streamlit run badminton_app.py ^
    --server.port=%PORT% ^
    --server.headless=false ^
    --browser.gatherUsageStats=false ^
    --client.toolbarMode=minimal

:: 6. 异常状态捕获
if %errorlevel% neq 0 (
    echo.
    echo ❌ [错误] 座舱启动失败！
    echo 常见原因: 
    echo 1. 端口 %PORT% 被占用 (请关闭已打开的黑窗口)
    echo 2. 缺少依赖包 (检查 Lib/site-packages)
    echo.
    pause
)