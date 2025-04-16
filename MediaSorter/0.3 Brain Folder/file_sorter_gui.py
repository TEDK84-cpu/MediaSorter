# file_sorter_gui.py v1.0

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QTabWidget, QListWidget, QAbstractItemView, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
import logging
from pathlib import Path
import shutil
import file_sorter  # Import file_sorter for processing logic
from GUI_addons import gui_addon_test

# Configure logging for GUI
log_file = "gui_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
class FileSorterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Sorter Application")
        self.setGeometry(100, 100, 600, 400)
        self.setAcceptDrops(True)  # Enable drag-and-drop for the main window

        # Define sorting folder relative to the main MediaSorter directory
        self.main_folder = Path(__file__).resolve().parent.parent  # Adjust to main MediaSorter directory
        self.sorting_folder = self.main_folder / "0.1 Sorting Folder"
        self.sorting_folder.mkdir(parents=True, exist_ok=True)

        logging.info(f"Sorting folder initialized at: {self.sorting_folder}")
        if not self.sorting_folder.exists():
            logging.error(f"Failed to initialize sorting folder at: {self.sorting_folder}")

        self.initUI()

        # Add Status tab from GUI Add-ons
        if hasattr(gui_addon_test, 'add_status_tab'):
            gui_addon_test.add_status_tab(self)
        else:
            logging.error("add_status_tab method not found in gui_addon_test.")

        if hasattr(gui_addon_test, 'add_movie_sorting_tab'):
            gui_addon_test.add_movie_sorting_tab(self)
        else:
            logging.error("add_movie_sorting_tab method not found in gui_addon_test.")

    def initUI(self):
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Tabs for different features
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(self.create_sort_tab(), "Sort Files")
        self.tabs.addTab(self.create_settings_tab(), "Settings")
        self.tabs.addTab(self.create_logs_tab(), "Logs")

    def create_sort_tab(self):
        """Tab for sorting files."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Instructions
        instructions = QLabel("Drag and drop files here or use the 'Add Files' button.")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Drag-and-Drop Area
        self.file_list = QListWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.setDragDropMode(QAbstractItemView.DropOnly)
        self.file_list.setAlternatingRowColors(True)
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.file_list)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Add Files Button
        add_files_button = QPushButton("Add Files")
        add_files_button.clicked.connect(self.add_files)
        layout.addWidget(add_files_button)

        # Sort Now button
        sort_button = QPushButton("Sort Now")
        sort_button.clicked.connect(self.sort_files)
        layout.addWidget(sort_button)

        return tab

    def create_settings_tab(self):
        """Tab for managing settings."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Basic settings placeholder
        layout.addWidget(QLabel("Settings will allow you to configure custom sorting rules."))
        layout.addWidget(QLabel("For example: Enable file type filtering, duplicate handling, etc."))

        return tab

    def create_logs_tab(self):
        """Tab for viewing logs."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Logs display
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        layout.addWidget(self.logs_display)

        return tab

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for the main window."""
        logging.info("Main Window Drag Enter Event Triggered")
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event for the main window."""
        logging.info("Main Window Drop Event Triggered")
        for url in event.mimeData().urls():
            file_path = Path(url.toLocalFile())
            try:
                if file_path.is_file():
                    destination = self.sorting_folder / file_path.name
                    shutil.move(str(file_path), str(destination))
                    self.log_action(f"Moved file to sorting folder: {destination}")

                elif file_path.is_dir():
                    for item in file_path.iterdir():
                        dest = self.sorting_folder / item.name
                        shutil.move(str(item), str(dest))
                        self.log_action(f"Moved file from folder to sorting folder: {dest}")
                else:
                    self.log_action(f"Skipped unsupported item: {file_path}")

            except Exception as e:
                self.log_action(f"Error moving {file_path}: {e}")

    def add_files(self):
        """Fallback to add files manually."""
        from PyQt5.QtWidgets import QFileDialog
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        for file_path in file_paths:
            if Path(file_path).is_file():
                destination = self.sorting_folder / Path(file_path).name
                shutil.move(file_path, str(destination))
                self.log_action(f"Moved file to sorting folder: {destination}")

    def sort_files(self):
        """Pass files in sorting folder to file_sorter for processing."""
        file_list = list(self.sorting_folder.iterdir())
        total_files = len(file_list)
        if total_files == 0:
            self.log_action("No files to sort.")
            return

        self.progress_bar.setMaximum(total_files)
        sorted_count = 0

        for idx, file in enumerate(file_list, start=1):
            try:
                file_sorter.process_files([str(file)])
                self.progress_bar.setValue(idx)
                sorted_count += 1
                self.log_action(f"Processed file: {file.name}")
            except Exception as e:
                self.log_action(f"Error processing {file.name}: {e}")

        self.log_action(f"Sorting complete. Total files: {total_files}, Successfully sorted: {sorted_count}.")

    def log_action(self, message):
        """Log actions to the logs tab and log file."""
        self.logs_display.append(message)
        logging.info(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = FileSorterApp()
    main_window.show()
    sys.exit(app.exec_())
