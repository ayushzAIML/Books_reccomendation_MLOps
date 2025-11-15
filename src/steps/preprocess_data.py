"""[DEPRECATED] Data preprocessing step - kept for backward compatibility.

For the ZenML pipeline, data is expected to be pre-processed.
This module is NOT used in the new ZenML initialization pipeline.

Pre-processed data is expected at: data/processed/books_metadata_with_genre.csv
"""

import logging
from zenml.logger import get_logger

logger = get_logger(__name__)

# This step is no longer used - data should be pre-processed
logger.info(
    "ℹ️  This module is deprecated. "
    "Data should be pre-processed before running the pipeline."
)
