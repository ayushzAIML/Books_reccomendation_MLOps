"""
Run ZenML Pipeline for Books Recommendation System

This script initializes and runs the ZenML pipeline for loading and validating
all artifacts and models needed by the recommendation system.

Usage:
    python src/run_zenml_pipeline.py
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from zenml_pipelines import books_recommendation_initialization


def main():
    """Run the initialization pipeline."""
    logger.info("=" * 80)
    logger.info(" Starting ZenML Books Recommendation Pipeline")
    logger.info("=" * 80)
    
    try:
        # Run the pipeline
        logger.info("\n📋 Executing pipeline...")
        result = books_recommendation_initialization()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Pipeline executed successfully!")
        logger.info("=" * 80)
        logger.info(f"Result: {result}")
        
        return 0
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f" Pipeline execution failed: {e}")
        logger.error("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
