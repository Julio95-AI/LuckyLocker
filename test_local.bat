@echo off
echo ========================================
echo 启动 LuckyLocker 测试服务器
echo ========================================
echo.

REM 激活conda环境
call conda activate study

REM 启动Flask应用
cd backend
python app.py

pause
