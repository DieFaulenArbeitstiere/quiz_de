#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "========================================"
echo " Quiz-Projekt - Server stoppen"
echo "========================================"
echo ""

if command -v docker &> /dev/null; then
    if docker compose version &> /dev/null; then
        CMD="docker compose"
    else
        CMD="docker-compose"
    fi
    if groups "$USER" | grep -q docker 2>/dev/null; then
        $CMD -f backend/docker-compose.yml down
    else
        echo "Stoppe mit sudo..."
        sudo $CMD -f backend/docker-compose.yml down
    fi
    echo ""
    echo "Container gestoppt."
else
    echo "Docker ist nicht installiert. Nichts zu stoppen."
fi
echo ""
