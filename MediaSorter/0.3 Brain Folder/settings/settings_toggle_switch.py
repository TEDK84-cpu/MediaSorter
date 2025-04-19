# settings_toggle_switch.py v1.3
# Updated to ensure proper path handling for season folder
 
from pathlib import Path
import json
import os
import logging

def use_season_folder():
    """Check if custom season folder should be used"""
    config_path = Path("settings/user_settings.json")
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            use_folder = data.get("use_season_folder", False)
            
            # Only return True if both the toggle is enabled AND the path exists and is valid
            if use_folder and data.get("season_sort_path"):
                path = data["season_sort_path"]
                if os.path.exists(path):
                    return True
                else:
                    logging.warning(f"Custom season path set but doesn't exist: {path}")
            return False
        except Exception as e:
            logging.error(f"Error reading settings: {e}")
            return False
    return False

def get_season_folder_path():
    """Get the path to use for season sorting"""
    config_path = Path("settings/user_settings.json")
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            # If path exists, return it
            if data.get("season_sort_path"):
                path = data["season_sort_path"]
                # Make sure the path is valid
                if os.path.exists(path):
                    return path
                else:
                    logging.warning(f"Custom season path doesn't exist: {path}")
        except Exception as e:
            logging.error(f"Error getting season folder path: {e}")
    
    # Default folder if settings don't exist or aren't valid
    return "0.1 Sorting Folder"