# -*- coding: utf-8 -*-
import os
import shutil
import time
import zipfile
import subprocess
import re
from datetime import datetime
from xml.etree import ElementTree as ET
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from packaging.version import Version

# --- Konfiguration --------------------------------------------------
INPUT_DIR = "/app/input"
ADDONS_DIR = "/app/addons"
REPO_DIR = "/app/web"
ARCHIVE_DIR = "/app/zips"
GENERATOR_SCRIPT = "/app/generator.py"
# --------------------------------------------------------------------

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)

def run_generator():
    log(f"▶️ Führe generator.py aus. Quelle: '{ADDONS_DIR}', Ziel: '{REPO_DIR}'...")
    try:
        process = subprocess.run(
            ["python", GENERATOR_SCRIPT, ADDONS_DIR, REPO_DIR],
            capture_output=True, text=True, check=True
        )
        log("✅ generator.py wurde erfolgreich ausgeführt.")
        if process.stdout:
            log("--- Ausgabe von generator.py ---")
            print(process.stdout)
            log("---------------------------------")
        return True
    except subprocess.CalledProcessError as e:
        log(f"‼️ FEHLER bei der Ausführung von generator.py:\n{e.stderr}")
        return False
    except Exception as e:
        log(f"‼️ Kritischer Fehler beim Aufruf von generator.py: {e}")
        return False

class ZipHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.zip'):
            return
        
        time.sleep(1)
        original_path = event.src_path
        log(f"📦 Neue Datei erkannt: {os.path.basename(original_path)}")

        try:
            if not zipfile.is_zipfile(original_path):
                 log(f"‼️ FEHLER: '{os.path.basename(original_path)}' ist keine gültige ZIP-Datei.")
                 return

            with zipfile.ZipFile(original_path, 'r') as zf:
                xml_path_list = [name for name in zf.namelist() if name.count('/') == 1 and name.endswith('addon.xml')]
                if not xml_path_list:
                    log(f"!! FEHLER: Konnte 'addon.xml' in '{os.path.basename(original_path)}' nicht finden.")
                    return
                
                with zf.open(xml_path_list[0]) as f:
                    tree = ET.parse(f)
                    addon_id = tree.getroot().get('id')
                    original_version_str = tree.getroot().get('version')
                    
                    safe_version_str = original_version_str.replace('~', '-')
                    comparable_version_str = re.sub(r'~[a-zA-Z_.-]+', '.dev', original_version_str)
                    new_version = Version(comparable_version_str)
                
                log(f"   -> Info aus ZIP: ID='{addon_id}', Version='{new_version}' (Original: '{original_version_str}')")

                existing_version = Version("0.0.0")
                addon_folder_name = xml_path_list[0].split('/')[0]
                existing_addon_path = os.path.join(ADDONS_DIR, addon_folder_name)

                if os.path.exists(existing_addon_path):
                    log(f"   -> Addon existiert bereits. Prüfe Version in '{existing_addon_path}'...")
                    try:
                        existing_xml_path = os.path.join(existing_addon_path, 'addon.xml')
                        if os.path.exists(existing_xml_path):
                            tree = ET.parse(existing_xml_path)
                            existing_comparable_str = re.sub(r'~[a-zA-Z_.-]+', '.dev', tree.getroot().get('version'))
                            existing_version = Version(existing_comparable_str)
                            log(f"   -> Existierende Version gefunden: {existing_version}")
                    except Exception as e:
                        log(f"   -> WARNUNG: Konnte existierende addon.xml nicht lesen. Fehler: {e}")

                new_archive_filename = f"{addon_id}-{safe_version_str}.zip"
                archive_path = os.path.join(ARCHIVE_DIR, new_archive_filename)

                if new_version <= existing_version:
                    log(f"   -> AKTION: Neue Version ({new_version}) ist älter oder gleich der existierenden ({existing_version}). Addon wird nur archiviert.")
                    shutil.move(original_path, archive_path)
                    log(f"   -> Originaldatei nach '{archive_path}' archiviert.")
                    log(f"✨ Verarbeitung für '{os.path.basename(original_path)}' abgeschlossen (keine Repo-Änderung).")
                    return

                log(f"   -> AKTION: Neue Version ({new_version}) ist neuer als die existierende ({existing_version}). Repository wird aktualisiert.")
                if os.path.exists(existing_addon_path):
                    log(f"   -> Lösche alten Addon-Ordner: '{existing_addon_path}'")
                    shutil.rmtree(existing_addon_path)

                log(f"   -> Entpacke '{os.path.basename(original_path)}' nach {ADDONS_DIR}...")
                zf.extractall(ADDONS_DIR)
                log("   -> Entpacken erfolgreich.")

            if run_generator():
                shutil.move(original_path, archive_path)
                log(f"   -> Originaldatei erfolgreich nach '{archive_path}' archiviert.")
                log(f"✨ Verarbeitung für '{os.path.basename(original_path)}' komplett (Repo aktualisiert).")
            else:
                log("   -> Da generator.py fehlgeschlagen ist, verbleibt die Originaldatei im Input-Ordner.")

        except Exception as e:
            log(f"‼️ EIN UNERWARTETER FEHLER ist aufgetreten: {e}")

# --- MAIN ---
if __name__ == "__main__":
    for d in [INPUT_DIR, ADDONS_DIR, REPO_DIR, ARCHIVE_DIR]:
        os.makedirs(d, exist_ok=True)
    log("Initialisiere Kodi Repository Automator...")
    run_generator()
    log(f"🚀 Server gestartet. Überwache den Ordner: '{INPUT_DIR}'")
    observer = Observer()
    observer.schedule(ZipHandler(), INPUT_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        log("\nBeende Server...")
        observer.stop()
    observer.join()
    log("Server erfolgreich beendet.")