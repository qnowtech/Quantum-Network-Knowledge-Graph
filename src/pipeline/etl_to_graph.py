"""
ETL Pipeline for Quantum Network Knowledge Graph

This module contains the normalization and transformation functions
necessary to process CSV data and load it into Neo4j.

PIPELINE STEPS:
1. EXTRACT: Load CSV file
2. TRANSFORM: Normalize and clean data
3. LOAD: Insert into Neo4j graph database
"""

import logging
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import pandas as pd
from neo4j import Driver, GraphDatabase

from src.config.conf import settings
from src.core.logger import get_logger

# Initialize logger
logger = get_logger(__name__)


# ============================================================================
# STEP 1: COLUMN NAME NORMALIZATION
# ============================================================================

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize CSV column names to more manageable names.
    
    Mapping:
    - 'Nombre completo' -> 'name'
    - 'Correo electrónico' -> 'email'
    - 'Organización / Empresa' -> 'organization'
    - 'Cargo / Rol' -> 'role'
    - 'Sector al que pertenece su organización' -> 'industry_sector'
    - 'Interés principal en Computación Cuántica - (Seleccionar una o más)' -> 'interests'
    - '¿Ha trabajado previamente con tecnologías cuánticas?' -> 'quantum_experience'
    - '¿Qué espera obtener de este evento?' -> 'event_expectations'
    - 'LinkedIn' -> 'linkedin_url'
    
    Args:
        df: DataFrame with original column names
        
    Returns:
        DataFrame with normalized column names
    """
    column_mapping = {
        'Nombre completo': 'name',
        'Correo electrónico': 'email',
        'Organización / Empresa': 'organization',
        'Cargo / Rol': 'role',
        'Sector al que pertenece su organización': 'industry_sector',
        'Interés principal en Computación Cuántica - (Seleccionar una o más)': 'interests',
        '¿Ha trabajado previamente con tecnologías cuánticas?': 'quantum_experience',
        '¿Qué espera obtener de este evento?': 'event_expectations',
        'LinkedIn': 'linkedin_url',
        'Timestamp': 'timestamp'  # Keep timestamp for reference
    }
    
    # Rename only columns that exist
    df_normalized = df.rename(
        columns={k: v for k, v in column_mapping.items() if k in df.columns}
    )
    
    logger.debug(f"Normalized {len(column_mapping)} column names")
    
    return df_normalized


# ============================================================================
# STEP 2: VALUE CLEANING AND NORMALIZATION
# ============================================================================

def clean_text(value: Any) -> Optional[str]:
    """
    Clean text values: remove extra spaces, convert to string,
    handle NaN and empty values.
    
    Args:
        value: Value to clean
        
    Returns:
        Cleaned string or None if empty
    """
    if pd.isna(value) or value == '':
        return None
    
    # Convert to string and clean
    text = str(value).strip()
    
    # If empty after cleaning, return None
    if text == '' or text.lower() == 'nan':
        return None
    
    return text


def normalize_linkedin_url(url: Any) -> Optional[str]:
    """
    Normalize LinkedIn URLs to standard format.
    
    Handles different formats:
    - Full URLs: https://www.linkedin.com/in/username/
    - Partial URLs: www.linkedin.com/in/username
    - Username only: username
    - URLs with errors: http://linkedin.com/in/username (without www)
    
    Args:
        url: LinkedIn URL or username
        
    Returns:
        Normalized URL or None if not valid
    """
    if pd.isna(url) or url == '':
        return None
    
    url_str = str(url).strip()
    
    # If empty, return None
    if url_str == '' or url_str.lower() == 'nan':
        return None
    
    # If already a complete and valid URL, normalize it
    if url_str.startswith('http://') or url_str.startswith('https://'):
        try:
            parsed = urlparse(url_str)
            # Ensure it has the correct domain
            if 'linkedin.com' in parsed.netloc.lower():
                # Normalize to https://www.linkedin.com/in/username
                path = parsed.path.strip('/')
                if path.startswith('in/'):
                    return f"https://www.linkedin.com/{path}"
                elif path.startswith('/in/'):
                    return f"https://www.linkedin.com{path}"
                else:
                    return f"https://www.linkedin.com/in/{path}"
        except Exception:
            logger.debug(f"Failed to parse LinkedIn URL: {url_str}")
            pass
    
    # If starts with www.linkedin.com
    if url_str.startswith('www.linkedin.com') or url_str.startswith('linkedin.com'):
        url_str = url_str.replace('www.', '').replace('linkedin.com', '')
        url_str = url_str.strip('/')
        if url_str.startswith('/in/'):
            return f"https://www.linkedin.com{url_str}"
        elif url_str.startswith('in/'):
            return f"https://www.linkedin.com/{url_str}"
        else:
            return f"https://www.linkedin.com/in/{url_str}"
    
    # If only a username (without URL)
    # Verify it's not a full name (more than one word)
    if ' ' not in url_str and '/' not in url_str:
        return f"https://www.linkedin.com/in/{url_str}"
    
    # If we can't normalize it, return None
    return None


def normalize_quantum_experience(experience: Any) -> Optional[str]:
    """
    Normalize quantum experience values to standard categories.
    
    Possible values:
    - 'active': "Sí, actualmente en proyectos activos"
    - 'exploration': "Sí, en etapa de exploración / piloto"
    - 'academic': "No, solo como interés académico / general"
    - 'interested': "No, pero me interesa iniciar"
    - 'industry_interest': "No, pero me interesa entender su aplicación potencial en la industria"
    
    Args:
        experience: Experience value from CSV
        
    Returns:
        Normalized category or None
    """
    if pd.isna(experience) or experience == '':
        return None
    
    exp_str = str(experience).strip().lower()
    
    if 'actualmente en proyectos activos' in exp_str or 'proyectos activos' in exp_str:
        return 'active'
    elif 'exploración' in exp_str or 'piloto' in exp_str or 'exploracion' in exp_str:
        return 'exploration'
    elif 'interés académico' in exp_str or 'interes academico' in exp_str or 'académico' in exp_str:
        return 'academic'
    elif 'me interesa iniciar' in exp_str or 'interesa iniciar' in exp_str:
        return 'interested'
    elif 'aplicación potencial' in exp_str or 'aplicacion potencial' in exp_str or 'industria' in exp_str:
        return 'industry_interest'
    
    return None


def parse_interests(interests_str: Any) -> List[str]:
    """
    Parse comma-separated interests string into a list.
    
    The 'interests' field may contain values like:
    "Investigación académica, Casos de uso en Finanzas, Desarrollo de software / algoritmos"
    
    Args:
        interests_str: String with comma-separated interests
        
    Returns:
        List of normalized interests
    """
    if pd.isna(interests_str) or interests_str == '':
        return []
    
    interests_list = str(interests_str).split(',')
    
    # Clean each interest
    cleaned_interests = []
    for interest in interests_list:
        cleaned = interest.strip()
        if cleaned and cleaned.lower() != 'nan':
            cleaned_interests.append(cleaned)
    
    return cleaned_interests


def normalize_organization_name(org_name: Any) -> Optional[str]:
    """
    Normalize organization names.
    
    Args:
        org_name: Organization name
        
    Returns:
        Normalized name or None
    """
    if pd.isna(org_name) or org_name == '':
        return None
    
    org_str = str(org_name).strip()
    
    # Clean extra spaces and special characters at start/end
    org_str = re.sub(r'^\s+|\s+$', '', org_str)
    
    if org_str == '' or org_str.lower() == 'nan':
        return None
    
    return org_str


def normalize_industry_sector(sector: Any) -> Optional[str]:
    """
    Normalize industry sector.
    
    Args:
        sector: Industry sector
        
    Returns:
        Normalized sector or None
    """
    if pd.isna(sector) or sector == '':
        return None
    
    sector_str = str(sector).strip()
    
    if sector_str == '' or sector_str.lower() == 'nan':
        return None
    
    return sector_str


# ============================================================================
# STEP 3: COMPLETE DATAFRAME TRANSFORMATION
# ============================================================================

def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all normalization and cleaning transformations to the DataFrame.
    
    Args:
        df: Original DataFrame from CSV
        
    Returns:
        Transformed and normalized DataFrame
    """
    logger.info("Starting DataFrame transformation")
    
    # Step 1: Normalize column names
    df_transformed = normalize_column_names(df.copy())
    
    # Step 2: Clean basic text values
    text_columns = ['name', 'email', 'role', 'organization', 'industry_sector', 
                   'event_expectations']
    
    for col in text_columns:
        if col in df_transformed.columns:
            df_transformed[col] = df_transformed[col].apply(clean_text)
    
    # Step 3: Normalize LinkedIn URLs
    if 'linkedin_url' in df_transformed.columns:
        df_transformed['linkedin_url'] = df_transformed['linkedin_url'].apply(
            normalize_linkedin_url
        )
    
    # Step 4: Normalize quantum experience
    if 'quantum_experience' in df_transformed.columns:
        df_transformed['quantum_experience'] = df_transformed['quantum_experience'].apply(
            normalize_quantum_experience
        )
    
    # Step 5: Parse interests (keep as list for later processing)
    if 'interests' in df_transformed.columns:
        df_transformed['interests_list'] = df_transformed['interests'].apply(
            parse_interests
        )
    
    # Step 6: Normalize organization
    if 'organization' in df_transformed.columns:
        df_transformed['organization'] = df_transformed['organization'].apply(
            normalize_organization_name
        )
    
    # Step 7: Normalize sector
    if 'industry_sector' in df_transformed.columns:
        df_transformed['industry_sector'] = df_transformed['industry_sector'].apply(
            normalize_industry_sector
        )
    
    logger.info(f"DataFrame transformation completed: {len(df_transformed)} rows")
    
    return df_transformed


# ============================================================================
# STEP 4: DATA PREPARATION FOR NEO4J
# ============================================================================

def prepare_row_for_neo4j(row: pd.Series) -> Dict[str, Any]:
    """
    Prepare a DataFrame row for insertion into Neo4j.
    
    Converts the row into a dictionary with normalized data
    ready to use in Cypher queries.
    
    Args:
        row: Pandas Series (one row from DataFrame)
        
    Returns:
        Dictionary with normalized data
    """
    data = {
        'name': row.get('name'),
        'email': row.get('email'),
        'role': row.get('role'),
        'linkedin_url': row.get('linkedin_url'),
        'quantum_experience': row.get('quantum_experience'),
        'event_expectations': row.get('event_expectations'),
        'organization': row.get('organization'),
        'industry_sector': row.get('industry_sector'),
        'interests': row.get('interests_list', []),  # List of interests
    }
    
    return data


# ============================================================================
# STEP 5: CYPHER QUERY GENERATION
# ============================================================================

def generate_cypher_query() -> str:
    """
    Generate the Cypher query to insert data into Neo4j.
    
    This query:
    1. Creates or updates Person nodes
    2. Creates or updates Organization nodes
    3. Creates the WORKS_AT relationship
    4. Creates Domain nodes for each interest (quantum computing areas)
    5. Creates HAS_INTEREST relationships between Person and Domain
    6. Creates HAS_EXPERIENCE_IN relationships based on quantum_experience
    
    The model is designed to facilitate conversations: finding people
    with common interests (same Domains) to initiate dialogues.
    
    Returns:
        String with the Cypher query
    """
    query = """
    // Query to insert a complete row into the graph
    // Expected parameters: $row (dictionary with normalized data)
    // Purpose: Facilitate conversations by connecting people with common interests
    
    UNWIND [$row] AS row
    
    // 1. Create or update Person node
    MERGE (p:Person {email: row.email})
    ON CREATE SET
        p.name = row.name,
        p.role = row.role,
        p.linkedin_url = row.linkedin_url,
        p.quantum_experience = row.quantum_experience,
        p.event_expectations = row.event_expectations,
        p.created_at = datetime()
    ON MATCH SET
        p.name = COALESCE(row.name, p.name),
        p.role = COALESCE(row.role, p.role),
        p.linkedin_url = COALESCE(row.linkedin_url, p.linkedin_url),
        p.quantum_experience = COALESCE(row.quantum_experience, p.quantum_experience),
        p.updated_at = datetime()
    
    // 2. Create or update Organization node
    WITH p, row
    WHERE row.organization IS NOT NULL
    MERGE (o:Organization {name: row.organization})
    ON CREATE SET
        o.industry_sector = row.industry_sector,
        o.created_at = datetime()
    ON MATCH SET
        o.industry_sector = COALESCE(row.industry_sector, o.industry_sector),
        o.updated_at = datetime()
    
    // 3. Create WORKS_AT relationship
    WITH p, o, row
    WHERE row.organization IS NOT NULL
    MERGE (p)-[w:WORKS_AT]->(o)
    ON CREATE SET
        w.created_at = datetime()
    
    // 4. Create Domain nodes for each interest and HAS_INTEREST relationship
    // Domains represent areas of interest in quantum computing
    // This relationship allows finding people with common interests for conversation
    WITH p, o, row
    UNWIND [interest IN row.interests WHERE interest IS NOT NULL AND interest <> ''] AS interest
    MERGE (d:Domain {name: trim(interest)})
    ON CREATE SET
        d.created_at = datetime()
    
    MERGE (p)-[hi:HAS_INTEREST]->(d)
    ON CREATE SET
        hi.created_at = datetime()
    
    // 5. Create HAS_EXPERIENCE_IN relationship based on quantum_experience
    // Only for people with active or exploration experience
    // Connects with all their interest Domains
    WITH p, row
    WHERE row.quantum_experience IN ['active', 'exploration']
    UNWIND [interest IN row.interests WHERE interest IS NOT NULL AND interest <> ''] AS interest
    MATCH (d:Domain {name: trim(interest)})
    MERGE (p)-[e:HAS_EXPERIENCE_IN]->(d)
    ON CREATE SET
        e.experience_level = row.quantum_experience,
        e.created_at = datetime()
    
    RETURN count(p) AS persons_processed
    """
    
    return query


# ============================================================================
# STEP 6: NEO4J CONNECTION FUNCTIONS
# ============================================================================

def create_driver(uri: str, user: str, password: str) -> Driver:
    """
    Create a Neo4j connection driver.
    
    Args:
        uri: Connection URI (e.g., "bolt://localhost:7687")
        user: Neo4j username
        password: Neo4j password
        
    Returns:
        Neo4j Driver instance
    """
    logger.debug(f"Creating Neo4j driver for URI: {uri}")
    return GraphDatabase.driver(uri, auth=(user, password))


def close_driver(driver: Driver) -> None:
    """
    Close the driver connection.
    
    Args:
        driver: Neo4j Driver instance
    """
    logger.debug("Closing Neo4j driver connection")
    driver.close()


@contextmanager
def get_session(driver: Driver):
    """
    Context manager for handling Neo4j sessions.
    
    Usage:
        with get_session(driver) as session:
            # use session
    
    Args:
        driver: Neo4j Driver instance
        
    Yields:
        Neo4j Session instance
    """
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


# ============================================================================
# STEP 7: NEO4J INSERTION FUNCTION
# ============================================================================

def insert_row_to_neo4j(session: Any, row_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert a row of data into Neo4j using the Cypher query.
    
    Args:
        session: Neo4j session
        row_data: Dictionary with normalized row data
        
    Returns:
        Execution result with counters
    """
    query = generate_cypher_query()
    
    result = session.run(query, row=row_data)
    
    # Get the result
    summary = result.consume()
    
    return {
        'nodes_created': summary.counters.nodes_created,
        'nodes_deleted': summary.counters.nodes_deleted,
        'relationships_created': summary.counters.relationships_created,
        'relationships_deleted': summary.counters.relationships_deleted,
    }


# ============================================================================
# STEP 8: COMPLETE ETL PIPELINE
# ============================================================================

def run_etl_pipeline(
    csv_path: Optional[str] = None,
    neo4j_uri: Optional[str] = None,
    neo4j_user: Optional[str] = None,
    neo4j_password: Optional[str] = None,
    batch_size: int = 10
) -> Dict[str, Any]:
    """
    Execute the complete ETL pipeline.
    
    Neo4j credentials and CSV path can be provided as arguments or will be
    loaded from environment variables via Settings:
    - NEO4J_URI: Neo4j connection URI (e.g., "bolt://localhost:7687")
    - NEO4J_USER: Neo4j username
    - NEO4J_QUANTUM_NETWORK_AURA: Neo4j password
    - CSV_PATH: Path to CSV file (optional, default: "data/quantum_network.csv")
    
    Args:
        csv_path: Path to CSV file (optional, uses Settings.CSV_PATH or default)
        neo4j_uri: Neo4j connection URI (optional, uses Settings.NEO4J_URI)
        neo4j_user: Neo4j username (optional, uses Settings.NEO4J_USER)
        neo4j_password: Neo4j password (optional, uses Settings.NEO4J_QUANTUM_NETWORK_AURA)
        batch_size: Batch size for processing (optional, for future optimizations)
        
    Returns:
        Dictionary with process statistics
        
    Raises:
        ValueError: If required credentials are not provided
        FileNotFoundError: If CSV file is not found
    """
    # Get values from Settings if not provided as arguments
    csv_path = csv_path or settings.CSV_PATH
    neo4j_uri = neo4j_uri or settings.NEO4J_URI
    neo4j_user = neo4j_user or settings.NEO4J_USER
    neo4j_password = neo4j_password or settings.NEO4J_QUANTUM_NETWORK_AURA
    
    # Validate that we have the necessary credentials
    if not neo4j_uri:
        raise ValueError(
            "NEO4J_URI is not defined. Provide it as an argument or in environment variables."
        )
    if not neo4j_user:
        raise ValueError(
            "NEO4J_USER is not defined. Provide it as an argument or in environment variables."
        )
    if not neo4j_password:
        raise ValueError(
            "NEO4J_QUANTUM_NETWORK_AURA is not defined. "
            "Provide it as an argument or in environment variables."
        )
    
    stats = {
        'rows_processed': 0,
        'rows_with_errors': 0,
        'errors': []
    }
    
    # EXTRACT: Load CSV
    logger.info("EXTRACT: Loading CSV file")
    logger.info(f"CSV path: {csv_path}")
    
    # Resolve path relative to project root
    csv_file = Path(csv_path)
    if not csv_file.is_absolute():
        # If relative path, resolve from project root
        project_root = Path(__file__).parent.parent.parent
        csv_file = project_root / csv_file
    
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    df = pd.read_csv(csv_file)
    logger.info(f"Loaded {len(df)} rows from CSV")
    
    # TRANSFORM: Normalize and clean
    logger.info("TRANSFORM: Normalizing and cleaning data")
    df_transformed = transform_dataframe(df)
    logger.info(f"DataFrame transformed: {len(df_transformed)} rows")
    logger.debug(f"Columns: {list(df_transformed.columns)}")
    
    # LOAD: Insert into Neo4j
    logger.info("LOAD: Inserting data into Neo4j")
    logger.info(f"Neo4j URI: {neo4j_uri}")
    logger.info(f"Neo4j User: {neo4j_user}")
    
    # Create driver and execute pipeline
    driver = create_driver(neo4j_uri, neo4j_user, neo4j_password)
    
    try:
        with get_session(driver) as session:
            for idx, row in df_transformed.iterrows():
                try:
                    # Prepare row data
                    row_data = prepare_row_for_neo4j(row)
                    
                    # Insert into Neo4j
                    result = insert_row_to_neo4j(session, row_data)
                    
                    stats['rows_processed'] += 1
                    
                    if stats['rows_processed'] % 10 == 0:
                        logger.info(f"Processed {stats['rows_processed']} rows...")
                        
                except Exception as e:
                    stats['rows_with_errors'] += 1
                    stats['errors'].append({
                        'row_index': idx,
                        'error': str(e),
                        'row_data': row_data if 'row_data' in locals() else None
                    })
                    logger.error(f"Error processing row {idx}: {str(e)}", exc_info=True)
    finally:
        close_driver(driver)
    
    logger.info("Pipeline completed successfully")
    logger.info(f"Rows processed: {stats['rows_processed']}")
    logger.info(f"Rows with errors: {stats['rows_with_errors']}")
    
    if stats['errors']:
        logger.warning(f"Total errors encountered: {len(stats['errors'])}")
        for error in stats['errors'][:5]:  # Log first 5 errors
            logger.warning(f"Error in row {error['row_index']}: {error['error']}")
    
    return stats


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Execute the complete ETL pipeline using environment variables.
    
    Required environment variables (via Settings):
    - NEO4J_URI: Neo4j connection URI (e.g., "bolt://localhost:7687")
    - NEO4J_USER: Neo4j username
    - NEO4J_QUANTUM_NETWORK_AURA: Neo4j password
    
    Optional environment variables:
    - CSV_PATH: Path to CSV file (default: "data/quantum_network.csv")
    """
    
    logger.info("=" * 80)
    logger.info("EXECUTING ETL PIPELINE")
    logger.info("=" * 80)
    
    try:
        # Execute pipeline (uses Settings automatically)
        stats = run_etl_pipeline()
        
        logger.info("=" * 80)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total rows processed: {stats['rows_processed']}")
        logger.info(f"Total errors: {stats['rows_with_errors']}")
        
        if stats['errors']:
            logger.info("Errors found:")
            for error in stats['errors'][:5]:  # Show only first 5
                logger.info(f"  - Row {error['row_index']}: {error['error']}")
            if len(stats['errors']) > 5:
                logger.info(f"  ... and {len(stats['errors']) - 5} more errors")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Make sure you have configured the following environment variables:")
        logger.error("  - NEO4J_URI")
        logger.error("  - NEO4J_USER")
        logger.error("  - NEO4J_QUANTUM_NETWORK_AURA")
        logger.error("Or provide these values as arguments to run_etl_pipeline()")
        raise
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        raise
