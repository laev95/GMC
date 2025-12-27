# GQ GMC Web-Interface

Ein Python-basiertes Projekt zur Interaktion mit GQ GMC Geigerzählern über ein modernes Web-Interface.

## Projektübersicht

Dieses Projekt bietet eine grafische Benutzeroberfläche (Web-GUI), um Daten von GQ GMC Geigerzählern auszulesen und das Gerät zu steuern. Es nutzt das GQ Geiger Counter Communication Protocol (RFC1801).

### Unterstützte Modelle
Das Interface ist primär für das Modell **GMC-500+** konzipiert, unterstützt aber die gesamte Reihe:
- GMC-500
- GMC-500+
- GMC-600
- GMC-600+

## Features

- **Echtzeit-CPM-Anzeige:** Verfolgen Sie die Counts Per Minute (CPM) direkt im Browser.
- **Geräteinformationen:** Auslesen von Hardware-Modell, Firmware-Version und Batteriespannung.
- **Automatische Verbindung:** Sucht automatisch nach angeschlossenen Geräten am USB-Port.

## Installation

### Voraussetzungen

- Python 3.8+
- Ein GQ GMC Geigerzähler (verbunden via USB)

### Abhängigkeiten installieren

Das Projekt verwendet `NiceGUI` für das Frontend und `pyserial` für die Kommunikation. Installieren Sie die benötigten Pakete mit:

```bash
pip install nicegui pyserial
```

## Benutzung

1. Verbinden Sie Ihren GMC Geigerzähler über USB mit Ihrem Computer.
2. Starten Sie die Anwendung. Stellen Sie sicher, dass das Projektverzeichnis im `PYTHONPATH` enthalten ist, damit die Module korrekt gefunden werden.

**Linux / macOS:**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python src/main.py
```

Alternativ in einem Befehl:
```bash
PYTHONPATH=. python src/main.py
```

**Windows (Eingabeaufforderung / CMD):**
```cmd
set PYTHONPATH=%PYTHONPATH%;.
python src/main.py
```

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH += ";."
python src/main.py
```

> **Hinweis:** Ein Ausführungsskript wird in Zukunft hinzugefügt, um diesen manuellen Schritt zu automatisieren.

3. Öffnen Sie Ihren Browser und navigieren Sie zu der in der Konsole angezeigten Adresse (standardmäßig `http://localhost:8080`).

## Dokumentation

Die Kommunikation basiert auf dem offiziellen GQ-RFC1801 Protokoll. Eine Kopie der Spezifikation befindet sich im Ordner `docs/`.