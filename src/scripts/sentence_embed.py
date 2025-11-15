# from sentence_transformers import SentenceTransformer
# import pandas as pd
# from tqdm import tqdm
# import numpy as np


# df = pd.read_csv("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/processed/books_final_for_embedding.csv", encoding='latin-1')


# model = SentenceTransformer('all-MiniLM-L6-v2')

# def embed_sentences(texts , batch_size = 1000):
#     embeddings = []
#     for i in tqdm(range(0, len(texts),batch_size )):
#         batch_texts = texts[i:i+batch_size]
#         batch_encodings = model.encode(batch_texts, batch_size=64, show_progress_bar=False)
#         embeddings.extend(batch_encodings)

#     return np.array(embeddings)

    

# df["embeddings"] = embed_sentences(df["text_for_embedding"].tolist())

# df[["ISBN", "embeddings"]].to_csv("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/embeddings/books_embeddings.csv", index=False)


# print("embedded csv is saved ")

import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

df = pd.read_csv("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/processed/books_final_for_embedding.csv", encoding='latin-1')

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

embeddings = []
batch_size = 1000

for i in tqdm(range(0, len(df), batch_size)):
    batch = df["text_for_embedding"][i:i+batch_size].tolist()
    batch_emb = model.encode(batch, batch_size=64, show_progress_bar=False)
    embeddings.extend(batch_emb)

df["embeddings"] = np.array(embeddings).tolist()

df[["ISBN", "embeddings"]].to_csv(
    "/home/ayushz/Projects/Books_recommendation_END_TO_END/data/embeddings/books_embeddings.csv",
    index=False
)

print("✅ Done! Embeddings saved.")


import ast

df = pd.read_csv("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/embeddings/books_embeddings.csv")

# Convert string → list → numpy array safely
embeddings_array = np.array([np.array(ast.literal_eval(e)) for e in df["embeddings"]])

# Save embeddings
np.save("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/embeddings/embeddings.npy", embeddings_array)

# Save ISBN list
df["ISBN"].to_csv("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/embeddings/isbn_list.csv", index=False)

print("✅ Done! Numpy embeddings and ISBN list saved.")