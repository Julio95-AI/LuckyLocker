#!/bin/bash

echo "========================================"
echo " LuckyLocker 项目清理脚本"
echo "========================================"
echo ""
echo "即将删除以下文件和目录："
echo ""
echo "临时脚本 (3个):"
echo "  - backend/fix_database.py"
echo "  - backend/test_qrcode.py"
echo "  - quick_test.sh"
echo ""
echo "临时文档 (6个):"
echo "  - COMPLETED_v0.1.2.md"
echo "  - FINAL_FIXES.md"
echo "  - FIXES_v0.1.2.md"
echo "  - START_HERE.md"
echo "  - UPDATE_LOG_v0.1.1.md"
echo "  - VERIFICATION_CHECKLIST.md"
echo ""
echo "临时目录 (3个):"
echo "  - doc/"
echo "  - uploads/"
echo "  - backend/__pycache__/"
echo ""
echo "========================================"
echo ""
read -p "确认清理? (y/n): " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "取消清理。"
    exit 0
fi

echo ""
echo "开始清理..."
echo ""

# 删除临时脚本
if [ -f backend/fix_database.py ]; then
    rm -f backend/fix_database.py
    echo "[✓] 删除 backend/fix_database.py"
fi

if [ -f backend/test_qrcode.py ]; then
    rm -f backend/test_qrcode.py
    echo "[✓] 删除 backend/test_qrcode.py"
fi

if [ -f quick_test.sh ]; then
    rm -f quick_test.sh
    echo "[✓] 删除 quick_test.sh"
fi

# 删除临时文档
if [ -f COMPLETED_v0.1.2.md ]; then
    rm -f COMPLETED_v0.1.2.md
    echo "[✓] 删除 COMPLETED_v0.1.2.md"
fi

if [ -f FINAL_FIXES.md ]; then
    rm -f FINAL_FIXES.md
    echo "[✓] 删除 FINAL_FIXES.md"
fi

if [ -f FIXES_v0.1.2.md ]; then
    rm -f FIXES_v0.1.2.md
    echo "[✓] 删除 FIXES_v0.1.2.md"
fi

if [ -f START_HERE.md ]; then
    rm -f START_HERE.md
    echo "[✓] 删除 START_HERE.md"
fi

if [ -f UPDATE_LOG_v0.1.1.md ]; then
    rm -f UPDATE_LOG_v0.1.1.md
    echo "[✓] 删除 UPDATE_LOG_v0.1.1.md"
fi

if [ -f VERIFICATION_CHECKLIST.md ]; then
    rm -f VERIFICATION_CHECKLIST.md
    echo "[✓] 删除 VERIFICATION_CHECKLIST.md"
fi

# 删除临时目录
if [ -d doc ]; then
    rm -rf doc/
    echo "[✓] 删除 doc/ 目录"
fi

if [ -d uploads ]; then
    rm -rf uploads/
    echo "[✓] 删除 uploads/ 目录"
fi

if [ -d backend/__pycache__ ]; then
    rm -rf backend/__pycache__/
    echo "[✓] 删除 backend/__pycache__/ 目录"
fi

echo ""
echo "========================================"
echo " 清理完成！"
echo "========================================"
echo ""
echo "保留的核心文件："
echo "  ✓ backend/app.py"
echo "  ✓ frontend/index.html"
echo "  ✓ frontend/admin.html"
echo "  ✓ README.md"
echo "  ✓ CHANGELOG.md"
echo "  ✓ DEPLOY.md"
echo "  ✓ requirements.txt"
echo "  ✓ start.bat / start.sh"
echo ""
