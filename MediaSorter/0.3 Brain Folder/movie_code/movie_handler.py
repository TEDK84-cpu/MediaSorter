# movie_handler.py v3.0

import os
import logging
from pathlib import Path

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
        return False

    name, year = parse_movie_name(file_path.name)
    if year:  # Include year only if it exists
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
        return True
    except Exception as e:
        logging.error(f"Failed to move {file_path} to {destination}: {e}")
        return False

if __name__ == "__main__":
    # Example usage for testing
    test_file = "Harlock Space Pirate 2013.mkv"
    test_movies_folder = "Sorted Movies"
    sort_movie(test_file, test_movies_folder)