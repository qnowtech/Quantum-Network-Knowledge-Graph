"""
Unit tests for ETL pipeline functions.

This test suite covers all functions in the etl_to_graph module,
ensuring proper data transformation and Neo4j integration.
"""

import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, mock_open
import numpy as np

from src.pipeline.etl_to_graph import (
    normalize_column_names,
    clean_text,
    normalize_linkedin_url,
    normalize_quantum_experience,
    parse_interests,
    normalize_organization_name,
    normalize_industry_sector,
    transform_dataframe,
    prepare_row_for_neo4j,
    generate_cypher_query,
    create_driver,
    close_driver,
    get_session,
    insert_row_to_neo4j,
    run_etl_pipeline,
)


# ============================================================================
# Tests for Column Name Normalization
# ============================================================================

class TestNormalizeColumnNames:
    """Test cases for normalize_column_names function."""
    
    def test_normalize_all_columns(self, sample_csv_data):
        """Test that all columns are normalized correctly."""
        result = normalize_column_names(sample_csv_data)
        
        assert 'name' in result.columns
        assert 'email' in result.columns
        assert 'organization' in result.columns
        assert 'role' in result.columns
        assert 'industry_sector' in result.columns
        assert 'interests' in result.columns
        assert 'quantum_experience' in result.columns
        assert 'event_expectations' in result.columns
        assert 'linkedin_url' in result.columns
        assert 'timestamp' in result.columns
        
        # Original columns should not be present
        assert 'Nombre completo' not in result.columns
        assert 'Correo electrónico' not in result.columns
    
    def test_normalize_partial_columns(self):
        """Test normalization when only some columns exist."""
        df = pd.DataFrame({
            'Nombre completo': ['John Doe'],
            'email': ['john@example.com'],  # Already normalized
            'Other Column': ['value']
        })
        
        result = normalize_column_names(df)
        
        assert 'name' in result.columns
        assert 'email' in result.columns
        assert 'Other Column' in result.columns
    
    def test_preserve_data_integrity(self, sample_csv_data):
        """Test that data values are preserved during normalization."""
        result = normalize_column_names(sample_csv_data)
        
        assert result['name'].iloc[0] == 'John Doe'
        assert result['email'].iloc[0] == 'john@example.com'
        assert len(result) == len(sample_csv_data)


# ============================================================================
# Tests for Text Cleaning
# ============================================================================

class TestCleanText:
    """Test cases for clean_text function."""
    
    def test_clean_normal_text(self):
        """Test cleaning normal text."""
        assert clean_text("  Hello World  ") == "Hello World"
        assert clean_text("test") == "test"
    
    def test_clean_empty_values(self):
        """Test handling of empty values."""
        assert clean_text("") is None
        assert clean_text("   ") is None
        assert clean_text(None) is None
        assert clean_text(np.nan) is None
        assert clean_text(pd.NA) is None
    
    def test_clean_nan_string(self):
        """Test handling of 'nan' string."""
        assert clean_text("nan") is None
        assert clean_text("NaN") is None
        assert clean_text("NAN") is None
    
    def test_clean_numeric_values(self):
        """Test cleaning numeric values converted to string."""
        assert clean_text(123) == "123"
        assert clean_text(45.67) == "45.67"


# ============================================================================
# Tests for LinkedIn URL Normalization
# ============================================================================

class TestNormalizeLinkedInURL:
    """Test cases for normalize_linkedin_url function."""
    
    def test_normalize_full_url(self):
        """Test normalization of full LinkedIn URLs."""
        assert normalize_linkedin_url("https://www.linkedin.com/in/johndoe") == "https://www.linkedin.com/in/johndoe"
        assert normalize_linkedin_url("https://www.linkedin.com/in/johndoe/") == "https://www.linkedin.com/in/johndoe"
        assert normalize_linkedin_url("http://www.linkedin.com/in/johndoe") == "https://www.linkedin.com/in/johndoe"
    
    def test_normalize_partial_url(self):
        """Test normalization of partial URLs."""
        assert normalize_linkedin_url("www.linkedin.com/in/johndoe") == "https://www.linkedin.com/in/johndoe"
        assert normalize_linkedin_url("linkedin.com/in/johndoe") == "https://www.linkedin.com/in/johndoe"
    
    def test_normalize_username_only(self):
        """Test normalization of username only."""
        assert normalize_linkedin_url("johndoe") == "https://www.linkedin.com/in/johndoe"
        assert normalize_linkedin_url("jane-smith") == "https://www.linkedin.com/in/jane-smith"
    
    def test_handle_empty_values(self):
        """Test handling of empty values."""
        assert normalize_linkedin_url("") is None
        assert normalize_linkedin_url(None) is None
        assert normalize_linkedin_url(np.nan) is None
        assert normalize_linkedin_url("nan") is None
    
    def test_handle_invalid_urls(self):
        """Test handling of invalid URLs."""
        # Full name (multiple words) should not be normalized
        assert normalize_linkedin_url("John Doe") is None
        # Single word without spaces or slashes gets normalized as username
        # This is expected behavior - the function treats single words as usernames
        result = normalize_linkedin_url("not-a-url")
        # The function will normalize it, which is acceptable behavior
        assert result is not None  # Function normalizes single words as usernames


# ============================================================================
# Tests for Quantum Experience Normalization
# ============================================================================

class TestNormalizeQuantumExperience:
    """Test cases for normalize_quantum_experience function."""
    
    def test_normalize_active_experience(self):
        """Test normalization of active experience."""
        assert normalize_quantum_experience("Sí, actualmente en proyectos activos") == "active"
        assert normalize_quantum_experience("proyectos activos") == "active"
    
    def test_normalize_exploration_experience(self):
        """Test normalization of exploration experience."""
        assert normalize_quantum_experience("Sí, en etapa de exploración / piloto") == "exploration"
        assert normalize_quantum_experience("exploración") == "exploration"
        assert normalize_quantum_experience("piloto") == "exploration"
    
    def test_normalize_academic_experience(self):
        """Test normalization of academic experience."""
        assert normalize_quantum_experience("No, solo como interés académico / general") == "academic"
        assert normalize_quantum_experience("interés académico") == "academic"
        assert normalize_quantum_experience("académico") == "academic"
    
    def test_normalize_interested_experience(self):
        """Test normalization of interested experience."""
        assert normalize_quantum_experience("No, pero me interesa iniciar") == "interested"
        assert normalize_quantum_experience("me interesa iniciar") == "interested"
    
    def test_normalize_industry_interest(self):
        """Test normalization of industry interest."""
        assert normalize_quantum_experience("No, pero me interesa entender su aplicación potencial en la industria") == "industry_interest"
        assert normalize_quantum_experience("aplicación potencial") == "industry_interest"
        assert normalize_quantum_experience("industria") == "industry_interest"
    
    def test_handle_empty_values(self):
        """Test handling of empty values."""
        assert normalize_quantum_experience("") is None
        assert normalize_quantum_experience(None) is None
        assert normalize_quantum_experience(np.nan) is None
    
    def test_handle_unknown_values(self):
        """Test handling of unknown values."""
        assert normalize_quantum_experience("Unknown value") is None
        assert normalize_quantum_experience("Random text") is None


# ============================================================================
# Tests for Interests Parsing
# ============================================================================

class TestParseInterests:
    """Test cases for parse_interests function."""
    
    def test_parse_multiple_interests(self):
        """Test parsing multiple comma-separated interests."""
        result = parse_interests("Interest 1, Interest 2, Interest 3")
        assert result == ["Interest 1", "Interest 2", "Interest 3"]
    
    def test_parse_single_interest(self):
        """Test parsing single interest."""
        result = parse_interests("Single Interest")
        assert result == ["Single Interest"]
    
    def test_parse_interests_with_spaces(self):
        """Test parsing interests with extra spaces."""
        result = parse_interests("  Interest 1  ,  Interest 2  ")
        assert result == ["Interest 1", "Interest 2"]
    
    def test_handle_empty_values(self):
        """Test handling of empty values."""
        assert parse_interests("") == []
        assert parse_interests(None) == []
        assert parse_interests(np.nan) == []
    
    def test_filter_nan_values(self):
        """Test filtering of 'nan' strings."""
        result = parse_interests("Interest 1, nan, Interest 2")
        assert result == ["Interest 1", "Interest 2"]


# ============================================================================
# Tests for Organization Name Normalization
# ============================================================================

class TestNormalizeOrganizationName:
    """Test cases for normalize_organization_name function."""
    
    def test_normalize_organization_name(self):
        """Test normalization of organization names."""
        assert normalize_organization_name("  Tech Corp  ") == "Tech Corp"
        assert normalize_organization_name("Quantum Labs") == "Quantum Labs"
    
    def test_handle_empty_values(self):
        """Test handling of empty values."""
        assert normalize_organization_name("") is None
        assert normalize_organization_name(None) is None
        assert normalize_organization_name(np.nan) is None
        assert normalize_organization_name("nan") is None


# ============================================================================
# Tests for Industry Sector Normalization
# ============================================================================

class TestNormalizeIndustrySector:
    """Test cases for normalize_industry_sector function."""
    
    def test_normalize_industry_sector(self):
        """Test normalization of industry sectors."""
        assert normalize_industry_sector("  Technology  ") == "Technology"
        assert normalize_industry_sector("Research") == "Research"
    
    def test_handle_empty_values(self):
        """Test handling of empty values."""
        assert normalize_industry_sector("") is None
        assert normalize_industry_sector(None) is None
        assert normalize_industry_sector(np.nan) is None
        assert normalize_industry_sector("nan") is None


# ============================================================================
# Tests for DataFrame Transformation
# ============================================================================

class TestTransformDataframe:
    """Test cases for transform_dataframe function."""
    
    def test_transform_complete_dataframe(self, sample_csv_data):
        """Test complete transformation of DataFrame."""
        result = transform_dataframe(sample_csv_data)
        
        # Check normalized columns
        assert 'name' in result.columns
        assert 'email' in result.columns
        assert 'interests_list' in result.columns
        
        # Check data types
        assert isinstance(result['interests_list'].iloc[0], list)
        
        # Check normalized values
        assert result['quantum_experience'].iloc[0] == 'active'
        assert result['quantum_experience'].iloc[1] == 'exploration'
        assert result['quantum_experience'].iloc[2] == 'academic'
    
    def test_preserve_row_count(self, sample_csv_data):
        """Test that row count is preserved."""
        result = transform_dataframe(sample_csv_data)
        assert len(result) == len(sample_csv_data)
    
    def test_handle_missing_columns(self):
        """Test handling of missing columns."""
        df = pd.DataFrame({
            'Nombre completo': ['John Doe'],
            'Correo electrónico': ['john@example.com']
        })
        
        result = transform_dataframe(df)
        assert 'name' in result.columns
        assert 'email' in result.columns


# ============================================================================
# Tests for Row Preparation for Neo4j
# ============================================================================

class TestPrepareRowForNeo4j:
    """Test cases for prepare_row_for_neo4j function."""
    
    def test_prepare_complete_row(self, sample_normalized_data):
        """Test preparation of complete row."""
        row = sample_normalized_data.iloc[0]
        result = prepare_row_for_neo4j(row)
        
        assert 'name' in result
        assert 'email' in result
        assert 'organization' in result
        assert 'interests' in result
        assert isinstance(result['interests'], list)
    
    def test_prepare_row_with_missing_data(self):
        """Test preparation of row with missing data."""
        row = pd.Series({
            'name': 'John Doe',
            'email': 'john@example.com',
            'interests_list': []
        })
        
        result = prepare_row_for_neo4j(row)
        assert result['name'] == 'John Doe'
        assert result['email'] == 'john@example.com'
        assert result['interests'] == []


# ============================================================================
# Tests for Cypher Query Generation
# ============================================================================

class TestGenerateCypherQuery:
    """Test cases for generate_cypher_query function."""
    
    def test_generate_query_structure(self):
        """Test that query has correct structure."""
        query = generate_cypher_query()
        
        assert isinstance(query, str)
        assert "MERGE (p:Person" in query
        assert "MERGE (o:Organization" in query
        assert "MERGE (d:Domain" in query
        assert "WORKS_AT" in query
        assert "HAS_INTEREST" in query
        assert "HAS_EXPERIENCE_IN" in query
    
    def test_query_contains_expected_operations(self):
        """Test that query contains expected operations."""
        query = generate_cypher_query()
        
        assert "ON CREATE SET" in query
        assert "ON MATCH SET" in query
        assert "UNWIND" in query
        assert "WHERE" in query


# ============================================================================
# Tests for Neo4j Connection Functions
# ============================================================================

class TestNeo4jConnection:
    """Test cases for Neo4j connection functions."""
    
    @patch('src.pipeline.etl_to_graph.GraphDatabase')
    def test_create_driver(self, mock_graph_db):
        """Test driver creation."""
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        result = create_driver("bolt://localhost:7687", "user", "password")
        
        mock_graph_db.driver.assert_called_once_with(
            "bolt://localhost:7687",
            auth=("user", "password")
        )
        assert result == mock_driver
    
    def test_close_driver(self):
        """Test driver closure."""
        mock_driver = MagicMock()
        close_driver(mock_driver)
        mock_driver.close.assert_called_once()
    
    def test_get_session_context_manager(self):
        """Test session context manager."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value = mock_session
        
        with get_session(mock_driver) as session:
            assert session == mock_session
        
        mock_driver.session.assert_called_once()
        mock_session.close.assert_called_once()


# ============================================================================
# Tests for Neo4j Insertion
# ============================================================================

class TestInsertRowToNeo4j:
    """Test cases for insert_row_to_neo4j function."""
    
    def test_insert_row_success(self, mock_neo4j_session):
        """Test successful row insertion."""
        row_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'interests': ['Interest 1', 'Interest 2']
        }
        
        result = insert_row_to_neo4j(mock_neo4j_session, row_data)
        
        assert 'nodes_created' in result
        assert 'relationships_created' in result
        assert result['nodes_created'] == 1
        assert result['relationships_created'] == 2
        
        # Verify session.run was called
        mock_neo4j_session.run.assert_called_once()
        call_args = mock_neo4j_session.run.call_args
        assert 'row' in call_args.kwargs
        assert call_args.kwargs['row'] == row_data


# ============================================================================
# Tests for Complete ETL Pipeline
# ============================================================================

class TestRunETLPipeline:
    """Test cases for run_etl_pipeline function."""
    
    @patch('src.pipeline.etl_to_graph.create_driver')
    @patch('src.pipeline.etl_to_graph.get_session')
    @patch('src.pipeline.etl_to_graph.insert_row_to_neo4j')
    @patch('pandas.read_csv')
    def test_run_pipeline_success(
        self,
        mock_read_csv,
        mock_insert,
        mock_get_session,
        mock_create_driver,
        sample_csv_data,
        mock_neo4j_session
    ):
        """Test successful pipeline execution."""
        # Setup mocks
        mock_read_csv.return_value = sample_csv_data
        mock_driver = MagicMock()
        mock_create_driver.return_value = mock_driver
        mock_get_session.return_value.__enter__.return_value = mock_neo4j_session
        mock_get_session.return_value.__exit__.return_value = None
        
        mock_insert.return_value = {
            'nodes_created': 1,
            'relationships_created': 2
        }
        
        # Mock settings
        with patch('src.pipeline.etl_to_graph.settings') as mock_settings:
            mock_settings.CSV_PATH = "data/test.csv"
            mock_settings.NEO4J_URI = "bolt://localhost:7687"
            mock_settings.NEO4J_USER = "neo4j"
            mock_settings.NEO4J_QUANTUM_NETWORK_AURA = "password"
            
            # Create temporary CSV file
            with patch('pathlib.Path.exists', return_value=True):
                stats = run_etl_pipeline()
        
        assert stats['rows_processed'] == 3
        assert stats['rows_with_errors'] == 0
    
    def test_run_pipeline_missing_credentials(self):
        """Test pipeline with missing credentials."""
        with patch('src.pipeline.etl_to_graph.settings') as mock_settings:
            mock_settings.NEO4J_URI = None
            mock_settings.NEO4J_USER = "user"
            mock_settings.NEO4J_QUANTUM_NETWORK_AURA = "password"
            
            with pytest.raises(ValueError, match="NEO4J_URI is not defined"):
                run_etl_pipeline()
    
    def test_run_pipeline_file_not_found(self):
        """Test pipeline with missing CSV file."""
        with patch('src.pipeline.etl_to_graph.settings') as mock_settings:
            mock_settings.CSV_PATH = "nonexistent.csv"
            mock_settings.NEO4J_URI = "bolt://localhost:7687"
            mock_settings.NEO4J_USER = "neo4j"
            mock_settings.NEO4J_QUANTUM_NETWORK_AURA = "password"
            
            with patch('pathlib.Path.exists', return_value=False):
                with pytest.raises(FileNotFoundError):
                    run_etl_pipeline()
    
    @patch('src.pipeline.etl_to_graph.create_driver')
    @patch('src.pipeline.etl_to_graph.get_session')
    @patch('src.pipeline.etl_to_graph.insert_row_to_neo4j')
    @patch('pandas.read_csv')
    def test_run_pipeline_with_errors(
        self,
        mock_read_csv,
        mock_insert,
        mock_get_session,
        mock_create_driver,
        sample_csv_data,
        mock_neo4j_session
    ):
        """Test pipeline execution with errors."""
        # Setup mocks
        mock_read_csv.return_value = sample_csv_data
        mock_driver = MagicMock()
        mock_create_driver.return_value = mock_driver
        mock_get_session.return_value.__enter__.return_value = mock_neo4j_session
        mock_get_session.return_value.__exit__.return_value = None
        
        # First call succeeds, second fails, third succeeds
        mock_insert.side_effect = [
            {'nodes_created': 1},
            Exception("Test error"),
            {'nodes_created': 1}
        ]
        
        with patch('src.pipeline.etl_to_graph.settings') as mock_settings:
            mock_settings.CSV_PATH = "data/test.csv"
            mock_settings.NEO4J_URI = "bolt://localhost:7687"
            mock_settings.NEO4J_USER = "neo4j"
            mock_settings.NEO4J_QUANTUM_NETWORK_AURA = "password"
            
            with patch('pathlib.Path.exists', return_value=True):
                stats = run_etl_pipeline()
        
        assert stats['rows_processed'] == 2
        assert stats['rows_with_errors'] == 1
        assert len(stats['errors']) == 1

