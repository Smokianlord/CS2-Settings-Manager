::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFChcQxOQPX36PLQR6ebHy+WQrEESVeYsRIbY1bqdeK0A71HwfJgqxTcOyJtCBRhXHg==
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCuDJH6N4GolKid3f1bPD26uErwS7/u23O+Lp04JW/ADW7yJmoeLNPQa5EL3NaUo2n9ZjMQeTC0WLFyudgpU
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
cls

echo ==========================================
echo         CS2 SETTINGS SELECTOR
echo ==========================================
echo.
echo [1] MAIN
echo [2] TRYHARD
echo [3] FARM
echo [4] ARMSRACE
echo [5] SKIN INSPECT
echo [6] PLAYHOUR
echo [0] EXIT
echo.
echo ==========================================

set /p "choice=Enter your choice (0/1/2/3/4/5/6): "

if "%choice%"=="0" exit /b

for /d %%d in ("%~dp0..\*") do (
    if exist "%%d\SET MAIN" (
        set "baseFolder=%%d"
        goto foundBaseFolder
    )
)

echo.
echo ==========================================
echo ERROR: Could not find settings folder.
echo Make sure the SET folders are one level
echo above this script.
echo ==========================================
pause
exit /b

:foundBaseFolder

if "%choice%"=="1" (
    set "settingFolder=SET MAIN"
) else if "%choice%"=="2" (
    set "settingFolder=SET TRYHARD"
) else if "%choice%"=="3" (
    set "settingFolder=SET FARMING"
) else if "%choice%"=="4" (
    set "settingFolder=SET ARMSRACE"
) else if "%choice%"=="5" (
    set "settingFolder=SET SKIN INSPECT"
) else if "%choice%"=="6" (
    set "settingFolder=SET PLAYHOUR"
) else (
    echo.
    echo ==========================================
    echo Invalid choice. Please try again.
    echo ==========================================
    pause
    exit /b
)

echo.
echo ==========================================
echo Selected Setting: %settingFolder%
echo Path to Apply: %baseFolder%\%settingFolder%
echo ==========================================

if not exist "%baseFolder%\%settingFolder%" (
    echo.
    echo ==========================================
    echo ERROR: Folder "%baseFolder%\%settingFolder%" not found!
    echo Please ensure the folder exists.
    echo ==========================================
    pause
    exit /b
)

echo.
echo ==========================================
echo Applying settings from:
echo %baseFolder%\%settingFolder%
echo ==========================================
echo.

for /D %%a in ("C:\Program Files (x86)\Steam\userdata\*") do (
    echo Applying settings to: %%a
    xcopy "%baseFolder%\%settingFolder%\*" "%%a\\" /s /e /y >nul
)

echo.
echo ==========================================
echo Settings applied successfully!
echo ==========================================
pause