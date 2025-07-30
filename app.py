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
        proc_vector = np.array(item["embedding"])
        sim = cosine_similarity([question_vector], [proc_vector])[0][0]
        similarities.append((sim, item))

    top_chunks = sorted(similarities, reverse=True, key=lambda x: x[0])[:3]
    result = [chunk[1] for chunk in top_chunks]

    return jsonify(result)

@app.route("/search-procedure", methods=["POST"])
def search_procedure():
    data = request.get_json()
    question = data.get("question")
    similarity_threshold = data.get("similarity", 0.5)

    if not question:
        return jsonify({"error": "Missing question"}), 400

    # Charger les métadonnées de toutes les procédures complètes
    with open("Guides/procedures-index.json", "r", encoding="utf-8") as f:
        procedures_index = json.load(f)

    question_vector = np.array(get_embedding(question))

    best_match = None
    best_score = 0

    for procedure in procedures_index:
        proc_vector = np.array(procedure["embedding"])
        score = cosine_similarity([question_vector], [proc_vector])[0][0]

        if score > similarity_threshold and score > best_score:
            best_score = score
            best_match = procedure

    if not best_match:
        return jsonify({"error": "Aucune procédure trouvée pour la question."})

    # Lire les étapes de la procédure la plus pertinente
    with open(f"Guides/{best_match['filename']}", "r", encoding="utf-8") as f:
        procedure_steps = json.load(f)

    response = f"Voici les étapes pour {question} :\n\n"
    for step in procedure_steps:
        response += f"{step['step']}. {step['title']}\n"
        response += f"{step['text']}\n"
        response += f"Image : {step['image_url']}\n\n"

    return jsonify({"response": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
