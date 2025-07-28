import json
import argparse

# Configuration de argparse pour accepter un argument de ligne de commande
parser = argparse.ArgumentParser(description="Traiter le fichier JSON des procédures")
parser.add_argument("json_file", help="Le fichier JSON des procédures à traiter")
args = parser.parse_args()

# Charger le fichier de procédure index passé en argument
with open(args.json_file, "r", encoding="utf-8") as f:
    procedures_index = json.load(f)

# Supposons que la similarité entre la question et les chunks soit dans une variable `similarity`
question_similar = "ajouter des CGV sur un devis"  # Exemple de question

# Rechercher le fichier correspondant dans procedures_index.json
file_to_fetch = None
for procedure in procedures_index:
    if "cgv" in procedure["filename"].lower():  # Exemple d'un critère de correspondance
        file_to_fetch = procedure["filename"]
        break

# Si on trouve le fichier, on charge les étapes correspondantes
if file_to_fetch:
    # Charger le fichier correspondant (ex : cgv-v1.json)
    with open(f"Guides/Images/{file_to_fetch}", "r", encoding="utf-8") as f:
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
