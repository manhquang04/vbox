from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QProgressBar, QPushButton, QHBoxLayout, 
    QLabel, QCheckBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from system_toolbox.system_info import get_disk_usage
import os

def is_system_mount(partition):
    """
    Returns True if the partition is likely a system/loop/snap mount.
    """
    mountpoint = partition["mountpoint"]
    device = partition["device"]
    fstype = partition.get("fstype", "")

    # Filter loop devices
    if "loop" in device:
        return True
    
    # Filter snap mounts
    if "/snap/" in mountpoint or "/var/lib/snapd" in mountpoint:
        return True
        
    # Filter docker/overlay
    if "docker" in mountpoint or "overlay" in mountpoint:
        return True

    # Filter common system tmpfs/dev mounts if they show up (psutil usually handles some, but not all)
    if mountpoint.startswith("/run") or mountpoint.startswith("/sys") or mountpoint.startswith("/proc"):
        return True
        
    return False

class NumericTableWidgetItem(QTableWidgetItem):
    """Custom Item to sort numbers correctly"""
    def __lt__(self, other):
        try:
            # Remove " GB" or "%" to parse float
            text_self = self.text().replace(" GB", "").replace("%", "")
            text_other = other.text().replace(" GB", "").replace("%", "")
            return float(text_self) < float(text_other)
        except ValueError:
            return super().__lt__(other)

class DiskTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(15, 15, 15, 15)
        


        # 2. Controls Section
        self.controls_layout = QHBoxLayout()
        
        self.chk_show_all = QCheckBox("Show system/loop mounts")
        self.chk_show_all.stateChanged.connect(self.load_data)
        self.controls_layout.addWidget(self.chk_show_all)
        
        self.controls_layout.addStretch()
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setObjectName("primaryBtn")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.load_data)
        self.controls_layout.addWidget(self.btn_refresh)
        
        self.layout.addLayout(self.controls_layout)

        # 3. Table Section
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Device", "Mountpoint", "Total", "Used", "Free", "Usage %"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        
        # Column resizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Device
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Mountpoint stretches
        header.setSectionResizeMode(5, QHeaderView.Fixed)            # Usage % fixed width
        self.table.setColumnWidth(5, 200) # Wider for better progress bar

        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Increase row height for better spacing
        self.table.verticalHeader().setDefaultSectionSize(50)
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding-left: 10px;
                padding-right: 10px;
                border-bottom: 1px solid #f5f5f5;
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
                color: #757575;
                text-transform: uppercase;
                font-size: 12px;
            }
        """)
        
        self.layout.addWidget(self.table)

        # Load initial data
        self.load_data()

    def load_data(self):
        # Disable sorting while updating to prevent jumping
        self.table.setSortingEnabled(False)
        
        data = get_disk_usage()
        self.table.setRowCount(0)
        

        
        # Filter data
        show_all = self.chk_show_all.isChecked()
        filtered_data = []
        for disk in data:
            if show_all or not is_system_mount(disk):
                filtered_data.append(disk)
        
        # Custom Sort for Display (Root first, then Home, etc.)
        # We assign a priority score for sorting
        def sort_key(d):
            mp = d["mountpoint"]
            if mp == "/": return 0
            if mp == "/home": return 1
            if mp == "/boot": return 2
            if mp == "/boot/efi": return 3
            return 4 # Others
            
        filtered_data.sort(key=sort_key)
        
        # Populate Table
        for row_idx, disk in enumerate(filtered_data):
            self.table.insertRow(row_idx)
            
            # Helper to format bytes to GB
            def to_gb(bytes_val):
                return f"{bytes_val / (1024**3):.2f} GB"

            # Device
            item_device = QTableWidgetItem(disk["device"])
            self._set_tooltip(item_device, disk)
            self.table.setItem(row_idx, 0, item_device)
            
            # Mountpoint
            item_mount = QTableWidgetItem(disk["mountpoint"])
            self._set_tooltip(item_mount, disk)
            self.table.setItem(row_idx, 1, item_mount)
            
            # Numeric Columns (Right Aligned)
            self._add_numeric_item(row_idx, 2, to_gb(disk["total"]), disk)
            self._add_numeric_item(row_idx, 3, to_gb(disk["used"]), disk)
            self._add_numeric_item(row_idx, 4, to_gb(disk["free"]), disk)
            
            # Usage % Progress Bar
            progress_container = QWidget()
            progress_layout = QHBoxLayout(progress_container)
            progress_layout.setContentsMargins(10, 5, 10, 5)
            progress_layout.setAlignment(Qt.AlignCenter)
            
            progress = QProgressBar()
            percent = disk["percent"]
            progress.setValue(int(percent))
            progress.setAlignment(Qt.AlignCenter)
            progress.setFixedHeight(20)
            
            # Color Coding
            if percent > 90:
                color = "#ef5350" # Red
            elif percent > 75:
                color = "#ffa726" # Orange
            else:
                color = "#66bb6a" # Green
                
            progress.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    background-color: #f5f5f5;
                    border-radius: 10px;
                    text-align: center;
                    color: #424242;
                    font-weight: bold;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 10px;
                }}
            """)
            
            progress_layout.addWidget(progress)
            self.table.setCellWidget(row_idx, 5, progress_container)

        # Re-enable sorting
        self.table.setSortingEnabled(True)



    def _add_numeric_item(self, row, col, text, disk_data):
        item = NumericTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._set_tooltip(item, disk_data)
        self.table.setItem(row, col, item)

    def _set_tooltip(self, item, disk):
        tooltip = (
            f"Device: {disk['device']}\n"
            f"Mountpoint: {disk['mountpoint']}\n"
            f"Filesystem: {disk.get('fstype', 'Unknown')}\n"
            f"Options: {disk.get('opts', 'Unknown')}"
        )
        item.setToolTip(tooltip)
