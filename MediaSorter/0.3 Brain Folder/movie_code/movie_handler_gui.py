# movie_handler_gui.py - v1.0

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QTabWidget, QListWidget, QAbstractItemView, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from pathlib import Path
import shutil
import logging
import movie_handler
from GUI_addons import gui_addon_test  # Import movie logic

# Configure logging
log_file = "movie_gui_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class moviehandlerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("movie handler Application")
        self.setGeometry(150, 150, 600, 400)
        self.setAcceptDrops(True)

        self.main_folder = Path(__file__).resolve().parent.parent
        self.sorting_folder = self.main_folder / "0.1 Sorting Folder"
        self.sorting_folder.mkdir(parents=True, exist_ok=True)

        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self.create_sort_tab(), "Sort Movies")
        self.tabs.addTab(self.create_logs_tab(), "Logs")

    def create_sort_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        instructions = QLabel("Drag and drop movie files here or use the 'Add Files' button.")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        self.file_list = QListWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.setDragDropMode(QAbstractItemView.DropOnly)
        self.file_list.setAlternatingRowColors(True)
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.file_list)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        add_files_button = QPushButton("Add Files")
        add_files_button.clicked.connect(self.add_files)
        layout.addWidget(add_files_button)

        sort_button = QPushButton("Sort Now")
        sort_button.clicked.connect(self.sort_files)
        layout.addWidget(sort_button)

        return tab

    def create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        layout.addWidget(self.logs_display)

        return tab

    def dragEnterEvent(self, event: QDragEnterEvent):
        logging.info("Drag Enter Event Triggered")
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        logging.info("Drop Event Triggered")
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
        from PyQt5.QtWidgets import QFileDialog
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Movie Files")
        for file_path in file_paths:
            if Path(file_path).is_file():
                destination = self.sorting_folder / Path(file_path).name
                shutil.move(file_path, str(destination))
                self.log_action(f"Moved file to sorting folder: {destination}")

    def sort_files(self):
        file_list = list(self.sorting_folder.iterdir())
        total_files = len(file_list)
        if total_files == 0:
            self.log_action("No files to sort.")
            return

        self.progress_bar.setMaximum(total_files)
        sorted_count = 0

        for idx, file in enumerate(file_list, start=1):
            try:
                movie_handler.sort_movie(file, self.main_folder / "Movies")
                self.progress_bar.setValue(idx)
                sorted_count += 1
                self.log_action(f"Processed file: {file.name}")
            except Exception as e:
                self.log_action(f"Error processing {file.name}: {e}")

        self.log_action(f"Sorting complete. Total files: {total_files}, Successfully sorted: {sorted_count}.")

    def log_action(self, message):
        self.logs_display.append(message)
        logging.info(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MovieSorterApp()
    main_window.show()
    sys.exit(app.exec_())
