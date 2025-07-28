import json
import numpy as np
from flask import Flask, request, jsonify
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Charger les embeddings vectorisés
with open("embeddings.json", "r", encoding="utf-8") as f:
    PROCEDURES = json.load(f)

app = Flask(__name__)

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    question = data.get("question")
    similarity = data.get("similarity")  # Ajouter la similarité

    if not question:
        return jsonify({"error": "Missing question"}), 400

    if similarity is None:
        return jsonify({"error": "Missing similarity"}), 400

    # Rechercher le fichier correspondant à la similarité calculée
    # Charger le fichier de procédure index
    with open("Guides/procedures-index.json", "r", encoding="utf-8") as f:
        procedures_index = json.load(f)

    file_to_fetch = None
    for procedure in procedures_index:
        if similarity >= 0.7 and "cgv" in procedure["filename"].lower():  # Exemple avec un critère de similarité
            file_to_fetch = procedure["filename"]
            break

    if file_to_fetch:
        # Charger le fichier correspondant (ex : cgv-v1.json)
        with open(f"Guides/Images/{file_to_fetch}", "r", encoding="utf-8") as f:
            procedure_steps = json.load(f)

        # Construire la réponse
        response = f"Voici les étapes pour {question} :\n\n"
        for step in procedure_steps:
            response += f"{step['step']}. {step['title']}\n"
            response += f"{step['text']}\n"
            response += f"Image : {step['image_url']}\n\n"

        return jsonify({"response": response})
    
    return jsonify({"error": "Aucune procédure trouvée pour la question."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
