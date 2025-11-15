"""[DEPRECATED] Model training step - kept for backward compatibility.

For the ZenML pipeline, models are pre-trained and loaded via load_models step.
This module is NOT used in the new ZenML initialization pipeline.

Models are loaded from HuggingFace:
- Bi-encoder: sentence-transformers/all-MiniLM-L6-v2
- Cross-encoder: cross-encoder/ms-marco-MiniLM-L-6-v2
"""

import logging
from zenml.logger import get_logger

logger = get_logger(__name__)

# This step is no longer used - models should be pre-trained
logger.info(
    "ℹ️  This module is deprecated. "
    "ML models are loaded from HuggingFace via load_models step."
)
