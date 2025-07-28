import json
import numpy as np
from flask import Flask, request, jsonify
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os
import subprocess

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
    if not question:
        return jsonify({"error": "Missing question"}), 400

    question_vector = np.array(get_embedding(question))
    similarities = []

    for item in PROCEDURES:
        proc_vector = np.array(item["embedding"])
        sim = cosine_similarity([question_vector], [proc_vector])[0][0]
        similarities.append((sim, item))

    # Trier par similarité et sélectionner le meilleur
    top_chunk = sorted(similarities, reverse=True, key=lambda x: x[0])[0]  # Le meilleur chunk basé sur la similarité
    best_matching_file = top_chunk[1]["filename"]  # Le fichier correspondant

    # Appeler le fichier `prepare_reponse.py` pour récupérer les étapes de la procédure
    command = f"python prepare_reponse.py {best_matching_file}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return jsonify({"error": "Erreur lors de l'appel de `prepare_reponse.py`", "details": stderr.decode()}), 500

    response = stdout.decode()
    return jsonify({"steps": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
