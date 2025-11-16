"""
Pytest configuration and shared fixtures for ETL pipeline tests.
"""

import os
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import MagicMock, Mock

# Set environment variables before any imports that use settings
os.environ.setdefault('NEO4J_URI', 'bolt://localhost:7687')
os.environ.setdefault('NEO4J_USER', 'neo4j')
os.environ.setdefault('NEO4J_QUANTUM_NETWORK_AURA', 'password')


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return pd.DataFrame({
        'Nombre completo': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'Correo electrónico': ['john@example.com', 'jane@example.com', 'bob@example.com'],
        'Organización / Empresa': ['Tech Corp', 'Quantum Labs', 'Research Inc'],
        'Cargo / Rol': ['Engineer', 'Scientist', 'Researcher'],
        'Sector al que pertenece su organización': ['Technology', 'Research', 'Academia'],
        'Interés principal en Computación Cuántica - (Seleccionar una o más)': [
            'Investigación académica, Desarrollo de software',
            'Casos de uso en Finanzas',
            'Investigación académica'
        ],
        '¿Ha trabajado previamente con tecnologías cuánticas?': [
            'Sí, actualmente en proyectos activos',
            'Sí, en etapa de exploración / piloto',
            'No, solo como interés académico / general'
        ],
        '¿Qué espera obtener de este evento?': [
            'Networking',
            'Knowledge sharing',
            'Collaboration'
        ],
        'LinkedIn': [
            'https://www.linkedin.com/in/johndoe',
            'janesmith',
            'www.linkedin.com/in/bobjohnson'
        ],
        'Timestamp': ['2024-01-01', '2024-01-02', '2024-01-03']
    })


@pytest.fixture
def sample_normalized_data():
    """Sample normalized data after transformation."""
    return pd.DataFrame({
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
        'organization': ['Tech Corp', 'Quantum Labs', 'Research Inc'],
        'role': ['Engineer', 'Scientist', 'Researcher'],
        'industry_sector': ['Technology', 'Research', 'Academia'],
        'interests': [
            'Investigación académica, Desarrollo de software',
            'Casos de uso en Finanzas',
            'Investigación académica'
        ],
        'quantum_experience': ['active', 'exploration', 'academic'],
        'event_expectations': ['Networking', 'Knowledge sharing', 'Collaboration'],
        'linkedin_url': [
            'https://www.linkedin.com/in/johndoe',
            'https://www.linkedin.com/in/janesmith',
            'https://www.linkedin.com/in/bobjohnson'
        ],
        'interests_list': [
            ['Investigación académica', 'Desarrollo de software'],
            ['Casos de uso en Finanzas'],
            ['Investigación académica']
        ]
    })


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver for testing."""
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value = session
    return driver, session


@pytest.fixture
def mock_neo4j_session():
    """Mock Neo4j session for testing."""
    session = MagicMock()
    result = MagicMock()
    summary = MagicMock()
    summary.counters = MagicMock()
    summary.counters.nodes_created = 1
    summary.counters.nodes_deleted = 0
    summary.counters.relationships_created = 2
    summary.counters.relationships_deleted = 0
    result.consume.return_value = summary
    session.run.return_value = result
    return session


@pytest.fixture
def temp_csv_file(tmp_path):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_data.csv"
    df = pd.DataFrame({
        'Nombre completo': ['Test User'],
        'Correo electrónico': ['test@example.com'],
        'Organización / Empresa': ['Test Org'],
        'Cargo / Rol': ['Test Role'],
        'Sector al que pertenece su organización': ['Test Sector'],
        'Interés principal en Computación Cuántica - (Seleccionar una o más)': ['Test Interest'],
        '¿Ha trabajado previamente con tecnologías cuánticas?': ['Sí, actualmente en proyectos activos'],
        '¿Qué espera obtener de este evento?': ['Test Expectation'],
        'LinkedIn': ['testuser'],
        'Timestamp': ['2024-01-01']
    })
    df.to_csv(csv_file, index=False)
    return csv_file

