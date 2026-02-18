#!/bin/bash
echo "========================================"
echo "发票管理系统 - OCR功能安装脚本"
echo "========================================"
echo ""
echo "请选择OCR方案："
echo "1. PaddleOCR (推荐，中文识别效果好)"
echo "2. Tesseract OCR (备选方案)"
echo ""
read -p "请输入选项 (1 或 2): " choice

if [ "$choice" == "1" ]; then
    echo ""
    echo "正在安装 PaddleOCR..."
    pip3 install paddleocr paddlepaddle
    if [ $? -eq 0 ]; then
        echo ""
        echo "PaddleOCR 安装成功！"
        echo "现在可以使用OCR识别功能了。"
    else
        echo ""
        echo "安装失败，请检查网络连接或Python环境。"
    fi
elif [ "$choice" == "2" ]; then
    echo ""
    echo "正在安装 Tesseract OCR Python库..."
    pip3 install pytesseract pillow
    if [ $? -eq 0 ]; then
        echo ""
        echo "Python库安装成功！"
        echo ""
        echo "注意：您还需要安装 Tesseract-OCR 软件："
        echo "Mac: brew install tesseract tesseract-lang"
        echo "Linux: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim"
    else
        echo ""
        echo "安装失败，请检查网络连接或Python环境。"
    fi
else
    echo ""
    echo "无效的选项！"
fi
