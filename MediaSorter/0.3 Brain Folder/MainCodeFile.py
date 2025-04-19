# MainCodeFile.py v4.1

import sys
import shutil
import logging
import re  # Added missing import for regex
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QTextEdit, QTabWidget, QListWidget, QAbstractItemView, QProgressBar, QFileDialog,
    QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

# Add access to the sorting logic files
sys.path.append(str(Path(__file__).resolve().parent / "file_sorter_code"))
sys.path.append(str(Path(__file__).resolve().parent / "movie_code"))
import file_sorter
from settings.settings_manager import get_settings_widget

# LOGGING SETUP:
# Configures logging to write to gui_log.txt
log_file = "gui_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# UTILITY FUNCTION:
# Finds the root directory of the MediaSorter application
def find_mediasorter_root():
    current = Path(__file__).resolve()
    while current.name != 'MediaSorter':
        current = current.parent
        
    return current

# CUSTOM WIDGET CLASS:
# Custom QListWidget with drag-and-drop functionality for files
class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.main_window = None
        self.file_paths = []  # Store actual file paths

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
            self.add_files(file_paths)
            event.accept()
        else:
            event.ignore()
    
    def add_files(self, file_paths):
        for file_path in file_paths:
            path = Path(file_path)
            if path.is_file():
                self.file_paths.append(str(path))
                self.addItem(path.name)

# CUSTOM WIDGET CLASS:
# Custom QListWidget with drag-and-drop functionality for movie files
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

# MAIN WINDOW CLASS:
# The primary application window containing all UI elements and functionality
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

    # UI INITIALIZATION:
    # Creates the main UI components and tab structure
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.tabs = QTabWidget()
        # --- Status Tab ---
        self.status_tab = QWidget()
        self.status_layout = QVBoxLayout()

        self.status_label = QLabel("Loading status...")
        self.status_layout.addWidget(self.status_label)

        self.status_tab.setLayout(self.status_layout)
        self.tabs.addTab(self.status_tab, "Status")

        self.update_status_tab()

        layout.addWidget(self.tabs)

        self.tabs.addTab(self.create_sort_tab(), "Sort Files")
        self.tabs.addTab(self.create_settings_tab(), "Settings")
        self.tabs.addTab(self.create_logs_tab(), "Logs")
        self.tabs.addTab(self.create_status_tab(), "Status")
        self.tabs.addTab(self.create_movies_tab(), "Movies")

    # STATUS TAB FUNCTIONALITY:
    # Updates the status tab with information from the log file
    def update_status_tab(self):
        log_path = Path("file_sorter_log.txt")
        total, sorted_count, unsorted_count, last_file = 0, 0, 0, "N/A"

        if log_path.exists():
            lines = log_path.read_text(encoding="utf-8").splitlines()
            for line in lines:
                if "Processing:" in line:
                    total += 1
                    last_match = re.search(r"Processing: (.+?)$", line)
                    if last_match:
                        last_file = last_match.group(1)
                if "Successfully moved" in line:
                    sorted_count += 1
                if "Failed to move" in line:
                    unsorted_count += 1

        status_msg = f"Total Files Processed: {total}\nSorted: {sorted_count}\nUnsorted: {unsorted_count}\nLast File: {last_file}"
        self.status_label.setText(status_msg)

    # SORT TAB CREATION:
    # Creates the "Sort Files" tab for sorting general media files
    def create_sort_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        instructions = QLabel("Drag and drop files here or use the 'Add Files' button.")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Use the custom FileListWidget
        self.file_list = FileListWidget()
        self.file_list.set_main_window(self)
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

    # SETTINGS TAB CREATION:
    # Creates the settings tab (currently a placeholder)
    def create_settings_tab(self):
        return get_settings_widget()

    # LOGS TAB CREATION:
    # Creates the logs tab that displays application logs
    def create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        layout.addWidget(self.logs_display)
        return tab

    # STATUS TAB CREATION:
    # Creates another status tab (seems to be duplicated in the code)
    def create_status_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Status tab placeholder."))
        tab.setLayout(layout)
        return tab

    # MOVIES TAB CREATION:
    # Creates the tab for handling movie files specifically
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

    # DRAG AND DROP EVENT HANDLING:
    # Handles files dragged into the main window
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

    # FILE HANDLING METHODS:
    # Methods for adding and sorting general files
    def add_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if file_paths:
            self.file_list.add_files(file_paths)
            self.log_action(f"Added {len(file_paths)} files to the list")

    # Updated sort_files method to process files in the GUI list
    def sort_files(self):
        file_paths = self.file_list.file_paths
        if not file_paths:
            QMessageBox.information(self, "No Files", "No files to sort. Please add files first.")
            return

        total_files = len(file_paths)
        self.progress_bar.setMaximum(total_files)
        self.log_action(f"Starting to sort {total_files} files...")

        try:
            # Import the button sorter
            from file_sorter_code.file_sorter_button import process_gui_files
            
            # First, get the current settings
            from settings.settings_toggle_switch import get_season_folder_path
            sorting_path = get_season_folder_path()
            
            # Log where we're sorting to
            if sorting_path != "0.1 Sorting Folder":
                self.log_action(f"Using custom sorting folder: {sorting_path}")
            else:
                self.log_action("Using default sorting folder")

            # Update progress callback
            def update_progress(current, total, message):
                self.progress_bar.setValue(current)
                self.log_action(message)

            # Process the files
            total, sorted_count, unsorted_count = process_gui_files(file_paths, update_progress)
            
            # Clear the list after sorting
            self.file_list.clear()
            self.file_list.file_paths = []
            
            # Show results
            self.log_action(f"Sorting complete. Total: {total}, Sorted: {sorted_count}, Unsorted: {unsorted_count}")
            QMessageBox.information(
                self, 
                "Sorting Complete", 
                f"Successfully processed {total} files.\n"
                f"Sorted: {sorted_count}\n"
                f"Unsorted: {unsorted_count}"
            )
            
            # Update the status tab
            self.update_status_tab()
            
        except Exception as e:
            self.log_action(f"Error during sorting: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while sorting files: {e}")

    # MOVIE HANDLING METHODS:
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

    # LOGGING METHOD:
    # Adds messages to the log display and logs to file
    def log_action(self, message):
        self.logs_display.append(message)
        logging.info(message)

# APPLICATION ENTRY POINT:
# Creates and runs the application when the script is executed directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())