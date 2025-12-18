# VBox - Linux System Toolbox

**VBox** is a powerful, all-in-one system utility designed for Linux users to manage applications, monitor system resources, and optimize performance. Built with **Python** and **PySide6**, it offers a modern, clean, and responsive graphical user interface (GUI) that integrates seamlessly with your desktop environment.

##  Key Features

### 1. Application Manager
Take control of your installed software with a unified view of all applications.
*   **Universal Support:** Detects and lists applications from multiple sources:
    *   **Native Packages:** `.rpm` (Fedora/RHEL) and `.deb` (Ubuntu/Debian).
    *   **Sandboxed Apps:** Flatpak and Snap.
    *   **Portable Apps:** AppImage.
    *   **Desktop Shortcuts:** Scans `.desktop` files for a complete list.
*   **Smart Search:** Instantly filter applications by name.
*   **Detailed Info:** View version, installation size, and package type for every app.
*   **Easy Uninstall:** Remove unwanted applications directly from the interface.
    *   *Note: System package removal requires root privileges (handled securely via `pkexec`).*

### 2. Resource Monitor (RAM & Processes)
Keep an eye on your system's health in real-time.
*   **Live RAM Usage:** Visual progress bar showing used vs. total memory with color-coded health indicators (Green/Orange/Red).
*   **Process Manager:** Lists top memory-consuming processes.
*   **Task Killer:** Right-click on any process to terminate (kill) it immediately if it's freezing your system.
*   **Auto-Refresh:** Data updates automatically every 3 seconds.

### 3. Disk Usage Analyzer
*   Visualize your disk space usage to identify what's taking up the most room.
*   Clean up unnecessary files to free up storage.

## 🛠️ Technical Architecture

VBox is built on a robust and modular architecture:

*   **Core Language:** Python 3.10+
*   **GUI Framework:** PySide6 (Qt for Python) for a native look and feel.
*   **System Integration:**
    *   **`psutil`**: For retrieving real-time system information (RAM, CPU, Processes).
    *   **`subprocess`**: For interacting with system package managers (`dnf`, `apt`, `rpm`, `dpkg`).
    *   **`pkexec`**: For securely executing privileged commands (like uninstalling software).
*   **Cross-Distro Compatibility:** Automatically detects the underlying Linux distribution (Fedora/RHEL vs. Ubuntu/Debian) to select the appropriate backend logic.

## 📥 Installation

### Option 1: Pre-built Packages (Recommended)
Download the latest release for your distribution from our [Website](https://manhquang04.github.io/vbox/) or [GitHub Releases](https://github.com/manhquang04/vbox/releases).

*   **Fedora / RHEL / CentOS:**
    ```bash
    sudo dnf install ./vbox-*.rpm
    ```

*   **Ubuntu / Debian / Linux Mint:**
    ```bash
    sudo apt install ./vbox_*.deb
    ```
    *Troubleshooting for Ubuntu 22.04:* If the app fails to launch, install the missing library:
    ```bash
    sudo apt install libxcb-cursor0
    ```

*   **AppImage (Universal):**
    1.  Download the `.AppImage` file.
    2.  Make it executable:
        ```bash
        chmod +x VBox-*.AppImage
        ```
    3.  Run it:
        ```bash
        ./VBox-*.AppImage
        ```

### Option 2: Run from Source
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/manhquang04/vbox.git
    cd vbox
    ```

2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python3 -m system_toolbox.main
    ```

## 📦 Building from Source

If you want to package the application yourself, we provide scripts for various formats.

**Prerequisites:**
*   `python3-pip`, `python3-venv`
*   `dpkg` (for .deb)
*   `rpm-build` (for .rpm)
*   `imagemagick` (for icon processing)

**Build Commands:**

1.  **Build Binary (PyInstaller):**
    ```bash
    ./build_app.sh
    ```

2.  **Build .deb Package (Ubuntu/Debian):**
    ```bash
    ./build_deb.sh
    ```
    *Output:* `deb_dist/vbox_*.deb`

3.  **Build .rpm Package (Fedora/RHEL):**
    ```bash
    ./build_rpm.sh
    ```
    *Output:* `rpm_dist/vbox-*.rpm`

4.  **Build AppImage:**
    ```bash
    ./build_appimage.sh
    ```
    *Output:* `VBox-*.AppImage`

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License.

---
*Developed by ManhQuang*
