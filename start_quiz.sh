#!/bin/bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "========================================"
echo " Quiz-Projekt - Server starten"
echo "========================================"
echo ""

if ! command -v docker &> /dev/null; then
    echo "Docker ist nicht installiert."
    echo ""
    echo "Moechtest du Docker automatisch installieren?"
    echo "  [1] Ja (apt install docker.io docker-compose-v2)"
    echo "  [2] Nein (Skript beenden)"
    echo ""
    read -rp "Auswahl (1/2): " choice
    if [ "$choice" = "1" ]; then
        echo "Installiere Docker (sudo erforderlich)..."
        sudo apt update
        sudo apt install -y docker.io docker-compose-v2
        sudo systemctl enable docker --now
        echo "Docker installiert."
    else
        exit 1
    fi
fi

if ! docker compose version &> /dev/null; then
    echo "Docker Compose ist nicht verfuegbar."
    echo "Installiere mit: sudo apt install docker-compose-v2"
    exit 1
fi

# User zur docker-Gruppe hinzufuegen, falls nicht schon
if ! groups "$USER" | grep -q docker; then
    echo "Fuege Benutzer zur docker-Gruppe hinzu (damit sudo nicht noetig)..."
    sudo usermod -aG docker "$USER"
    echo "Bitte einmal aus- und wieder einloggen, oder neues Terminal oeffnen."
    echo "Fuehre das Skript danach erneut aus."
    echo ""
    echo "Starte jetzt mit sudo..."
fi

echo "Starte Docker-Container..."
if groups "$USER" | grep -q docker; then
    docker compose -f backend/docker-compose.yml up -d --build
else
    sudo docker compose -f backend/docker-compose.yml up -d --build
fi

echo "Warte auf Server..."
sleep 3

echo "Oeffne http://localhost:5000..."
xdg-open http://localhost:5000 2>/dev/null || \
    sensible-browser http://localhost:5000 2>/dev/null || \
    echo "Oeffne manuell: http://localhost:5000"

echo ""
echo "========================================"
echo " Server laeuft unter http://localhost:5000"
echo "========================================"
echo ""
echo " Bestenliste-Daten: backend/daten/bestenliste.db"
echo ""
echo " STOPPEN: docker compose -f backend/docker-compose.yml down"
echo "         (oder: sudo docker compose ... falls noetig)"
echo ""
