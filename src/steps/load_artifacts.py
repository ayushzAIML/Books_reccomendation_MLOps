"""ZenML step to load and validate all artifacts needed for recommendations."""

import logging
import os
import numpy as np
import pandas as pd
import faiss
from typing import Tuple, Dict, List

from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def load_artifacts(
    meta_csv: str,
    emb_npy: str,
    faiss_index_path: str,
    isbn_list_path: str,
) -> Tuple[pd.DataFrame, np.ndarray, faiss.IndexFlatIP, List[str], Dict]:
    """
    Load all pre-computed artifacts for the recommendation engine.
    
    This step validates that all required files exist and loads them into memory.
    
    Args:
        meta_csv: Path to books metadata CSV
        emb_npy: Path to embeddings numpy array
        faiss_index_path: Path to FAISS index binary
        isbn_list_path: Path to ISBN list CSV
    
    Returns:
        Tuple containing:
        - metadata DataFrame
        - embeddings numpy array (normalized)
        - FAISS index
        - ISBN list
        - metadata dict with index mappings
    """
    logger.info("🔄 Loading recommendation artifacts...")
    
    # Validate all files exist
    required_files = {
        "Metadata CSV": meta_csv,
        "Embeddings NPY": emb_npy,
        "FAISS Index": faiss_index_path,
        "ISBN List": isbn_list_path,
    }
    
    for file_name, file_path in required_files.items():
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ {file_name} not found at {file_path}")
        logger.info(f"✓ Found {file_name}")
    
    # Load metadata
    logger.info("📖 Loading metadata...")
    df = pd.read_csv(meta_csv, dtype=str).fillna("")
    df.columns = [c.lower() for c in df.columns]
    
    if "isbn" not in df.columns:
        raise ValueError("❌ Metadata CSV must contain 'isbn' column")
    
    logger.info(f"✓ Loaded {len(df)} books from metadata")
    
    # Load embeddings
    logger.info("📊 Loading embeddings...")
    embeddings = np.load(emb_npy).astype("float32")
    logger.info(f"✓ Loaded embeddings with shape {embeddings.shape}")
    
    # Normalize embeddings for cosine similarity
    from sklearn.preprocessing import normalize
    embeddings_norm = normalize(embeddings.copy(), axis=1)
    
    # Load ISBN list
    logger.info("🏷️  Loading ISBN list...")
    isbn_list_df = pd.read_csv(isbn_list_path, dtype=str).fillna("")
    isbn_list = isbn_list_df.iloc[:, 0].tolist()
    logger.info(f"✓ Loaded {len(isbn_list)} ISBNs")
    
    # Build ISBN to index mapping
    isbn_to_idx = {isbn: i for i, isbn in enumerate(isbn_list)}
    
    # Load FAISS index
    logger.info("⚡ Loading FAISS index...")
    try:
        faiss_index = faiss.read_index(faiss_index_path)
        logger.info(f"✓ Loaded FAISS index with {faiss_index.ntotal} vectors")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load FAISS index: {e}")
    
    # Validate consistency
    if len(df) != len(isbn_list):
        logger.warning(
            f"⚠️  Size mismatch: metadata={len(df)}, isbn_list={len(isbn_list)}"
        )
    
    if embeddings.shape[0] != len(isbn_list):
        logger.warning(
            f"⚠️  Size mismatch: embeddings={embeddings.shape[0]}, isbn_list={len(isbn_list)}"
        )
    
    if faiss_index.ntotal != len(isbn_list):
        logger.warning(
            f"⚠️  Size mismatch: faiss_index={faiss_index.ntotal}, isbn_list={len(isbn_list)}"
        )
    
    metadata_dict = {
        "isbn_to_idx": isbn_to_idx,
        "embeddings_norm": embeddings_norm,
        "num_books": len(df),
        "embedding_dim": embeddings.shape[1],
    }
    
    logger.info("✅ All artifacts loaded successfully!")
    
    return df, embeddings, faiss_index, isbn_list, metadata_dict
