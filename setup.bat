@echo off
chcp 65001 >nul
echo ===========================================
echo   业务员重点客户管理 - 一键安装
echo ===========================================
echo.

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"

:: Detect main exe regardless of filename encoding
set "MAIN_EXE="
for %%f in ("%APP_DIR%\*.exe") do (
    echo %%~nxf | findstr /v /i "卸载 uninstall" >nul
    if not errorlevel 1 set "MAIN_EXE=%%~nxf"
)
if "%MAIN_EXE%"=="" (
    echo [错误] 未找到程序 EXE 文件。
    echo 请将本 bat 放在与客户管理.exe 同一个文件夹内。
    pause
    exit /b 1
)
echo [OK] 已找到 %MAIN_EXE%

:: Create VBS launcher (silent start, no console)
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
    echo [警告] 开机自启失败，请手动复制以下文件到启动文件夹：
    echo   %VBS_FILE%
    echo   → %STARTUP_DIR%
)

:: Create desktop shortcut pointing to EXE
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "DESKTOP_SHORTCUT=%DESKTOP_DIR%\业务员重点客户管理.lnk"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $s = $WshShell.CreateShortcut('%DESKTOP_SHORTCUT%'); $s.TargetPath = '%APP_DIR%\%MAIN_EXE%'; $s.WorkingDirectory = '%APP_DIR%'; $s.Save()" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 桌面快捷方式已创建
) else (
    echo [提示] 桌面快捷方式创建失败，可手动右键 exe 发送到桌面
)

echo.
echo ===========================================
echo   安装完成！程序将开机自动启动。
echo   也可双击 %MAIN_EXE% 手动打开。
echo ===========================================
pause
