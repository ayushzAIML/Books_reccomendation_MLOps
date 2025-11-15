import pandas as pd
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util

df = pd.read_csv("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/processed/books_metadata_final_clean.csv")

GENRE_LABELS = [
    "Mystery", "Detective", "Thriller", "Crime", "Suspense",
    "Fantasy", "Science Fiction", "Horror",
    "Romance", "Young Adult", "Historical Fiction", "Classics",
    "Biography", "Memoir", "History",
    "Self Help", "Philosophy", "Psychology",
    "Poetry", "Art", "Travel",
    "Religion", "Spirituality",
    "Science", "Technology",
    "Business", "Economics",
    "Children's Books"
]

df["Genre"] = df["Genre"].fillna("Unknown Genre")
unknown_mask = df["Genre"] == "Unknown Genre"

model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# embed labels once
label_embeddings = model.encode(GENRE_LABELS, convert_to_tensor=True)

texts = df.loc[unknown_mask, "text_for_embedding"].tolist()
genres = []

batch_size = 256  # large batch runs fast on GPU / okay on CPU

for i in tqdm(range(0, len(texts), batch_size)):
    batch = texts[i:i+batch_size]
    text_embeddings = model.encode(batch, convert_to_tensor=True)
    cos_scores = util.cos_sim(text_embeddings, label_embeddings)
    top_labels = cos_scores.argmax(dim=1)
    genres.extend([GENRE_LABELS[idx] for idx in top_labels])

df.loc[unknown_mask, "Genre"] = genres
df.to_csv("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/processed/books_metadata_with_genre.csv", index=False)

print("✅ Done! Fast genre inference saved.")
