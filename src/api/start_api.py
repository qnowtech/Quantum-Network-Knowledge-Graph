"""
Script para iniciar el servidor FastAPI.

Uso:
    python src/api/start_api.py

O con uvicorn directamente:
    uvicorn src.api.api:app --reload --host 0.0.0.0 --port 8000
"""

import uvicorn
from src.core.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Iniciando servidor FastAPI...")
    logger.info("API disponible en: http://localhost:8000")
    logger.info("Documentación disponible en: http://localhost:8000/docs")
    
    uvicorn.run(
        "src.api.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

