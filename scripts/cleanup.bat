@echo off
chcp 65001 >nul
echo ========================================
echo  LuckyLocker 项目清理脚本
echo ========================================
echo.
echo 即将删除以下文件和目录：
echo.
echo 临时脚本 (3个):
echo   - backend\fix_database.py
echo   - backend\test_qrcode.py
echo   - quick_test.sh
echo.
echo 临时文档 (6个):
echo   - COMPLETED_v0.1.2.md
echo   - FINAL_FIXES.md
echo   - FIXES_v0.1.2.md
echo   - START_HERE.md
echo   - UPDATE_LOG_v0.1.1.md
echo   - VERIFICATION_CHECKLIST.md
echo.
echo 临时目录 (1个):
echo   - backend\__pycache__\
echo.
echo ========================================
echo.
set /p confirm="确认清理? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo 取消清理。
    pause
    exit /b
)

echo.
echo 开始清理...
echo.

REM 删除临时脚本
if exist backend\fix_database.py (
    del /Q backend\fix_database.py
    echo [✓] 删除 backend\fix_database.py
)
if exist backend\test_qrcode.py (
    del /Q backend\test_qrcode.py
    echo [✓] 删除 backend\test_qrcode.py
)
if exist quick_test.sh (
    del /Q quick_test.sh
    echo [✓] 删除 quick_test.sh
)

REM 删除临时文档
if exist COMPLETED_v0.1.2.md (
    del /Q COMPLETED_v0.1.2.md
    echo [✓] 删除 COMPLETED_v0.1.2.md
)
if exist FINAL_FIXES.md (
    del /Q FINAL_FIXES.md
    echo [✓] 删除 FINAL_FIXES.md
)
if exist FIXES_v0.1.2.md (
    del /Q FIXES_v0.1.2.md
    echo [✓] 删除 FIXES_v0.1.2.md
)
if exist START_HERE.md (
    del /Q START_HERE.md
    echo [✓] 删除 START_HERE.md
)
if exist UPDATE_LOG_v0.1.1.md (
    del /Q UPDATE_LOG_v0.1.1.md
    echo [✓] 删除 UPDATE_LOG_v0.1.1.md
)
if exist VERIFICATION_CHECKLIST.md (
    del /Q VERIFICATION_CHECKLIST.md
    echo [✓] 删除 VERIFICATION_CHECKLIST.md
)

REM 删除临时目录
if exist backend\__pycache__\ (
    rmdir /S /Q backend\__pycache__
    echo [✓] 删除 backend\__pycache__\ 目录
)

echo.
echo ========================================
echo  清理完成！
echo ========================================
echo.
echo 保留的核心文件：
echo   ✓ backend/app.py
echo   ✓ frontend/index.html
echo   ✓ frontend/admin.html
echo   ✓ README.md
echo   ✓ CHANGELOG.md
echo   ✓ DEPLOY.md
echo   ✓ requirements.txt
echo   ✓ start.bat / start.sh
echo.
pause
