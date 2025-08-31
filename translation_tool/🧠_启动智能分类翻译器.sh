#!/bin/bash
# 智能分类翻译器启动脚本

echo "🧠 智能分类翻译器启动脚本"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

# 检查tkinter支持
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ tkinter未安装，正在尝试安装..."
    if command -v brew &> /dev/null; then
        brew install python-tk
    else
        echo "请手动安装tkinter支持"
        exit 1
    fi
fi

# 检查requests库
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装requests库..."
    pip3 install requests
fi

# 进入脚本目录
cd "$(dirname "$0")"

echo "🚀 启动智能分类翻译器..."
echo ""
echo "✨ 功能特色:"
echo "   • 自动识别单词和句子"
echo "   • 单词 → 词典查询（音标、释义、例句）"
echo "   • 句子 → 智能翻译（中英互译）"
echo "   • 一键生成Anki卡片"
echo ""

# 启动程序
python3 智能分类翻译器.py

echo ""
echo "👋 智能分类翻译器已关闭"