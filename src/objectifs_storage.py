import json
import os

OBJECTIFS_FILE = os.path.join('data', 'objectifs.json')

def load_objectifs():
    if os.path.exists(OBJECTIFS_FILE):
        with open(OBJECTIFS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_objectifs(objectifs):
    os.makedirs('data', exist_ok=True)  # Create directory if it doesn't exist
    with open(OBJECTIFS_FILE, 'w') as f:
        json.dump(objectifs, f, indent=4)
