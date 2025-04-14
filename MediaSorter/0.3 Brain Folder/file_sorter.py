import os
import shutil
import logging
from pathlib import Path
import re
from time import sleep

# Configure logging
log_file = "file_sorter_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define folders
main_folder = Path(__file__).resolve().parent.parent
sorting_folder = main_folder / "0.1 Sorting Folder"
unsorted_folder = main_folder / "0.2 Unsorted Folder"

# Ensure necessary folders exist
for folder in [sorting_folder, unsorted_folder]:
    folder.mkdir(parents=True, exist_ok=True)

logging.info("Folders verified.")

def process_files(file_paths):
    """Process a list of file paths and sort them."""
    total_files = len(file_paths)
    sorted_files = 0
    unsorted_files = 0

    print("Starting file processing...")  # Real-time progress feedback

    for idx, file_path in enumerate(file_paths, start=1):
        file = Path(file_path)
        try:
            if not file.is_file():
                logging.warning(f"Skipped: {file} is not a file.")
                print(f"[{idx}/{total_files}] Skipped: {file.name} is not a file.")
                continue

            logging.info(f"Processing file: {file.name}")
            print(f"[{idx}/{total_files}] Processing: {file.name}")
            sleep(0.1)  # Simulate processing time

            # Match for TV shows
            match = re.match(r"(.+?)[\s._-]*(?:S(\d{2})[\s._-]*E(\d{2})|Season[\s]*(\d+)[\s]*Episode[\s]*(\d+))", file.name, re.IGNORECASE)
            if match:
                series_name = match.group(1)
                season = match.group(2) or match.group(4)
                episode = match.group(3) or match.group(5)

                # Normalize series name
                series_name = re.sub(r"[._-]+", " ", series_name).strip()

                # Create target folders
                series_folder = main_folder / series_name
                season_folder = series_folder / f"Season {season.zfill(2)}"
                season_folder.mkdir(parents=True, exist_ok=True)

                # Standardize filename
                standardized_name = f"{series_name} - S{season.zfill(2)}E{episode.zfill(2)}{file.suffix}"
                destination = season_folder / standardized_name

                if not destination.exists():
                    shutil.move(str(file), str(destination))
                    logging.info(f"Moved {file.name} to {destination}")
                    print(f"Moved: {file.name} to {destination}")
                    sorted_files += 1
                else:
                    move_to_unsorted(file, "Duplicate file.")
                    unsorted_files += 1
                continue

            # If no match, move to unsorted
            logging.warning(f"Filename format not recognized: {file.name}")
            print(f"[{idx}/{total_files}] Unrecognized format: {file.name}")
            move_to_unsorted(file, "Unrecognized format.")
            unsorted_files += 1

        except Exception as e:
            logging.error(f"Unexpected error with file {file.name}: {e}")
            print(f"[{idx}/{total_files}] Error: {e}")
            move_to_unsorted(file, "Processing error.")
            unsorted_files += 1

    # Log summary
    logging.info(f"Processing complete. Total files: {total_files}, Sorted: {sorted_files}, Unsorted: {unsorted_files}.")
    print(f"Processing complete. Total files: {total_files}, Sorted: {sorted_files}, Unsorted: {unsorted_files}.")

def move_to_unsorted(file, reason):
    """Move a file to the unsorted folder with a reason."""
    try:
        destination = unsorted_folder / file.name
        shutil.move(str(file), str(destination))
        logging.info(f"Moved {file.name} to Unsorted Folder: {destination} (Reason: {reason})")
        print(f"Moved {file.name} to Unsorted Folder: {destination} (Reason: {reason})")
    except Exception as e:
        logging.error(f"Failed to move {file.name} to Unsorted Folder: {e}")
        print(f"Failed to move {file.name} to Unsorted Folder: {e}")

if __name__ == "__main__":
    # If running directly, process files in the sorting folder
    file_list = list(sorting_folder.iterdir())
    process_files([str(file) for file in file_list])
