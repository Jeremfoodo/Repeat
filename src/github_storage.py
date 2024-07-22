import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'votre_nom_utilisateur'  # Remplacez par votre nom d'utilisateur GitHub
REPO_NAME = 'votre_nom_depot'  # Remplacez par le nom de votre dépôt
BRANCH_NAME = 'main'  # Branche sur laquelle vous souhaitez travailler
FILE_PATH = 'data/objectifs.json'  # Chemin du fichier dans le dépôt

def get_file_sha(file_path):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['sha']

def load_objectifs():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        import base64
        import json
        file_content = base64.b64decode(content['content']).decode('utf-8')
        return json.loads(file_content)
    return {}

def save_objectifs(objectifs):
    import json
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    sha = get_file_sha(FILE_PATH) if os.path.exists(FILE_PATH) else None
    data = {
        "message": "Mettre à jour les objectifs",
        "content": base64.b64encode(json.dumps(objectifs).encode('utf-8')).decode('utf-8'),
        "branch": BRANCH_NAME,
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"Objectifs sauvegardés dans le dépôt GitHub : {REPO_NAME}")

def test_write_access():
    try:
        load_objectifs()
        print("Test d'accès en lecture réussi")
        save_objectifs({"test": "test"})
        print("Test d'accès en écriture réussi")
    except Exception as e:
        print(f"Erreur lors du test d'accès : {e}")

