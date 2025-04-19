# status_checker.py

from pathlib import Path
import re

# STATUS SUMMARY FUNCTION:
# Parses the log file to extract statistics about file processing
def get_status_summary():
    log_path = Path("file_sorter_log.txt")
    total, sorted_count, unsorted_count, last_file = 0, 0, 0, "N/A"

    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if "Processing:" in line:
                total += 1
                match = re.search(r"Processing: (.+)$", line)
                if match:
                    last_file = match.group(1)
            if "Successfully moved" in line:
                sorted_count += 1
            if "Failed to move" in line:
                unsorted_count += 1

    return f"Total Files Processed: {total}\nSorted: {sorted_count}\nUnsorted: {unsorted_count}\nLast File: {last_file}"