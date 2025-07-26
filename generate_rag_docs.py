import json
import os
from pathlib import Path

# Répertoire de base
base_dir = Path("Guides")
images_dir = base_dir / "Images"
output_file = base_dir / "rag_documents.json"

# Descriptions manuelles
DESCRIPTIONS = {
    "favoris-v1": "Ajouter ou retirer un écran dans les favoris pour un accès rapide depuis l’accueil.",
    "filtres-v1": "Création, modification, application et suppression de filtres dans la section Clients.",
    "cgv-v1": "Ajouter les Conditions Générales de Vente (CGV) sur un devis ou une facture."
}

# Génération des documents RAG-ready
rag_documents = []

for file in base_dir.glob("*-v1.json"):
    name = file.stem  # exemple: 'favoris-v1'
    with open(file, "r") as f:
        steps = json.load(f)
    
    for step in steps:
        rag_documents.append({
            "procedure": name,
            "description": DESCRIPTIONS.get(name, ""),
            "step": step["step"],
            "title": step["title"],
            "text": step["text"],
            "image_url": step.get("image_url", "")
        })

# Écriture dans un fichier JSON final
with open(output_file, "w") as f:
    json.dump(rag_documents, f, indent=2, ensure_ascii=False)

print(f"{len(rag_documents)} documents RAG prêts enregistrés dans {output_file}")