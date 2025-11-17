"""
End-to-End Test for ETL Pipeline with LLM Integration

This script tests the complete ETL pipeline including:
1. CSV loading
2. Data transformation
3. LLM-based problem inference
4. Graph cleanup
5. Neo4j data loading

Run this script to validate the entire pipeline works correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.etl_to_graph import (
    run_etl_pipeline,
    clear_graph,
    create_driver,
    get_session,
    close_driver
)
from src.config.conf import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


def test_graph_cleanup():
    """Test the graph cleanup function."""
    logger.info("=" * 80)
    logger.info("TEST: Graph Cleanup Function")
    logger.info("=" * 80)
    
    neo4j_uri = settings.NEO4J_URI
    neo4j_user = settings.NEO4J_USER
    neo4j_password = settings.NEO4J_QUANTUM_NETWORK_AURA
    
    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        logger.error("Neo4j credentials not configured. Skipping test.")
        return False
    
    driver = create_driver(neo4j_uri, neo4j_user, neo4j_password)
    
    try:
        with get_session(driver) as session:
            # Test cleanup function
            clear_stats = clear_graph(session, confirm=True)
            logger.info(f"Cleanup successful:")
            logger.info(f"  - Nodes deleted: {clear_stats['nodes_deleted']}")
            logger.info(f"  - Relationships deleted: {clear_stats['relationships_deleted']}")
            return True
    except Exception as e:
        logger.error(f"Error during cleanup test: {e}", exc_info=True)
        return False
    finally:
        close_driver(driver)


def test_etl_pipeline_with_cleanup():
    """Test the complete ETL pipeline with graph cleanup."""
    logger.info("=" * 80)
    logger.info("TEST: Complete ETL Pipeline (with cleanup)")
    logger.info("=" * 80)
    
    try:
        # Run pipeline with cleanup enabled
        stats = run_etl_pipeline(clear_before_load=True)
        
        logger.info("=" * 80)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Rows processed: {stats['rows_processed']}")
        logger.info(f"Rows with errors: {stats['rows_with_errors']}")
        
        if 'graph_cleared' in stats:
            logger.info(f"Graph cleared: {stats['graph_cleared']}")
        
        if stats['errors']:
            logger.warning(f"Total errors: {len(stats['errors'])}")
            for error in stats['errors'][:5]:
                logger.warning(f"  - Row {error['row_index']}: {error['error']}")
        else:
            logger.info("No errors encountered!")
        
        return stats['rows_with_errors'] == 0
        
    except Exception as e:
        logger.error(f"Error during ETL pipeline test: {e}", exc_info=True)
        return False


def test_etl_pipeline_without_cleanup():
    """Test the ETL pipeline without cleanup (incremental load)."""
    logger.info("=" * 80)
    logger.info("TEST: ETL Pipeline (without cleanup - incremental)")
    logger.info("=" * 80)
    
    try:
        # Run pipeline without cleanup (incremental load)
        stats = run_etl_pipeline(clear_before_load=False)
        
        logger.info("=" * 80)
        logger.info("INCREMENTAL LOAD SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Rows processed: {stats['rows_processed']}")
        logger.info(f"Rows with errors: {stats['rows_with_errors']}")
        
        if stats['errors']:
            logger.warning(f"Total errors: {len(stats['errors'])}")
        else:
            logger.info("No errors encountered!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during incremental load test: {e}", exc_info=True)
        return False


def main():
    """Run all end-to-end tests."""
    logger.info("=" * 80)
    logger.info("END-TO-END ETL PIPELINE TEST")
    logger.info("=" * 80)
    logger.info("")
    
    # Check configuration
    logger.info("Checking configuration...")
    if not settings.NEO4J_URI:
        logger.error("NEO4J_URI not configured")
        return 1
    if not settings.NEO4J_USER:
        logger.error("NEO4J_USER not configured")
        return 1
    if not settings.NEO4J_QUANTUM_NETWORK_AURA:
        logger.error("NEO4J_QUANTUM_NETWORK_AURA not configured")
        return 1
    
    csv_path = settings.CSV_PATH or "data/quantum_network.csv"
    csv_file = project_root / csv_path
    if not csv_file.exists():
        logger.error(f"CSV file not found: {csv_file}")
        return 1
    
    logger.info("Configuration OK")
    logger.info("")
    
    # Run tests
    results = {}
    
    # Test 1: Graph cleanup
    logger.info("Running Test 1: Graph Cleanup...")
    results['cleanup'] = test_graph_cleanup()
    logger.info("")
    
    # Test 2: Complete pipeline with cleanup
    logger.info("Running Test 2: Complete ETL Pipeline (with cleanup)...")
    results['full_pipeline'] = test_etl_pipeline_with_cleanup()
    logger.info("")
    
    # Test 3: Incremental load (optional - comment out if you don't want to test this)
    # logger.info("Running Test 3: Incremental Load...")
    # results['incremental'] = test_etl_pipeline_without_cleanup()
    # logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("")
        logger.info("All tests passed!")
        return 0
    else:
        logger.error("")
        logger.error("Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

