@echo off
setlocal
title CS2 Folder Setup

cls
echo.
echo  ==========================================
echo           CS2 FOLDER SETUP
echo  ==========================================
echo.

:: Correct folders only
for %%F in (
    "SET MAIN"
    "SET TRYHARD"
    "SET FARMING"
    "SET ARMSRACE"
    "SET SKIN INSPECT"
    "SET PLAYHOUR"
) do (
    if not exist %%F (
        mkdir %%F
        echo  [+] Created: %%F
    ) else (
        echo  [=] Already exists: %%F
    )
)

echo.
echo  ==========================================
echo        Folder setup completed!
echo  ==========================================
echo.
pause