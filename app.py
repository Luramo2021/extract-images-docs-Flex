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

@app.route("/search-chunks", methods=["POST"])
def search_chunks():
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing question"}), 400

    question_vector = np.array(get_embedding(question))
    similarities = []

    # Calcul de la similarité entre la question et chaque chunk
    for item in PROCEDURES:
        proc_vector = np.array(item["embedding"])
        sim = cosine_similarity([question_vector], [proc_vector])[0][0]
        similarities.append((sim, item))

    # Récupérer les 3 chunks les plus similaires
    top_chunks = sorted(similarities, reverse=True, key=lambda x: x[0])[:3]
    result = [chunk[1] for chunk in top_chunks]

    return jsonify(result)

@app.route("/search-procedure", methods=["POST"])
def search_procedure():
    data = request.get_json()
    question = data.get("question")
    similarity = data.get("similarity")

    if not question or similarity is None:
        return jsonify({"error": "Missing question or similarity"}), 400

    # Rechercher la procédure correspondante dans procedures_index.json
    with open("Guides/procedures-index.json", "r", encoding="utf-8") as f:
        procedures_index = json.load(f)

    file_to_fetch = None
    for procedure in procedures_index:
        if similarity >= 0.7 and "cgv" in procedure["filename"].lower():  # Critère basé sur la similarité
            file_to_fetch = procedure["filename"]
            break

    # Si on trouve le fichier, charger les étapes correspondantes
    if file_to_fetch:
        with open(f"Guides/Images/{file_to_fetch}", "r", encoding="utf-8") as f:
            procedure_steps = json.load(f)

        # Construire la réponse avec les étapes de la procédure
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
