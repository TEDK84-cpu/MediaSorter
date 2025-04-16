# GUI Add-on Framework Test

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt
from status import status_checker

def add_status_tab(main_window):
    """Add a Status tab to the main GUI."""
    tab = QWidget()
    layout = QVBoxLayout()
    tab.setLayout(layout)

    # Status display area
    status_container = QWidget()
    status_layout = QVBoxLayout()
    status_container.setLayout(status_layout)
    layout.addWidget(status_container)

    # Refresh button
    refresh_button = QPushButton("Refresh Status")
    layout.addWidget(refresh_button)

    def create_status_item(file_name, status):
        """Create a single status item with a visual indicator."""
        item_layout = QHBoxLayout()

        # Add visual indicator
        color = QColor("green") if status == "Working Properly" else QColor("red")
        pixmap = QPixmap(20, 20)
        pixmap.fill(color)
        indicator = QLabel()
        indicator.setPixmap(pixmap)
        item_layout.addWidget(indicator)

        # Add text description
        description = QLabel(f"{file_name}: {status}")
        item_layout.addWidget(description)

        # Align items
        item_layout.addStretch()
        status_widget = QWidget()
        status_widget.setLayout(item_layout)
        return status_widget

    def refresh_status():
        """Refresh and display the status report."""
        status_report = status_checker.check_status()

        # Clear existing status items
        for i in reversed(range(status_layout.count())):
            widget = status_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Populate status items
        for folder, files in status_report.items():
            folder_label = QLabel(f"Folder: {folder or 'Root'}")
            folder_label.setStyleSheet("font-weight: bold;")
            status_layout.addWidget(folder_label)

            for file, status in files.items():
                status_item = create_status_item(file, status)
                status_layout.addWidget(status_item)

            status_layout.addSpacing(10)

        # Log the status
        status_checker.log_status(status_report)

    refresh_button.clicked.connect(refresh_status)

    # Add the tab to the main window's tab widget
    main_window.tabs.addTab(tab, "Status")

    # Initial status display
    refresh_status()

if __name__ == "__main__":
    print("This module is designed to be imported into file_sorter_gui.py.")
