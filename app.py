# app.py
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)