import sys
from PyQt5.QtWidgets import QApplication
import file_sorter_gui  # Import the stable GUI module
from settings import settings_handler  # Import the settings handler
from status import status_checker
import os
sys.path.append(os.path.dirname(__file__))
from GUI_addons import gui_addon_test
from movie_code import movie_handler

# Load settings at the start
general_settings = settings_handler.load_general_settings()
seasons_settings = settings_handler.load_seasons_settings()
movies_settings = settings_handler.load_movies_settings()

# Check and log the status at the start
status_report = status_checker.check_status()
status_checker.log_status(status_report)

# Add debug prints to ensure settings are loaded
print("Loaded General Settings:", general_settings)
print("Loaded Seasons Settings:", seasons_settings)
print("Loaded Movies Settings:", movies_settings)

if __name__ == "__main__":
    # Create the application instance
    app = QApplication(sys.argv)

    # Initialize the main GUI window from file_sorter_gui
    main_window = file_sorter_gui.FileSorterApp()

    # Pass loaded settings to the GUI (if needed)
    main_window.settings = {
        "general": general_settings,
        "seasons": seasons_settings,
        "movies": movies_settings,
    }

    main_window.show()

    # Execute the application
    sys.exit(app.exec_())
