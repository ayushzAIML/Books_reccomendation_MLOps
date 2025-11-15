"""ZenML step to validate pipeline readiness."""

import logging
from typing import Dict, List

from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def validate_pipeline(
    metadata_dict: Dict,
    user_profiles_count: int,
) -> bool:
    """
    Validate that all pipeline components are ready for serving.
    
    This step performs final checks before the pipeline is considered ready
    for handling recommendation requests.
    
    Args:
        metadata_dict: Metadata from artifact loading step
        user_profiles_count: Number of loaded user profiles
    
    Returns:
        True if pipeline is valid, raises exception otherwise
    """
    logger.info("🔍 Validating pipeline readiness...")
    
    checks = {
        "Books loaded": metadata_dict.get("num_books", 0) > 0,
        "Embeddings available": metadata_dict.get("embedding_dim", 0) > 0,
        "ISBN mapping exists": len(metadata_dict.get("isbn_to_idx", {})) > 0,
    }
    
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        logger.info(f"{status} {check_name}")
        if not result:
            raise ValueError(f"❌ Validation failed: {check_name}")
    
    logger.info(f"👥 User profiles loaded: {user_profiles_count}")
    logger.info(f"📊 Total books: {metadata_dict['num_books']}")
    logger.info(f"🔗 Embedding dimension: {metadata_dict['embedding_dim']}")
    logger.info("✅ Pipeline validation passed!")
    
    return True
