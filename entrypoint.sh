#!/bin/sh
# Dieses Skript stellt sicher, dass die notwendigen Verzeichnisse existieren,
# bevor die Hauptanwendung gestartet wird.

# Beendet das Skript sofort, wenn ein Befehl fehlschlägt
set -e

# Erstelle die Verzeichnisstruktur innerhalb des /app-Volumes.
# Der '-p' Parameter sorgt dafür, dass keine Fehler auftreten, wenn die Ordner bereits existieren.
echo "Stelle sicher, dass die Verzeichnisstruktur existiert..."
mkdir -p /app/input
mkdir -p /app/addons
mkdir -p /app/web
mkdir -p /app/zips
echo "Verzeichnisstruktur ist bereit."

# Führe den Befehl aus, der nach dem Entrypoint übergeben wird
# (In unserem Fall das CMD aus der Dockerfile).
exec "$@"
