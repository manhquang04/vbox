# System Toolbox: App Uninstaller & Resource Monitor

A Python desktop application for Linux (Ubuntu/Debian) to manage applications and monitor system resources.

## Features
- **Uninstall Applications**: List and uninstall apt packages.
- **Disk Usage**: Monitor disk space usage.
- **RAM & Processes**: Monitor memory usage and top processes.

## Requirements
- Python 3.x
- PySide6
- psutil

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python3 -m system_toolbox.main
```

## Packaging (Optional)
To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller -F -w system_toolbox/system_toolbox/main.py -n system-toolbox
   ```
   * `-F`: Create a one-file bundled executable.
   * `-w`: Windowed mode (no console window).
   * `-n`: Name of the executable.

3. Run the executable:
   ```bash
   ./dist/system-toolbox
   ```

## Architecture
- **main.py**: Entry point, sets up the main window and tabs.
- **apps_tab.py**: Handles listing and uninstalling applications.
- **disk_tab.py**: Displays disk usage information.
- **ram_tab.py**: Monitors RAM usage and processes.
- **system_info.py**: Helper functions for system stats (psutil).
- **package_manager.py**: Helper functions for package management (dpkg/apt).
