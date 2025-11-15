"""ZenML step to load or initialize user profiles."""

import logging
import os
import json
from typing import Dict

from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def load_user_profiles(user_profile_path: str) -> Dict:
    """
    Load existing user profiles from JSON or initialize empty profiles dict.
    
    This step ensures the user profile file exists and loads all user embeddings
    and preferences for personalization.
    
    Args:
        user_profile_path: Path to user profiles JSON file
    
    Returns:
        Dictionary of user profiles {user_id: {"vector": [...], "liked_isbns": [...]}}
    """
    logger.info("👥 Loading user profiles...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(user_profile_path), exist_ok=True)
    
    # Load or initialize profiles
    if os.path.exists(user_profile_path):
        try:
            with open(user_profile_path, "r") as f:
                user_profiles = json.load(f)
            logger.info(f"✓ Loaded {len(user_profiles)} existing user profiles")
        except json.JSONDecodeError:
            logger.warning(f"⚠️  User profiles JSON corrupted, initializing empty")
            user_profiles = {}
    else:
        logger.info("📝 User profiles file not found, initializing empty")
        user_profiles = {}
        # Create file
        with open(user_profile_path, "w") as f:
            json.dump(user_profiles, f)
    
    logger.info(f"✅ User profiles ready: {len(user_profiles)} profiles in memory")
    
    return user_profiles
