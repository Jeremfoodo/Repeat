import json
import os

OBJECTIFS_FILE = 'objectifs.json'

def load_objectifs():
    if os.path.exists(OBJECTIFS_FILE):
        with open(OBJECTIFS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_objectifs(objectifs):
    with open(OBJECTIFS_FILE, 'w') as f:
        json.dump(objectifs, f)
