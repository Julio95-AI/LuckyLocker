@echo off
chcp 65001 >nul
echo ========================================
echo   LuckyLocker 幸运格子柜抽奖系统
echo ========================================
echo.
echo 正在启动服务...
echo.

cd backend
python app.py

pause
