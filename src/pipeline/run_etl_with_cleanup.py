"""
Script to run ETL pipeline with graph cleanup.

This script executes the complete ETL pipeline and clears the graph
before loading to avoid duplicates.

Usage:
    python src/app/scripts/run_etl_with_cleanup.py

Or set environment variable:
    CLEAR_BEFORE_LOAD=true python src/pipeline/etl_to_graph.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.etl_to_graph import run_etl_pipeline
from src.core.logger import get_logger

logger = get_logger(__name__)


def main():
    """Run ETL pipeline with cleanup enabled."""
    logger.info("=" * 80)
    logger.info("ETL PIPELINE WITH GRAPH CLEANUP")
    logger.info("=" * 80)
    logger.warning("This will DELETE ALL existing data in Neo4j before loading!")
    logger.info("")
    
    try:
        # Run pipeline with cleanup enabled
        stats = run_etl_pipeline(clear_before_load=True)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Rows processed: {stats['rows_processed']}")
        logger.info(f"Rows with errors: {stats['rows_with_errors']}")
        
        if 'graph_cleared' in stats:
            cleared = stats['graph_cleared']
            logger.info(f"Graph cleared: {cleared['nodes_deleted']} nodes, "
                       f"{cleared['relationships_deleted']} relationships")
        
        if stats['errors']:
            logger.warning(f"Errors encountered: {len(stats['errors'])}")
            for error in stats['errors'][:5]:
                logger.warning(f"  - Row {error['row_index']}: {error['error']}")
        else:
            logger.info("✓ No errors encountered!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

