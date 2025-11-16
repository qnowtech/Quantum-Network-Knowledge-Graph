"""
Script para exportar datos de Neo4j al formato esperado por React.

Este script:
1. Conecta a Neo4j usando las credenciales del proyecto
2. Extrae todos los nodos y relaciones
3. Transforma los datos al formato esperado por @neo4j-nvl/react
4. Genera un archivo JSON estático que React puede consumir

Uso:
    python src/app/scripts/export_neo4j_data.py

El archivo se genera en: src/app/ui/public/graph-data.json
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Agregar el directorio raíz al path para importar módulos del proyecto
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from neo4j import GraphDatabase

# Cargar credenciales de Neo4j desde múltiples fuentes
def load_neo4j_credentials():
    """
    Carga las credenciales de Neo4j en este orden de prioridad:
    1. Archivo .cursor/mcp.json (configuración MCP)
    2. Variables de entorno
    3. Archivo .env
    4. Valores por defecto del proyecto
    """
    import os
    
    # 1. Intentar leer de .cursor/mcp.json (configuración MCP)
    mcp_config_path = project_root / ".cursor" / "mcp.json"
    if mcp_config_path.exists():
        try:
            with open(mcp_config_path, "r", encoding="utf-8") as f:
                mcp_config = json.load(f)
                mcp_servers = mcp_config.get("mcpServers", {})
                neo4j_config = mcp_servers.get("neo4j-quantum-network-aura", {})
                env_config = neo4j_config.get("env", {})
                
                if env_config.get("NEO4J_URI") and env_config.get("NEO4J_PASSWORD"):
                    print("[OK] Credenciales cargadas desde .cursor/mcp.json")
                    return {
                        "uri": env_config.get("NEO4J_URI"),
                        "user": env_config.get("NEO4J_USERNAME", "neo4j"),
                        "password": env_config.get("NEO4J_PASSWORD"),
                        "database": env_config.get("NEO4J_DATABASE", "neo4j")
                    }
        except Exception as e:
            print(f"[WARN] No se pudo leer .cursor/mcp.json: {e}")
    
    # 2. Intentar variables de entorno
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_QUANTUM_NETWORK_AURA")
    
    if uri and password:
        print("[OK] Credenciales cargadas desde variables de entorno")
        return {
            "uri": uri,
            "user": user or "neo4j",
            "password": password,
            "database": os.getenv("NEO4J_DATABASE", "neo4j")
        }
    
    # 3. Intentar archivo .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_QUANTUM_NETWORK_AURA")
        
        if uri and password:
            print("[OK] Credenciales cargadas desde .env")
            return {
                "uri": uri,
                "user": user or "neo4j",
                "password": password,
                "database": os.getenv("NEO4J_DATABASE", "neo4j")
            }
    except ImportError:
        pass
    
    # 4. Intentar módulo de configuración del proyecto (último recurso)
    try:
        from src.config.conf import settings
        print("[OK] Credenciales cargadas desde src.config.conf")
        return {
            "uri": settings.NEO4J_URI,
            "user": settings.NEO4J_USER,
            "password": settings.NEO4J_QUANTUM_NETWORK_AURA,
            "database": getattr(settings, "NEO4J_DATABASE", "neo4j")
        }
    except Exception as e:
        print(f"[WARN] No se pudo cargar desde src.config.conf: {e}")
    
    # 5. Valores por defecto (solo para desarrollo, sin contraseña)
    print("[WARN] Usando valores por defecto (sin contraseña)")
    return {
        "uri": "neo4j+s://87983fcb.databases.neo4j.io",
        "user": "neo4j",
        "password": "",
        "database": "neo4j"
    }

# Cargar credenciales
credentials = load_neo4j_credentials()
NEO4J_URI = credentials["uri"]
NEO4J_USER = credentials["user"]
NEO4J_PASSWORD = credentials["password"]


def transform_node(node_data: Dict[str, Any], node_id: str) -> Dict[str, Any]:
    """
    Transforma un nodo de Neo4j al formato esperado por @neo4j-nvl/react.
    
    Formato esperado:
    {
        "id": "string",
        "caption": "string",
        "labels": ["string"],
        "properties": {...}
    }
    """
    labels = node_data.get("labels", [])
    properties = {k: v for k, v in node_data.items() if k != "labels"}
    
    # Usar 'name' como caption si está disponible, sino el primer label
    caption = properties.get("name", labels[0] if labels else "Node")
    
    return {
        "id": node_id,
        "caption": str(caption),
        "labels": labels,
        "properties": properties
    }


def transform_relationship(rel_data: Dict[str, Any], rel_id: str, from_id: str, to_id: str) -> Dict[str, Any]:
    """
    Transforma una relación de Neo4j al formato esperado por @neo4j-nvl/react.
    
    Formato esperado:
    {
        "id": "string",
        "from": "string",
        "to": "string",
        "type": "string",
        "caption": "string"
    }
    """
    rel_type = rel_data.get("type", "RELATED_TO")
    
    return {
        "id": rel_id,
        "from": from_id,
        "to": to_id,
        "type": rel_type,
        "caption": rel_type,
        "properties": {k: v for k, v in rel_data.items() if k != "type"}
    }


def extract_graph_data(driver) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extrae todos los nodos y relaciones del grafo de Neo4j.
    
    Returns:
        Dict con 'nodes' y 'relationships'
    """
    nodes = []
    relationships = []
    node_id_map = {}  # Mapea el ID interno de Neo4j a nuestro ID secuencial
    
    with driver.session() as session:
        # Query para obtener todos los nodos con sus propiedades
        nodes_query = """
        MATCH (n)
        RETURN id(n) AS internal_id, labels(n) AS labels, properties(n) AS properties
        ORDER BY internal_id
        """
        
        result = session.run(nodes_query)
        node_counter = 1
        
        for record in result:
            internal_id = record["internal_id"]
            labels = record["labels"]
            properties = record["properties"]
            
            # Crear ID único para el nodo
            node_id = str(node_counter)
            node_id_map[internal_id] = node_id
            
            # Transformar nodo
            node_data = {
                "labels": labels,
                **properties
            }
            nodes.append(transform_node(node_data, node_id))
            node_counter += 1
        
        # Query para obtener todas las relaciones
        rels_query = """
        MATCH (a)-[r]->(b)
        RETURN id(a) AS from_internal_id, id(b) AS to_internal_id, 
               type(r) AS type, properties(r) AS properties, id(r) AS rel_internal_id
        ORDER BY rel_internal_id
        """
        
        result = session.run(rels_query)
        rel_counter = 1
        
        for record in result:
            from_internal_id = record["from_internal_id"]
            to_internal_id = record["to_internal_id"]
            rel_type = record["type"]
            rel_properties = record["properties"]
            
            # Obtener IDs de los nodos
            from_id = node_id_map.get(from_internal_id)
            to_id = node_id_map.get(to_internal_id)
            
            if from_id and to_id:
                rel_id = f"r{rel_counter}"
                rel_data = {
                    "type": rel_type,
                    **rel_properties
                }
                relationships.append(transform_relationship(rel_data, rel_id, from_id, to_id))
                rel_counter += 1
    
    return {
        "nodes": nodes,
        "relationships": relationships
    }


def generate_stats(nodes: List[Dict], relationships: List[Dict]) -> Dict[str, Any]:
    """Genera estadísticas del grafo."""
    node_types = set()
    for node in nodes:
        node_types.update(node.get("labels", []))
    
    rel_types = set()
    for rel in relationships:
        rel_types.add(rel.get("type", "UNKNOWN"))
    
    return {
        "totalNodes": len(nodes),
        "totalRelationships": len(relationships),
        "nodeTypes": sorted(list(node_types)),
        "relationshipTypes": sorted(list(rel_types))
    }


def main():
    """Función principal."""
    print("[INFO] Conectando a Neo4j...")
    
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        
        # Verificar conexión
        driver.verify_connectivity()
        print("[OK] Conexion exitosa a Neo4j")
        
        print("[INFO] Extrayendo datos del grafo...")
        graph_data = extract_graph_data(driver)
        
        # Generar estadísticas
        stats = generate_stats(graph_data["nodes"], graph_data["relationships"])
        
        # Combinar datos
        output_data = {
            "nodes": graph_data["nodes"],
            "relationships": graph_data["relationships"],
            "stats": stats
        }
        
        # Guardar en archivo JSON
        output_path = project_root / "src" / "app" / "ui" / "public" / "graph-data.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"[OK] Datos exportados exitosamente a: {output_path}")
        print(f"   - Nodos: {stats['totalNodes']}")
        print(f"   - Relaciones: {stats['totalRelationships']}")
        print(f"   - Tipos de nodos: {', '.join(stats['nodeTypes'])}")
        print(f"   - Tipos de relaciones: {', '.join(stats['relationshipTypes'])}")
        
        driver.close()
        
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

