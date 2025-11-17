import React, { useRef, useState, useEffect } from "react";
import { InteractiveNvlWrapper } from "@neo4j-nvl/react";
import { useGraphData } from "../hooks/useGraphData";
import NodeInfoPanel from "./NodeInfoPanel";
import "./GraphVisualization.css";

// Mapeo de colores para cada tipo de nodo
const NODE_COLORS = {
  Person: "#2E5FCC", // Azul para Personas
  Organization: "#50C878", // Verde para Organizaciones
  Domain: "#DC143C", // Rojo para Dominios
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
function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
  return nodes.map((node) => {
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

    // Tamaños base multiplicados por el factor de escala
    let baseSize;
    if (node.labels?.includes("Person")) {
      baseSize = 2.5 * sizeMultiplier;
    } else if (node.labels?.includes("Organization")) {
      baseSize = 3.5 * sizeMultiplier;
    } else if (node.labels?.includes("Domain")) {
      baseSize = 2.0 * sizeMultiplier;
    } else {
      baseSize = 2.0 * sizeMultiplier;
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
    };
  });
}

// Layouts disponibles en @neo4j-nvl/react
// Nota: Los nombres pueden variar según la versión de la librería
const AVAILABLE_LAYOUTS = [
  {
    value: "force",
    label: "Force-Directed",
    description: "Layout basado en fuerzas físicas (recomendado)",
  },
  {
    value: "hierarchical",
    label: "Jerárquico",
    description: "Organiza nodos en niveles jerárquicos",
  },
  {
    value: "circular",
    label: "Circular",
    description: "Dispone nodos en círculo",
  },
  {
    value: "grid",
    label: "Cuadrícula",
    description: "Organiza nodos en una cuadrícula regular",
  },
  {
    value: "d3Force",
    label: "Force-Directed (alt)",
    description: "Variante del layout de fuerzas",
  },
];

function GraphVisualization() {
  const eventLogRef = useRef(null);
  const { nodes, relationships, stats, loading, error } = useGraphData();
  const [selectedNode, setSelectedNode] = useState(null);
  const [currentLayout, setCurrentLayout] = useState("d3Force");
  const [layoutKey, setLayoutKey] = useState(0); // Key para forzar re-render
  const [nodeSizeMultiplier, setNodeSizeMultiplier] = useState(1.5); // Multiplicador de tamaño (1.0 = normal)
  const [showControls, setShowControls] = useState(true); // Mostrar/ocultar controles

  // Filtros de nodos por tipo
  const [nodeFilters, setNodeFilters] = useState({
    Person: true,
    Organization: true,
    Domain: true,
  });

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

  // Enriquecer nodos con colores y hacerlos más visibles
  // Incluir nodos visibles y nodos fantasma (conectados pero ocultos)
  const enrichedNodes = React.useMemo(() => {
    return enrichNodesWithColors(allVisibleNodes, nodeSizeMultiplier);
  }, [allVisibleNodes, nodeSizeMultiplier]);

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

  const mouseEventCallbacks = {
    onHover: (element, hitTargets, originalEvent) => {
      logEvent("Hover", { originalEvent, data: element, hitTargets });
      // Mostrar información del nodo al hacer hover
      if (element && element.id) {
        const hoveredNode = enrichedNodes.find((n) => n.id === element.id);
        if (hoveredNode) {
          setSelectedNode(hoveredNode);
        }
      }
    },

    onNodeClick: (node, hitTargets, originalEvent) => {
      logEvent("Click en Nodo", { originalEvent, data: node, hitTargets });
      // Seleccionar nodo al hacer click
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
  const nvlOptions = React.useMemo(() => {
    const baseOptions = {
      layout: currentLayout,
      allowDynamicMinZoom: true,
      disableWebGL: false,
      maxZoom: 5,
      minZoom: 0.1,
      layoutOptions: { enableCytoscape: true },
    };

    // Opciones específicas para layout circular
    if (currentLayout === "circular") {
      // Forzar que el layout se aplique correctamente
      return {
        ...baseOptions,
        // Algunas librerías necesitan estas opciones para circular
        circular: {
          enabled: true,
        },
      };
    }

    // Debug: ver qué opciones se están pasando
    console.log("NVL Options:", baseOptions);

    return baseOptions;
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
            Asegúrate de que el archivo graph-data.json existe en la carpeta
            public/. Ejecuta:{" "}
            <code>python src/app/scripts/export_neo4j_data.py</code>
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
    <div className={`graph-container ${selectedNode ? "has-panel" : ""}`}>
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
              <label htmlFor="layout-select">Layout:</label>
              <select
                id="layout-select"
                value={currentLayout}
                onChange={(e) => setCurrentLayout(e.target.value)}
                className="control-select"
              >
                {AVAILABLE_LAYOUTS.map((layout) => (
                  <option key={layout.value} value={layout.value}>
                    {layout.label}
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

            {/* Filtros de Tipos de Nodos */}
            <div className="control-group">
              <label>Filtrar por Tipo:</label>
              <div className="node-filters">
                <label className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={nodeFilters.Person}
                    onChange={(e) =>
                      setNodeFilters((prev) => ({
                        ...prev,
                        Person: e.target.checked,
                      }))
                    }
                  />
                  <span className="filter-label">
                    <span
                      className="filter-color"
                      style={{ backgroundColor: NODE_COLORS.Person }}
                    ></span>
                    Personas (
                    {nodes.filter((n) => n.labels?.includes("Person")).length})
                  </span>
                </label>
                <label className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={nodeFilters.Organization}
                    onChange={(e) =>
                      setNodeFilters((prev) => ({
                        ...prev,
                        Organization: e.target.checked,
                      }))
                    }
                  />
                  <span className="filter-label">
                    <span
                      className="filter-color"
                      style={{ backgroundColor: NODE_COLORS.Organization }}
                    ></span>
                    Organizaciones (
                    {
                      nodes.filter((n) => n.labels?.includes("Organization"))
                        .length
                    }
                    )
                  </span>
                </label>
                <label className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={nodeFilters.Domain}
                    onChange={(e) =>
                      setNodeFilters((prev) => ({
                        ...prev,
                        Domain: e.target.checked,
                      }))
                    }
                  />
                  <span className="filter-label">
                    <span
                      className="filter-color"
                      style={{ backgroundColor: NODE_COLORS.Domain }}
                    ></span>
                    Dominios (
                    {nodes.filter((n) => n.labels?.includes("Domain")).length})
                  </span>
                </label>
              </div>
              <span className="control-description">
                Muestra u oculta tipos específicos de nodos en el grafo
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Botón para mostrar controles si están ocultos */}
      {!showControls && (
        <button
          className="show-controls-btn"
          onClick={() => setShowControls(true)}
          aria-label="Mostrar controles"
        >
          ⚙️
        </button>
      )}

      <div className="graph-canvas">
        <InteractiveNvlWrapper
          key={`${currentLayout}-${layoutKey}`} // Forzar re-render completo cuando cambia el layout
          nodes={enrichedNodes}
          rels={filteredRelationships}
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
