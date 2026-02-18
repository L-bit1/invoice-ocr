@echo off
chcp 65001 >nul
echo ========================================
echo 发票管理系统 - OCR功能安装脚本
echo ========================================
echo.
echo 请选择OCR方案：
echo 1. PaddleOCR (推荐，中文识别效果好)
echo 2. Tesseract OCR (备选方案)
echo.
set /p choice=请输入选项 (1 或 2): 

if "%choice%"=="1" (
    echo.
    echo 正在安装 PaddleOCR...
    pip install paddleocr paddlepaddle
    if %errorlevel% == 0 (
        echo.
        echo PaddleOCR 安装成功！
        echo 现在可以使用OCR识别功能了。
    ) else (
        echo.
        echo 安装失败，请检查网络连接或Python环境。
    )
) else if "%choice%"=="2" (
    echo.
    echo 正在安装 Tesseract OCR Python库...
    pip install pytesseract pillow
    if %errorlevel% == 0 (
        echo.
        echo Python库安装成功！
        echo.
        echo 注意：您还需要安装 Tesseract-OCR 软件：
        echo Windows: https://github.com/UB-Mannheim/tesseract/wiki
        echo Mac: brew install tesseract tesseract-lang
        echo Linux: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
    ) else (
        echo.
        echo 安装失败，请检查网络连接或Python环境。
    )
) else (
    echo.
    echo 无效的选项！
)

echo.
pause
