@echo off
chcp 65001 >nul
title 打包下载器

echo ========================================
echo   Windows 多线程下载器 - 打包工具
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 安装 PyInstaller...
pip install pyinstaller -q

echo [2/3] 打包程序...
pyinstaller --onefile --noconsole --name "Downloader" --clean downloader.py

echo [3/3] 打包完成!
echo.
echo 生成的文件在 dist 目录下: dist\Downloader.exe
echo.

:: 清理
if exist "build" rmdir /s /q build
if exist "downloader.spec" del /f /q downloader.spec

pause
