import faiss
import numpy as np
import pickle
import fitz
import os
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')


def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def process_all_pdfs(folder_path):
    all_chunks = []
    metadata = []

    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

    print(f"📂 Found {len(pdf_files)} PDFs")

    chunk_size = 400
    overlap = 150

    for pdf_file in pdf_files:
        path = os.path.join(folder_path, pdf_file)
        print(f"📄 Processing: {pdf_file}")

        text = extract_text(path)

        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]

            if len(chunk.strip()) < 50:
                continue

            all_chunks.append(chunk)

            metadata.append({
                "source": pdf_file
            })

    print(f"✂️ Total chunks: {len(all_chunks)}")

    # Create embeddings
    embeddings = model.encode(all_chunks)
    embeddings = np.array(embeddings).astype("float32")

    # Normalize vectors
    faiss.normalize_L2(embeddings)

    # Create FAISS index
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    # Save index
    faiss.write_index(index, "vectors.index")

    # Save chunks + metadata
    with open("chunks.pkl", "wb") as f:
        pickle.dump({
            "chunks": all_chunks,
            "metadata": metadata
        }, f)

    print("✅ Vector DB ready!")


if __name__ == "__main__":
    process_all_pdfs("pdfs")