# MainCodeFile.py v3.0

import sys
import shutil
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QTextEdit, QTabWidget, QListWidget, QAbstractItemView, QProgressBar, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

# Add access to the sorting logic files
sys.path.append(str(Path(__file__).resolve().parent / "file_sorter_code"))
sys.path.append(str(Path(__file__).resolve().parent / "movie_code"))
import file_sorter

# Setup logging
log_file = "gui_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def find_mediasorter_root():
    current = Path(__file__).resolve()
    while current.name != 'MediaSorter':
        current = current.parent
    return current

# Custom QListWidget that handles drag and drop for movies
class MovieListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.main_window = None
    
    def set_main_window(self, main_window):
        self.main_window = main_window
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        if event.mimeData().hasUrls() and self.main_window:
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.main_window.add_movie_files_from_drop(file_paths)
            event.accept()
        else:
            event.ignore()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MediaSorter")
        self.setGeometry(100, 100, 600, 400)
        self.setAcceptDrops(True)

        self.main_folder = find_mediasorter_root()
        self.sorting_folder = self.main_folder / "0.1 Sorting Folder"
        self.sorting_folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize movie files list
        self.movie_files = []
        
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self.create_sort_tab(), "Sort Files")
        self.tabs.addTab(self.create_settings_tab(), "Settings")
        self.tabs.addTab(self.create_logs_tab(), "Logs")
        self.tabs.addTab(self.create_status_tab(), "Status")
        self.tabs.addTab(self.create_movies_tab(), "Movies")

    def create_sort_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        instructions = QLabel("Drag and drop files here or use the 'Add Files' button.")
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

    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        layout.addWidget(QLabel("Settings tab placeholder."))
        return tab

    def create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        layout.addWidget(self.logs_display)
        return tab

    def create_status_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Status tab placeholder."))
        tab.setLayout(layout)
        return tab

    def create_movies_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        instructions = QLabel("Drag and drop movie files here or use the 'Add Files' button.")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Use the built-in custom MovieListWidget from this file
        self.movie_list = MovieListWidget(tab)
        self.movie_list.set_main_window(self)  # Set the main window reference
        layout.addWidget(self.movie_list)

        add_button = QPushButton("Add Movie Files")
        add_button.clicked.connect(self.add_movie_files)
        layout.addWidget(add_button)

        sort_button = QPushButton("Sort Movies")
        sort_button.clicked.connect(self.sort_movies)
        layout.addWidget(sort_button)

        self.movie_progress = QProgressBar()
        self.movie_progress.setValue(0)
        layout.addWidget(self.movie_progress)

        return tab

    def dragEnterEvent(self, event: QDragEnterEvent):
        logging.info("Main Window Drag Enter Event Triggered")
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
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
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files")
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
                file_sorter.process_files([str(file)])
                self.progress_bar.setValue(idx)
                sorted_count += 1
                self.log_action(f"Processed file: {file.name}")
            except Exception as e:
                self.log_action(f"Error processing {file.name}: {e}")

        self.log_action(f"Sorting complete. Total files: {total_files}, Successfully sorted: {sorted_count}.")

    def add_movie_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Movie Files")
        if file_paths:
            self.add_movie_files_from_drop(file_paths)

    def add_movie_files_from_drop(self, file_paths):
        """Process movie files that were dropped into the list widget"""
        for file_path in file_paths:
            path = Path(file_path)
            if path.is_file():
                self.movie_files.append(str(path))  # Store the full path as string
                self.movie_list.addItem(path.name)  # Show only filename in list
        
        self.log_action(f"Added {len(file_paths)} movie files for sorting")

    def sort_movies(self):
        movie_folder = self.main_folder / "Movies"
        movie_folder.mkdir(exist_ok=True)
        
        total_movies = len(self.movie_files)
        if total_movies == 0:
            self.log_action("No movie files to sort.")
            return

        self.movie_progress.setMaximum(total_movies)
        sorted_count = 0
        
        # Import the sort_movie function here to avoid circular imports
        from movie_handler import sort_movie
        
        for idx, file_path in enumerate(self.movie_files, start=1):
            try:
                path = Path(file_path)
                if path.exists() and path.is_file():
                    # Call the sort_movie function
                    if sort_movie(path, movie_folder):
                        sorted_count += 1
                        self.log_action(f"Sorted movie: {path.name}")
                    else:
                        self.log_action(f"Failed to sort movie: {path.name}")
                else:
                    self.log_action(f"Movie file not found: {file_path}")
            except Exception as e:
                self.log_action(f"Error sorting movie {Path(file_path).name}: {e}")
            
            self.movie_progress.setValue(idx)
        
        # Clear the list after sorting
        self.movie_list.clear()
        self.movie_files = []
        self.log_action(f"Movie sorting complete. Sorted {sorted_count} of {total_movies} movies.")

    def log_action(self, message):
        self.logs_display.append(message)
        logging.info(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())