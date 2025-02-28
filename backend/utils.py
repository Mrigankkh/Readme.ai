import os
import json

IGNORE_LIST_PATH = os.path.join(os.path.dirname(__file__), 'config', 'ignore_file_list.json')
try:
    with open(IGNORE_LIST_PATH, 'r') as f:
        ignore_data = json.load(f)
except Exception as e:
    raise FileNotFoundError(f"Unable to load ignore file list at {IGNORE_LIST_PATH}: {e}")

IGNORED_DIRS = set(ignore_data.get("directories", []))

IGNORED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.lock', '.json'}
IGNORED_FILES = set(ignore_data.get("files", []))


def is_valid_file(file, file_path):
    """
    Helper function to check if the file is valid based on its name, extension, and size.
    """
    # Skip files starting with '.' (hidden files)
    if file.startswith('.'):
        return False
    
    # Skip files in the ignored list
    if file in IGNORED_FILES:
        return False
    
    # Get file extension and check if it's in the ignored extensions list
    ext = os.path.splitext(file)[1].lower()
    if ext in IGNORED_EXTENSIONS:
        return False
    
    # Skip files larger than 100KB
    if os.path.getsize(file_path) >= 100 * 1024:
        return False
    
    return True


def get_file_size(file_path):
    """
    Returns the size of a file in KB.
    """
    try:
        return os.path.getsize(file_path) / 1024  # in KB
    except Exception as e:
        print(f"Error getting file size for {file_path}: {e}")
        return 0
    