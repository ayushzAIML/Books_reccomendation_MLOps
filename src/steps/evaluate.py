"""[DEPRECATED] Model evaluation step - kept for backward compatibility.

For the ZenML pipeline, model evaluation should be done separately.
This module is NOT used in the new ZenML initialization pipeline.

Use validate_pipeline step to check if all components are ready.
"""

import logging
from zenml.logger import get_logger

logger = get_logger(__name__)

# This step is no longer used - use validate_pipeline instead
logger.info(
    "ℹ️  This module is deprecated. "
    "Use validate_pipeline step for pipeline readiness checks."
)
