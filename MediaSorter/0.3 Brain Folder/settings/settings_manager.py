from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QHBoxLayout, QCheckBox, QMessageBox
import json
from pathlib import Path
import os

settings_file = Path("settings/user_settings.json")

def load_settings():
    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
    return {"season_sort_path": "", "movie_sort_path": "", "use_season_folder": False}

def save_settings(data):
    try:
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def get_settings_widget():
    widget = QWidget()
    layout = QVBoxLayout()
    settings = load_settings()

    # Season Sort Path
    use_season_toggle = QCheckBox("Use this folder for season sorting")
    use_season_toggle.setChecked(settings.get("use_season_folder", False))
    
    season_layout = QHBoxLayout()
    season_label = QLabel("Season Sort Folder:")
    season_input = QLineEdit(settings.get("season_sort_path", ""))
    season_button = QPushButton("Browse")
    
    season_layout.addWidget(season_label)
    season_layout.addWidget(season_input)
    season_layout.addWidget(season_button)
    
    def set_season_path():
        path = QFileDialog.getExistingDirectory(widget, "Select Season Folder")
        if path:
            # Convert to string and save the path
            path_str = str(path)
            season_input.setText(path_str)
            settings["season_sort_path"] = path_str
            if save_settings(settings):
                QMessageBox.information(widget, "Settings Saved", 
                                       f"Season sort folder set to:\n{path_str}")
            else:
                QMessageBox.warning(widget, "Settings Error", 
                                   "Failed to save season sort path")

    def update_use_season_toggle():
        settings["use_season_folder"] = use_season_toggle.isChecked()
        if save_settings(settings):
            status = "enabled" if use_season_toggle.isChecked() else "disabled"
            QMessageBox.information(widget, "Settings Updated", 
                                  f"Custom season folder {status}")
        else:
            QMessageBox.warning(widget, "Settings Error", 
                               "Failed to update season folder toggle")

    def update_season_path_manually():
        path = season_input.text().strip()
        if path:
            # Check if path exists
            if os.path.exists(path):
                settings["season_sort_path"] = path
                if save_settings(settings):
                    QMessageBox.information(widget, "Settings Saved", 
                                           f"Season sort folder set to:\n{path}")
                else:
                    QMessageBox.warning(widget, "Settings Error", 
                                       "Failed to save season sort path")
            else:
                QMessageBox.warning(widget, "Invalid Path", 
                                   f"The path does not exist:\n{path}")

    season_button.clicked.connect(set_season_path)
    use_season_toggle.stateChanged.connect(update_use_season_toggle)
    season_input.editingFinished.connect(update_season_path_manually)
    
    # Movie Sort Path
    movie_layout = QHBoxLayout()
    movie_label = QLabel("Movie Sort Folder:")
    movie_input = QLineEdit(settings.get("movie_sort_path", ""))
    movie_button = QPushButton("Browse")
    
    movie_layout.addWidget(movie_label)
    movie_layout.addWidget(movie_input)
    movie_layout.addWidget(movie_button)

    def set_movie_path():
        path = QFileDialog.getExistingDirectory(widget, "Select Movie Folder")
        if path:
            path_str = str(path)
            movie_input.setText(path_str)
            settings["movie_sort_path"] = path_str
            if save_settings(settings):
                QMessageBox.information(widget, "Settings Saved", 
                                       f"Movie sort folder set to:\n{path_str}")
            else:
                QMessageBox.warning(widget, "Settings Error", 
                                   "Failed to save movie sort path")

    def update_movie_path_manually():
        path = movie_input.text().strip()
        if path:
            if os.path.exists(path):
                settings["movie_sort_path"] = path
                if save_settings(settings):
                    QMessageBox.information(widget, "Settings Saved", 
                                           f"Movie sort folder set to:\n{path}")
                else:
                    QMessageBox.warning(widget, "Settings Error", 
                                       "Failed to save movie sort path")
            else:
                QMessageBox.warning(widget, "Invalid Path", 
                                   f"The path does not exist:\n{path}")

    movie_button.clicked.connect(set_movie_path)
    movie_input.editingFinished.connect(update_movie_path_manually)

    # Add all components to the main layout
    layout.addWidget(use_season_toggle)
    layout.addLayout(season_layout)
    layout.addLayout(movie_layout)
    
    # Save button
    save_button = QPushButton("Save All Settings")
    
    def save_all_settings():
        season_path = season_input.text().strip()
        movie_path = movie_input.text().strip()
        
        # Validate paths if not empty
        paths_valid = True
        if season_path and not os.path.exists(season_path):
            QMessageBox.warning(widget, "Invalid Path", 
                               f"Season sort folder does not exist:\n{season_path}")
            paths_valid = False
        
        if movie_path and not os.path.exists(movie_path):
            QMessageBox.warning(widget, "Invalid Path", 
                               f"Movie sort folder does not exist:\n{movie_path}")
            paths_valid = False
        
        if paths_valid:
            settings["season_sort_path"] = season_path
            settings["movie_sort_path"] = movie_path
            settings["use_season_folder"] = use_season_toggle.isChecked()
            
            if save_settings(settings):
                QMessageBox.information(widget, "Settings Saved", "All settings saved successfully")
            else:
                QMessageBox.warning(widget, "Settings Error", "Failed to save settings")
    
    save_button.clicked.connect(save_all_settings)
    layout.addWidget(save_button)
    
    widget.setLayout(layout)
    return widget