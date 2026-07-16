@echo off
chcp 65001 >nul
title Quiz-Projekt Server stoppen

echo ========================================
echo  Quiz-Projekt - Server stoppen
echo ========================================
echo.

cd /d "%~dp0"

echo Stoppe und entferne Container...
docker compose -f backend\docker-compose.yml down

if %errorlevel% equ 0 (
    echo.
    echo Container gestoppt und entfernt.
) else (
    echo.
    echo Container lief wohl nicht.
)

echo.
pause
