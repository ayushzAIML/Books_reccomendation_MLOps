"""ZenML step to load ML models for embedding and cross-encoding."""

import logging
from typing import Tuple

from zenml import step
from zenml.logger import get_logger
from sentence_transformers import SentenceTransformer, CrossEncoder

logger = get_logger(__name__)


@step
def load_models(
    bi_encoder_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    cross_encoder_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
) -> Tuple[SentenceTransformer, CrossEncoder]:
    """
    Load SentenceTransformer bi-encoder and cross-encoder models.
    
    This step downloads/loads pre-trained models for query encoding and 
    semantic relevance scoring.
    
    Args:
        bi_encoder_model_name: HuggingFace model ID for bi-encoder
        cross_encoder_model_name: HuggingFace model ID for cross-encoder
    
    Returns:
        Tuple of (bi_encoder, cross_encoder) models
    """
    logger.info("🤖 Loading ML models...")
    
    logger.info(f"⏳ Loading bi-encoder: {bi_encoder_model_name}")
    try:
        bi_encoder = SentenceTransformer(bi_encoder_model_name)
        logger.info(f"✓ Bi-encoder loaded successfully")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load bi-encoder: {e}")
    
    logger.info(f"⏳ Loading cross-encoder: {cross_encoder_model_name}")
    try:
        cross_encoder = CrossEncoder(cross_encoder_model_name)
        logger.info(f"✓ Cross-encoder loaded successfully")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load cross-encoder: {e}")
    
    logger.info("✅ All models loaded successfully!")
    
    return bi_encoder, cross_encoder
