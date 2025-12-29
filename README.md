# GQ GMC Web-Interface

A Python-based project for interacting with GQ GMC Geiger counters via a modern web interface.

## Project Overview

This project provides a graphical user interface (Web-GUI) to read data from GQ GMC Geiger counters and control the device. It uses the GQ Geiger Counter Communication Protocol (RFC1801).

### Supported Models
The interface is primarily designed for the **GMC-500+** model but supports the entire series:
- GMC-500
- GMC-500+
- GMC-600
- GMC-600+

## Features

- **Real-time CPM Display:** Track Counts Per Minute (CPM) directly in the browser.
- **Automatic Connection:** Automatically searches for connected devices on the USB port.

## Installation

### Prerequisites

- Python 3.8+
- A GQ GMC Geiger counter (connected via USB)

### Installing Dependencies

The project uses `NiceGUI` for the frontend and `pyserial` for communication. Install the required packages with:

```bash
pip install nicegui pyserial
```

## Usage

1. Connect your GMC Geiger counter to your computer via USB.
2. Start the application. Ensure that the project directory is included in the `PYTHONPATH` so that modules are found correctly.

**Linux / macOS:**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python src/main.py
```

Alternatively in one command:
```bash
PYTHONPATH=. python src/main.py
```

**Windows (Command Prompt / CMD):**
```cmd
set PYTHONPATH=%PYTHONPATH%;.
python src/main.py
```

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH += ";."
python src/main.py
```

> **Note:** An execution script will be added in the future to automate this step.

3. Open your browser and navigate to the address displayed in the console (default is `http://localhost:8080`).

## Documentation

Communication is based on the official GQ-RFC1801 protocol. A copy of the specification can be found in the `docs/` folder.
