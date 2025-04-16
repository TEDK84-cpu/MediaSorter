import json
import os

# Paths to settings files
settings_folder = os.path.dirname(__file__)
general_settings_file = os.path.join(settings_folder, "general_settings.json")
seasons_settings_file = os.path.join(settings_folder, "seasons_settings.json")
movies_settings_file = os.path.join(settings_folder, "movies_settings.json")
custom_rules_file = os.path.join(settings_folder, "custom_rules.json")

# Default settings
default_general_settings = {
    "appearance": "light",
    "logging_enabled": True
}

default_seasons_settings = {
    "folder_structure": "Series Name/Season 01/",
    "filename_format": "Series Name - S01E01"
}

default_movies_settings = {
    "folder_structure": "Movies/",
    "filename_format": "Movie Name (Year)"
}

default_custom_rules = {}

# Helper functions
def load_settings(file_path, default_settings):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default_settings

def save_settings(file_path, settings):
    with open(file_path, "w") as file:
        json.dump(settings, file, indent=4)

def reset_settings(file_path, default_settings):
    save_settings(file_path, default_settings)
    return default_settings

# Specific load/save/reset functions
def load_general_settings():
    return load_settings(general_settings_file, default_general_settings)

def save_general_settings(settings):
    save_settings(general_settings_file, settings)

def reset_general_settings():
    return reset_settings(general_settings_file, default_general_settings)

def load_seasons_settings():
    return load_settings(seasons_settings_file, default_seasons_settings)

def save_seasons_settings(settings):
    save_settings(seasons_settings_file, settings)

def reset_seasons_settings():
    return reset_settings(seasons_settings_file, default_seasons_settings)

def load_movies_settings():
    return load_settings(movies_settings_file, default_movies_settings)

def save_movies_settings(settings):
    save_settings(movies_settings_file, settings)

def reset_movies_settings():
    return reset_settings(movies_settings_file, default_movies_settings)

def load_custom_rules():
    return load_settings(custom_rules_file, default_custom_rules)

def save_custom_rules(rules):
    save_settings(custom_rules_file, rules)

def validate_rule(rule):
    """Validate a sorting rule's structure."""
    required_keys = {"file_type", "sort_criteria"}
    if not isinstance(rule, dict):
        return False
    if not required_keys.issubset(rule.keys()):
        return False
    return True

if __name__ == "__main__":
    # Example usage
    print("General Settings:", load_general_settings())
    print("Seasons Settings:", load_seasons_settings())
    print("Movies Settings:", load_movies_settings())

    # Custom Rules Example
    custom_rules = load_custom_rules()
    print("Custom Rules:", custom_rules)

    # Add a new rule
    new_rule = {"file_type": ".mp4", "sort_criteria": "By Year"}
    if validate_rule(new_rule):
        custom_rules[".mp4"] = new_rule
        save_custom_rules(custom_rules)
    else:
        print("Invalid rule format.")
