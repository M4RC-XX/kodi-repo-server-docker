# Verwende ein schlankes Python-Image
FROM python:3.9-slim

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere die Skripte
COPY repo_automator.py .
COPY generator.py .
COPY entrypoint.sh .

# *** KORREKTUR: Installiere dos2unix, um Zeilenende-Probleme zu beheben ***
RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir watchdog packaging

# *** KORREKTUR: Konvertiere die Zeilenenden der entrypoint.sh ***
RUN dos2unix /app/entrypoint.sh

# Mache das Entrypoint-Skript ausführbar
RUN chmod +x /app/entrypoint.sh

# Erstelle einen Standardbenutzer und gib ihm die Rechte für das /app-Verzeichnis
RUN useradd -m -u 1000 pi && \
    chown -R pi:pi /app

# Wechsle zum neuen Benutzer
USER pi

# Setze den Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Definiere den Standardbefehl
CMD ["sh", "-c", "python repo_automator.py & python -m http.server 8008 --directory /app/web"]