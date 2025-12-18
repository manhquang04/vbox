import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction

# Import tabs
from system_toolbox.apps_tab import AppsTab
from system_toolbox.disk_tab import DiskTab
from system_toolbox.ram_tab import RamTab
from system_toolbox.styles import get_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VBox")
        self.resize(1100, 750)
        
        # Set App Icon
        # Prefer PNG if available for better quality on Linux
        icon_path = resource_path(os.path.join("image", "logo.png"))
        if not os.path.exists(icon_path):
             icon_path = resource_path(os.path.join("image", "logo.ico"))
             
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Theme State
        self.current_theme = "dark" # Default

        # Main layout container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Initialize Tab Widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Create Tabs
        self.tab_apps = AppsTab()
        self.tab_disk = DiskTab()
        self.tab_ram = RamTab()

        # Add tabs to the widget
        self.tabs.addTab(self.tab_apps, "Applications")
        self.tabs.addTab(self.tab_disk, "Disk Usage")
        self.tabs.addTab(self.tab_ram, "RAM Processes")
        
        # Apply Theme (Light Mode Only)
        self.apply_theme()

    def apply_theme(self):
        app = QApplication.instance()
        app.setStyleSheet(get_stylesheet())

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)
    
    # Apply a clean fusion style for better look on Linux as base
    app.setStyle("Fusion")

    # Set App Icon globally
    icon_path = resource_path(os.path.join("image", "logo.png"))
    if not os.path.exists(icon_path):
        icon_path = resource_path(os.path.join("image", "logo.ico"))
    
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        # Also set distinct app name/id for some DEs
        app.setDesktopFileName("vbox")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
