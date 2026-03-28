@echo off
setlocal EnableExtensions EnableDelayedExpansion
title CS2 Settings Selector

:menu
cls
echo.
echo  =========================================================
echo                    CS2 SETTINGS SELECTOR
echo  =========================================================
echo.
echo    [1] MAIN
echo    [2] TRYHARD
echo    [3] FARMING
echo    [4] ARMSRACE
echo    [5] SKIN INSPECT
echo    [6] PLAYHOUR
echo    [0] EXIT
echo.
echo  =========================================================
echo.

set "choice="
set /p "choice=Enter your choice (0-6): "

if /i "%choice%"=="0" exit /b
if /i "%choice%"=="1" set "settingFolder=SET MAIN" & goto continue
if /i "%choice%"=="2" set "settingFolder=SET TRYHARD" & goto continue
if /i "%choice%"=="3" set "settingFolder=SET FARMING" & goto continue
if /i "%choice%"=="4" set "settingFolder=SET ARMSRACE" & goto continue
if /i "%choice%"=="5" set "settingFolder=SET SKIN INSPECT" & goto continue
if /i "%choice%"=="6" set "settingFolder=SET PLAYHOUR" & goto continue

echo.
echo  [ERROR] Invalid choice. Please enter a number from 0 to 6.
echo.
pause
goto menu

:continue
set "baseFolder="

:: Find the parent folder that contains the setting folders
for /d %%d in ("%~dp0..\*") do (
    if exist "%%d\SET MAIN" (
        set "baseFolder=%%~fd"
        goto foundBaseFolder
    )
)

echo.
echo  [ERROR] Could not locate the settings base folder.
echo  Make sure the script is inside a subfolder, and the parent folder
echo  contains folders like:
echo     SET MAIN
echo     SET TRYHARD
echo     SET FARMING
echo     SET ARMSRACE
echo     SET SKIN INSPECT
echo     SET PLAYHOUR
echo.
pause
goto menu

:foundBaseFolder
set "sourcePath=%baseFolder%\%settingFolder%"
set "steamUserdata=C:\Program Files (x86)\Steam\userdata"

cls
echo.
echo  =========================================================
echo                    APPLYING CS2 SETTINGS
echo  =========================================================
echo.
echo    Selected preset : %settingFolder%
echo    Source path     : %sourcePath%
echo    Steam userdata  : %steamUserdata%
echo.
echo  =========================================================
echo.

if not exist "%sourcePath%\" (
    echo  [ERROR] Preset folder not found:
    echo  %sourcePath%
    echo.
    pause
    goto menu
)

if not exist "%steamUserdata%\" (
    echo  [ERROR] Steam userdata folder not found:
    echo  %steamUserdata%
    echo.
    echo  Check that Steam is installed in the default location.
    echo.
    pause
    goto menu
)

set /a appliedCount=0

for /d %%a in ("%steamUserdata%\*") do (
    echo  Applying to: %%~nxa
    xcopy "%sourcePath%\*" "%%~fa\" /s /e /i /y >nul
    if not errorlevel 1 (
        set /a appliedCount+=1
    ) else (
        echo    Warning: Copy may have failed for %%~fa
    )
)

echo.
echo  =========================================================
if %appliedCount% GTR 0 (
    echo  Done. Settings applied to %appliedCount% Steam userdata folder^(s^).
) else (
    echo  No Steam userdata folders were updated.
)
echo  =========================================================
echo.
pause
goto menu