@echo off
chcp 65001 >nul
echo ===========================================
echo   业务员重点客户管理 - 一键安装
echo ===========================================
echo.

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"

:: Use PowerShell to reliably find the main EXE (skip uninstaller)
for /f "delims=" %%f in ('powershell -Command "Get-ChildItem '%APP_DIR%' -Filter *.exe | Where-Object { $_.Name -notmatch 'uninstall|卸载' } | Sort-Object Length -Descending | Select-Object -First 1 -ExpandProperty Name"') do set "MAIN_EXE=%%f"

if "%MAIN_EXE%"=="" (
    echo [错误] 未找到程序文件。
    echo 请将本 bat 与 客户管理.exe 放在同一文件夹内。
    pause
    exit /b 1
)
echo [OK] 已找到主程序: %MAIN_EXE%

:: Create VBS launcher (silent start, no console window)
set "VBS_FILE=%APP_DIR%\launcher.vbs"
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_FILE%"
echo WshShell.Run """%APP_DIR%\%MAIN_EXE%"" --silent", 0 >> "%VBS_FILE%"
echo [OK] 启动器已创建

:: Copy VBS to Windows Startup folder
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP_DIR%\业务员重点客户管理.vbs"
copy "%VBS_FILE%" "%SHORTCUT%" /Y >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 开机自启已设置
) else (
    echo [警告] 开机自启失败，请手动复制:
    echo   %VBS_FILE%
    echo   到 %STARTUP_DIR%
)

:: Create desktop shortcut pointing to the main EXE
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "DESKTOP_SHORTCUT=%DESKTOP_DIR%\业务员重点客户管理.lnk"
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%DESKTOP_SHORTCUT%');$s.TargetPath='%APP_DIR%\%MAIN_EXE%';$s.WorkingDirectory='%APP_DIR%';$s.Save()" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 桌面快捷方式已创建
) else (
    echo [提示] 桌面快捷方式创建失败，可手动右键 %MAIN_EXE% 发送到桌面
)

echo.
echo ===========================================
echo   安装完成！程序将开机自动启动。
echo   也可双击 %MAIN_EXE% 手动打开。
echo ===========================================
pause
