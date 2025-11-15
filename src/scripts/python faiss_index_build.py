import faiss
import numpy as np

# Load embeddings
embeddings = np.load("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/embeddings/embeddings.npy").astype('float32')

# Normalize embeddings (important for cosine-like search)
faiss.normalize_L2(embeddings)

# Create index (Flat IP = cosine similarity)
index = faiss.IndexFlatIP(embeddings.shape[1])

# Add embeddings to index
index.add(embeddings)

# Save index
faiss.write_index(index, "/home/ayushz/Projects/Books_recommendation_END_TO_END/data/faiss/faiss_index.bin")

print("✅ FAISS index built & saved successfully.")
