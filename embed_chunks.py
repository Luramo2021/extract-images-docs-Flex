# embed_chunks.py

import os
import json
import glob
import openai
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()  # Charge les variables d'environnement depuis un fichier .env
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_procedures(folder="procedures"):
    files = glob.glob(f"{folder}/*-v1.json")
    data = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            steps = json.load(f)
            text = "\n".join(f"{step['title']} : {step['text']}" for step in steps)
            filename = os.path.basename(file)
            data.append({"filename": filename, "content": text})
    return data

def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response["data"][0]["embedding"]

def main():
    procedures = load_procedures()
    output = []

    for proc in tqdm(procedures, desc="Generating embeddings"):
        embedding = get_embedding(proc["content"])
        output.append({
            "filename": proc["filename"],
            "content": proc["content"],
            "embedding": embedding
        })

    with open("embeddings.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
