"""[DEPRECATED] FAISS index building step - kept for backward compatibility.

For the ZenML pipeline, the FAISS index is pre-built and loaded via load_artifacts step.
This module is NOT used in the new ZenML initialization pipeline.

The FAISS index is expected to already exist at: data/faiss/faiss_index.bin
"""

import logging
from zenml.logger import get_logger

logger = get_logger(__name__)

# This step is no longer used - FAISS index should be pre-built
logger.info(
    "ℹ️  This module is deprecated. "
    "FAISS index is pre-built and loaded via load_artifacts step."
)
