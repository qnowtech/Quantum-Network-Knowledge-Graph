"""
Configuration settings for the Quantum Network Knowledge Graph project.

This module uses Pydantic Settings to load configuration from environment
variables and .env files.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Required environment variables:
    - NEO4J_URI: Neo4j connection URI
    - NEO4J_USER: Neo4j username
    - NEO4J_QUANTUM_NETWORK_AURA: Neo4j password
    
    Optional environment variables:
    - CSV_PATH: Path to CSV file (default: "data/quantum_network.csv")
    """
    
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_QUANTUM_NETWORK_AURA: str
    CSV_PATH: Optional[str] = "data/quantum_network.csv"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )


# Global settings instance
settings = Settings()