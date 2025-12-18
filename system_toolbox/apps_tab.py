from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QTextEdit, QDialog, QLabel, QComboBox, QMenu
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtGui import QIcon, QAction
from system_toolbox.package_manager import get_package_manager
import subprocess
import os
import glob

DENYLIST = ["linux-image", "ubuntu-desktop", "systemd", "python3", "gnome-shell", "kernel", "filesystem"]

class IconLoader:
    def __init__(self, preloaded_map=None):
        self.desktop_map = preloaded_map if preloaded_map is not None else {}
        self.icon_cache = {}
        if preloaded_map is None:
            self._scan_desktop_files()

    def _scan_desktop_files(self):
        # This is now only a fallback if not preloaded
        # Logic moved to thread for performance
        pass

    def get_icon(self, package_name):
        if package_name in self.icon_cache:
            return self.icon_cache[package_name]

        icon = self._resolve_icon(package_name)
        self.icon_cache[package_name] = icon
        return icon

    def _find_fallback_icon(self, name):
        # Search common paths for png/svg/xpm/ico
        # This helps find icons for apps that don't fully integrate with the icon theme
        search_paths = [
            "/usr/share/pixmaps",
            "/usr/share/icons/hicolor/128x128/apps",
            "/usr/share/icons/hicolor/48x48/apps",
            "/usr/share/icons/hicolor/256x256/apps",
            "/usr/share/icons/hicolor/512x512/apps",
            "/usr/share/icons/hicolor/scalable/apps",
            "/usr/share/icons",
            "/usr/share/app-install/icons",
            os.path.expanduser("~/.local/share/icons"),
            os.path.expanduser("~/.icons")
        ]
        
        extensions = [".png", ".svg", ".xpm", ".ico", ".icns"]
        
        for path in search_paths:
            if not os.path.exists(path):
                continue
            
            for ext in extensions:
                full_path = os.path.join(path, name + ext)
                if os.path.exists(full_path):
                    return QIcon(full_path)
        return None

    def _resolve_icon(self, package_name):
        # 1. Try finding in desktop_map (Most accurate)
        candidates = [package_name]
        
        # Remove common suffixes/prefixes for mapping lookup
        clean_name = package_name
        for suffix in ["-stable", "-bin", "-git", "-edition", "-core", "-browser"]:
            clean_name = clean_name.replace(suffix, "")
        
        if clean_name != package_name:
            candidates.append(clean_name)

        for cand in candidates:
            if cand in self.desktop_map:
                icon_val = self.desktop_map[cand]
                
                # If it's an absolute path
                if icon_val.startswith("/"):
                    if os.path.exists(icon_val):
                        return QIcon(icon_val)
                
                # If it's a name, try loading from theme
                icon = QIcon.fromTheme(icon_val)
                if not icon.isNull():
                    return icon
                
                # If theme failed, try finding file with that name
                fallback = self._find_fallback_icon(icon_val)
                if fallback:
                    return fallback

        # 2. Try exact theme match
        icon = QIcon.fromTheme(package_name)
        if not icon.isNull():
            return icon
            
        # Try fallback file search for package name
        fallback = self._find_fallback_icon(package_name)
        if fallback:
            return fallback

        # 3. Try heuristics with theme
        if clean_name != package_name:
            icon = QIcon.fromTheme(clean_name)
            if not icon.isNull():
                return icon
            
            # Try fallback file search for clean name
            fallback = self._find_fallback_icon(clean_name)
            if fallback:
                return fallback
                    
        # 4. Fallback to generic
        return QIcon.fromTheme("package-x-generic")

class UninstallWorker(QThread):
    finished = Signal(bool, str) # success, message

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            process = subprocess.Popen(
                self.command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.finished.emit(True, stdout)
            else:
                self.finished.emit(False, stderr or stdout)
                
        except Exception as e:
            self.finished.emit(False, str(e))

class LogDialog(QDialog):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(content)
        layout.addWidget(text_edit)
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

class NumericTableWidgetItem(QTableWidgetItem):
    """Custom Item to sort numbers correctly"""
    def __lt__(self, other):
        try:
            # Sort by raw value stored in UserRole
            my_value = self.data(Qt.UserRole)
            other_value = other.data(Qt.UserRole)
            
            if my_value is not None and other_value is not None:
                return float(my_value) < float(other_value)
                
            # Fallback to text parsing if UserRole is missing
            return float(self.text().split()[0]) < float(other.text().split()[0])
        except Exception:
            # Fallback to string comparison
            return super().__lt__(other)

from concurrent.futures import ThreadPoolExecutor
from system_toolbox.package_manager import PackageInfo

class PackageLoaderThread(QThread):
    data_loaded = Signal(list, dict) # packages, desktop_map
    
    def __init__(self, pkg_manager):
        super().__init__()
        self.pkg_manager = pkg_manager
        
    def parse_desktop_file(self, filepath):
        try:
            filename = os.path.basename(filepath).lower()
            key_filename = filename[:-8] # remove .desktop
            
            icon = None
            exec_name = None
            app_name = None
            startup_class = None
            cmd_path = None
            
            with open(filepath, 'r', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("Icon="):
                        icon = line.split("=", 1)[1].strip()
                        icon = icon.replace('"', '').replace("'", "")
                        if icon.startswith("~"):
                            icon = os.path.expanduser(icon)
                        if not os.path.isabs(icon):
                            base, ext = os.path.splitext(icon)
                            if ext in ['.png', '.svg', '.xpm', '.ico']:
                                icon = base
                    elif line.startswith("Exec="):
                        cmd = line.split("=", 1)[1].strip()
                        cmd = cmd.replace('"', '').replace("'", "")
                        cmd_path = cmd.split()[0]
                        exec_name = os.path.basename(cmd_path).lower()
                    elif line.startswith("Name="):
                        app_name = line.split("=", 1)[1].strip()
                    elif line.startswith("StartupWMClass="):
                        startup_class = line.split("=", 1)[1].strip().lower()
            
            return {
                'filepath': filepath,
                'filename': filename,
                'key_filename': key_filename,
                'icon': icon,
                'exec_name': exec_name,
                'app_name': app_name,
                'startup_class': startup_class,
                'cmd_path': cmd_path
            }
        except Exception:
            return None

    def run(self):
        # 1. List Packages (Subprocess)
        packages = []
        installed_names = set()
        
        if self.pkg_manager:
            packages = self.pkg_manager.list_installed()
            for p in packages:
                installed_names.add(p.name.lower())
                clean = p.name.lower().replace("-stable", "").replace("-bin", "")
                installed_names.add(clean)

        # 2. Scan Desktop Files (Parallel)
        desktop_map = {}
        extra_packages = []
        added_desktop_apps = set()
        
        paths = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            os.path.expanduser("~/.local/share/applications"),
            "/var/lib/snapd/desktop/applications",
            "/var/lib/flatpak/exports/share/applications",
            os.path.expanduser("~/.local/share/flatpak/exports/share/applications")
        ]
        
        all_desktop_files = []
        for path in paths:
            if os.path.exists(path):
                all_desktop_files.extend(glob.glob(os.path.join(path, "*.desktop")))
        
        # Use ThreadPool to parse files in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.parse_desktop_file, all_desktop_files)
            
            for res in results:
                if not res:
                    continue
                    
                # Map Logic
                if res['icon']:
                    if res['key_filename']:
                        desktop_map[res['key_filename']] = res['icon']
                    if res['startup_class']:
                        desktop_map[res['startup_class']] = res['icon']
                    if res['exec_name'] and res['exec_name'] != res['key_filename']:
                        desktop_map[res['exec_name']] = res['icon']
                    if res['app_name'] and res['app_name'].lower() != res['key_filename']:
                        desktop_map[res['app_name'].lower()] = res['icon']

                # App Discovery Logic
                if res['app_name']:
                    display_name = res['app_name']
                else:
                    display_name = res['key_filename'].title()
                    
                norm_name = display_name.lower()
                
                is_installed = False
                if norm_name in installed_names: is_installed = True
                if res['key_filename'] in installed_names: is_installed = True
                if res['exec_name'] and res['exec_name'] in installed_names: is_installed = True
                if display_name in added_desktop_apps: is_installed = True

                if not is_installed:
                    size_mb = 0.0
                    if res['cmd_path'] and os.path.exists(res['cmd_path']):
                            try:
                                size_mb = os.path.getsize(res['cmd_path']) / (1024*1024)
                            except: pass
                    
                    pkg_type = "Desktop App"
                    if "flatpak" in res['filepath']:
                        pkg_type = "Flatpak"
                    elif "snap" in res['filepath']:
                        pkg_type = "Snap"
                    elif res['cmd_path'] and ".AppImage" in res['cmd_path']:
                        pkg_type = "AppImage"
                        
                    pkg = PackageInfo(
                        name=display_name,
                        size_mb=size_mb,
                        version="N/A",
                        type=pkg_type,
                        status="Installed",
                        desktop_file_path=res['filepath'],
                        exec_path=res['cmd_path']
                    )
                    extra_packages.append(pkg)
                    added_desktop_apps.add(display_name)

        # Combine lists
        packages.extend(extra_packages)
            
        self.data_loaded.emit(packages, desktop_map)

class AppsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Get Package Manager
        self.pkg_manager = get_package_manager()
        
        # Placeholder IconLoader (will be updated after thread finishes)
        self.icon_loader = IconLoader(preloaded_map={})

        if self.pkg_manager is None:
            self.layout.addWidget(QLabel("Error: Unsupported distribution. Only Debian/Ubuntu and Fedora/RHEL based systems are supported."))
            return

        # Top Controls Layout
        top_controls = QHBoxLayout()
        self.layout.addLayout(top_controls)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search packages...")
        
        # Debounce timer for search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300) # 300ms delay
        self.search_timer.timeout.connect(self.perform_filter)
        
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        top_controls.addWidget(self.search_bar)

        # Refresh Button (Moved to top right)
        self.refresh_btn = QPushButton("Refresh List")
        self.refresh_btn.setObjectName("primaryBtn") # Use primary style
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.load_packages)
        self.refresh_btn.setFixedWidth(150) # Fixed width for better look
        top_controls.addWidget(self.refresh_btn)
        
        # Packages Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Version", "Size"])
        self.table.setAlternatingRowColors(False) # Clean white look
        self.table.setShowGrid(False) # Cleaner look
        self.table.verticalHeader().setVisible(False) # Hide row numbers
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setIconSize(QSize(32, 32)) # Larger icons
        
        # Style the table to match reference
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            QHeaderView::section {
                background-color: white;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                padding: 12px;
                font-weight: bold;
                color: #9e9e9e;
                text-transform: uppercase;
                font-size: 12px;
            }
        """)
        
        # Column resizing
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch) # Name stretches
        self.table.setColumnWidth(1, 150) # Version fixed
        self.table.setColumnWidth(2, 120) # Size fixed
        
        # Custom Sorting Setup
        self.table.setSortingEnabled(False) # We handle sorting manually
        self.table.horizontalHeader().setSectionsClickable(True)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        # Context Menu for Uninstall
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Default Sort State
        self.current_sort_col = 0 # Name
        self.current_sort_order = Qt.AscendingOrder
        
        self.layout.addWidget(self.table)
        
        # Loading Indicator
        self.loading_label = QLabel("Loading packages... Please wait.")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #666; font-style: italic;")
        self.layout.addWidget(self.loading_label)
        self.loading_label.hide() # Hide initially

        # Initial Load
        self.load_packages()

    def load_packages(self):
        if not self.pkg_manager:
            return

        # UI State for Loading
        self.table.setRowCount(0)
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("Loading...")
        self.loading_label.setText("Scanning system... Please wait.")
        self.loading_label.show()
        
        # Start Thread
        self.loader_thread = PackageLoaderThread(self.pkg_manager)
        self.loader_thread.data_loaded.connect(self.on_data_loaded)
        self.loader_thread.start()

    def on_data_loaded(self, packages, desktop_map):
        # Store full dataset
        self.all_packages = packages
        
        # Update IconLoader
        self.icon_loader = IconLoader(preloaded_map=desktop_map)
        
        # Render all packages initially
        self.render_packages(self.all_packages)

    def render_packages(self, packages_to_render):
        # Reset Table
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)
        self.table.setUpdatesEnabled(False)
        
        # Update label (optional, might not render if we block immediately)
        self.loading_label.setText(f"Processing {len(packages_to_render)} packages...")
        self.loading_label.show()
        
        for i, pkg in enumerate(packages_to_render):
            row_idx = i
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 50) # Reduced height slightly for compactness
            
            # Name Column
            icon = self.icon_loader.get_icon(pkg.name)
            name_item = QTableWidgetItem(pkg.name)
            name_item.setIcon(icon)
            font = name_item.font()
            name_item.setData(Qt.UserRole, pkg) # Store full pkg object
            font.setPointSize(11) # Slightly smaller font
            font.setBold(True)
            name_item.setFont(font)
            self.table.setItem(row_idx, 0, name_item)

            # Version
            self.table.setItem(row_idx, 1, QTableWidgetItem(pkg.version))
            
            # Size
            size_item = NumericTableWidgetItem(f"{pkg.size_mb:.2f} MB")
            size_item.setData(Qt.UserRole, pkg.size_mb) # Store raw float for sorting
            size_item.setForeground(Qt.gray)
            self.table.setItem(row_idx, 2, size_item)

        self.table.setUpdatesEnabled(True)
        self.finish_loading()

    def show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return
            
        row = item.row()
        name_item = self.table.item(row, 0)
        if not name_item:
            return
            
        pkg = name_item.data(Qt.UserRole)
        if not pkg:
            return
            
        menu = QMenu(self)
        
        # Add Uninstall Action
        uninstall_action = QAction("Uninstall", self)
        # Optional: Add icon to menu
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "image", "delete.svg")
        if not os.path.exists(icon_path):
             icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "image", "delete.ico")
             
        if os.path.exists(icon_path):
            uninstall_action.setIcon(QIcon(icon_path))
        else:
            uninstall_action.setIcon(QIcon.fromTheme("user-trash"))
            
        uninstall_action.triggered.connect(lambda: self.confirm_uninstall(pkg))
        menu.addAction(uninstall_action)
        
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def finish_loading(self):
        # Restore UI State
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("Refresh List")
        self.loading_label.hide()
        
        # Apply current sort
        self.table.sortItems(self.current_sort_col, self.current_sort_order)
        self.table.horizontalHeader().setSortIndicator(self.current_sort_col, self.current_sort_order)

    def on_header_clicked(self, logicalIndex):
        # Custom sort logic
        if logicalIndex == 2: # Size Column
            if self.current_sort_col == 2:
                # Toggle
                if self.current_sort_order == Qt.DescendingOrder:
                    self.current_sort_order = Qt.AscendingOrder
                else:
                    self.current_sort_order = Qt.DescendingOrder
            else:
                # Initial sort for Size is Descending (Highest to Lowest)
                self.current_sort_col = 2
                self.current_sort_order = Qt.DescendingOrder
        
        elif logicalIndex == 0: # Name Column
            if self.current_sort_col == 0:
                # Toggle
                if self.current_sort_order == Qt.AscendingOrder:
                    self.current_sort_order = Qt.DescendingOrder
                else:
                    self.current_sort_order = Qt.AscendingOrder
            else:
                # Initial sort for Name is Ascending (A-Z)
                self.current_sort_col = 0
                self.current_sort_order = Qt.AscendingOrder
        
        else:
            # Default for other columns (Version, Controls)
            if self.current_sort_col == logicalIndex:
                 if self.current_sort_order == Qt.AscendingOrder:
                    self.current_sort_order = Qt.DescendingOrder
                 else:
                    self.current_sort_order = Qt.AscendingOrder
            else:
                self.current_sort_col = logicalIndex
                self.current_sort_order = Qt.AscendingOrder

        # Apply Sort
        self.table.sortItems(self.current_sort_col, self.current_sort_order)
        self.table.horizontalHeader().setSortIndicator(self.current_sort_col, self.current_sort_order)

    def on_search_text_changed(self, text):
        # Restart timer on every keystroke
        self.search_timer.start()

    def perform_filter(self):
        text = self.search_bar.text().lower()
        
        if not hasattr(self, 'all_packages'):
            return

        # If we are currently batch loading, we should probably let it finish 
        # or just filter what we have. For simplicity, we filter what is currently in the table.
        # If the table is incomplete (still loading), this might look weird, but it's better than crashing.
        
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0) # Name column
            if not item:
                continue
                
            name = item.text().lower()
            should_show = text in name
            self.table.setRowHidden(row, not should_show)

    def confirm_uninstall(self, pkg):
        package_name = pkg.name
        # Safety Check
        for safe_word in DENYLIST:
            if safe_word in package_name:
                QMessageBox.warning(self, "Safety Warning", f"Cannot uninstall '{package_name}' because it might be a critical system package.")
                return

        msg = f"Are you sure you want to uninstall '{package_name}'?\n"
        if pkg.type in ["Desktop App", "AppImage"]:
            msg += "This will remove the application shortcut and associated files."
        else:
            msg += "This action requires root privileges and will PURGE the package (remove config files)."

        reply = QMessageBox.question(
            self, "Confirm Uninstall", 
            msg,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.run_uninstall(pkg)

    def run_uninstall(self, pkg):
        self.current_uninstall_pkg = pkg.name
        
        # Handle non-system packages (AppImages, Desktop Shortcuts)
        if pkg.type in ["Desktop App", "AppImage"] and pkg.desktop_file_path:
            try:
                # 1. Remove Desktop File
                if os.path.exists(pkg.desktop_file_path):
                    os.remove(pkg.desktop_file_path)
                
                # 2. Remove Executable (Optional/Risky - only if it looks like a standalone file)
                # For AppImages, usually the user wants the file gone.
                if pkg.exec_path and os.path.exists(pkg.exec_path):
                    # Only delete if it's in user home or we are sure?
                    # Let's be careful. If it's an AppImage file, delete it.
                    if ".AppImage" in pkg.exec_path or pkg.type == "AppImage":
                        os.remove(pkg.exec_path)
                
                self.on_uninstall_finished(True, f"Removed desktop file: {pkg.desktop_file_path}")
                return
            except Exception as e:
                self.on_uninstall_finished(False, f"Error removing files: {e}")
                return

        if not self.pkg_manager:
            return

        cmd = self.pkg_manager.uninstall_cmd(pkg.name)
        self.worker = UninstallWorker(cmd)
        self.worker.finished.connect(self.on_uninstall_finished)
        self.worker.start()
        
        # Disable UI temporarily
        self.setEnabled(False)
        self.refresh_btn.setText(f"Uninstalling {pkg.name}...")

    def on_uninstall_finished(self, success, message):
        self.setEnabled(True)
        self.refresh_btn.setText("Refresh List")
        
        if success:
            QMessageBox.information(self, "Success", "Package uninstalled successfully.")
            
            # Optimistic UI update: Remove row without reloading everything
            if hasattr(self, 'current_uninstall_pkg'):
                pkg_name = self.current_uninstall_pkg
                
                # Remove from data source
                if hasattr(self, 'all_packages'):
                    self.all_packages = [p for p in self.all_packages if p.name != pkg_name]
                
                # Remove from Table
                for row in range(self.table.rowCount()):
                    item = self.table.item(row, 0)
                    if item and item.text() == pkg_name:
                        self.table.removeRow(row)
                        break
        else:
            QMessageBox.critical(self, "Error", "Uninstall failed.")
        
        # Show log
        log_dialog = LogDialog("Uninstall Log", message, self)
        log_dialog.exec()
