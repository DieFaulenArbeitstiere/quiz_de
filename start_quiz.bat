@echo off
chcp 65001 >nul
title Quiz-Projekt Server
setlocal enabledelayedexpansion

echo ========================================
echo  Quiz-Projekt - Server starten
echo ========================================
echo.

where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker wurde nicht gefunden.
    echo.
    echo Moechtest du Docker Desktop installieren?
    echo [1] Ja, Download-Seite oeffnen
    echo [2] Nein, Skript beenden
    echo.
    choice /c 12 /n /m "Auswahl (1/2): "
    if errorlevel 2 exit /b 1
    if errorlevel 1 (
        echo Oeffne https://www.docker.com/products/docker-desktop/ ...
        start https://www.docker.com/products/docker-desktop/
        echo.
        echo Installiere Docker Desktop und starte dieses Skript erneut.
        pause
        exit /b 1
    )
)

echo Starte Docker-Container...
cd /d "%~dp0"

REM Docker Desktop starten falls noch nicht aktiv (Windows)
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker ist noch nicht gestartet. Bitte Docker Desktop starten und warten...
    echo Starte Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Warte bis zu 60 Sekunden auf Docker...
    for /l %%i in (1,1,60) do (
        timeout /t 1 /nobreak >nul
        docker info >nul 2>&1
        if !errorlevel! equ 0 goto docker_ready
    )
    echo Docker konnte nicht erreicht werden. Bitte manuell starten.
    pause
    exit /b 1
)
:docker_ready

docker compose -f backend\docker-compose.yml up -d --build
if %errorlevel% neq 0 (
    echo FEHLER: Docker-Container konnte nicht gestartet werden.
    pause
    exit /b 1
)

echo Warte auf Server...
timeout /t 3 /nobreak >nul

echo Oeffne http://localhost:5000 im Browser...
start http://localhost:5000

echo.
echo ========================================
echo  Server laeuft unter http://localhost:5000
echo ========================================
echo.
echo  Bestenliste-Daten: backend\daten\bestenliste.db
echo.
echo  STOPPEN: docker compose -f backend\docker-compose.yml down
echo  (Dafuer Terminal hier oeffnen ^& Befehl eingeben)
echo.
pause
