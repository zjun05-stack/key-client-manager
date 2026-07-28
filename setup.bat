@echo off
chcp 65001 >nul
echo ===========================================
echo   业务员重点客户管理 - 一键安装
echo ===========================================
echo.

set "APP_DIR=%~dp0"

:: ── Detect mode: EXE or Python ──
if exist "%APP_DIR%客户管理.exe" (
    set "MODE=exe"
    echo [检测] 独立 EXE 模式（无需 Python）
) else (
    set "MODE=python"
    echo [检测] Python 脚本模式
)

:: ── Python mode: check & install dependencies ──
if "%MODE%"=="python" (
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [错误] 未检测到 Python
        echo.
        echo 请按以下步骤安装 Python：
        echo   1. 打开浏览器，访问 https://www.python.org/downloads/
        echo   2. 点击黄色 "Download Python" 按钮
        echo   3. 运行下载的安装程序
        echo   4. 务必勾选底部的 "Add Python to PATH" ✓
        echo   5. 点击 Install Now 等待完成
        echo   6. 重新运行本 setup.bat
        echo.
        pause
        exit /b 1
    )
    echo [OK] Python 已安装

    echo [*] 正在安装依赖库...
    pip install -r "%APP_DIR%requirements.txt" --user --quiet
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo [OK] 依赖库安装完成
)

:: ── Create VBS launcher (no black console window) ──
set "VBS_FILE=%APP_DIR%launcher.vbs"
if "%MODE%"=="exe" (
    echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_FILE%"
    echo WshShell.Run """%APP_DIR%客户管理.exe"" --silent", 0 >> "%VBS_FILE%"
) else (
    echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_FILE%"
    echo WshShell.Run "pythonw ""%APP_DIR%main.py"" --silent", 0 >> "%VBS_FILE%"
)
echo [OK] 启动器已创建

:: ── Copy VBS to Windows Startup folder ──
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP_DIR%\业务员重点客户管理.vbs"

copy "%VBS_FILE%" "%SHORTCUT%" /Y >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 开机自启已设置
) else (
    echo [警告] 开机自启设置失败，请手动复制：
    echo        %VBS_FILE%
    echo    到 %STARTUP_DIR%
)

:: ── Create desktop shortcut ──
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "DESKTOP_SHORTCUT=%DESKTOP_DIR%\业务员重点客户管理.lnk"

if "%MODE%"=="exe" (
    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_SHORTCUT%'); $Shortcut.TargetPath = '%APP_DIR%客户管理.exe'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.Save()" >nul 2>&1
) else (
    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_SHORTCUT%'); $Shortcut.TargetPath = 'pythonw.exe'; $Shortcut.Arguments = '""%APP_DIR%main.py""'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.Save()" >nul 2>&1
)
if %errorlevel% equ 0 (
    echo [OK] 桌面快捷方式已创建
) else (
    echo [提示] 可手动在桌面创建快捷方式
)

echo.
echo ===========================================
echo   安装完成！
echo   程序将随电脑开机自动启动
echo   双击桌面快捷方式或 EXE 即可手动打开
echo ===========================================
pause
