"""Configuration module for the recommendation pipeline."""

import os
from pathlib import Path


# Data paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
FAISS_DIR = DATA_DIR / "faiss"
USER_DIR = DATA_DIR / "userss"

# File paths
META_CSV = str(PROCESSED_DATA_DIR / "books_metadata_with_genre.csv")
EMB_NPY = str(EMBEDDINGS_DIR / "embeddings.npy")
FAISS_INDEX = str(FAISS_DIR / "faiss_index.bin")
ISBN_LIST = str(EMBEDDINGS_DIR / "isbn_list.csv")
RATINGS_CSV = str(DATA_DIR / "user" / "cleaned_ratings.csv")
USER_PROFILE_PATH = str(USER_DIR / "user_profiles.json")

# Model configurations
BI_ENCODER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Blending weights (must sum to 1.0 for normalized scores)
W_CE = 0.55         # cross-encoder weight (semantic relevance)
W_GENRE = 0.15      # genre boost weight
W_USER = 0.15       # long-term personalization weight
W_SESSION = 0.15    # short-term session (mood) weight

# Operational sizes
RETRIEVE_TOP = 50
FINAL_K = 10

# Session memory limits
SESSION_HISTORY_LIMIT = 12

# Smoothing factor for profile updates
PROFILE_SMOOTHING = 0.6

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
os.makedirs(FAISS_DIR, exist_ok=True)
os.makedirs(USER_DIR, exist_ok=True)
