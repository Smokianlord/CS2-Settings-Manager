::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFChcQxOQPX36PLQR6ebHy+WQrEESVeYsRIbY1bqdeK0V5UngcIRggysI1sIPA3s=
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
::Zh4grVQjdCuDJH6N4GolKid3f1bPD26uErwS7/u23O+Lp04JW/ADTIfempKBLOQW+AXJdJ0oxDRfgM5s
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
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