import os
import json
import glob
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

# Charger les variables d'environnement (.env)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("La clé OPENAI_API_KEY est manquante dans le fichier .env.")

# Initialiser le client OpenAI (meilleure pratique que openai.api_key = ...)
client = OpenAI(api_key=OPENAI_API_KEY)

def load_procedures(folder="Guides"):
    """Charge tous les fichiers *-v1.json et assemble le texte."""
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
    """Appelle l’API OpenAI pour générer un embedding."""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def split_into_chunks(text, chunk_size=1000):
    """Divise le texte en morceaux de taille maximale 'chunk_size'."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

def main():
    procedures = load_procedures()
    output = []

    for proc in tqdm(procedures, desc="📌 Génération des embeddings"):
        chunks = split_into_chunks(proc["content"])
        for idx, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            output.append({
                "filename": proc["filename"],
                "chunk_index": idx,  # Ajout d'un index pour chaque chunk
                "chunk": chunk,
                "embedding": embedding
            })

    with open("embeddings.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
