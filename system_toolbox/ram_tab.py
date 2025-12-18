from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QTableWidget, 
    QTableWidgetItem, QHeaderView, QHBoxLayout, QMenu, QMessageBox
)
from PySide6.QtCore import QTimer, QThread, Signal, Qt, QPoint
from PySide6.QtGui import QAction
from system_toolbox.system_info import get_ram_usage, get_process_list
import os
import signal

class ProcessWorker(QThread):
    finished = Signal(list)

    def run(self):
        data = get_process_list()
        self.finished.emit(data)

class RamTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(15, 15, 15, 15)

        # RAM Usage Section
        self.ram_label = QLabel("RAM Usage: ...")
        self.ram_label.setObjectName("headerLabel")
        self.ram_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.ram_label)

        self.ram_progress = QProgressBar()
        self.ram_progress.setAlignment(Qt.AlignCenter)
        self.ram_progress.setFixedHeight(25)
        self.layout.addWidget(self.ram_progress)

        # Process Table
        self.layout.addSpacing(10)
        lbl_proc = QLabel("Top Processes by Memory:")
        lbl_proc.setObjectName("subHeaderLabel")
        self.layout.addWidget(lbl_proc)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PID", "Name", "Memory %", "Memory (MB)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        
        # Context Menu Setup
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.layout.addWidget(self.table)

        # Timer for auto-refresh
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(3000) # 3 seconds

        # Initial load
        self.refresh_data()

    def refresh_data(self):
        # Update RAM usage (fast, main thread is fine)
        ram = get_ram_usage()
        total_gb = ram['total'] / (1024**3)
        used_gb = ram['used'] / (1024**3)
        self.ram_label.setText(f"RAM: {used_gb:.2f} GB / {total_gb:.2f} GB ({ram['percent']}%)")
        self.ram_progress.setValue(int(ram['percent']))
        
        # Color coding for RAM
        if ram['percent'] > 90:
            self.ram_progress.setStyleSheet("QProgressBar::chunk { background-color: #d9534f; }")
        elif ram['percent'] > 70:
            self.ram_progress.setStyleSheet("QProgressBar::chunk { background-color: #f0ad4e; }")
        else:
            self.ram_progress.setStyleSheet("QProgressBar::chunk { background-color: #5cb85c; }")

        # Update Process List (slow, use thread)
        self.worker = ProcessWorker()
        self.worker.finished.connect(self.update_table)
        self.worker.start()

    def update_table(self, processes):
        # Save current scroll position
        current_scroll = self.table.verticalScrollBar().value()
        
        # Save current selection if any
        selected_pids = set()
        for item in self.table.selectedItems():
            # Only track selection by PID (column 0)
            if item.column() == 0:
                selected_pids.add(item.text())

        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)

        # Show top 50 processes
        target_count = min(len(processes), 50)
        current_count = self.table.rowCount()
        
        # 1. Update/Add rows
        for row_idx in range(target_count):
            proc = processes[row_idx]
            
            if row_idx >= current_count:
                self.table.insertRow(row_idx)
                # Create items if new row
                self.table.setItem(row_idx, 0, QTableWidgetItem())
                self.table.setItem(row_idx, 1, QTableWidgetItem())
                self.table.setItem(row_idx, 2, QTableWidgetItem())
                self.table.setItem(row_idx, 3, QTableWidgetItem())
                
                # Alignments for numeric columns
                self.table.item(row_idx, 2).setTextAlignment(Qt.AlignCenter)
                self.table.item(row_idx, 3).setTextAlignment(Qt.AlignCenter)

            # Update Data
            self.table.item(row_idx, 0).setText(str(proc['pid']))
            self.table.item(row_idx, 1).setText(proc['name'])
            self.table.item(row_idx, 2).setText(f"{proc['memory_percent']:.2f}%")
            
            mem_mb = proc['memory_rss'] / (1024**2)
            self.table.item(row_idx, 3).setText(f"{mem_mb:.2f} MB")
            
            # Restore selection
            if str(proc['pid']) in selected_pids:
                self.table.selectRow(row_idx)

        # 2. Remove extra rows
        while self.table.rowCount() > target_count:
            self.table.removeRow(self.table.rowCount() - 1)

        self.table.setUpdatesEnabled(True)
        
        # Restore scroll position (if it changed unexpectedly, though sync usually keeps it)
        # We only set it if the count is sufficient to support the old scroll
        if self.table.rowCount() > 0:
             self.table.verticalScrollBar().setValue(current_scroll)

    def show_context_menu(self, pos: QPoint):
        item = self.table.itemAt(pos)
        if item is None:
            return
            
        row = item.row()
        pid_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        
        if not pid_item or not name_item:
            return
            
        pid = pid_item.text()
        name = name_item.text()
        
        menu = QMenu(self.table)
        kill_action = QAction(f"Kill Process {pid} ({name})", self)
        kill_action.triggered.connect(lambda: self.kill_process(pid, name))
        menu.addAction(kill_action)
        
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def kill_process(self, pid_str, name):
        try:
            pid = int(pid_str)
            
            reply = QMessageBox.question(
                self, "Confirm Kill", 
                f"Are you sure you want to kill process '{name}' (PID: {pid})?\nUnsaved data may be lost.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                os.kill(pid, signal.SIGKILL)
                QMessageBox.information(self, "Success", f"Process {pid} killed.")
                self.refresh_data() # Refresh immediately
                
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid PID.")
        except ProcessLookupError:
            QMessageBox.warning(self, "Error", "Process not found (already terminated?).")
        except PermissionError:
            QMessageBox.warning(self, "Error", "Permission denied. You may need root privileges to kill this process.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to kill process: {e}")
