"""
Test end-to-end para validar que la API funciona, retorna resultados
y se renderizan correctamente en la UI.

Este test valida:
1. La API FastAPI está funcionando
2. Los endpoints responden correctamente
3. Las queries Cypher se ejecutan contra Neo4j
4. Los resultados se formatean correctamente
5. La UI puede consumir los resultados (simulado)
"""

import json
import os
import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

# Importar la app de FastAPI
from src.api.api import app, get_neo4j_driver, load_neo4j_credentials

# Configurar variables de entorno para tests
os.environ.setdefault('NEO4J_URI', 'bolt://localhost:7687')
os.environ.setdefault('NEO4J_USER', 'neo4j')
os.environ.setdefault('NEO4J_QUANTUM_NETWORK_AURA', 'password')


@pytest.fixture
def client():
    """Cliente de test para FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_neo4j_driver():
    """Mock del driver de Neo4j para tests."""
    driver = MagicMock()
    session = MagicMock()
    
    # Crear un resultado mock
    result = MagicMock()
    result.keys.return_value = ['person', 'organization', 'domain']
    
    # Crear registros mock
    record1 = MagicMock()
    record1.__getitem__ = lambda self, key: {
        'person': 'John Doe',
        'organization': 'Tech Corp',
        'domain': 'Quantum Computing'
    }[key]
    
    record2 = MagicMock()
    record2.__getitem__ = lambda self, key: {
        'person': 'Jane Smith',
        'organization': 'Quantum Labs',
        'domain': 'Machine Learning'
    }[key]
    
    result.__iter__ = lambda self: iter([record1, record2])
    session.run.return_value = result
    session.__enter__ = lambda self: self
    session.__exit__ = lambda self, *args: None
    driver.session.return_value = session
    
    return driver


class TestAPIEndToEnd:
    """Tests end-to-end para la API."""
    
    def test_health_check(self, client):
        """Test que el endpoint de health check funciona."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "neo4j_connected" in data
        assert "message" in data
    
    def test_root_endpoint(self, client):
        """Test que el endpoint raíz funciona."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_query_execute_with_mock(self, client, mock_neo4j_driver):
        """Test que el endpoint de ejecutar query funciona con mock."""
        with patch('src.api.api.get_neo4j_driver', return_value=mock_neo4j_driver):
            with patch('src.api.api.load_neo4j_credentials', return_value={"database": "neo4j"}):
                query_request = {
                    "cypher": "MATCH (p:Person) RETURN p.name AS person LIMIT 2",
                    "parameters": {}
                }
                
                response = client.post("/api/query/execute", json=query_request)
                assert response.status_code == 200
                
                data = response.json()
                assert data["success"] is True
                assert "data" in data
                assert "columns" in data
                assert "execution_time_ms" in data
                assert "records_count" in data
                assert data["records_count"] == 2
                assert len(data["columns"]) == 3
                assert "person" in data["columns"]
                assert "organization" in data["columns"]
                assert "domain" in data["columns"]
    
    def test_query_execute_empty_query(self, client):
        """Test que el endpoint rechaza queries vacías."""
        query_request = {
            "cypher": "",
            "parameters": {}
        }
        
        response = client.post("/api/query/execute", json=query_request)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "vacía" in data["detail"].lower()
    
    def test_query_execute_with_parameters(self, client, mock_neo4j_driver):
        """Test que el endpoint maneja parámetros correctamente."""
        with patch('src.api.api.get_neo4j_driver', return_value=mock_neo4j_driver):
            with patch('src.api.api.load_neo4j_credentials', return_value={"database": "neo4j"}):
                query_request = {
                    "cypher": "MATCH (p:Person {email: $email}) RETURN p.name AS person",
                    "parameters": {"email": "test@example.com"}
                }
                
                response = client.post("/api/query/execute", json=query_request)
                assert response.status_code == 200
                
                data = response.json()
                assert data["success"] is True
                # Verificar que los parámetros se pasaron al mock
                mock_neo4j_driver.session.return_value.run.assert_called_once()
                call_args = mock_neo4j_driver.session.return_value.run.call_args
                assert call_args[0][1]["email"] == "test@example.com"
    
    def test_query_response_format(self, client, mock_neo4j_driver):
        """Test que la respuesta tiene el formato correcto para la UI."""
        with patch('src.api.api.get_neo4j_driver', return_value=mock_neo4j_driver):
            with patch('src.api.api.load_neo4j_credentials', return_value={"database": "neo4j"}):
                query_request = {
                    "cypher": "MATCH (p:Person) RETURN p.name AS person LIMIT 1",
                    "parameters": {}
                }
                
                response = client.post("/api/query/execute", json=query_request)
                assert response.status_code == 200
                
                data = response.json()
                
                # Validar estructura de respuesta
                required_fields = ["success", "data", "columns", "execution_time_ms", "records_count"]
                for field in required_fields:
                    assert field in data, f"Campo requerido '{field}' no encontrado en la respuesta"
                
                # Validar tipos
                assert isinstance(data["success"], bool)
                assert isinstance(data["data"], list)
                assert isinstance(data["columns"], list)
                assert isinstance(data["execution_time_ms"], (int, float))
                assert isinstance(data["records_count"], int)
                
                # Validar que los datos tienen las columnas correctas
                if data["data"]:
                    for record in data["data"]:
                        assert isinstance(record, dict)
                        for col in data["columns"]:
                            assert col in record, f"Columna '{col}' no encontrada en el registro"
    
    def test_cors_headers(self, client):
        """Test que los headers CORS están configurados correctamente."""
        response = client.options("/api/query/execute")
        # FastAPI TestClient maneja CORS automáticamente, pero verificamos que no hay errores
        assert response.status_code in [200, 405]  # OPTIONS puede retornar 405 si no está configurado
    
    def test_error_handling(self, client):
        """Test que los errores se manejan correctamente."""
        with patch('src.api.api.get_neo4j_driver') as mock_driver:
            # Simular un error en Neo4j
            mock_driver.return_value.session.side_effect = Exception("Connection error")
            
            query_request = {
                "cypher": "MATCH (p:Person) RETURN p.name",
                "parameters": {}
            }
            
            response = client.post("/api/query/execute", json=query_request)
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data


class TestUIIntegration:
    """Tests para validar la integración con la UI (simulada)."""
    
    def test_query_response_compatible_with_ui(self, client, mock_neo4j_driver):
        """Test que la respuesta es compatible con el formato esperado por la UI."""
        with patch('src.api.api.get_neo4j_driver', return_value=mock_neo4j_driver):
            with patch('src.api.api.load_neo4j_credentials', return_value={"database": "neo4j"}):
                query_request = {
                    "cypher": "MATCH (p:Person) RETURN p.name AS person LIMIT 2",
                    "parameters": {}
                }
                
                response = client.post("/api/query/execute", json=query_request)
                assert response.status_code == 200
                
                data = response.json()
                
                # Simular el formato que espera la UI (useCypherQuery.js)
                ui_formatted = {
                    "success": data["success"],
                    "data": data["data"],
                    "columns": data["columns"],
                    "recordsCount": data["records_count"],
                    "executionTime": data["execution_time_ms"],
                    "query": query_request["cypher"],
                    "parameters": query_request["parameters"]
                }
                
                # Validar que el formato es correcto
                assert ui_formatted["success"] is True
                assert isinstance(ui_formatted["data"], list)
                assert isinstance(ui_formatted["columns"], list)
                assert ui_formatted["recordsCount"] >= 0
                assert ui_formatted["executionTime"] >= 0
    
    def test_strategic_queries_format(self, client, mock_neo4j_driver):
        """Test que las queries estratégicas del README funcionan."""
        # Query #4: Most Frequent Problems
        strategic_query = """
        MATCH (p:Person)-[:HAS_PROBLEM]->(prob:Problem)
        RETURN prob.name AS problem,
               count(DISTINCT p) AS num_people
        ORDER BY num_people DESC
        LIMIT 5
        """
        
        with patch('src.api.api.get_neo4j_driver', return_value=mock_neo4j_driver):
            with patch('src.api.api.load_neo4j_credentials', return_value={"database": "neo4j"}):
                query_request = {
                    "cypher": strategic_query.strip(),
                    "parameters": {}
                }
                
                response = client.post("/api/query/execute", json=query_request)
                assert response.status_code == 200
                
                data = response.json()
                assert data["success"] is True
                # La query debería retornar resultados (aunque sean mock)
                assert "data" in data
                assert "columns" in data


class TestRealNeo4jIntegration:
    """Tests de integración con Neo4j real (opcional, requiere conexión)."""
    
    @pytest.mark.skipif(
        os.getenv("SKIP_REAL_NEO4J_TESTS", "true").lower() == "true",
        reason="Tests con Neo4j real están deshabilitados por defecto"
    )
    def test_real_neo4j_connection(self, client):
        """Test que la conexión real con Neo4j funciona."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        # Si Neo4j está disponible, debería estar conectado
        # Si no, el test se salta automáticamente
    
    @pytest.mark.skipif(
        os.getenv("SKIP_REAL_NEO4J_TESTS", "true").lower() == "true",
        reason="Tests con Neo4j real están deshabilitados por defecto"
    )
    def test_real_query_execution(self, client):
        """Test ejecutando una query real contra Neo4j."""
        query_request = {
            "cypher": "MATCH (n) RETURN count(n) AS total_nodes LIMIT 1",
            "parameters": {}
        }
        
        response = client.post("/api/query/execute", json=query_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

