"""
FastAPI server for executing Cypher queries against Neo4j.

This is a monolithic API that provides endpoints to execute strategic queries
from the Quantum Network Knowledge Graph.

Endpoints:
- POST /api/query/execute - Execute a Cypher query
- GET /api/health - Health check
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from neo4j import GraphDatabase
from pydantic import BaseModel, Field
from pathlib import Path
import sys

# Importar configuración y logger del proyecto
from src.config.conf import settings
from src.core.logger import get_logger

# Agregar el directorio raíz al path para importar módulos del proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configurar logger
logger = get_logger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Quantum Network Knowledge Graph API",
    description="API para ejecutar queries Cypher estratégicas contra Neo4j",
    version="1.0.0"
)

# Configurar CORS para permitir llamadas desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente Neo4j (se inicializa al arrancar)
driver: Optional[GraphDatabase.driver] = None


class QueryRequest(BaseModel):
    """Request model para ejecutar una query Cypher."""
    cypher: str = Field(..., description="Query Cypher a ejecutar")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parámetros para la query")


class QueryResponse(BaseModel):
    """Response model con los resultados de la query."""
    success: bool
    data: List[Dict[str, Any]]
    columns: List[str]
    execution_time_ms: float
    records_count: int


class HealthResponse(BaseModel):
    """Response model para health check."""
    status: str
    neo4j_connected: bool
    message: str


class ETLRunRequest(BaseModel):
    """Request model para ejecutar ETL pipeline."""
    clear_before_load: bool = Field(default=False, description="Si True, limpia el grafo antes de cargar")
    csv_path: str = Field(default=None, description="Ruta al archivo CSV (opcional, usa default del proyecto)")


class ETLRunResponse(BaseModel):
    """Response model para ejecución de ETL."""
    success: bool
    message: str
    stats: Dict[str, Any]
    execution_time_ms: float


class ExportGraphResponse(BaseModel):
    """Response model para exportación del grafo."""
    success: bool
    message: str
    output_path: str
    stats: Dict[str, Any]
    execution_time_ms: float


def load_neo4j_credentials() -> Dict[str, str]:
    """
    Carga las credenciales de Neo4j en este orden de prioridad:
    1. Archivo .cursor/mcp.json (configuración MCP)
    2. Variables de entorno (settings)
    3. Valores por defecto
    """
    project_root = Path(__file__).parent.parent.parent
    
    # 1. Intentar leer de .cursor/mcp.json
    mcp_config_path = project_root / ".cursor" / "mcp.json"
    if mcp_config_path.exists():
        try:
            with open(mcp_config_path, "r", encoding="utf-8") as f:
                mcp_config = json.load(f)
                mcp_servers = mcp_config.get("mcpServers", {})
                neo4j_config = mcp_servers.get("neo4j-quantum-network-aura", {})
                env_config = neo4j_config.get("env", {})
                
                if env_config.get("NEO4J_URI") and env_config.get("NEO4J_PASSWORD"):
                    logger.info("Credenciales cargadas desde .cursor/mcp.json")
                    return {
                        "uri": env_config.get("NEO4J_URI"),
                        "user": env_config.get("NEO4J_USERNAME", "neo4j"),
                        "password": env_config.get("NEO4J_PASSWORD"),
                        "database": env_config.get("NEO4J_DATABASE", "neo4j")
                    }
        except Exception as e:
            logger.warning(f"No se pudo leer .cursor/mcp.json: {e}")
    
    # 2. Usar settings (variables de entorno o .env)
    try:
        if settings.NEO4J_URI and settings.NEO4J_QUANTUM_NETWORK_AURA:
            logger.info("Credenciales cargadas desde settings")
            return {
                "uri": settings.NEO4J_URI,
                "user": settings.NEO4J_USER,
                "password": settings.NEO4J_QUANTUM_NETWORK_AURA,
                "database": getattr(settings, "NEO4J_DATABASE", "neo4j")
            }
    except Exception as e:
        logger.warning(f"No se pudo cargar desde settings: {e}")
    
    # 3. Valores por defecto (solo para desarrollo)
    logger.warning("Usando valores por defecto (sin contraseña)")
    return {
        "uri": "neo4j+s://87983fcb.databases.neo4j.io",
        "user": "neo4j",
        "password": "",
        "database": "neo4j"
    }


def get_neo4j_driver() -> GraphDatabase.driver:
    """Obtiene o crea el driver de Neo4j."""
    global driver
    
    if driver is None:
        credentials = load_neo4j_credentials()
        driver = GraphDatabase.driver(
            credentials["uri"],
            auth=(credentials["user"], credentials["password"])
        )
        logger.info(f"Driver Neo4j inicializado: {credentials['uri']}")
    
    return driver


def test_neo4j_connection() -> bool:
    """Prueba la conexión con Neo4j."""
    try:
        test_driver = get_neo4j_driver()
        with test_driver.session() as session:
            result = session.run("RETURN 1 AS test")
            result.consume()
        return True
    except Exception as e:
        logger.error(f"Error conectando a Neo4j: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """Inicializa la conexión con Neo4j al arrancar."""
    logger.info("Iniciando API...")
    if test_neo4j_connection():
        logger.info("✅ Conexión con Neo4j establecida")
    else:
        logger.error("❌ No se pudo conectar a Neo4j")


@app.on_event("shutdown")
async def shutdown_event():
    """Cierra la conexión con Neo4j al apagar."""
    global driver
    if driver:
        driver.close()
        logger.info("Conexión con Neo4j cerrada")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint raíz."""
    return {
        "message": "Quantum Network Knowledge Graph API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    neo4j_connected = test_neo4j_connection()
    return HealthResponse(
        status="healthy" if neo4j_connected else "degraded",
        neo4j_connected=neo4j_connected,
        message="API is running" if neo4j_connected else "API is running but Neo4j connection failed"
    )


@app.post("/api/query/execute", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    Ejecuta una query Cypher contra Neo4j.
    
    Args:
        request: QueryRequest con la query Cypher y parámetros
        
    Returns:
        QueryResponse con los resultados
        
    Raises:
        HTTPException: Si hay un error ejecutando la query
    """
    import time
    
    start_time = time.time()
    
    try:
        # Validar que la query no esté vacía
        if not request.cypher or not request.cypher.strip():
            raise HTTPException(
                status_code=400,
                detail="La query Cypher no puede estar vacía"
            )
        
        # Obtener driver y ejecutar query
        neo4j_driver = get_neo4j_driver()
        credentials = load_neo4j_credentials()
        database = credentials.get("database", "neo4j")
        
        with neo4j_driver.session(database=database) as session:
            logger.info(f"Ejecutando query: {request.cypher[:100]}...")
            logger.debug(f"Parámetros: {request.parameters}")
            
            result = session.run(request.cypher, request.parameters)
            
            # Obtener columnas de los resultados
            keys = result.keys()
            
            # Convertir resultados a lista de diccionarios
            records = []
            for record in result:
                record_dict = {}
                for key in keys:
                    value = record[key]
                    # Convertir tipos especiales de Neo4j a tipos nativos de Python
                    if value is None:
                        record_dict[key] = None
                    elif isinstance(value, (str, int, float, bool)):
                        record_dict[key] = value
                    elif isinstance(value, list):
                        # Convertir listas recursivamente
                        record_dict[key] = [
                            dict(item) if hasattr(item, 'get') else str(item) if hasattr(item, '__dict__') else item
                            for item in value
                        ]
                    elif hasattr(value, 'get'):
                        # Objetos tipo dict (ej: Node, Relationship)
                        record_dict[key] = dict(value)
                    elif hasattr(value, '__dict__'):
                        # Otros objetos de Neo4j, convertir a string
                        record_dict[key] = str(value)
                    else:
                        record_dict[key] = value
                records.append(record_dict)
            
            execution_time = (time.time() - start_time) * 1000  # en milisegundos
            
            logger.info(f"Query ejecutada exitosamente: {len(records)} registros en {execution_time:.2f}ms")
            
            return QueryResponse(
                success=True,
                data=records,
                columns=list(keys),
                execution_time_ms=execution_time,
                records_count=len(records)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"Error ejecutando query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando query: {str(e)}"
        )




# Manejo de excepciones global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones no capturadas."""
    logger.error(f"Excepción no capturada: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Iniciando servidor FastAPI...")
    uvicorn.run(
        "src.api.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

