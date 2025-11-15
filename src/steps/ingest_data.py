"""[DEPRECATED] This step is kept for backward compatibility only.

For the ZenML pipeline, use load_artifacts step instead.
This module is NOT used in the new ZenML initialization pipeline.
"""

import logging
import pandas as pd
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def ingest_data(meta_csv: str = "./data/processed/books_metadata_with_genre.csv") -> pd.DataFrame:
    """
    [DEPRECATED] Legacy data ingestion step.
    
    Use load_artifacts from steps/load_artifacts.py instead.
    This is kept only for backward compatibility.
    
    Args:
        meta_csv: Path to metadata CSV
        
    Returns:
        Metadata DataFrame
    """
    logger.warning(
        "⚠️  This step is deprecated. Use load_artifacts from steps/load_artifacts.py"
    )
    
    try:
        df = pd.read_csv(meta_csv)
        logger.info(f"Loaded {len(df)} rows from metadata CSV")
        return df
    except Exception as e:
        logger.error(f"Error in data ingestion: {e}")
        raise e
    






