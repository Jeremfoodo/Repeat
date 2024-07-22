import json
import os

# Chemin du fichier JSON
OBJECTIFS_FILE = os.path.join('data', 'objectifs.json')

def load_objectifs():
    if os.path.exists(OBJECTIFS_FILE):
        with open(OBJECTIFS_FILE, 'r') as f:
            print(f"Chargement des objectifs depuis {OBJECTIFS_FILE}")
            return json.load(f)
    print(f"Aucun fichier d'objectifs trouvé, création d'un nouveau.")
    return {}

def save_objectifs(objectifs):
    try:
        os.makedirs('data', exist_ok=True)
        with open(OBJECTIFS_FILE, 'w') as f:
            json.dump(objectifs, f, indent=4)
        print(f"Objectifs sauvegardés dans {OBJECTIFS_FILE}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des objectifs : {e}")

# Fonction pour vérifier l'existence du fichier JSON
def check_json_file():
    if os.path.exists(OBJECTIFS_FILE):
        print(f"Le fichier JSON existe : {OBJECTIFS_FILE}")
    else:
        print(f"Le fichier JSON n'existe pas : {OBJECTIFS_FILE}")

# Tester l'écriture dans le fichier JSON
def test_write_access():
    try:
        os.makedirs('data', exist_ok=True)
        test_file = os.path.join('data', 'test.json')
        with open(test_file, 'w') as f:
            json.dump({"test": "test"}, f, indent=4)
        print(f"Test d'écriture réussi : {test_file}")
        os.remove(test_file)  # Supprimer le fichier de test après vérification
    except Exception as e:
        print(f"Erreur lors du test d'écriture : {e}")

