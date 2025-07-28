import json
import sys

# Récupérer la question et la similarité depuis les arguments de ligne de commande
question_similar = sys.argv[1]  # La question passée en argument
similarity = float(sys.argv[2])  # La similarité passée en argument

# Charger le fichier de procédure index
with open("Guides/procedures-index.json", "r", encoding="utf-8") as f:
    procedures_index = json.load(f)

# Rechercher le fichier correspondant dans procedures_index.json en fonction de la similarité
file_to_fetch = None
for procedure in procedures_index:
    # Utiliser la similarité pour décider quel fichier correspond (par exemple)
    if similarity >= 0.7 and "cgv" in procedure["filename"].lower():  # Ajuster le critère si nécessaire
        file_to_fetch = procedure["filename"]
        break

# Si on trouve le fichier, on charge les étapes correspondantes
if file_to_fetch:
    # Charger le fichier correspondant (ex : cgv-v1.json)
    with open(f"Guides/{file_to_fetch}", "r", encoding="utf-8") as f:
        procedure_steps = json.load(f)

    # Construire la réponse
    response = f"Voici les étapes pour {question_similar} :\n\n"
    for step in procedure_steps:
        response += f"{step['step']}. {step['title']}\n"
        response += f"{step['text']}\n"
        response += f"Image : {step['image_url']}\n\n"
    
    print(response)

else:
    print("Aucune procédure trouvée pour la question.")
