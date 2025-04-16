# movie_handler.py v1.3

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QTabWidget, QListWidget, QAbstractItemView, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
import os
from pathlib import Path
import logging

# Configure logging
log_file = "movie_sorter_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def parse_movie_name(file_name):
    """Extract movie name and year from the file name."""
    import re

    # Default values
    name, year = "Unknown", ""

    # Regex pattern to match movie name and year
    match = re.search(r"^(.*?)(?:\.|\s|-)?(\d{4})(?:\.|\s|$|_)", file_name)
    if match:
        name = match.group(1).strip().replace('.', ' ').replace('_', ' ')
        year = f"({match.group(2)})"  # Format year in brackets
    else:
        # Handle files without a clear year
        name = file_name.rsplit(".", 1)[0].replace('.', ' ').replace('_', ' ').strip()

    # Clean up name to remove trailing dashes or extra spaces
    name = re.sub(r"[-\s]+$", "", name)

    return name, year

def sort_movie(file_path, movies_folder):
    """Sort a movie file into the appropriate folder and format the filename."""
    file_path = Path(file_path)
    if not file_path.is_file():
        logging.warning(f"Invalid file path: {file_path}")
        return

    name, year = parse_movie_name(file_path.name)
    if year:
        movie_folder = Path(movies_folder) / f"{name} {year}"
        formatted_name = f"{name} {year}{file_path.suffix}"
    else:
        movie_folder = Path(movies_folder) / f"{name}"
        formatted_name = f"{name}{file_path.suffix}"

    movie_folder.mkdir(parents=True, exist_ok=True)

    destination = movie_folder / formatted_name
    try:
        file_path.rename(destination)
        logging.info(f"Moved {file_path} to {destination}")
    except Exception as e:
        logging.error(f"Failed to move {file_path} to {destination}: {e}")

def add_movie_sorting_tab(main_window):
    """Add a Movie Sorting tab to the main GUI."""
    tab = QWidget()
    layout = QVBoxLayout()
    tab.setLayout(layout)

    label = QLabel("Drag and drop movies here for sorting.")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    sort_button = QPushButton("Sort Now")
    layout.addWidget(sort_button)

    def sort_movies():
        movie_folder = main_window.main_folder / "0.1 Sorting Folder"
        movies_folder = main_window.main_folder / "Movies"

        for file in movie_folder.iterdir():
            if file.is_file():
                sort_movie(file, movies_folder)
                print(f"Sorted {file.name} into {movies_folder}")

    sort_button.clicked.connect(sort_movies)

    main_window.tabs.addTab(tab, "Movies")

if __name__ == "__main__":
    print("This module is designed to be imported by the main app.")
