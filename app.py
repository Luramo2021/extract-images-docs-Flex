import json
import numpy as np
from flask import Flask, request, jsonify
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Charger les embeddings vectorisés (chunks courts)
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

    for item in PROCEDURES:
        if "embedding" not in item:
            continue
        proc_vector = np.array(item["embedding"])
        sim = cosine_similarity([question_vector], [proc_vector])[0][0]
        similarities.append((sim, item))

    if not similarities:
        return jsonify([])

    top_chunks = sorted(similarities, reverse=True, key=lambda x: x[0])[:3]
    result = [chunk[1] for chunk in top_chunks]

    return jsonify(result)

@app.route("/search-procedure", methods=["POST"])
def search_procedure():
    data = request.get_json()
    question = data.get("question")
    filename = data.get("filename")  # récupéré depuis l'Assistant
    similarity = data.get("similarity", 0.5)

    if not question or not filename:
        return jsonify({"error": "Missing question or filename"}), 400

    # Lire les étapes de la procédure correspondant au fichier
    procedure_path = f"Guides/{filename}"
    if not os.path.exists(procedure_path):
        return jsonify({"error": f"Fichier introuvable : {procedure_path}"}), 500

    with open(procedure_path, "r", encoding="utf-8") as f:
        procedure_steps = json.load(f)

    response = f"Voici les étapes pour {question} :\n\n"
    for step in procedure_steps:
        response += f"{step.get('step', '')}. {step.get('title', '')}\n"
        response += f"{step.get('text', '')}\n"
        response += f"Image : {step.get('image_url', '')}\n\n"

    return jsonify({"response": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
