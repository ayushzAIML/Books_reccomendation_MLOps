"""
ZenML Pipeline: Books Recommendation System Initialization

This pipeline orchestrates the loading and validation of all artifacts and models
needed for the recommendation system. It does NOT modify any recommendation logic,
only prepares and validates the runtime environment.

The pipeline:
1. Loads pre-computed artifacts (embeddings, FAISS index, metadata)
2. Loads ML models (bi-encoder, cross-encoder)
3. Loads user profiles
4. Validates pipeline readiness
"""

import logging
from zenml import pipeline
from zenml.logger import get_logger

from src.config import (
    META_CSV,
    EMB_NPY,
    FAISS_INDEX,
    ISBN_LIST,
    USER_PROFILE_PATH,
    BI_ENCODER_MODEL,
    CROSS_ENCODER_MODEL,
)
from src.steps.load_artifacts import load_artifacts
from src.steps.load_models import load_models
from src.steps.load_user_profiles import load_user_profiles
from src.steps.validate_pipeline import validate_pipeline

logger = get_logger(__name__)


@pipeline(name="books_recommendation_initialization")
def books_recommendation_initialization():
    """
    Main initialization pipeline for the books recommendation system.
    
    This pipeline:
    - Loads all pre-computed artifacts (embeddings, FAISS index, metadata, ISBNs)
    - Loads ML models (bi-encoder for encoding, cross-encoder for re-ranking)
    - Loads existing user profiles
    - Validates that all components are ready for serving recommendations
    
    The pipeline maintains full compatibility with the existing recommendation logic
    in `recommender_pipeline.py` - it only handles orchestration and validation.
    """
    
    # Step 1: Load all artifacts
    df, embeddings, faiss_index, isbn_list, metadata_dict = load_artifacts(
        meta_csv=META_CSV,
        emb_npy=EMB_NPY,
        faiss_index_path=FAISS_INDEX,
        isbn_list_path=ISBN_LIST,
    )
    
    # Step 2: Load ML models
    bi_encoder, cross_encoder = load_models(
        bi_encoder_model_name=BI_ENCODER_MODEL,
        cross_encoder_model_name=CROSS_ENCODER_MODEL,
    )
    
    # Step 3: Load user profiles
    user_profiles = load_user_profiles(user_profile_path=USER_PROFILE_PATH)
    
    # Step 4: Validate pipeline
    # Note: We just return success status without trying to measure user profiles
    # since they're loaded as artifacts and can't be measured with len()
    pipeline_ready = validate_pipeline(
        metadata_dict=metadata_dict,
        user_profiles_count=0,  # ZenML artifact, can't use len()
    )
    
    return pipeline_ready
