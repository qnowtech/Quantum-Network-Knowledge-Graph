"""
Verification script for ETL pipeline.

This script performs basic verification that the pipeline functions
are working correctly without requiring a live Neo4j connection or settings.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import pandas as pd
from unittest.mock import MagicMock, patch

# Set dummy environment variables to avoid Settings validation errors
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_QUANTUM_NETWORK_AURA'] = 'password'

# Now import the functions
from src.pipeline.etl_to_graph import (
    normalize_column_names,
    clean_text,
    normalize_linkedin_url,
    normalize_quantum_experience,
    parse_interests,
    normalize_organization_name,
    normalize_industry_sector,
    transform_dataframe,
    generate_cypher_query,
)


def test_basic_functions():
    """Test basic transformation functions."""
    print("Testing basic transformation functions...")
    
    # Test clean_text
    assert clean_text("  test  ") == "test"
    assert clean_text("") is None
    assert clean_text(None) is None
    print("[PASS] clean_text")
    
    # Test normalize_linkedin_url
    assert normalize_linkedin_url("johndoe") == "https://www.linkedin.com/in/johndoe"
    assert normalize_linkedin_url("https://www.linkedin.com/in/johndoe") == "https://www.linkedin.com/in/johndoe"
    assert normalize_linkedin_url("") is None
    print("[PASS] normalize_linkedin_url")
    
    # Test normalize_quantum_experience
    assert normalize_quantum_experience("Sí, actualmente en proyectos activos") == "active"
    assert normalize_quantum_experience("Sí, en etapa de exploración / piloto") == "exploration"
    assert normalize_quantum_experience("") is None
    print("[PASS] normalize_quantum_experience")
    
    # Test parse_interests
    assert parse_interests("Interest 1, Interest 2") == ["Interest 1", "Interest 2"]
    assert parse_interests("") == []
    print("[PASS] parse_interests")
    
    # Test normalize_organization_name
    assert normalize_organization_name("  Tech Corp  ") == "Tech Corp"
    assert normalize_organization_name("") is None
    print("[PASS] normalize_organization_name")
    
    # Test normalize_industry_sector
    assert normalize_industry_sector("  Technology  ") == "Technology"
    assert normalize_industry_sector("") is None
    print("[PASS] normalize_industry_sector")
    
    # Test generate_cypher_query
    query = generate_cypher_query()
    assert isinstance(query, str)
    assert "MERGE (p:Person" in query
    assert "WORKS_AT" in query
    assert "HAS_INTEREST" in query
    print("[PASS] generate_cypher_query")


def test_dataframe_transformation():
    """Test DataFrame transformation."""
    print("\nTesting DataFrame transformation...")
    
    # Create sample data
    df = pd.DataFrame({
        'Nombre completo': ['John Doe'],
        'Correo electrónico': ['john@example.com'],
        'Organización / Empresa': ['Tech Corp'],
        'Cargo / Rol': ['Engineer'],
        'Sector al que pertenece su organización': ['Technology'],
        'Interés principal en Computación Cuántica - (Seleccionar una o más)': ['Research'],
        '¿Ha trabajado previamente con tecnologías cuánticas?': ['Sí, actualmente en proyectos activos'],
        '¿Qué espera obtener de este evento?': ['Networking'],
        'LinkedIn': ['johndoe'],
        'Timestamp': ['2024-01-01']
    })
    
    # Transform
    result = transform_dataframe(df)
    
    # Verify
    assert 'name' in result.columns
    assert 'email' in result.columns
    assert 'interests_list' in result.columns
    assert result['quantum_experience'].iloc[0] == 'active'
    assert isinstance(result['interests_list'].iloc[0], list)
    assert result['linkedin_url'].iloc[0] == 'https://www.linkedin.com/in/johndoe'
    print("[PASS] transform_dataframe")


def test_column_normalization():
    """Test column name normalization."""
    print("\nTesting column name normalization...")
    
    df = pd.DataFrame({
        'Nombre completo': ['John Doe'],
        'Correo electrónico': ['john@example.com'],
        'Organización / Empresa': ['Tech Corp']
    })
    
    result = normalize_column_names(df)
    
    assert 'name' in result.columns
    assert 'email' in result.columns
    assert 'organization' in result.columns
    assert 'Nombre completo' not in result.columns
    print("[PASS] normalize_column_names")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("ETL Pipeline Verification")
    print("=" * 60)
    
    try:
        test_basic_functions()
        test_column_normalization()
        test_dataframe_transformation()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe pipeline transformation functions are working correctly!")
        return 0
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
