import os
import json

GUIDES_DIR = "Guides"
INDEX_FILE = os.path.join(GUIDES_DIR, "procedures-index.json")

# Descriptions manuelles (par nom de fichier sans extension)
# Descriptions manuelles (par nom de fichier sans extension)
DESCRIPTIONS = {
    "favoris-v1": "Ajouter ou retirer un écran dans les favoris pour un accès rapide depuis l’accueil.",
    "filtres-v1": "Création, modification, application et suppression de filtres dans la section Clients.",
    "cgv-v1": "Ajouter des conditions générales de vente (CGV) sur les devis et factures dans la configuration société."
}

def get_description(basename):
    return DESCRIPTIONS.get(basename, f"Procédure définie dans le fichier {basename}.json")

def generate_index():
    index = []
    for file in os.listdir(GUIDES_DIR):
        if file.endswith("-v1.json"):
            base = file[:-5]  # retire '.json'
            index.append({
                "filename": file,
                "description": get_description(base)
            })
    return index

if __name__ == "__main__":
    procedures = generate_index()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(procedures, f, indent=2, ensure_ascii=False)
    print(f"{len(procedures)} fichiers indexés dans {INDEX_FILE}")
