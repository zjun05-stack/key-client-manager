@echo off
chcp 65001 >nul
echo ===========================================
echo   打包为独立 EXE（无需 Python 环境）
echo ===========================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 本机未安装 Python，请先安装 Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)

:: Install PyInstaller
echo [*] 安装 PyInstaller...
pip install pyinstaller --user --quiet
if %errorlevel% neq 0 (
    echo [错误] 安装失败
    pause
    exit /b 1
)

:: Build
echo [*] 正在打包，约需 1-2 分钟...
pyinstaller --onefile --windowed --name "客户管理" --clean main.py
if %errorlevel% neq 0 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ===========================================
echo   打包完成！
echo   可分发文件: dist\客户管理.exe
echo   将 客户管理.exe + 重点客户名单.xlsx
echo   复制到同一个文件夹，即可分发给业务员
echo ===========================================
pause
