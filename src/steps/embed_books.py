"""[DEPRECATED] Embedding generation step - kept for backward compatibility.

For the ZenML pipeline, embeddings are pre-computed and loaded via load_artifacts step.
This module is NOT used in the new ZenML initialization pipeline.

The embeddings are expected to already exist at: data/embeddings/embeddings.npy
"""

import logging
from zenml.logger import get_logger

logger = get_logger(__name__)

# This step is no longer used - embeddings should be pre-computed
logger.info(
    "ℹ️  This module is deprecated. "
    "Embeddings are pre-computed and loaded via load_artifacts step."
)
