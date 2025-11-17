import React, { useRef, useState, useEffect } from 'react';
import { InteractiveNvlWrapper } from '@neo4j-nvl/react';
import { useGraphData } from '../hooks/useGraphData';
import NodeInfoPanel from './NodeInfoPanel';
import QueryPanel from './QueryPanel';
import './GraphVisualization.css';

// Mapeo de colores para cada tipo de nodo
const NODE_COLORS = {
  'Person': '#4A90E2',      // Azul para Personas
  'Organization': '#50C878', // Verde para Organizaciones
  'Domain': '#FF6B6B',       // Rojo para Dominios
  'Problem': '#FFA500'      // Naranja para Problemas
};

// Mapeo de nombres en español para cada tipo de nodo
const NODE_LABELS_ES = {
  'Person': 'Personas',
  'Organization': 'Organizaciones',
  'Domain': 'Dominios',
  'Problem': 'Problemas'
};

// Función para obtener el color según el tipo de nodo
function getNodeColor(labels) {
  if (!labels || labels.length === 0) return "#888888";

  // Buscar el primer label que tenga un color definido
  for (const label of labels) {
    if (NODE_COLORS[label]) {
      return NODE_COLORS[label];
    }
  }

  return "#888888"; // Color por defecto
}

// Función para enriquecer nodos con colores y hacerlos más visibles
function enrichNodesWithColors(nodes, sizeMultiplier = 1.0, nodeDegrees = new Map(), useDegreeForSize = false, degreeStats = { min: 0, max: 1 }) {
  return nodes.map(node => {
    // Si el nodo ya está marcado como oculto (fantasma), mantener su estilo
    if (node.hidden) {
      return {
        ...node,
        // Mantener opacidad reducida y estilo de nodo fantasma
        size: (node.size || 1.0) * sizeMultiplier * 0.7, // Más pequeños los nodos fantasma
        radius: Math.max(10, (node.size || 1.0) * sizeMultiplier * 7),
      };
    }

    const nodeColor = getNodeColor(node.labels);
    const degree = nodeDegrees.get(node.id) || 0;
    
    // Calcular tamaño base
    let baseSize;
    if (useDegreeForSize && degreeStats.max > 0) {
      // Usar degree para tamaño: normalizar entre 0.5 y 3.0
      const normalizedDegree = (degree - degreeStats.min) / (degreeStats.max - degreeStats.min || 1);
      baseSize = (0.5 + normalizedDegree * 2.5) * sizeMultiplier;
    } else {
      // Tamaños base multiplicados por el factor de escala
      if (node.labels?.includes('Person')) {
        baseSize = 2.5 * sizeMultiplier;
      } else if (node.labels?.includes('Organization')) {
        baseSize = 3.5 * sizeMultiplier;
      } else if (node.labels?.includes('Domain')) {
        baseSize = 2.0 * sizeMultiplier;
      } else if (node.labels?.includes('Problem')) {
        baseSize = 2.5 * sizeMultiplier;
      } else {
        baseSize = 2.0 * sizeMultiplier;
      }
    }

    // Calcular radio en píxeles (mínimo 15px para legibilidad)
    const radius = Math.max(15, baseSize * 10);

    return {
      ...node,
      // Intentar múltiples propiedades de color que la librería podría aceptar
      color: nodeColor,
      fill: nodeColor,
      backgroundColor: nodeColor,
      // Tamaños ajustables
      size: baseSize * 5,
      captions: [
        {
          key: "Bold text",
          styles: ["bold", "large"],
          value: node.caption,
        },
      ],
      radius: radius,
      degree: degree, // Agregar degree como propiedad
      // Agregar estilo personalizado si es necesario
      style: {
        fill: nodeColor,
        stroke: '#ffffff',
        strokeWidth: Math.max(2, 3 * sizeMultiplier),
        opacity: 0.9
      },
      // Asegurar que el texto sea visible
      fontColor: '#ffffff',
      fontSize: Math.max(12, 14 * sizeMultiplier),
      fontWeight: 'bold'
    };
  });
}

// Función para enriquecer relaciones con opacidad y grosor
function enrichRelationships(relationships, opacity = 0.6, width = 1.0) {
  return relationships.map(rel => ({
    ...rel,
    opacity: opacity,
    width: width,
    style: {
      ...rel.style,
      opacity: opacity,
      strokeWidth: width
    }
  }));
}

// Layouts disponibles en @neo4j-nvl/react
// Basado en la documentación oficial de @neo4j-nvl/react 0.3.9
const AVAILABLE_LAYOUTS = [
  { 
    value: 'forceDirected', 
    label: 'Force-Directed', 
    description: 'Layout basado en fuerzas físicas (recomendado para grafos de conocimiento)',
    recommended: true
  },
  { 
    value: 'hierarchical', 
    label: 'Jerárquico', 
    description: 'Organiza nodos en niveles jerárquicos basado en relaciones',
    recommended: false
  },
  { 
    value: 'circular', 
    label: 'Circular', 
    description: 'Dispone nodos en círculo (útil para visualizar comunidades)',
    recommended: false
  },
  { 
    value: 'grid', 
    label: 'Cuadrícula', 
    description: 'Organiza nodos en una cuadrícula regular (útil para comparación)',
    recommended: false
  }
];

// Función para calcular el degree (grado) de cada nodo
function calculateNodeDegrees(nodes, relationships) {
  const degreeMap = new Map();
  
  // Inicializar todos los nodos con degree 0
  nodes.forEach(node => {
    degreeMap.set(node.id, 0);
  });
  
  // Contar relaciones para cada nodo
  relationships.forEach(rel => {
    const fromDegree = degreeMap.get(rel.from) || 0;
    const toDegree = degreeMap.get(rel.to) || 0;
    degreeMap.set(rel.from, fromDegree + 1);
    degreeMap.set(rel.to, toDegree + 1);
  });
  
  return degreeMap;
}

function GraphVisualization() {
  const eventLogRef = useRef(null);
  const { nodes, relationships, stats, loading, error } = useGraphData();
  const [selectedNode, setSelectedNode] = useState(null);
  const [showQueryPanel, setShowQueryPanel] = useState(false); // Mostrar/ocultar panel de queries
  const [currentLayout, setCurrentLayout] = useState('forceDirected');
  const [layoutKey, setLayoutKey] = useState(0); // Key para forzar re-render
  const [nodeSizeMultiplier, setNodeSizeMultiplier] = useState(1.5); // Multiplicador de tamaño (1.0 = normal)
  const [showControls, setShowControls] = useState(true); // Mostrar/ocultar controles
  const [useDegreeForSize, setUseDegreeForSize] = useState(false); // Usar degree para tamaño
  const [relationshipOpacity, setRelationshipOpacity] = useState(0.6); // Opacidad de relaciones
  const [relationshipWidth, setRelationshipWidth] = useState(1.0); // Grosor de relaciones
  
  // Detectar dinámicamente todos los tipos de nodos presentes en los datos
  const availableNodeTypes = React.useMemo(() => {
    const types = new Set();
    nodes.forEach(node => {
      if (node.labels && node.labels.length > 0) {
        node.labels.forEach(label => types.add(label));
      }
    });
    return Array.from(types).sort();
  }, [nodes]);
  
  // Inicializar filtros dinámicamente basados en los tipos disponibles
  const [nodeFilters, setNodeFilters] = useState(() => {
    const initialFilters = {};
    // Inicializar todos los tipos como visibles por defecto
    availableNodeTypes.forEach(type => {
      initialFilters[type] = true;
    });
    return initialFilters;
  });
  
  // Actualizar filtros cuando cambian los tipos disponibles
  useEffect(() => {
    setNodeFilters(prev => {
      const updated = { ...prev };
      // Agregar nuevos tipos que no existían antes
      availableNodeTypes.forEach(type => {
        if (!(type in updated)) {
          updated[type] = true; // Por defecto visible
        }
      });
      // Mantener solo los tipos que existen actualmente
      Object.keys(updated).forEach(type => {
        if (!availableNodeTypes.includes(type)) {
          delete updated[type];
        }
      });
      return updated;
    });
  }, [availableNodeTypes]);
  
  // Calcular degrees de todos los nodos
  const nodeDegrees = React.useMemo(() => {
    return calculateNodeDegrees(nodes, relationships);
  }, [nodes, relationships]);
  
  // Calcular estadísticas de degree
  const degreeStats = React.useMemo(() => {
    const degrees = Array.from(nodeDegrees.values());
    if (degrees.length === 0) return { min: 0, max: 0, avg: 0 };
    return {
      min: Math.min(...degrees),
      max: Math.max(...degrees),
      avg: degrees.reduce((a, b) => a + b, 0) / degrees.length
    };
  }, [nodeDegrees]);
  
  // Filtrar nodos según los filtros activos
  const filteredNodes = React.useMemo(() => {
    return nodes.filter((node) => {
      if (!node.labels || node.labels.length === 0) return true;
      // Mostrar nodo si al menos uno de sus labels está activo
      return node.labels.some((label) => nodeFilters[label] !== false);
    });
  }, [nodes, nodeFilters]);

  // Filtrar relaciones: mostrar todas las relaciones de nodos visibles
  // Incluso si el otro extremo está oculto, para ver todas las conexiones
  const filteredRelationships = React.useMemo(() => {
    const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
    return relationships.filter(
      (rel) =>
        // Mostrar relación si al menos uno de sus nodos está visible
        visibleNodeIds.has(rel.from) || visibleNodeIds.has(rel.to)
    );
  }, [relationships, filteredNodes]);

  // Incluir nodos "fantasma" (ocultos pero conectados) para que las relaciones se vean correctamente
  const allVisibleNodes = React.useMemo(() => {
    const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
    const connectedNodeIds = new Set();

    // Encontrar todos los nodos conectados a nodos visibles
    // Usar relationships directamente para evitar dependencia circular
    relationships.forEach((rel) => {
      if (visibleNodeIds.has(rel.from)) {
        connectedNodeIds.add(rel.to);
      }
      if (visibleNodeIds.has(rel.to)) {
        connectedNodeIds.add(rel.from);
      }
    });

    // Obtener nodos conectados que no están visibles (para mostrar las relaciones)
    const ghostNodes = nodes.filter(
      (n) => connectedNodeIds.has(n.id) && !visibleNodeIds.has(n.id)
    );

    // Combinar nodos visibles con nodos fantasma (pero marcarlos como ocultos visualmente)
    return [
      ...filteredNodes,
      ...ghostNodes.map((node) => ({
        ...node,
        hidden: true, // Marcar como oculto para estilos diferentes
        opacity: 0.3, // Hacer más transparentes
        style: {
          ...node.style,
          opacity: 0.3,
          stroke: "#ccc",
          strokeWidth: 1,
        },
      })),
    ];
  }, [filteredNodes, relationships, nodes]);
  
  // Enriquecer relaciones con opacidad y grosor
  const enrichedRelationships = React.useMemo(() => {
    return enrichRelationships(filteredRelationships, relationshipOpacity, relationshipWidth);
  }, [filteredRelationships, relationshipOpacity, relationshipWidth]);
  
  // Enriquecer nodos con colores y hacerlos más visibles
  // Incluir nodos visibles y nodos fantasma (conectados pero ocultos)
  const enrichedNodes = React.useMemo(() => {
    return enrichNodesWithColors(allVisibleNodes, nodeSizeMultiplier, nodeDegrees, useDegreeForSize, degreeStats);
  }, [allVisibleNodes, nodeSizeMultiplier, nodeDegrees, useDegreeForSize, degreeStats]);

  // Forzar actualización del layout cuando cambia
  useEffect(() => {
    console.log("Layout cambiado a:", currentLayout);
    setLayoutKey((prev) => prev + 1);
    // Limpiar selección de nodo al cambiar layout para mejor experiencia
    setSelectedNode(null);
  }, [currentLayout]);

  const logEvent = (nvlEventName, nvlEventData) => {
    const { originalEvent, data, hitTargets } = nvlEventData;
    console.log(nvlEventName, data, hitTargets, originalEvent);
    const eventLog = eventLogRef.current;
    if (eventLog) {
      const displayData = data?.caption || data?.type || JSON.stringify(data);
      eventLog.innerHTML = `<strong>${nvlEventName}:</strong> ${displayData}`;
    }
  };

  // Detectar si es dispositivo móvil
  const isMobile = React.useMemo(() => {
    return window.innerWidth <= 768 || ('ontouchstart' in window);
  }, []);

  const mouseEventCallbacks = {
    onHover: (element, hitTargets, originalEvent) => {
      logEvent('Hover', { originalEvent, data: element, hitTargets });
      // En móvil, no mostrar automáticamente al hover (solo al click)
      if (!isMobile && element && element.id) {
        const hoveredNode = enrichedNodes.find(n => n.id === element.id);
        if (hoveredNode) {
          setSelectedNode(hoveredNode);
        }
      }
    },

    onNodeClick: (node, hitTargets, originalEvent) => {
      logEvent('Click en Nodo', { originalEvent, data: node, hitTargets });
      // Seleccionar nodo al hacer click (funciona en desktop y móvil)
      if (node && node.id) {
        const clickedNode = enrichedNodes.find((n) => n.id === node.id);
        if (clickedNode) {
          setSelectedNode(clickedNode);
        }
      }
    },

    onNodeRightClick: (node, hitTargets, originalEvent) =>
      logEvent("Click Derecho en Nodo", {
        originalEvent,
        data: node,
        hitTargets,
      }),

    onNodeDoubleClick: (node, hitTargets, originalEvent) =>
      logEvent("Doble Click en Nodo", {
        originalEvent,
        data: node,
        hitTargets,
      }),

    onRelationshipClick: (rel, hitTargets, originalEvent) =>
      logEvent("Click en Relación", { originalEvent, data: rel, hitTargets }),

    onRelationshipRightClick: (rel, hitTargets, originalEvent) =>
      logEvent("Click Derecho en Relación", {
        originalEvent,
        data: rel,
        hitTargets,
      }),

    onRelationshipDoubleClick: (rel, hitTargets, originalEvent) =>
      logEvent("Doble Click en Relación", {
        originalEvent,
        data: rel,
        hitTargets,
      }),

    onCanvasClick: (originalEvent) => {
      logEvent("Click en Canvas", { originalEvent });
      // Cerrar panel al hacer click en el canvas
      setSelectedNode(null);
    },

    onCanvasDoubleClick: (originalEvent) =>
      logEvent("Doble Click en Canvas", { originalEvent }),

    onCanvasRightClick: (originalEvent) =>
      logEvent("Click Derecho en Canvas", { originalEvent }),

    onDrag: (draggedNodes, originalEvent) =>
      logEvent("Arrastrando Nodos", { originalEvent, data: draggedNodes }),

    onPan: (pan, originalEvent) =>
      logEvent("Pan", { originalEvent, data: pan }),

    onZoom: (zoomLevel, originalEvent) =>
      logEvent("Zoom", { originalEvent, data: zoomLevel }),
  };

  // Configuración de opciones según el layout
  // Optimizado para el esquema: Person (39), Organization (34), Domain (11), Problem (4)
  const nvlOptions = React.useMemo(() => {
    const baseOptions = {
      layout: currentLayout,
      allowDynamicMinZoom: true,
      disableWebGL: false,
      maxZoom: 5,
      minZoom: 0.1,
      // Opciones para mejorar la visualización de relaciones y evitar solapamientos
      relationshipCurve: 'curved', // Usar curvas en lugar de líneas rectas para relaciones
      relationshipRouting: 'curved', // Enrutamiento curvo para relaciones paralelas
      relationshipSeparation: 10, // Separación mínima entre relaciones paralelas (píxeles)
    };

    // Configuraciones específicas por layout
    switch (currentLayout) {
      case 'forceDirected':
        return {
          ...baseOptions,
          initialZoom: 0.6, // Zoom inicial ajustado para ~88 nodos con más espaciado
          // Opciones de fuerza optimizadas para alejar más los nodos
          force: {
            charge: -600, // Fuerza de repulsión aumentada (más negativo = más separación)
            linkDistance: 180, // Distancia preferida aumentada entre nodos conectados
            linkStrength: 0.5, // Fuerza de los enlaces ligeramente reducida
            collisionRadius: 40, // Radio de colisión aumentado para más espacio
            centerStrength: 0.1, // Fuerza hacia el centro reducida (permite más dispersión)
            manyBodyStrength: -600, // Fuerza de repulsión aumentada entre todos los nodos
            // Parámetros adicionales para estabilidad con más espaciado
            alpha: 0.3, // Parámetro de enfriamiento inicial
            alphaDecay: 0.0228, // Tasa de enfriamiento (1 - pow(0.01, 1 / 200))
            velocityDecay: 0.4 // Fricción (0-1)
          }
        };

      case 'hierarchical':
        return {
          ...baseOptions,
          initialZoom: 0.7,
          hierarchical: {
            direction: 'LR', // Left to Right (también: TB, BT, RL)
            nodeSeparation: 150, // Separación horizontal aumentada entre nodos
            levelSeparation: 200, // Separación vertical aumentada entre niveles
            sortMethod: 'directed' // Ordenamiento: directed, hubsize, etc.
          }
        };

      case 'circular':
        return {
          ...baseOptions,
          initialZoom: 0.6, // Zoom menor para ver todo el círculo
          circular: {
            enabled: true,
            radius: null, // null = auto-calcular basado en número de nodos
            startAngle: 0, // Ángulo inicial en radianes
            clockwise: true // Dirección del ordenamiento
          }
        };

      case 'grid':
        return {
          ...baseOptions,
          initialZoom: 0.8,
          grid: {
            rows: null, // null = auto-calcular (sqrt(nodes))
            columns: null, // null = auto-calcular
            cellWidth: 200, // Ancho de celda aumentado
            cellHeight: 200 // Alto de celda aumentado
          }
        };

      default:
        return {
          ...baseOptions,
          initialZoom: 1.0
        };
    }
  }, [currentLayout]);

  // Mostrar estado de carga
  if (loading) {
    return (
      <div className="graph-container">
        <div className="loading-state">
          <h3>🔄 Cargando datos del grafo de conocimiento...</h3>
          <p>Conectando con Neo4j y preparando la visualización</p>
        </div>
      </div>
    );
  }

  // Mostrar error si hay
  if (error) {
    return (
      <div className="graph-container">
        <div className="error-state">
          <h3>❌ Error al cargar datos</h3>
          <p>{error}</p>
          <p className="error-hint">
            Asegúrate de que el archivo graph-data.json existe en la carpeta public/.
            Ejecuta: <code>node src/app/scripts/export_neo4j_data.js</code> o <code>npm run export-data</code>
          </p>
        </div>
      </div>
    );
  }

  // Mostrar mensaje si no hay datos
  if (!nodes || nodes.length === 0) {
    return (
      <div className="graph-container">
        <div className="empty-state">
          <h3>📊 No hay datos disponibles</h3>
          <p>
            El grafo está vacío. Ejecuta el script de exportación para generar
            datos.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`graph-container ${selectedNode ? 'has-panel' : ''} ${showQueryPanel ? 'has-query-panel' : ''}`}>
      {/* Panel de Controles */}
      {showControls && (
        <div className="controls-panel">
          <div className="controls-header">
            <h4>Configuración</h4>
            <button
              className="toggle-controls-btn"
              onClick={() => setShowControls(false)}
              aria-label="Ocultar controles"
            >
              −
            </button>
          </div>

          <div className="controls-content">
            {/* Selector de Layout */}
            <div className="control-group">
              <label htmlFor="layout-select">
                Layout:
                {AVAILABLE_LAYOUTS.find(l => l.value === currentLayout)?.recommended && (
                  <span className="recommended-badge"> ⭐ Recomendado</span>
                )}
              </label>
              <select
                id="layout-select"
                value={currentLayout}
                onChange={(e) => setCurrentLayout(e.target.value)}
                className="control-select"
              >
                {AVAILABLE_LAYOUTS.map((layout) => (
                  <option key={layout.value} value={layout.value}>
                    {layout.label} {layout.recommended ? '⭐' : ''}
                  </option>
                ))}
              </select>
              <span className="control-description">
                {
                  AVAILABLE_LAYOUTS.find((l) => l.value === currentLayout)
                    ?.description
                }
              </span>
            </div>

            {/* Control de Tamaño de Nodos */}
            <div className="control-group">
              <label htmlFor="node-size-slider">
                Tamaño de Nodos: {nodeSizeMultiplier.toFixed(1)}x
              </label>
              <input
                id="node-size-slider"
                type="range"
                min="0.5"
                max="3.0"
                step="0.1"
                value={nodeSizeMultiplier}
                onChange={(e) =>
                  setNodeSizeMultiplier(parseFloat(e.target.value))
                }
                className="control-slider"
              />
              <div className="slider-labels">
                <span>Pequeño</span>
                <span>Normal</span>
                <span>Grande</span>
              </div>
              <span className="control-description">
                Ajusta el tamaño de todos los nodos para mejorar la legibilidad
              </span>
            </div>

            {/* Filtros de Tipos de Nodos - Dinámicos */}
            <div className="control-group">
              <label>Filtrar por Tipo:</label>
              <div className="node-filters">
                {availableNodeTypes.map(nodeType => {
                  const count = nodes.filter(n => n.labels?.includes(nodeType)).length;
                  const color = NODE_COLORS[nodeType] || '#888888';
                  const label = NODE_LABELS_ES[nodeType] || nodeType;
                  
                  return (
                    <label key={nodeType} className="filter-checkbox">
                      <input
                        type="checkbox"
                        checked={nodeFilters[nodeType] !== false}
                        onChange={(e) => setNodeFilters(prev => ({ ...prev, [nodeType]: e.target.checked }))}
                      />
                      <span className="filter-label">
                        <span className="filter-color" style={{ backgroundColor: color }}></span>
                        {label} ({count})
                      </span>
                    </label>
                  );
                })}
              </div>
              <span className="control-description">
                Muestra u oculta tipos específicos de nodos en el grafo
              </span>
            </div>

            {/* Toggle para usar degree como tamaño */}
            <div className="control-group">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={useDegreeForSize}
                  onChange={(e) => setUseDegreeForSize(e.target.checked)}
                  className="toggle-input"
                />
                <span>Usar Degree para Tamaño</span>
              </label>
              {useDegreeForSize && (
                <div className="degree-stats">
                  <span className="degree-stat">Min: {degreeStats.min}</span>
                  <span className="degree-stat">Max: {degreeStats.max}</span>
                  <span className="degree-stat">Prom: {degreeStats.avg.toFixed(1)}</span>
                </div>
              )}
              <span className="control-description">
                El tamaño del nodo será proporcional a su número de conexiones (degree)
              </span>
            </div>

            {/* Control de Opacidad de Relaciones */}
            <div className="control-group">
              <label htmlFor="rel-opacity-slider">
                Opacidad de Relaciones: {(relationshipOpacity * 100).toFixed(0)}%
              </label>
              <input
                id="rel-opacity-slider"
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={relationshipOpacity}
                onChange={(e) => setRelationshipOpacity(parseFloat(e.target.value))}
                className="control-slider"
              />
              <div className="slider-labels">
                <span>Transparente</span>
                <span>Normal</span>
                <span>Opaco</span>
              </div>
            </div>

            {/* Control de Grosor de Relaciones */}
            <div className="control-group">
              <label htmlFor="rel-width-slider">
                Grosor de Relaciones: {relationshipWidth.toFixed(1)}px
              </label>
              <input
                id="rel-width-slider"
                type="range"
                min="0.5"
                max="5.0"
                step="0.5"
                value={relationshipWidth}
                onChange={(e) => setRelationshipWidth(parseFloat(e.target.value))}
                className="control-slider"
              />
              <div className="slider-labels">
                <span>Fino</span>
                <span>Normal</span>
                <span>Grueso</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Botones de control en la esquina superior derecha */}
      <div className="top-controls-buttons">
        {/* Botón para mostrar panel de queries */}
        <button 
          className={`control-btn queries-btn ${showQueryPanel ? 'active' : ''}`}
          onClick={() => setShowQueryPanel(!showQueryPanel)}
          aria-label={showQueryPanel ? "Ocultar queries" : "Mostrar queries"}
          title="Queries Estratégicas"
        >
          {showQueryPanel ? '✕' : '📊'}
        </button>

        {/* Botón para mostrar/ocultar controles */}
        <button 
          className={`control-btn config-btn ${showControls ? 'active' : ''}`}
          onClick={() => setShowControls(!showControls)}
          aria-label={showControls ? "Ocultar controles" : "Mostrar controles"}
          title="Configuración"
        >
          ⚙️
        </button>
      </div>

      {/* Panel de Queries */}
      {showQueryPanel && (
        <QueryPanel
          nodes={nodes}
          relationships={relationships}
          onClose={() => setShowQueryPanel(false)}
        />
      )}

      <div className="graph-canvas">
        <InteractiveNvlWrapper
          key={`${currentLayout}-${layoutKey}`} // Forzar re-render completo cuando cambia el layout
          nodes={enrichedNodes}
          rels={enrichedRelationships}
          nvlOptions={nvlOptions}
          mouseEventCallbacks={mouseEventCallbacks}
        />
      </div>
      {selectedNode && (
        <NodeInfoPanel
          node={selectedNode}
          relationships={relationships}
          allNodes={enrichedNodes}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}

export default GraphVisualization;
