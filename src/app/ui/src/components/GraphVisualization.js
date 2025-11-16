import React, { useRef, useState } from 'react';
import { InteractiveNvlWrapper } from '@neo4j-nvl/react';
import { useGraphData } from '../hooks/useGraphData';
import NodeInfoPanel from './NodeInfoPanel';
import './GraphVisualization.css';

// Mapeo de colores para cada tipo de nodo
const NODE_COLORS = {
  'Person': '#4A90E2',      // Azul para Personas
  'Organization': '#50C878', // Verde para Organizaciones
  'Domain': '#FF6B6B'        // Rojo para Dominios
};

// Función para obtener el color según el tipo de nodo
function getNodeColor(labels) {
  if (!labels || labels.length === 0) return '#888888';
  
  // Buscar el primer label que tenga un color definido
  for (const label of labels) {
    if (NODE_COLORS[label]) {
      return NODE_COLORS[label];
    }
  }
  
  return '#888888'; // Color por defecto
}

// Función para enriquecer nodos con colores y hacerlos más visibles
function enrichNodesWithColors(nodes) {
  return nodes.map(node => {
    const nodeColor = getNodeColor(node.labels);
    // Tamaños más grandes para mejor visibilidad
    const baseSize = node.labels?.includes('Person') ? 2.5 : 
                     node.labels?.includes('Organization') ? 3.5 : 
                     2.0;
    
    return {
      ...node,
      // Intentar múltiples propiedades de color que la librería podría aceptar
      color: nodeColor,
      fill: nodeColor,
      backgroundColor: nodeColor,
      // Tamaños más grandes para mejor visibilidad
      size: baseSize,
      radius: baseSize * 10, // Radio en píxeles
      // Agregar estilo personalizado si es necesario
      style: {
        fill: nodeColor,
        stroke: '#ffffff',
        strokeWidth: 3,
        opacity: 0.9
      },
      // Asegurar que el texto sea visible
      fontColor: '#ffffff',
      fontSize: 14,
      fontWeight: 'bold'
    };
  });
}

// Layouts disponibles en @neo4j-nvl/react
const AVAILABLE_LAYOUTS = [
  { value: 'force', label: 'Force-Directed', description: 'Layout basado en fuerzas físicas (recomendado)' },
  { value: 'hierarchical', label: 'Jerárquico', description: 'Organiza nodos en niveles jerárquicos' },
  { value: 'circular', label: 'Circular', description: 'Dispone nodos en círculo' },
  { value: 'grid', label: 'Cuadrícula', description: 'Organiza nodos en una cuadrícula regular' }
];

function GraphVisualization() {
  const eventLogRef = useRef(null);
  const { nodes, relationships, stats, loading, error } = useGraphData();
  const [selectedNode, setSelectedNode] = useState(null);
  const [currentLayout, setCurrentLayout] = useState('force');
  
  // Enriquecer nodos con colores y hacerlos más visibles
  const enrichedNodes = React.useMemo(() => {
    return enrichNodesWithColors(nodes);
  }, [nodes]);

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
      logEvent('Hover', { originalEvent, data: element, hitTargets });
      // Mostrar información del nodo al hacer hover
      if (element && element.id) {
        const hoveredNode = enrichedNodes.find(n => n.id === element.id);
        if (hoveredNode) {
          setSelectedNode(hoveredNode);
        }
      }
    },
    
    onNodeClick: (node, hitTargets, originalEvent) => {
      logEvent('Click en Nodo', { originalEvent, data: node, hitTargets });
      // Seleccionar nodo al hacer click
      if (node && node.id) {
        const clickedNode = enrichedNodes.find(n => n.id === node.id);
        if (clickedNode) {
          setSelectedNode(clickedNode);
        }
      }
    },
    
    onNodeRightClick: (node, hitTargets, originalEvent) =>
      logEvent('Click Derecho en Nodo', { originalEvent, data: node, hitTargets }),
    
    onNodeDoubleClick: (node, hitTargets, originalEvent) =>
      logEvent('Doble Click en Nodo', { originalEvent, data: node, hitTargets }),
    
    onRelationshipClick: (rel, hitTargets, originalEvent) =>
      logEvent('Click en Relación', { originalEvent, data: rel, hitTargets }),
    
    onRelationshipRightClick: (rel, hitTargets, originalEvent) =>
      logEvent('Click Derecho en Relación', { originalEvent, data: rel, hitTargets }),
    
    onRelationshipDoubleClick: (rel, hitTargets, originalEvent) =>
      logEvent('Doble Click en Relación', { originalEvent, data: rel, hitTargets }),
    
    onCanvasClick: (originalEvent) => {
      logEvent('Click en Canvas', { originalEvent });
      // Cerrar panel al hacer click en el canvas
      setSelectedNode(null);
    },
    
    onCanvasDoubleClick: (originalEvent) => 
      logEvent('Doble Click en Canvas', { originalEvent }),
    
    onCanvasRightClick: (originalEvent) => 
      logEvent('Click Derecho en Canvas', { originalEvent }),
    
    onDrag: (draggedNodes, originalEvent) =>
      logEvent('Arrastrando Nodos', { originalEvent, data: draggedNodes }),
    
    onPan: (pan, originalEvent) =>
      logEvent('Pan', { originalEvent, data: pan }),
    
    onZoom: (zoomLevel, originalEvent) => 
      logEvent('Zoom', { originalEvent, data: zoomLevel })
  };

  // Configuración simplificada de opciones - solo las que la librería acepta
  const nvlOptions = React.useMemo(() => {
    return {
      layout: currentLayout,
      initialZoom: 1.0,
      allowDynamicMinZoom: true,
      disableWebGL: false,
      maxZoom: 5,
      minZoom: 0.1
    };
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
            Ejecuta: <code>python src/app/scripts/export_neo4j_data.py</code>
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
          <p>El grafo está vacío. Ejecuta el script de exportación para generar datos.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`graph-container ${selectedNode ? 'has-panel' : ''}`}>
      {/* Selector de Layout */}
      <div className="layout-selector">
        <label htmlFor="layout-select">Layout:</label>
        <select
          id="layout-select"
          value={currentLayout}
          onChange={(e) => setCurrentLayout(e.target.value)}
          className="layout-select"
        >
          {AVAILABLE_LAYOUTS.map(layout => (
            <option key={layout.value} value={layout.value}>
              {layout.label}
            </option>
          ))}
        </select>
        <span className="layout-description">
          {AVAILABLE_LAYOUTS.find(l => l.value === currentLayout)?.description}
        </span>
      </div>

      <div className="graph-canvas">
        <InteractiveNvlWrapper
          nodes={enrichedNodes}
          rels={relationships}
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

