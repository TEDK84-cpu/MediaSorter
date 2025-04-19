# file_sorter_button.py v1.1
# Handles sorting files from the GUI list widget when the Sort button is clicked
# Updated to properly use custom sorting folder settings

import os
import shutil
import logging
import re
from pathlib import Path
from settings.settings_toggle_switch import get_season_folder_path, use_season_folder

# UTILITY FUNCTION:
# Finds the root directory of the MediaSorter application
def find_mediasorter_root():
    current = Path(__file__).resolve()
    while current.name != 'MediaSorter':
        current = current.parent
    return current

# LOGGING SETUP:
log_file = "file_sorter_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_gui_files(file_paths, progress_callback=None):
    """
    Process a list of file paths from the GUI and sort them.
    
    Args:
        file_paths: List of file paths to process
        progress_callback: Optional callback function to update progress in the GUI
    
    Returns:
        tuple: (total_files, sorted_files, unsorted_files)
    """
    # Get application folders
    main_folder = find_mediasorter_root()
    unsorted_folder = main_folder / "0.2 Unsorted Folder"
    unsorted_folder.mkdir(parents=True, exist_ok=True)
    
    # Determine if we should use the custom sorting path
    if use_season_folder():
        custom_path = get_season_folder_path()
        logging.info(f"Using custom sorting folder from settings: {custom_path}")
    else:
        logging.info("Using default sorting folder structure")
    
    total_files = len(file_paths)
    sorted_files = 0
    unsorted_files = 0

    logging.info(f"Starting GUI file processing for {total_files} files...")

    for idx, file_path in enumerate(file_paths, start=1):
        file = Path(file_path)
        try:
            if not file.is_file():
                logging.warning(f"Skipped: {file} is not a file.")
                continue

            logging.info(f"Processing file: {file.name}")
            
            # Update progress in the GUI if callback provided
            if progress_callback:
                progress_callback(idx, total_files, f"Processing: {file.name}")

            # Match for TV shows
            match = re.match(r"(.+?)[\s._-]*(?:S(\d{2})[\s._-]*E(\d{2})|Season[\s]*(\d+)[\s]*Episode[\s]*(\d+))", file.name, re.IGNORECASE)
            if match:
                series_name = match.group(1)
                season = match.group(2) or match.group(4)
                episode = match.group(3) or match.group(5)
            else:
                # Try to catch 'Episode 3' with no season info
                match_alt = re.match(r"(.+?)[\s._-]*Episode[\s]*(\d{1,3})", file.name, re.IGNORECASE)
                if match_alt:
                    series_name = match_alt.group(1)
                    episode = match_alt.group(2)
                    season = "01"  # Default season to 01

            if match or match_alt:
                # Normalize series name
                series_name = re.sub(r"[._-]+", " ", series_name)
                series_name = re.sub(r"\s+", " ", series_name).strip()

                # Create target folders based on settings
                if use_season_folder():
                    # Create series folder in the custom path
                    custom_base = Path(get_season_folder_path())
                    series_folder = custom_base / series_name
                else:
                    # Use default path under main folder
                    series_folder = main_folder / series_name
                
                season_folder = series_folder / f"{series_name} - Season {season.zfill(2)}"
                season_folder.mkdir(parents=True, exist_ok=True)

                # Standardize filename
                standardized_name = f"{series_name} - S{season.zfill(2)}E{episode.zfill(2)}{file.suffix}"
                destination = season_folder / standardized_name

                if not destination.exists():
                    shutil.copy2(str(file), str(destination))
                    logging.info(f"Copied {file.name} to {destination}")
                    sorted_files += 1
                    
                    # Update progress with success message
                    if progress_callback:
                        progress_callback(idx, total_files, f"Successfully moved: {file.name}")
                else:
                    move_to_unsorted(file, unsorted_folder, "Duplicate file.")
                    unsorted_files += 1
                    
                    # Update progress with failure message
                    if progress_callback:
                        progress_callback(idx, total_files, f"Failed to move (duplicate): {file.name}")
                continue

            # If no match, move to unsorted
            logging.warning(f"Filename format not recognized: {file.name}")
            move_to_unsorted(file, unsorted_folder, "Unrecognized format.")
            unsorted_files += 1
            
            # Update progress with failure message
            if progress_callback:
                progress_callback(idx, total_files, f"Failed to move (unrecognized): {file.name}")

        except Exception as e:
            logging.error(f"Unexpected error with file {file.name}: {e}")
            move_to_unsorted(file, unsorted_folder, f"Processing error: {e}")
            unsorted_files += 1
            
            # Update progress with error message
            if progress_callback:
                progress_callback(idx, total_files, f"Error processing: {file.name}")

    # Log summary
    logging.info(f"Processing complete. Total files: {total_files}, Sorted: {sorted_files}, Unsorted: {unsorted_files}.")
    return total_files, sorted_files, unsorted_files

def move_to_unsorted(file, unsorted_folder, reason):
    """Move a file to the unsorted folder with a reason."""
    try:
        destination = unsorted_folder / file.name
        shutil.copy2(str(file), str(destination))
        logging.info(f"Copied {file.name} to Unsorted Folder: {reason}")
    except Exception as e:
        logging.error(f"Failed to copy {file.name} to Unsorted Folder: {e}")