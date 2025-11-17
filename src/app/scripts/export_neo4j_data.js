/**
 * Script para exportar datos de Neo4j al formato esperado por React.
 *
 * Este script:
 * 1. Conecta a Neo4j usando las credenciales del proyecto
 * 2. Extrae todos los nodos y relaciones
 * 3. Transforma los datos al formato esperado por @neo4j-nvl/react
 * 4. Genera un archivo JSON estático que React puede consumir
 *
 * Uso:
 *     node src/app/scripts/export_neo4j_data.js
 *
 * El archivo se genera en: src/app/ui/public/graph-data.json
 */

const neo4j = require('neo4j-driver');
const fs = require('fs');
const path = require('path');

// Obtener la ruta raíz del proyecto
const projectRoot = path.resolve(__dirname, '..', '..', '..', '..');

/**
 * Carga las credenciales de Neo4j en este orden de prioridad:
 * 1. Archivo .cursor/mcp.json (configuración MCP)
 * 2. Variables de entorno
 * 3. Archivo .env
 * 4. Valores por defecto del proyecto
 */
function loadNeo4jCredentials() {
    // 1. Intentar leer de .cursor/mcp.json (configuración MCP)
    const mcpConfigPath = path.join(projectRoot, '.cursor', 'mcp.json');
    if (fs.existsSync(mcpConfigPath)) {
        try {
            const mcpConfig = JSON.parse(fs.readFileSync(mcpConfigPath, 'utf-8'));
            const mcpServers = mcpConfig.mcpServers || {};
            const neo4jConfig = mcpServers['neo4j-quantum-network-aura'] || {};
            const envConfig = neo4jConfig.env || {};
            
            if (envConfig.NEO4J_URI && envConfig.NEO4J_PASSWORD) {
                console.log('[OK] Credenciales cargadas desde .cursor/mcp.json');
                return {
                    uri: envConfig.NEO4J_URI,
                    user: envConfig.NEO4J_USERNAME || 'neo4j',
                    password: envConfig.NEO4J_PASSWORD,
                    database: envConfig.NEO4J_DATABASE || 'neo4j'
                };
            }
        } catch (error) {
            console.warn(`[WARN] No se pudo leer .cursor/mcp.json: ${error.message}`);
        }
    }
    
    // 2. Intentar variables de entorno
    const uri = process.env.NEO4J_URI;
    const user = process.env.NEO4J_USERNAME || process.env.NEO4J_USER;
    const password = process.env.NEO4J_PASSWORD || process.env.NEO4J_QUANTUM_NETWORK_AURA;
    
    if (uri && password) {
        console.log('[OK] Credenciales cargadas desde variables de entorno');
        return {
            uri: uri,
            user: user || 'neo4j',
            password: password,
            database: process.env.NEO4J_DATABASE || 'neo4j'
        };
    }
    
    // 3. Intentar archivo .env
    try {
        require('dotenv').config();
        
        const envUri = process.env.NEO4J_URI;
        const envUser = process.env.NEO4J_USERNAME || process.env.NEO4J_USER;
        const envPassword = process.env.NEO4J_PASSWORD || process.env.NEO4J_QUANTUM_NETWORK_AURA;
        
        if (envUri && envPassword) {
            console.log('[OK] Credenciales cargadas desde .env');
            return {
                uri: envUri,
                user: envUser || 'neo4j',
                password: envPassword,
                database: process.env.NEO4J_DATABASE || 'neo4j'
            };
        }
    } catch (error) {
        // dotenv no está instalado o hay un error
    }
    
    // 4. Valores por defecto (solo para desarrollo, sin contraseña)
    console.warn('[WARN] Usando valores por defecto (sin contraseña)');
    return {
        uri: 'neo4j+s://87983fcb.databases.neo4j.io',
        user: 'neo4j',
        password: '',
        database: 'neo4j'
    };
}

// Cargar credenciales
const credentials = loadNeo4jCredentials();
const NEO4J_URI = credentials.uri;
const NEO4J_USER = credentials.user;
const NEO4J_PASSWORD = credentials.password;
const NEO4J_DATABASE = credentials.database;

/**
 * Transforma un nodo de Neo4j al formato esperado por @neo4j-nvl/react.
 *
 * Formato esperado:
 * {
 *     "id": "string",
 *     "caption": "string",
 *     "labels": ["string"],
 *     "properties": {...}
 * }
 */
function transformNode(nodeData, nodeId) {
    const labels = nodeData.labels || [];
    const properties = {};
    
    // Copiar todas las propiedades excepto 'labels'
    for (const [key, value] of Object.entries(nodeData)) {
        if (key !== 'labels') {
            properties[key] = value;
        }
    }
    
    // Usar 'name' como caption si está disponible, sino el primer label
    const caption = properties.name || (labels.length > 0 ? labels[0] : 'Node');
    
    return {
        id: nodeId,
        caption: String(caption),
        labels: labels,
        properties: properties
    };
}

/**
 * Transforma una relación de Neo4j al formato esperado por @neo4j-nvl/react.
 *
 * Formato esperado:
 * {
 *     "id": "string",
 *     "from": "string",
 *     "to": "string",
 *     "type": "string",
 *     "caption": "string"
 * }
 */
function transformRelationship(relData, relId, fromId, toId) {
    const relType = relData.type || 'RELATED_TO';
    const properties = {};
    
    // Copiar todas las propiedades excepto 'type'
    for (const [key, value] of Object.entries(relData)) {
        if (key !== 'type') {
            properties[key] = value;
        }
    }
    
    return {
        id: relId,
        from: fromId,
        to: toId,
        type: relType,
        caption: relType,
        properties: properties
    };
}

/**
 * Extrae todos los nodos y relaciones del grafo de Neo4j.
 *
 * @param {neo4j.Driver} driver - Driver de Neo4j
 * @returns {Promise<{nodes: Array, relationships: Array}>}
 */
async function extractGraphData(driver) {
    const nodes = [];
    const relationships = [];
    const nodeIdMap = {}; // Mapea el ID interno de Neo4j a nuestro ID secuencial
    
    const session = driver.session({ database: NEO4J_DATABASE });
    
    try {
        // Query para obtener todos los nodos con sus propiedades
        const nodesQuery = `
            MATCH (n)
            RETURN id(n) AS internal_id, labels(n) AS labels, properties(n) AS properties
            ORDER BY internal_id
        `;
        
        const nodesResult = await session.run(nodesQuery);
        let nodeCounter = 1;
        
        for (const record of nodesResult.records) {
            const internalId = record.get('internal_id').toString();
            const labels = record.get('labels');
            const properties = record.get('properties');
            
            // Crear ID único para el nodo
            const nodeId = String(nodeCounter);
            nodeIdMap[internalId] = nodeId;
            
            // Transformar nodo
            const nodeData = {
                labels: labels,
                ...properties
            };
            nodes.push(transformNode(nodeData, nodeId));
            nodeCounter++;
        }
        
        // Query para obtener todas las relaciones
        const relsQuery = `
            MATCH (a)-[r]->(b)
            RETURN id(a) AS from_internal_id, id(b) AS to_internal_id, 
                   type(r) AS type, properties(r) AS properties, id(r) AS rel_internal_id
            ORDER BY rel_internal_id
        `;
        
        const relsResult = await session.run(relsQuery);
        let relCounter = 1;
        
        for (const record of relsResult.records) {
            const fromInternalId = record.get('from_internal_id').toString();
            const toInternalId = record.get('to_internal_id').toString();
            const relType = record.get('type');
            const relProperties = record.get('properties');
            
            // Obtener IDs de los nodos
            const fromId = nodeIdMap[fromInternalId];
            const toId = nodeIdMap[toInternalId];
            
            if (fromId && toId) {
                const relId = `r${relCounter}`;
                const relData = {
                    type: relType,
                    ...relProperties
                };
                relationships.push(transformRelationship(relData, relId, fromId, toId));
                relCounter++;
            }
        }
    } finally {
        await session.close();
    }
    
    return {
        nodes: nodes,
        relationships: relationships
    };
}

/**
 * Genera estadísticas del grafo.
 */
function generateStats(nodes, relationships) {
    const nodeTypes = new Set();
    for (const node of nodes) {
        const labels = node.labels || [];
        labels.forEach(label => nodeTypes.add(label));
    }
    
    const relTypes = new Set();
    for (const rel of relationships) {
        relTypes.add(rel.type || 'UNKNOWN');
    }
    
    return {
        totalNodes: nodes.length,
        totalRelationships: relationships.length,
        nodeTypes: Array.from(nodeTypes).sort(),
        relationshipTypes: Array.from(relTypes).sort()
    };
}

/**
 * Función principal.
 */
async function main() {
    console.log('[INFO] Conectando a Neo4j...');
    
    try {
        const driver = neo4j.driver(
            NEO4J_URI,
            neo4j.auth.basic(NEO4J_USER, NEO4J_PASSWORD)
        );
        
        // Verificar conexión
        await driver.verifyConnectivity();
        console.log('[OK] Conexión exitosa a Neo4j');
        
        console.log('[INFO] Extrayendo datos del grafo...');
        const graphData = await extractGraphData(driver);
        
        // Generar estadísticas
        const stats = generateStats(graphData.nodes, graphData.relationships);
        
        // Combinar datos
        const outputData = {
            nodes: graphData.nodes,
            relationships: graphData.relationships,
            stats: stats
        };
        
        // Guardar en archivo JSON
        const outputPath = path.join(
            projectRoot,
            'src',
            'app',
            'ui',
            'public',
            'graph-data.json'
        );
        
        // Asegurar que el directorio existe
        const outputDir = path.dirname(outputPath);
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        // Función para convertir valores especiales de Neo4j a tipos nativos de JavaScript
        const convertNeo4jTypes = (obj) => {
            if (obj === null || obj === undefined) {
                return obj;
            }
            
            // Convertir Integer de Neo4j a Number
            if (neo4j.isInt(obj)) {
                return obj.toNumber();
            }
            
            // Convertir Date de Neo4j a string ISO
            if (obj instanceof Date) {
                return obj.toISOString();
            }
            
            // Convertir arrays recursivamente
            if (Array.isArray(obj)) {
                return obj.map(item => convertNeo4jTypes(item));
            }
            
            // Convertir objetos recursivamente
            if (typeof obj === 'object') {
                const converted = {};
                for (const [key, val] of Object.entries(obj)) {
                    converted[key] = convertNeo4jTypes(val);
                }
                return converted;
            }
            
            return obj;
        };
        
        // Convertir todos los tipos de Neo4j antes de serializar
        const convertedData = convertNeo4jTypes(outputData);
        const jsonString = JSON.stringify(convertedData, null, 2);
        
        fs.writeFileSync(outputPath, jsonString, 'utf-8');
        
        console.log(`[OK] Datos exportados exitosamente a: ${outputPath}`);
        console.log(`   - Nodos: ${stats.totalNodes}`);
        console.log(`   - Relaciones: ${stats.totalRelationships}`);
        console.log(`   - Tipos de nodos: ${stats.nodeTypes.join(', ')}`);
        console.log(`   - Tipos de relaciones: ${stats.relationshipTypes.join(', ')}`);
        
        await driver.close();
        
    } catch (error) {
        console.error(`[ERROR] ${error.message}`);
        if (error.stack) {
            console.error(error.stack);
        }
        process.exit(1);
    }
}

// Ejecutar si es el módulo principal
if (require.main === module) {
    main().catch(error => {
        console.error(`[ERROR] Error no manejado: ${error.message}`);
        if (error.stack) {
            console.error(error.stack);
        }
        process.exit(1);
    });
}

module.exports = { main, loadNeo4jCredentials, transformNode, transformRelationship };
