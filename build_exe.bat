@echo off
chcp 65001 >nul
echo 正在打包发票管理系统为exe文件...
echo.

if not exist "dist" mkdir dist

pyinstaller --onefile --windowed --name="发票管理系统" --icon=NONE invoice_manager.py

if %errorlevel% == 0 (
    echo.
    echo 打包成功！exe文件位于 dist 目录中
) else (
    echo.
    echo 打包失败，请确保已安装 pyinstaller: pip install pyinstaller
)

pause
