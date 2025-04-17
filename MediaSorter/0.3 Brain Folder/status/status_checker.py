# status_checker.py v2.0

import os

def check_status():
    """Check the status of connected subfolders and files."""
    status_report = {}

    # Define required subfolders and files
    required_paths = {
        "settings/": ["settings_handler.py", "settings.json"],
        "": ["file_sorter_gui.py", "file_sorter.py"],
        "movie_code/": ["movie_handler.py"],  # Add the movie_code folder
    }

    # Check each path and file
    for folder, files in required_paths.items():
        folder_status = {}
        for file_name in files:
            file_path = os.path.join(folder, file_name)
            if os.path.exists(file_path):
                folder_status[file_name] = "Working Properly"
            else:
                folder_status[file_name] = "Missing"
        status_report[folder] = folder_status

    return status_report

def log_status(status_report):
    """Log the status report to a file."""
    log_file = os.path.join("status", "status_log.txt")
    with open(log_file, "w") as log:
        for folder, files in status_report.items():
            log.write(f"Folder: {folder or 'Root'}\n")
            for file, status in files.items():
                log.write(f"  {file}: {status}\n")
            log.write("\n")

if __name__ == "__main__":
    # Check and log the status
    status_report = check_status()
    log_status(status_report)
    for folder, files in status_report.items():
        print(f"Folder: {folder or 'Root'}")
        for file, status in files.items():
            print(f"  {file}: {status}")
        print()
