diff --git a/.gitignore b/.gitignore
index e58208d..7e830d2 100644
--- a/.gitignore
+++ b/.gitignore
@@ -35,6 +35,9 @@ MANIFEST
 *.manifest
 *.spec
 
+cambios.md
+commit.txt
+
 # Installer logs
 pip-log.txt
 pip-delete-this-directory.txt
diff --git a/cambios.md b/cambios.md
new file mode 100644
index 0000000..f464eac
--- /dev/null
+++ b/cambios.md
@@ -0,0 +1,1291 @@
+diff --git a/.gitignore b/.gitignore
+index e58208d..33f05f0 100644
+--- a/.gitignore
++++ b/.gitignore
+@@ -35,6 +35,9 @@ MANIFEST
+ *.manifest
+ *.spec
+ 
++cambiosDiff.md
++commit.txt
++
+ # Installer logs
+ pip-log.txt
+ pip-delete-this-directory.txt
+diff --git a/cambios.md b/cambios.md
+new file mode 100644
+index 0000000..8231d58
+--- /dev/null
++++ b/cambios.md
+@@ -0,0 +1,643 @@
++diff --git a/.gitignore b/.gitignore
++index e58208d..33f05f0 100644
++--- a/.gitignore
+++++ b/.gitignore
++@@ -35,6 +35,9 @@ MANIFEST
++ *.manifest
++ *.spec
++ 
+++cambiosDiff.md
+++commit.txt
+++
++ # Installer logs
++ pip-log.txt
++ pip-delete-this-directory.txt
++diff --git a/src/app/ui/src/components/GraphVisualization.js b/src/app/ui/src/components/GraphVisualization.js
++index 3c311da..439acc4 100644
++--- a/src/app/ui/src/components/GraphVisualization.js
+++++ b/src/app/ui/src/components/GraphVisualization.js
++@@ -1,60 +1,60 @@
++-import React, { useRef, useState, useEffect } from 'react';
++-import { InteractiveNvlWrapper } from '@neo4j-nvl/react';
++-import { useGraphData } from '../hooks/useGraphData';
++-import NodeInfoPanel from './NodeInfoPanel';
++-import './GraphVisualization.css';
+++import React, { useRef, useState, useEffect } from "react";
+++import { InteractiveNvlWrapper } from "@neo4j-nvl/react";
+++import { useGraphData } from "../hooks/useGraphData";
+++import NodeInfoPanel from "./NodeInfoPanel";
+++import "./GraphVisualization.css";
++ 
++ // Mapeo de colores para cada tipo de nodo
++ const NODE_COLORS = {
++-  'Person': '#4A90E2',      // Azul para Personas
++-  'Organization': '#50C878', // Verde para Organizaciones
++-  'Domain': '#FF6B6B'        // Rojo para Dominios
+++  Person: "#2E5FCC", // Azul para Personas
+++  Organization: "#50C878", // Verde para Organizaciones
+++  Domain: "#DC143C", // Rojo para Dominios
++ };
++ 
++ // Función para obtener el color según el tipo de nodo
++ function getNodeColor(labels) {
++-  if (!labels || labels.length === 0) return '#888888';
++-  
+++  if (!labels || labels.length === 0) return "#888888";
+++
++   // Buscar el primer label que tenga un color definido
++   for (const label of labels) {
++     if (NODE_COLORS[label]) {
++       return NODE_COLORS[label];
++     }
++   }
++-  
++-  return '#888888'; // Color por defecto
+++
+++  return "#888888"; // Color por defecto
++ }
++ 
++ // Función para enriquecer nodos con colores y hacerlos más visibles
++ function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
++-  return nodes.map(node => {
+++  return nodes.map((node) => {
++     // Si el nodo ya está marcado como oculto (fantasma), mantener su estilo
++     if (node.hidden) {
++       return {
++         ...node,
++         // Mantener opacidad reducida y estilo de nodo fantasma
++         size: (node.size || 1.0) * sizeMultiplier * 0.7, // Más pequeños los nodos fantasma
++-        radius: Math.max(10, (node.size || 1.0) * sizeMultiplier * 7)
+++        radius: Math.max(10, (node.size || 1.0) * sizeMultiplier * 7),
++       };
++     }
++-    
+++
++     const nodeColor = getNodeColor(node.labels);
++-    
+++
++     // Tamaños base multiplicados por el factor de escala
++     let baseSize;
++-    if (node.labels?.includes('Person')) {
+++    if (node.labels?.includes("Person")) {
++       baseSize = 2.5 * sizeMultiplier;
++-    } else if (node.labels?.includes('Organization')) {
+++    } else if (node.labels?.includes("Organization")) {
++       baseSize = 3.5 * sizeMultiplier;
++-    } else if (node.labels?.includes('Domain')) {
+++    } else if (node.labels?.includes("Domain")) {
++       baseSize = 2.0 * sizeMultiplier;
++     } else {
++       baseSize = 2.0 * sizeMultiplier;
++     }
++-    
+++
++     // Calcular radio en píxeles (mínimo 15px para legibilidad)
++     const radius = Math.max(15, baseSize * 10);
++-    
+++
++     return {
++       ...node,
++       // Intentar múltiples propiedades de color que la librería podría aceptar
++@@ -62,19 +62,15 @@ function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
++       fill: nodeColor,
++       backgroundColor: nodeColor,
++       // Tamaños ajustables
++-      size: baseSize,
+++      size: baseSize * 5,
+++      captions: [
+++        {
+++          key: "Bold text",
+++          styles: ["bold", "large"],
+++          value: node.caption,
+++        },
+++      ],
++       radius: radius,
++-      // Agregar estilo personalizado si es necesario
++-      style: {
++-        fill: nodeColor,
++-        stroke: '#ffffff',
++-        strokeWidth: Math.max(2, 3 * sizeMultiplier),
++-        opacity: 0.9
++-      },
++-      // Asegurar que el texto sea visible
++-      fontColor: '#ffffff',
++-      fontSize: Math.max(12, 14 * sizeMultiplier),
++-      fontWeight: 'bold'
++     };
++   });
++ }
++@@ -82,56 +78,77 @@ function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
++ // Layouts disponibles en @neo4j-nvl/react
++ // Nota: Los nombres pueden variar según la versión de la librería
++ const AVAILABLE_LAYOUTS = [
++-  { value: 'force', label: 'Force-Directed', description: 'Layout basado en fuerzas físicas (recomendado)' },
++-  { value: 'hierarchical', label: 'Jerárquico', description: 'Organiza nodos en niveles jerárquicos' },
++-  { value: 'circular', label: 'Circular', description: 'Dispone nodos en círculo' },
++-  { value: 'grid', label: 'Cuadrícula', description: 'Organiza nodos en una cuadrícula regular' },
++-  { value: 'forceDirected', label: 'Force-Directed (alt)', description: 'Variante del layout de fuerzas' }
+++  {
+++    value: "force",
+++    label: "Force-Directed",
+++    description: "Layout basado en fuerzas físicas (recomendado)",
+++  },
+++  {
+++    value: "hierarchical",
+++    label: "Jerárquico",
+++    description: "Organiza nodos en niveles jerárquicos",
+++  },
+++  {
+++    value: "circular",
+++    label: "Circular",
+++    description: "Dispone nodos en círculo",
+++  },
+++  {
+++    value: "grid",
+++    label: "Cuadrícula",
+++    description: "Organiza nodos en una cuadrícula regular",
+++  },
+++  {
+++    value: "forceDirected",
+++    label: "Force-Directed (alt)",
+++    description: "Variante del layout de fuerzas",
+++  },
++ ];
++ 
++ function GraphVisualization() {
++   const eventLogRef = useRef(null);
++   const { nodes, relationships, stats, loading, error } = useGraphData();
++   const [selectedNode, setSelectedNode] = useState(null);
++-  const [currentLayout, setCurrentLayout] = useState('force');
+++  const [currentLayout, setCurrentLayout] = useState("force");
++   const [layoutKey, setLayoutKey] = useState(0); // Key para forzar re-render
++   const [nodeSizeMultiplier, setNodeSizeMultiplier] = useState(1.5); // Multiplicador de tamaño (1.0 = normal)
++   const [showControls, setShowControls] = useState(true); // Mostrar/ocultar controles
++-  
+++
++   // Filtros de nodos por tipo
++   const [nodeFilters, setNodeFilters] = useState({
++     Person: true,
++     Organization: true,
++-    Domain: true
+++    Domain: true,
++   });
++-  
+++
++   // Filtrar nodos según los filtros activos
++   const filteredNodes = React.useMemo(() => {
++-    return nodes.filter(node => {
+++    return nodes.filter((node) => {
++       if (!node.labels || node.labels.length === 0) return true;
++       // Mostrar nodo si al menos uno de sus labels está activo
++-      return node.labels.some(label => nodeFilters[label] !== false);
+++      return node.labels.some((label) => nodeFilters[label] !== false);
++     });
++   }, [nodes, nodeFilters]);
++-  
+++
++   // Filtrar relaciones: mostrar todas las relaciones de nodos visibles
++   // Incluso si el otro extremo está oculto, para ver todas las conexiones
++   const filteredRelationships = React.useMemo(() => {
++-    const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
++-    return relationships.filter(rel => 
++-      // Mostrar relación si al menos uno de sus nodos está visible
++-      visibleNodeIds.has(rel.from) || visibleNodeIds.has(rel.to)
+++    const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
+++    return relationships.filter(
+++      (rel) =>
+++        // Mostrar relación si al menos uno de sus nodos está visible
+++        visibleNodeIds.has(rel.from) || visibleNodeIds.has(rel.to)
++     );
++   }, [relationships, filteredNodes]);
++-  
+++
++   // Incluir nodos "fantasma" (ocultos pero conectados) para que las relaciones se vean correctamente
++   const allVisibleNodes = React.useMemo(() => {
++-    const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
+++    const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
++     const connectedNodeIds = new Set();
++-    
+++
++     // Encontrar todos los nodos conectados a nodos visibles
++     // Usar relationships directamente para evitar dependencia circular
++-    relationships.forEach(rel => {
+++    relationships.forEach((rel) => {
++       if (visibleNodeIds.has(rel.from)) {
++         connectedNodeIds.add(rel.to);
++       }
++@@ -139,26 +156,29 @@ function GraphVisualization() {
++         connectedNodeIds.add(rel.from);
++       }
++     });
++-    
+++
++     // Obtener nodos conectados que no están visibles (para mostrar las relaciones)
++-    const ghostNodes = nodes.filter(n => 
++-      connectedNodeIds.has(n.id) && !visibleNodeIds.has(n.id)
+++    const ghostNodes = nodes.filter(
+++      (n) => connectedNodeIds.has(n.id) && !visibleNodeIds.has(n.id)
++     );
++-    
+++
++     // Combinar nodos visibles con nodos fantasma (pero marcarlos como ocultos visualmente)
++-    return [...filteredNodes, ...ghostNodes.map(node => ({
++-      ...node,
++-      hidden: true, // Marcar como oculto para estilos diferentes
++-      opacity: 0.3, // Hacer más transparentes
++-      style: {
++-        ...node.style,
++-        opacity: 0.3,
++-        stroke: '#ccc',
++-        strokeWidth: 1
++-      }
++-    }))];
+++    return [
+++      ...filteredNodes,
+++      ...ghostNodes.map((node) => ({
+++        ...node,
+++        hidden: true, // Marcar como oculto para estilos diferentes
+++        opacity: 0.3, // Hacer más transparentes
+++        style: {
+++          ...node.style,
+++          opacity: 0.3,
+++          stroke: "#ccc",
+++          strokeWidth: 1,
+++        },
+++      })),
+++    ];
++   }, [filteredNodes, relationships, nodes]);
++-  
+++
++   // Enriquecer nodos con colores y hacerlos más visibles
++   // Incluir nodos visibles y nodos fantasma (conectados pero ocultos)
++   const enrichedNodes = React.useMemo(() => {
++@@ -167,8 +187,8 @@ function GraphVisualization() {
++ 
++   // Forzar actualización del layout cuando cambia
++   useEffect(() => {
++-    console.log('Layout cambiado a:', currentLayout);
++-    setLayoutKey(prev => prev + 1);
+++    console.log("Layout cambiado a:", currentLayout);
+++    setLayoutKey((prev) => prev + 1);
++     // Limpiar selección de nodo al cambiar layout para mejor experiencia
++     setSelectedNode(null);
++   }, [currentLayout]);
++@@ -185,90 +205,106 @@ function GraphVisualization() {
++ 
++   const mouseEventCallbacks = {
++     onHover: (element, hitTargets, originalEvent) => {
++-      logEvent('Hover', { originalEvent, data: element, hitTargets });
+++      logEvent("Hover", { originalEvent, data: element, hitTargets });
++       // Mostrar información del nodo al hacer hover
++       if (element && element.id) {
++-        const hoveredNode = enrichedNodes.find(n => n.id === element.id);
+++        const hoveredNode = enrichedNodes.find((n) => n.id === element.id);
++         if (hoveredNode) {
++           setSelectedNode(hoveredNode);
++         }
++       }
++     },
++-    
+++
++     onNodeClick: (node, hitTargets, originalEvent) => {
++-      logEvent('Click en Nodo', { originalEvent, data: node, hitTargets });
+++      logEvent("Click en Nodo", { originalEvent, data: node, hitTargets });
++       // Seleccionar nodo al hacer click
++       if (node && node.id) {
++-        const clickedNode = enrichedNodes.find(n => n.id === node.id);
+++        const clickedNode = enrichedNodes.find((n) => n.id === node.id);
++         if (clickedNode) {
++           setSelectedNode(clickedNode);
++         }
++       }
++     },
++-    
+++
++     onNodeRightClick: (node, hitTargets, originalEvent) =>
++-      logEvent('Click Derecho en Nodo', { originalEvent, data: node, hitTargets }),
++-    
+++      logEvent("Click Derecho en Nodo", {
+++        originalEvent,
+++        data: node,
+++        hitTargets,
+++      }),
+++
++     onNodeDoubleClick: (node, hitTargets, originalEvent) =>
++-      logEvent('Doble Click en Nodo', { originalEvent, data: node, hitTargets }),
++-    
+++      logEvent("Doble Click en Nodo", {
+++        originalEvent,
+++        data: node,
+++        hitTargets,
+++      }),
+++
++     onRelationshipClick: (rel, hitTargets, originalEvent) =>
++-      logEvent('Click en Relación', { originalEvent, data: rel, hitTargets }),
++-    
+++      logEvent("Click en Relación", { originalEvent, data: rel, hitTargets }),
+++
++     onRelationshipRightClick: (rel, hitTargets, originalEvent) =>
++-      logEvent('Click Derecho en Relación', { originalEvent, data: rel, hitTargets }),
++-    
+++      logEvent("Click Derecho en Relación", {
+++        originalEvent,
+++        data: rel,
+++        hitTargets,
+++      }),
+++
++     onRelationshipDoubleClick: (rel, hitTargets, originalEvent) =>
++-      logEvent('Doble Click en Relación', { originalEvent, data: rel, hitTargets }),
++-    
+++      logEvent("Doble Click en Relación", {
+++        originalEvent,
+++        data: rel,
+++        hitTargets,
+++      }),
+++
++     onCanvasClick: (originalEvent) => {
++-      logEvent('Click en Canvas', { originalEvent });
+++      logEvent("Click en Canvas", { originalEvent });
++       // Cerrar panel al hacer click en el canvas
++       setSelectedNode(null);
++     },
++-    
++-    onCanvasDoubleClick: (originalEvent) => 
++-      logEvent('Doble Click en Canvas', { originalEvent }),
++-    
++-    onCanvasRightClick: (originalEvent) => 
++-      logEvent('Click Derecho en Canvas', { originalEvent }),
++-    
+++
+++    onCanvasDoubleClick: (originalEvent) =>
+++      logEvent("Doble Click en Canvas", { originalEvent }),
+++
+++    onCanvasRightClick: (originalEvent) =>
+++      logEvent("Click Derecho en Canvas", { originalEvent }),
+++
++     onDrag: (draggedNodes, originalEvent) =>
++-      logEvent('Arrastrando Nodos', { originalEvent, data: draggedNodes }),
++-    
+++      logEvent("Arrastrando Nodos", { originalEvent, data: draggedNodes }),
+++
++     onPan: (pan, originalEvent) =>
++-      logEvent('Pan', { originalEvent, data: pan }),
++-    
++-    onZoom: (zoomLevel, originalEvent) => 
++-      logEvent('Zoom', { originalEvent, data: zoomLevel })
+++      logEvent("Pan", { originalEvent, data: pan }),
+++
+++    onZoom: (zoomLevel, originalEvent) =>
+++      logEvent("Zoom", { originalEvent, data: zoomLevel }),
++   };
++ 
++   // Configuración de opciones según el layout
++   const nvlOptions = React.useMemo(() => {
++     const baseOptions = {
++-      layout: currentLayout,
++-      initialZoom: currentLayout === 'circular' ? 0.8 : 1.0, // Zoom inicial menor para circular
+++      layout: "d3Force",
++       allowDynamicMinZoom: true,
++       disableWebGL: false,
++       maxZoom: 5,
++-      minZoom: 0.1
+++      minZoom: 0.1,
+++      layoutOptions: { enableCytoscape: true },
++     };
++-    
+++
++     // Opciones específicas para layout circular
++-    if (currentLayout === 'circular') {
+++    if (currentLayout === "circular") {
++       // Forzar que el layout se aplique correctamente
++       return {
++         ...baseOptions,
++         // Algunas librerías necesitan estas opciones para circular
++         circular: {
++-          enabled: true
++-        }
+++          enabled: true,
+++        },
++       };
++     }
++-    
+++
++     // Debug: ver qué opciones se están pasando
++-    console.log('NVL Options:', baseOptions);
++-    
+++    console.log("NVL Options:", baseOptions);
+++
++     return baseOptions;
++   }, [currentLayout]);
++ 
++@@ -292,8 +328,9 @@ function GraphVisualization() {
++           <h3>❌ Error al cargar datos</h3>
++           <p>{error}</p>
++           <p className="error-hint">
++-            Asegúrate de que el archivo graph-data.json existe en la carpeta public/.
++-            Ejecuta: <code>python src/app/scripts/export_neo4j_data.py</code>
+++            Asegúrate de que el archivo graph-data.json existe en la carpeta
+++            public/. Ejecuta:{" "}
+++            <code>python src/app/scripts/export_neo4j_data.py</code>
++           </p>
++         </div>
++       </div>
++@@ -306,20 +343,23 @@ function GraphVisualization() {
++       <div className="graph-container">
++         <div className="empty-state">
++           <h3>📊 No hay datos disponibles</h3>
++-          <p>El grafo está vacío. Ejecuta el script de exportación para generar datos.</p>
+++          <p>
+++            El grafo está vacío. Ejecuta el script de exportación para generar
+++            datos.
+++          </p>
++         </div>
++       </div>
++     );
++   }
++ 
++   return (
++-    <div className={`graph-container ${selectedNode ? 'has-panel' : ''}`}>
+++    <div className={`graph-container ${selectedNode ? "has-panel" : ""}`}>
++       {/* Panel de Controles */}
++       {showControls && (
++         <div className="controls-panel">
++           <div className="controls-header">
++             <h4>Configuración</h4>
++-            <button 
+++            <button
++               className="toggle-controls-btn"
++               onClick={() => setShowControls(false)}
++               aria-label="Ocultar controles"
++@@ -327,7 +367,7 @@ function GraphVisualization() {
++               −
++             </button>
++           </div>
++-          
+++
++           <div className="controls-content">
++             {/* Selector de Layout */}
++             <div className="control-group">
++@@ -338,14 +378,17 @@ function GraphVisualization() {
++                 onChange={(e) => setCurrentLayout(e.target.value)}
++                 className="control-select"
++               >
++-                {AVAILABLE_LAYOUTS.map(layout => (
+++                {AVAILABLE_LAYOUTS.map((layout) => (
++                   <option key={layout.value} value={layout.value}>
++                     {layout.label}
++                   </option>
++                 ))}
++               </select>
++               <span className="control-description">
++-                {AVAILABLE_LAYOUTS.find(l => l.value === currentLayout)?.description}
+++                {
+++                  AVAILABLE_LAYOUTS.find((l) => l.value === currentLayout)
+++                    ?.description
+++                }
++               </span>
++             </div>
++ 
++@@ -361,7 +404,9 @@ function GraphVisualization() {
++                 max="3.0"
++                 step="0.1"
++                 value={nodeSizeMultiplier}
++-                onChange={(e) => setNodeSizeMultiplier(parseFloat(e.target.value))}
+++                onChange={(e) =>
+++                  setNodeSizeMultiplier(parseFloat(e.target.value))
+++                }
++                 className="control-slider"
++               />
++               <div className="slider-labels">
++@@ -382,33 +427,64 @@ function GraphVisualization() {
++                   <input
++                     type="checkbox"
++                     checked={nodeFilters.Person}
++-                    onChange={(e) => setNodeFilters(prev => ({ ...prev, Person: e.target.checked }))}
+++                    onChange={(e) =>
+++                      setNodeFilters((prev) => ({
+++                        ...prev,
+++                        Person: e.target.checked,
+++                      }))
+++                    }
++                   />
++                   <span className="filter-label">
++-                    <span className="filter-color" style={{ backgroundColor: NODE_COLORS.Person }}></span>
++-                    Personas ({nodes.filter(n => n.labels?.includes('Person')).length})
+++                    <span
+++                      className="filter-color"
+++                      style={{ backgroundColor: NODE_COLORS.Person }}
+++                    ></span>
+++                    Personas (
+++                    {nodes.filter((n) => n.labels?.includes("Person")).length})
++                   </span>
++                 </label>
++                 <label className="filter-checkbox">
++                   <input
++                     type="checkbox"
++                     checked={nodeFilters.Organization}
++-                    onChange={(e) => setNodeFilters(prev => ({ ...prev, Organization: e.target.checked }))}
+++                    onChange={(e) =>
+++                      setNodeFilters((prev) => ({
+++                        ...prev,
+++                        Organization: e.target.checked,
+++                      }))
+++                    }
++                   />
++                   <span className="filter-label">
++-                    <span className="filter-color" style={{ backgroundColor: NODE_COLORS.Organization }}></span>
++-                    Organizaciones ({nodes.filter(n => n.labels?.includes('Organization')).length})
+++                    <span
+++                      className="filter-color"
+++                      style={{ backgroundColor: NODE_COLORS.Organization }}
+++                    ></span>
+++                    Organizaciones (
+++                    {
+++                      nodes.filter((n) => n.labels?.includes("Organization"))
+++                        .length
+++                    }
+++                    )
++                   </span>
++                 </label>
++                 <label className="filter-checkbox">
++                   <input
++                     type="checkbox"
++                     checked={nodeFilters.Domain}
++-                    onChange={(e) => setNodeFilters(prev => ({ ...prev, Domain: e.target.checked }))}
+++                    onChange={(e) =>
+++                      setNodeFilters((prev) => ({
+++                        ...prev,
+++                        Domain: e.target.checked,
+++                      }))
+++                    }
++                   />
++                   <span className="filter-label">
++-                    <span className="filter-color" style={{ backgroundColor: NODE_COLORS.Domain }}></span>
++-                    Dominios ({nodes.filter(n => n.labels?.includes('Domain')).length})
+++                    <span
+++                      className="filter-color"
+++                      style={{ backgroundColor: NODE_COLORS.Domain }}
+++                    ></span>
+++                    Dominios (
+++                    {nodes.filter((n) => n.labels?.includes("Domain")).length})
++                   </span>
++                 </label>
++               </div>
++@@ -422,7 +498,7 @@ function GraphVisualization() {
++ 
++       {/* Botón para mostrar controles si están ocultos */}
++       {!showControls && (
++-        <button 
+++        <button
++           className="show-controls-btn"
++           onClick={() => setShowControls(true)}
++           aria-label="Mostrar controles"
++@@ -453,4 +529,3 @@ function GraphVisualization() {
++ }
++ 
++ export default GraphVisualization;
++-
++diff --git a/src/app/ui/src/interactions.js b/src/app/ui/src/interactions.js
++index 7e6a449..6afdff3 100644
++--- a/src/app/ui/src/interactions.js
+++++ b/src/app/ui/src/interactions.js
++@@ -1,22 +1,26 @@
++-import NVL from '@neo4j-nvl/base'
+++import NVL from "@neo4j-nvl/base";
++ import {
++   ClickInteraction,
++   DragNodeInteraction,
++   HoverInteraction,
++   PanInteraction,
++-  ZoomInteraction
++-} from '@neo4j-nvl/interaction-handlers'
+++  ZoomInteraction,
+++} from "@neo4j-nvl/interaction-handlers";
++ 
++ export default (parentContainer) => {
++-  const nodes = [{ id: '0' }, { id: '1' }]
++-  const rels = [{ id: '10', from: '0', to: '1' }]
++-  const myNvl = new NVL(parentContainer, nodes, rels)
+++  const nodes = [{ id: "0" }, { id: "1" }];
+++  const rels = [{ id: "10", from: "0", to: "1" }];
+++  const myNvl = new NVL(parentContainer, nodes, rels, {
+++    // Opciones de ForceDirected
+++    enableCytoscape: true, // Auto-switch a CoseBilkent para grafos pequeños
+++    enableVerlet: true, // Usar nuevo motor de física (recomendado)
+++    intelWorkaround: false, // Solo activar si hay problemas con GPUs Intel
+++  });
+++  new ZoomInteraction(myNvl);
+++  new PanInteraction(myNvl);
+++  new DragNodeInteraction(myNvl);
+++  new ClickInteraction(myNvl, { selectOnClick: true });
+++  new HoverInteraction(myNvl, { drawShadowOnHover: true });
++ 
++-  new ZoomInteraction(myNvl)
++-  new PanInteraction(myNvl)
++-  new DragNodeInteraction(myNvl)
++-  new ClickInteraction(myNvl, { selectOnClick: true })
++-  new HoverInteraction(myNvl, { drawShadowOnHover: true })
++-
++-  return myNvl
++-}
++\ No newline at end of file
+++  return myNvl;
+++};
+diff --git a/src/app/ui/src/components/GraphVisualization.js b/src/app/ui/src/components/GraphVisualization.js
+index 3c311da..e05d37e 100644
+--- a/src/app/ui/src/components/GraphVisualization.js
++++ b/src/app/ui/src/components/GraphVisualization.js
+@@ -1,60 +1,60 @@
+-import React, { useRef, useState, useEffect } from 'react';
+-import { InteractiveNvlWrapper } from '@neo4j-nvl/react';
+-import { useGraphData } from '../hooks/useGraphData';
+-import NodeInfoPanel from './NodeInfoPanel';
+-import './GraphVisualization.css';
++import React, { useRef, useState, useEffect } from "react";
++import { InteractiveNvlWrapper } from "@neo4j-nvl/react";
++import { useGraphData } from "../hooks/useGraphData";
++import NodeInfoPanel from "./NodeInfoPanel";
++import "./GraphVisualization.css";
+ 
+ // Mapeo de colores para cada tipo de nodo
+ const NODE_COLORS = {
+-  'Person': '#4A90E2',      // Azul para Personas
+-  'Organization': '#50C878', // Verde para Organizaciones
+-  'Domain': '#FF6B6B'        // Rojo para Dominios
++  Person: "#2E5FCC", // Azul para Personas
++  Organization: "#50C878", // Verde para Organizaciones
++  Domain: "#DC143C", // Rojo para Dominios
+ };
+ 
+ // Función para obtener el color según el tipo de nodo
+ function getNodeColor(labels) {
+-  if (!labels || labels.length === 0) return '#888888';
+-  
++  if (!labels || labels.length === 0) return "#888888";
++
+   // Buscar el primer label que tenga un color definido
+   for (const label of labels) {
+     if (NODE_COLORS[label]) {
+       return NODE_COLORS[label];
+     }
+   }
+-  
+-  return '#888888'; // Color por defecto
++
++  return "#888888"; // Color por defecto
+ }
+ 
+ // Función para enriquecer nodos con colores y hacerlos más visibles
+ function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
+-  return nodes.map(node => {
++  return nodes.map((node) => {
+     // Si el nodo ya está marcado como oculto (fantasma), mantener su estilo
+     if (node.hidden) {
+       return {
+         ...node,
+         // Mantener opacidad reducida y estilo de nodo fantasma
+         size: (node.size || 1.0) * sizeMultiplier * 0.7, // Más pequeños los nodos fantasma
+-        radius: Math.max(10, (node.size || 1.0) * sizeMultiplier * 7)
++        radius: Math.max(10, (node.size || 1.0) * sizeMultiplier * 7),
+       };
+     }
+-    
++
+     const nodeColor = getNodeColor(node.labels);
+-    
++
+     // Tamaños base multiplicados por el factor de escala
+     let baseSize;
+-    if (node.labels?.includes('Person')) {
++    if (node.labels?.includes("Person")) {
+       baseSize = 2.5 * sizeMultiplier;
+-    } else if (node.labels?.includes('Organization')) {
++    } else if (node.labels?.includes("Organization")) {
+       baseSize = 3.5 * sizeMultiplier;
+-    } else if (node.labels?.includes('Domain')) {
++    } else if (node.labels?.includes("Domain")) {
+       baseSize = 2.0 * sizeMultiplier;
+     } else {
+       baseSize = 2.0 * sizeMultiplier;
+     }
+-    
++
+     // Calcular radio en píxeles (mínimo 15px para legibilidad)
+     const radius = Math.max(15, baseSize * 10);
+-    
++
+     return {
+       ...node,
+       // Intentar múltiples propiedades de color que la librería podría aceptar
+@@ -62,19 +62,15 @@ function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
+       fill: nodeColor,
+       backgroundColor: nodeColor,
+       // Tamaños ajustables
+-      size: baseSize,
++      size: baseSize * 5,
++      captions: [
++        {
++          key: "Bold text",
++          styles: ["bold", "large"],
++          value: node.caption,
++        },
++      ],
+       radius: radius,
+-      // Agregar estilo personalizado si es necesario
+-      style: {
+-        fill: nodeColor,
+-        stroke: '#ffffff',
+-        strokeWidth: Math.max(2, 3 * sizeMultiplier),
+-        opacity: 0.9
+-      },
+-      // Asegurar que el texto sea visible
+-      fontColor: '#ffffff',
+-      fontSize: Math.max(12, 14 * sizeMultiplier),
+-      fontWeight: 'bold'
+     };
+   });
+ }
+@@ -82,56 +78,77 @@ function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
+ // Layouts disponibles en @neo4j-nvl/react
+ // Nota: Los nombres pueden variar según la versión de la librería
+ const AVAILABLE_LAYOUTS = [
+-  { value: 'force', label: 'Force-Directed', description: 'Layout basado en fuerzas físicas (recomendado)' },
+-  { value: 'hierarchical', label: 'Jerárquico', description: 'Organiza nodos en niveles jerárquicos' },
+-  { value: 'circular', label: 'Circular', description: 'Dispone nodos en círculo' },
+-  { value: 'grid', label: 'Cuadrícula', description: 'Organiza nodos en una cuadrícula regular' },
+-  { value: 'forceDirected', label: 'Force-Directed (alt)', description: 'Variante del layout de fuerzas' }
++  {
++    value: "force",
++    label: "Force-Directed",
++    description: "Layout basado en fuerzas físicas (recomendado)",
++  },
++  {
++    value: "hierarchical",
++    label: "Jerárquico",
++    description: "Organiza nodos en niveles jerárquicos",
++  },
++  {
++    value: "circular",
++    label: "Circular",
++    description: "Dispone nodos en círculo",
++  },
++  {
++    value: "grid",
++    label: "Cuadrícula",
++    description: "Organiza nodos en una cuadrícula regular",
++  },
++  {
++    value: "d3Force",
++    label: "Force-Directed (alt)",
++    description: "Variante del layout de fuerzas",
++  },
+ ];
+ 
+ function GraphVisualization() {
+   const eventLogRef = useRef(null);
+   const { nodes, relationships, stats, loading, error } = useGraphData();
+   const [selectedNode, setSelectedNode] = useState(null);
+-  const [currentLayout, setCurrentLayout] = useState('force');
++  const [currentLayout, setCurrentLayout] = useState("d3Force");
+   const [layoutKey, setLayoutKey] = useState(0); // Key para forzar re-render
+   const [nodeSizeMultiplier, setNodeSizeMultiplier] = useState(1.5); // Multiplicador de tamaño (1.0 = normal)
+   const [showControls, setShowControls] = useState(true); // Mostrar/ocultar controles
+-  
++
+   // Filtros de nodos por tipo
+   const [nodeFilters, setNodeFilters] = useState({
+     Person: true,
+     Organization: true,
+-    Domain: true
++    Domain: true,
+   });
+-  
++
+   // Filtrar nodos según los filtros activos
+   const filteredNodes = React.useMemo(() => {
+-    return nodes.filter(node => {
++    return nodes.filter((node) => {
+       if (!node.labels || node.labels.length === 0) return true;
+       // Mostrar nodo si al menos uno de sus labels está activo
+-      return node.labels.some(label => nodeFilters[label] !== false);
++      return node.labels.some((label) => nodeFilters[label] !== false);
+     });
+   }, [nodes, nodeFilters]);
+-  
++
+   // Filtrar relaciones: mostrar todas las relaciones de nodos visibles
+   // Incluso si el otro extremo está oculto, para ver todas las conexiones
+   const filteredRelationships = React.useMemo(() => {
+-    const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
+-    return relationships.filter(rel => 
+-      // Mostrar relación si al menos uno de sus nodos está visible
+-      visibleNodeIds.has(rel.from) || visibleNodeIds.has(rel.to)
++    const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
++    return relationships.filter(
++      (rel) =>
++        // Mostrar relación si al menos uno de sus nodos está visible
++        visibleNodeIds.has(rel.from) || visibleNodeIds.has(rel.to)
+     );
+   }, [relationships, filteredNodes]);
+-  
++
+   // Incluir nodos "fantasma" (ocultos pero conectados) para que las relaciones se vean correctamente
+   const allVisibleNodes = React.useMemo(() => {
+-    const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
++    const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
+     const connectedNodeIds = new Set();
+-    
++
+     // Encontrar todos los nodos conectados a nodos visibles
+     // Usar relationships directamente para evitar dependencia circular
+-    relationships.forEach(rel => {
++    relationships.forEach((rel) => {
+       if (visibleNodeIds.has(rel.from)) {
+         connectedNodeIds.add(rel.to);
+       }
+@@ -139,26 +156,29 @@ function GraphVisualization() {
+         connectedNodeIds.add(rel.from);
+       }
+     });
+-    
++
+     // Obtener nodos conectados que no están visibles (para mostrar las relaciones)
+-    const ghostNodes = nodes.filter(n => 
+-      connectedNodeIds.has(n.id) && !visibleNodeIds.has(n.id)
++    const ghostNodes = nodes.filter(
++      (n) => connectedNodeIds.has(n.id) && !visibleNodeIds.has(n.id)
+     );
+-    
++
+     // Combinar nodos visibles con nodos fantasma (pero marcarlos como ocultos visualmente)
+-    return [...filteredNodes, ...ghostNodes.map(node => ({
+-      ...node,
+-      hidden: true, // Marcar como oculto para estilos diferentes
+-      opacity: 0.3, // Hacer más transparentes
+-      style: {
+-        ...node.style,
+-        opacity: 0.3,
+-        stroke: '#ccc',
+-        strokeWidth: 1
+-      }
+-    }))];
++    return [
++      ...filteredNodes,
++      ...ghostNodes.map((node) => ({
++        ...node,
++        hidden: true, // Marcar como oculto para estilos diferentes
++        opacity: 0.3, // Hacer más transparentes
++        style: {
++          ...node.style,
++          opacity: 0.3,
++          stroke: "#ccc",
++          strokeWidth: 1,
++        },
++      })),
++    ];
+   }, [filteredNodes, relationships, nodes]);
+-  
++
+   // Enriquecer nodos con colores y hacerlos más visibles
+   // Incluir nodos visibles y nodos fantasma (conectados pero ocultos)
+   const enrichedNodes = React.useMemo(() => {
+@@ -167,8 +187,8 @@ function GraphVisualization() {
+ 
+   // Forzar actualización del layout cuando cambia
+   useEffect(() => {
+-    console.log('Layout cambiado a:', currentLayout);
+-    setLayoutKey(prev => prev + 1);
++    console.log("Layout cambiado a:", currentLayout);
++    setLayoutKey((prev) => prev + 1);
+     // Limpiar selección de nodo al cambiar layout para mejor experiencia
+     setSelectedNode(null);
+   }, [currentLayout]);
+@@ -185,90 +205,106 @@ function GraphVisualization() {
+ 
+   const mouseEventCallbacks = {
+     onHover: (element, hitTargets, originalEvent) => {
+-      logEvent('Hover', { originalEvent, data: element, hitTargets });
++      logEvent("Hover", { originalEvent, data: element, hitTargets });
+       // Mostrar información del nodo al hacer hover
+       if (element && element.id) {
+-        const hoveredNode = enrichedNodes.find(n => n.id === element.id);
++        const hoveredNode = enrichedNodes.find((n) => n.id === element.id);
+         if (hoveredNode) {
+           setSelectedNode(hoveredNode);
+         }
+       }
+     },
+-    
++
+     onNodeClick: (node, hitTargets, originalEvent) => {
+-      logEvent('Click en Nodo', { originalEvent, data: node, hitTargets });
++      logEvent("Click en Nodo", { originalEvent, data: node, hitTargets });
+       // Seleccionar nodo al hacer click
+       if (node && node.id) {
+-        const clickedNode = enrichedNodes.find(n => n.id === node.id);
++        const clickedNode = enrichedNodes.find((n) => n.id === node.id);
+         if (clickedNode) {
+           setSelectedNode(clickedNode);
+         }
+       }
+     },
+-    
++
+     onNodeRightClick: (node, hitTargets, originalEvent) =>
+-      logEvent('Click Derecho en Nodo', { originalEvent, data: node, hitTargets }),
+-    
++      logEvent("Click Derecho en Nodo", {
++        originalEvent,
++        data: node,
++        hitTargets,
++      }),
++
+     onNodeDoubleClick: (node, hitTargets, originalEvent) =>
+-      logEvent('Doble Click en Nodo', { originalEvent, data: node, hitTargets }),
+-    
++      logEvent("Doble Click en Nodo", {
++        originalEvent,
++        data: node,
++        hitTargets,
++      }),
++
+     onRelationshipClick: (rel, hitTargets, originalEvent) =>
+-      logEvent('Click en Relación', { originalEvent, data: rel, hitTargets }),
+-    
++      logEvent("Click en Relación", { originalEvent, data: rel, hitTargets }),
++
+     onRelationshipRightClick: (rel, hitTargets, originalEvent) =>
+-      logEvent('Click Derecho en Relación', { originalEvent, data: rel, hitTargets }),
+-    
++      logEvent("Click Derecho en Relación", {
++        originalEvent,
++        data: rel,
++        hitTargets,
++      }),
++
+     onRelationshipDoubleClick: (rel, hitTargets, originalEvent) =>
+-      logEvent('Doble Click en Relación', { originalEvent, data: rel, hitTargets }),
+-    
++      logEvent("Doble Click en Relación", {
++        originalEvent,
++        data: rel,
++        hitTargets,
++      }),
++
+     onCanvasClick: (originalEvent) => {
+-      logEvent('Click en Canvas', { originalEvent });
++      logEvent("Click en Canvas", { originalEvent });
+       // Cerrar panel al hacer click en el canvas
+       setSelectedNode(null);
+     },
+-    
+-    onCanvasDoubleClick: (originalEvent) => 
+-      logEvent('Doble Click en Canvas', { originalEvent }),
+-    
+-    onCanvasRightClick: (originalEvent) => 
+-      logEvent('Click Derecho en Canvas', { originalEvent }),
+-    
++
++    onCanvasDoubleClick: (originalEvent) =>
++      logEvent("Doble Click en Canvas", { originalEvent }),
++
++    onCanvasRightClick: (originalEvent) =>
++      logEvent("Click Derecho en Canvas", { originalEvent }),
++
+     onDrag: (draggedNodes, originalEvent) =>
+-      logEvent('Arrastrando Nodos', { originalEvent, data: draggedNodes }),
+-    
++      logEvent("Arrastrando Nodos", { originalEvent, data: draggedNodes }),
++
+     onPan: (pan, originalEvent) =>
+-      logEvent('Pan', { originalEvent, data: pan }),
+-    
+-    onZoom: (zoomLevel, originalEvent) => 
+-      logEvent('Zoom', { originalEvent, data: zoomLevel })
++      logEvent("Pan", { originalEvent, data: pan }),
++
++    onZoom: (zoomLevel, originalEvent) =>
++      logEvent("Zoom", { originalEvent, data: zoomLevel }),
+   };
+ 
+   // Configuración de opciones según el layout
+   const nvlOptions = React.useMemo(() => {
+     const baseOptions = {
+       layout: currentLayout,
+-      initialZoom: currentLayout === 'circular' ? 0.8 : 1.0, // Zoom inicial menor para circular
+       allowDynamicMinZoom: true,
+       disableWebGL: false,
+       maxZoom: 5,
+-      minZoom: 0.1
++      minZoom: 0.1,
++      layoutOptions: { enableCytoscape: true },
+     };
+-    
++
+     // Opciones específicas para layout circular
+-    if (currentLayout === 'circular') {
++    if (currentLayout === "circular") {
+       // Forzar que el layout se aplique correctamente
+       return {
+         ...baseOptions,
+         // Algunas librerías necesitan estas opciones para circular
+         circular: {
+-          enabled: true
+-        }
++          enabled: true,
++        },
+       };
+     }
+-    
++
+     // Debug: ver qué opciones se están pasando
+-    console.log('NVL Options:', baseOptions);
+-    
++    console.log("NVL Options:", baseOptions);
++
+     return baseOptions;
+   }, [currentLayout]);
+ 
+@@ -292,8 +328,9 @@ function GraphVisualization() {
+           <h3>❌ Error al cargar datos</h3>
+           <p>{error}</p>
+           <p className="error-hint">
+-            Asegúrate de que el archivo graph-data.json existe en la carpeta public/.
+-            Ejecuta: <code>python src/app/scripts/export_neo4j_data.py</code>
++            Asegúrate de que el archivo graph-data.json existe en la carpeta
++            public/. Ejecuta:{" "}
++            <code>python src/app/scripts/export_neo4j_data.py</code>
+           </p>
+         </div>
+       </div>
+@@ -306,20 +343,23 @@ function GraphVisualization() {
+       <div className="graph-container">
+         <div className="empty-state">
+           <h3>📊 No hay datos disponibles</h3>
+-          <p>El grafo está vacío. Ejecuta el script de exportación para generar datos.</p>
++          <p>
++            El grafo está vacío. Ejecuta el script de exportación para generar
++            datos.
++          </p>
+         </div>
+       </div>
+     );
+   }
+ 
+   return (
+-    <div className={`graph-container ${selectedNode ? 'has-panel' : ''}`}>
++    <div className={`graph-container ${selectedNode ? "has-panel" : ""}`}>
+       {/* Panel de Controles */}
+       {showControls && (
+         <div className="controls-panel">
+           <div className="controls-header">
+             <h4>Configuración</h4>
+-            <button 
++            <button
+               className="toggle-controls-btn"
+               onClick={() => setShowControls(false)}
+               aria-label="Ocultar controles"
+@@ -327,7 +367,7 @@ function GraphVisualization() {
+               −
+             </button>
+           </div>
+-          
++
+           <div className="controls-content">
+             {/* Selector de Layout */}
+             <div className="control-group">
+@@ -338,14 +378,17 @@ function GraphVisualization() {
+                 onChange={(e) => setCurrentLayout(e.target.value)}
+                 className="control-select"
+               >
+-                {AVAILABLE_LAYOUTS.map(layout => (
++                {AVAILABLE_LAYOUTS.map((layout) => (
+                   <option key={layout.value} value={layout.value}>
+                     {layout.label}
+                   </option>
+                 ))}
+               </select>
+               <span className="control-description">
+-                {AVAILABLE_LAYOUTS.find(l => l.value === currentLayout)?.description}
++                {
++                  AVAILABLE_LAYOUTS.find((l) => l.value === currentLayout)
++                    ?.description
++                }
+               </span>
+             </div>
+ 
+@@ -361,7 +404,9 @@ function GraphVisualization() {
+                 max="3.0"
+                 step="0.1"
+                 value={nodeSizeMultiplier}
+-                onChange={(e) => setNodeSizeMultiplier(parseFloat(e.target.value))}
++                onChange={(e) =>
++                  setNodeSizeMultiplier(parseFloat(e.target.value))
++                }
+                 className="control-slider"
+               />
+               <div className="slider-labels">
+@@ -382,33 +427,64 @@ function GraphVisualization() {
+                   <input
+                     type="checkbox"
+                     checked={nodeFilters.Person}
+-                    onChange={(e) => setNodeFilters(prev => ({ ...prev, Person: e.target.checked }))}
++                    onChange={(e) =>
++                      setNodeFilters((prev) => ({
++                        ...prev,
++                        Person: e.target.checked,
++                      }))
++                    }
+                   />
+                   <span className="filter-label">
+-                    <span className="filter-color" style={{ backgroundColor: NODE_COLORS.Person }}></span>
+-                    Personas ({nodes.filter(n => n.labels?.includes('Person')).length})
++                    <span
++                      className="filter-color"
++                      style={{ backgroundColor: NODE_COLORS.Person }}
++                    ></span>
++                    Personas (
++                    {nodes.filter((n) => n.labels?.includes("Person")).length})
+                   </span>
+                 </label>
+                 <label className="filter-checkbox">
+                   <input
+                     type="checkbox"
+                     checked={nodeFilters.Organization}
+-                    onChange={(e) => setNodeFilters(prev => ({ ...prev, Organization: e.target.checked }))}
++                    onChange={(e) =>
++                      setNodeFilters((prev) => ({
++                        ...prev,
++                        Organization: e.target.checked,
++                      }))
++                    }
+                   />
+                   <span className="filter-label">
+-                    <span className="filter-color" style={{ backgroundColor: NODE_COLORS.Organization }}></span>
+-                    Organizaciones ({nodes.filter(n => n.labels?.includes('Organization')).length})
++                    <span
++                      className="filter-color"
++                      style={{ backgroundColor: NODE_COLORS.Organization }}
++                    ></span>
++                    Organizaciones (
++                    {
++                      nodes.filter((n) => n.labels?.includes("Organization"))
++                        .length
++                    }
++                    )
+                   </span>
+                 </label>
+                 <label className="filter-checkbox">
+                   <input
+                     type="checkbox"
+                     checked={nodeFilters.Domain}
+-                    onChange={(e) => setNodeFilters(prev => ({ ...prev, Domain: e.target.checked }))}
++                    onChange={(e) =>
++                      setNodeFilters((prev) => ({
++                        ...prev,
++                        Domain: e.target.checked,
++                      }))
++                    }
+                   />
+                   <span className="filter-label">
+-                    <span className="filter-color" style={{ backgroundColor: NODE_COLORS.Domain }}></span>
+-                    Dominios ({nodes.filter(n => n.labels?.includes('Domain')).length})
++                    <span
++                      className="filter-color"
++                      style={{ backgroundColor: NODE_COLORS.Domain }}
++                    ></span>
++                    Dominios (
++                    {nodes.filter((n) => n.labels?.includes("Domain")).length})
+                   </span>
+                 </label>
+               </div>
+@@ -422,7 +498,7 @@ function GraphVisualization() {
+ 
+       {/* Botón para mostrar controles si están ocultos */}
+       {!showControls && (
+-        <button 
++        <button
+           className="show-controls-btn"
+           onClick={() => setShowControls(true)}
+           aria-label="Mostrar controles"
+@@ -453,4 +529,3 @@ function GraphVisualization() {
+ }
+ 
+ export default GraphVisualization;
+-
+diff --git a/src/app/ui/src/interactions.js b/src/app/ui/src/interactions.js
+index 7e6a449..6afdff3 100644
+--- a/src/app/ui/src/interactions.js
++++ b/src/app/ui/src/interactions.js
+@@ -1,22 +1,26 @@
+-import NVL from '@neo4j-nvl/base'
++import NVL from "@neo4j-nvl/base";
+ import {
+   ClickInteraction,
+   DragNodeInteraction,
+   HoverInteraction,
+   PanInteraction,
+-  ZoomInteraction
+-} from '@neo4j-nvl/interaction-handlers'
++  ZoomInteraction,
++} from "@neo4j-nvl/interaction-handlers";
+ 
+ export default (parentContainer) => {
+-  const nodes = [{ id: '0' }, { id: '1' }]
+-  const rels = [{ id: '10', from: '0', to: '1' }]
+-  const myNvl = new NVL(parentContainer, nodes, rels)
++  const nodes = [{ id: "0" }, { id: "1" }];
++  const rels = [{ id: "10", from: "0", to: "1" }];
++  const myNvl = new NVL(parentContainer, nodes, rels, {
++    // Opciones de ForceDirected
++    enableCytoscape: true, // Auto-switch a CoseBilkent para grafos pequeños
++    enableVerlet: true, // Usar nuevo motor de física (recomendado)
++    intelWorkaround: false, // Solo activar si hay problemas con GPUs Intel
++  });
++  new ZoomInteraction(myNvl);
++  new PanInteraction(myNvl);
++  new DragNodeInteraction(myNvl);
++  new ClickInteraction(myNvl, { selectOnClick: true });
++  new HoverInteraction(myNvl, { drawShadowOnHover: true });
+ 
+-  new ZoomInteraction(myNvl)
+-  new PanInteraction(myNvl)
+-  new DragNodeInteraction(myNvl)
+-  new ClickInteraction(myNvl, { selectOnClick: true })
+-  new HoverInteraction(myNvl, { drawShadowOnHover: true })
+-
+-  return myNvl
+-}
+\ No newline at end of file
++  return myNvl;
++};
diff --git a/src/app/ui/src/components/GraphVisualization.js b/src/app/ui/src/components/GraphVisualization.js
index 3c311da..e05d37e 100644
--- a/src/app/ui/src/components/GraphVisualization.js
+++ b/src/app/ui/src/components/GraphVisualization.js
@@ -1,60 +1,60 @@
-import React, { useRef, useState, useEffect } from 'react';
-import { InteractiveNvlWrapper } from '@neo4j-nvl/react';
-import { useGraphData } from '../hooks/useGraphData';
-import NodeInfoPanel from './NodeInfoPanel';
-import './GraphVisualization.css';
+import React, { useRef, useState, useEffect } from "react";
+import { InteractiveNvlWrapper } from "@neo4j-nvl/react";
+import { useGraphData } from "../hooks/useGraphData";
+import NodeInfoPanel from "./NodeInfoPanel";
+import "./GraphVisualization.css";
 
 // Mapeo de colores para cada tipo de nodo
 const NODE_COLORS = {
-  'Person': '#4A90E2',      // Azul para Personas
-  'Organization': '#50C878', // Verde para Organizaciones
-  'Domain': '#FF6B6B'        // Rojo para Dominios
+  Person: "#2E5FCC", // Azul para Personas
+  Organization: "#50C878", // Verde para Organizaciones
+  Domain: "#DC143C", // Rojo para Dominios
 };
 
 // Función para obtener el color según el tipo de nodo
 function getNodeColor(labels) {
-  if (!labels || labels.length === 0) return '#888888';
-  
+  if (!labels || labels.length === 0) return "#888888";
+
   // Buscar el primer label que tenga un color definido
   for (const label of labels) {
     if (NODE_COLORS[label]) {
       return NODE_COLORS[label];
     }
   }
-  
-  return '#888888'; // Color por defecto
+
+  return "#888888"; // Color por defecto
 }
 
 // Función para enriquecer nodos con colores y hacerlos más visibles
 function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
-  return nodes.map(node => {
+  return nodes.map((node) => {
     // Si el nodo ya está marcado como oculto (fantasma), mantener su estilo
     if (node.hidden) {
       return {
         ...node,
         // Mantener opacidad reducida y estilo de nodo fantasma
         size: (node.size || 1.0) * sizeMultiplier * 0.7, // Más pequeños los nodos fantasma
-        radius: Math.max(10, (node.size || 1.0) * sizeMultiplier * 7)
+        radius: Math.max(10, (node.size || 1.0) * sizeMultiplier * 7),
       };
     }
-    
+
     const nodeColor = getNodeColor(node.labels);
-    
+
     // Tamaños base multiplicados por el factor de escala
     let baseSize;
-    if (node.labels?.includes('Person')) {
+    if (node.labels?.includes("Person")) {
       baseSize = 2.5 * sizeMultiplier;
-    } else if (node.labels?.includes('Organization')) {
+    } else if (node.labels?.includes("Organization")) {
       baseSize = 3.5 * sizeMultiplier;
-    } else if (node.labels?.includes('Domain')) {
+    } else if (node.labels?.includes("Domain")) {
       baseSize = 2.0 * sizeMultiplier;
     } else {
       baseSize = 2.0 * sizeMultiplier;
     }
-    
+
     // Calcular radio en píxeles (mínimo 15px para legibilidad)
     const radius = Math.max(15, baseSize * 10);
-    
+
     return {
       ...node,
       // Intentar múltiples propiedades de color que la librería podría aceptar
@@ -62,19 +62,15 @@ function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
       fill: nodeColor,
       backgroundColor: nodeColor,
       // Tamaños ajustables
-      size: baseSize,
+      size: baseSize * 5,
+      captions: [
+        {
+          key: "Bold text",
+          styles: ["bold", "large"],
+          value: node.caption,
+        },
+      ],
       radius: radius,
-      // Agregar estilo personalizado si es necesario
-      style: {
-        fill: nodeColor,
-        stroke: '#ffffff',
-        strokeWidth: Math.max(2, 3 * sizeMultiplier),
-        opacity: 0.9
-      },
-      // Asegurar que el texto sea visible
-      fontColor: '#ffffff',
-      fontSize: Math.max(12, 14 * sizeMultiplier),
-      fontWeight: 'bold'
     };
   });
 }
@@ -82,56 +78,77 @@ function enrichNodesWithColors(nodes, sizeMultiplier = 1.0) {
 // Layouts disponibles en @neo4j-nvl/react
 // Nota: Los nombres pueden variar según la versión de la librería
 const AVAILABLE_LAYOUTS = [
-  { value: 'force', label: 'Force-Directed', description: 'Layout basado en fuerzas físicas (recomendado)' },
-  { value: 'hierarchical', label: 'Jerárquico', description: 'Organiza nodos en niveles jerárquicos' },
-  { value: 'circular', label: 'Circular', description: 'Dispone nodos en círculo' },
-  { value: 'grid', label: 'Cuadrícula', description: 'Organiza nodos en una cuadrícula regular' },
-  { value: 'forceDirected', label: 'Force-Directed (alt)', description: 'Variante del layout de fuerzas' }
+  {
+    value: "force",
+    label: "Force-Directed",
+    description: "Layout basado en fuerzas físicas (recomendado)",
+  },
+  {
+    value: "hierarchical",
+    label: "Jerárquico",
+    description: "Organiza nodos en niveles jerárquicos",
+  },
+  {
+    value: "circular",
+    label: "Circular",
+    description: "Dispone nodos en círculo",
+  },
+  {
+    value: "grid",
+    label: "Cuadrícula",
+    description: "Organiza nodos en una cuadrícula regular",
+  },
+  {
+    value: "d3Force",
+    label: "Force-Directed (alt)",
+    description: "Variante del layout de fuerzas",
+  },
 ];
 
 function GraphVisualization() {
   const eventLogRef = useRef(null);
   const { nodes, relationships, stats, loading, error } = useGraphData();
   const [selectedNode, setSelectedNode] = useState(null);
-  const [currentLayout, setCurrentLayout] = useState('force');
+  const [currentLayout, setCurrentLayout] = useState("d3Force");
   const [layoutKey, setLayoutKey] = useState(0); // Key para forzar re-render
   const [nodeSizeMultiplier, setNodeSizeMultiplier] = useState(1.5); // Multiplicador de tamaño (1.0 = normal)
   const [showControls, setShowControls] = useState(true); // Mostrar/ocultar controles
-  
+
   // Filtros de nodos por tipo
   const [nodeFilters, setNodeFilters] = useState({
     Person: true,
     Organization: true,
-    Domain: true
+    Domain: true,
   });
-  
+
   // Filtrar nodos según los filtros activos
   const filteredNodes = React.useMemo(() => {
-    return nodes.filter(node => {
+    return nodes.filter((node) => {
       if (!node.labels || node.labels.length === 0) return true;
       // Mostrar nodo si al menos uno de sus labels está activo
-      return node.labels.some(label => nodeFilters[label] !== false);
+      return node.labels.some((label) => nodeFilters[label] !== false);
     });
   }, [nodes, nodeFilters]);
-  
+
   // Filtrar relaciones: mostrar todas las relaciones de nodos visibles
   // Incluso si el otro extremo está oculto, para ver todas las conexiones
   const filteredRelationships = React.useMemo(() => {
-    const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
-    return relationships.filter(rel => 
-      // Mostrar relación si al menos uno de sus nodos está visible
-      visibleNodeIds.has(rel.from) || visibleNodeIds.has(rel.to)
+    const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
+    return relationships.filter(
+      (rel) =>
+        // Mostrar relación si al menos uno de sus nodos está visible
+        visibleNodeIds.has(rel.from) || visibleNodeIds.has(rel.to)
     );
   }, [relationships, filteredNodes]);
-  
+
   // Incluir nodos "fantasma" (ocultos pero conectados) para que las relaciones se vean correctamente
   const allVisibleNodes = React.useMemo(() => {
-    const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
+    const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
     const connectedNodeIds = new Set();
-    
+
     // Encontrar todos los nodos conectados a nodos visibles
     // Usar relationships directamente para evitar dependencia circular
-    relationships.forEach(rel => {
+    relationships.forEach((rel) => {
       if (visibleNodeIds.has(rel.from)) {
         connectedNodeIds.add(rel.to);
       }
@@ -139,26 +156,29 @@ function GraphVisualization() {
         connectedNodeIds.add(rel.from);
       }
     });
-    
+
     // Obtener nodos conectados que no están visibles (para mostrar las relaciones)
-    const ghostNodes = nodes.filter(n => 
-      connectedNodeIds.has(n.id) && !visibleNodeIds.has(n.id)
+    const ghostNodes = nodes.filter(
+      (n) => connectedNodeIds.has(n.id) && !visibleNodeIds.has(n.id)
     );
-    
+
     // Combinar nodos visibles con nodos fantasma (pero marcarlos como ocultos visualmente)
-    return [...filteredNodes, ...ghostNodes.map(node => ({
-      ...node,
-      hidden: true, // Marcar como oculto para estilos diferentes
-      opacity: 0.3, // Hacer más transparentes
-      style: {
-        ...node.style,
-        opacity: 0.3,
-        stroke: '#ccc',
-        strokeWidth: 1
-      }
-    }))];
+    return [
+      ...filteredNodes,
+      ...ghostNodes.map((node) => ({
+        ...node,
+        hidden: true, // Marcar como oculto para estilos diferentes
+        opacity: 0.3, // Hacer más transparentes
+        style: {
+          ...node.style,
+          opacity: 0.3,
+          stroke: "#ccc",
+          strokeWidth: 1,
+        },
+      })),
+    ];
   }, [filteredNodes, relationships, nodes]);
-  
+
   // Enriquecer nodos con colores y hacerlos más visibles
   // Incluir nodos visibles y nodos fantasma (conectados pero ocultos)
   const enrichedNodes = React.useMemo(() => {
@@ -167,8 +187,8 @@ function GraphVisualization() {
 
   // Forzar actualización del layout cuando cambia
   useEffect(() => {
-    console.log('Layout cambiado a:', currentLayout);
-    setLayoutKey(prev => prev + 1);
+    console.log("Layout cambiado a:", currentLayout);
+    setLayoutKey((prev) => prev + 1);
     // Limpiar selección de nodo al cambiar layout para mejor experiencia
     setSelectedNode(null);
   }, [currentLayout]);
@@ -185,90 +205,106 @@ function GraphVisualization() {
 
   const mouseEventCallbacks = {
     onHover: (element, hitTargets, originalEvent) => {
-      logEvent('Hover', { originalEvent, data: element, hitTargets });
+      logEvent("Hover", { originalEvent, data: element, hitTargets });
       // Mostrar información del nodo al hacer hover
       if (element && element.id) {
-        const hoveredNode = enrichedNodes.find(n => n.id === element.id);
+        const hoveredNode = enrichedNodes.find((n) => n.id === element.id);
         if (hoveredNode) {
           setSelectedNode(hoveredNode);
         }
       }
     },
-    
+
     onNodeClick: (node, hitTargets, originalEvent) => {
-      logEvent('Click en Nodo', { originalEvent, data: node, hitTargets });
+      logEvent("Click en Nodo", { originalEvent, data: node, hitTargets });
       // Seleccionar nodo al hacer click
       if (node && node.id) {
-        const clickedNode = enrichedNodes.find(n => n.id === node.id);
+        const clickedNode = enrichedNodes.find((n) => n.id === node.id);
         if (clickedNode) {
           setSelectedNode(clickedNode);
         }
       }
     },
-    
+
     onNodeRightClick: (node, hitTargets, originalEvent) =>
-      logEvent('Click Derecho en Nodo', { originalEvent, data: node, hitTargets }),
-    
+      logEvent("Click Derecho en Nodo", {
+        originalEvent,
+        data: node,
+        hitTargets,
+      }),
+
     onNodeDoubleClick: (node, hitTargets, originalEvent) =>
-      logEvent('Doble Click en Nodo', { originalEvent, data: node, hitTargets }),
-    
+      logEvent("Doble Click en Nodo", {
+        originalEvent,
+        data: node,
+        hitTargets,
+      }),
+
     onRelationshipClick: (rel, hitTargets, originalEvent) =>
-      logEvent('Click en Relación', { originalEvent, data: rel, hitTargets }),
-    
+      logEvent("Click en Relación", { originalEvent, data: rel, hitTargets }),
+
     onRelationshipRightClick: (rel, hitTargets, originalEvent) =>
-      logEvent('Click Derecho en Relación', { originalEvent, data: rel, hitTargets }),
-    
+      logEvent("Click Derecho en Relación", {
+        originalEvent,
+        data: rel,
+        hitTargets,
+      }),
+
     onRelationshipDoubleClick: (rel, hitTargets, originalEvent) =>
-      logEvent('Doble Click en Relación', { originalEvent, data: rel, hitTargets }),
-    
+      logEvent("Doble Click en Relación", {
+        originalEvent,
+        data: rel,
+        hitTargets,
+      }),
+
     onCanvasClick: (originalEvent) => {
-      logEvent('Click en Canvas', { originalEvent });
+      logEvent("Click en Canvas", { originalEvent });
       // Cerrar panel al hacer click en el canvas
       setSelectedNode(null);
     },
-    
-    onCanvasDoubleClick: (originalEvent) => 
-      logEvent('Doble Click en Canvas', { originalEvent }),
-    
-    onCanvasRightClick: (originalEvent) => 
-      logEvent('Click Derecho en Canvas', { originalEvent }),
-    
+
+    onCanvasDoubleClick: (originalEvent) =>
+      logEvent("Doble Click en Canvas", { originalEvent }),
+
+    onCanvasRightClick: (originalEvent) =>
+      logEvent("Click Derecho en Canvas", { originalEvent }),
+
     onDrag: (draggedNodes, originalEvent) =>
-      logEvent('Arrastrando Nodos', { originalEvent, data: draggedNodes }),
-    
+      logEvent("Arrastrando Nodos", { originalEvent, data: draggedNodes }),
+
     onPan: (pan, originalEvent) =>
-      logEvent('Pan', { originalEvent, data: pan }),
-    
-    onZoom: (zoomLevel, originalEvent) => 
-      logEvent('Zoom', { originalEvent, data: zoomLevel })
+      logEvent("Pan", { originalEvent, data: pan }),
+
+    onZoom: (zoomLevel, originalEvent) =>
+      logEvent("Zoom", { originalEvent, data: zoomLevel }),
   };
 
   // Configuración de opciones según el layout
   const nvlOptions = React.useMemo(() => {
     const baseOptions = {
       layout: currentLayout,
-      initialZoom: currentLayout === 'circular' ? 0.8 : 1.0, // Zoom inicial menor para circular
       allowDynamicMinZoom: true,
       disableWebGL: false,
       maxZoom: 5,
-      minZoom: 0.1
+      minZoom: 0.1,
+      layoutOptions: { enableCytoscape: true },
     };
-    
+
     // Opciones específicas para layout circular
-    if (currentLayout === 'circular') {
+    if (currentLayout === "circular") {
       // Forzar que el layout se aplique correctamente
       return {
         ...baseOptions,
         // Algunas librerías necesitan estas opciones para circular
         circular: {
-          enabled: true
-        }
+          enabled: true,
+        },
       };
     }
-    
+
     // Debug: ver qué opciones se están pasando
-    console.log('NVL Options:', baseOptions);
-    
+    console.log("NVL Options:", baseOptions);
+
     return baseOptions;
   }, [currentLayout]);
 
@@ -292,8 +328,9 @@ function GraphVisualization() {
           <h3>❌ Error al cargar datos</h3>
           <p>{error}</p>
           <p className="error-hint">
-            Asegúrate de que el archivo graph-data.json existe en la carpeta public/.
-            Ejecuta: <code>python src/app/scripts/export_neo4j_data.py</code>
+            Asegúrate de que el archivo graph-data.json existe en la carpeta
+            public/. Ejecuta:{" "}
+            <code>python src/app/scripts/export_neo4j_data.py</code>
           </p>
         </div>
       </div>
@@ -306,20 +343,23 @@ function GraphVisualization() {
       <div className="graph-container">
         <div className="empty-state">
           <h3>📊 No hay datos disponibles</h3>
-          <p>El grafo está vacío. Ejecuta el script de exportación para generar datos.</p>
+          <p>
+            El grafo está vacío. Ejecuta el script de exportación para generar
+            datos.
+          </p>
         </div>
       </div>
     );
   }
 
   return (
-    <div className={`graph-container ${selectedNode ? 'has-panel' : ''}`}>
+    <div className={`graph-container ${selectedNode ? "has-panel" : ""}`}>
       {/* Panel de Controles */}
       {showControls && (
         <div className="controls-panel">
           <div className="controls-header">
             <h4>Configuración</h4>
-            <button 
+            <button
               className="toggle-controls-btn"
               onClick={() => setShowControls(false)}
               aria-label="Ocultar controles"
@@ -327,7 +367,7 @@ function GraphVisualization() {
               −
             </button>
           </div>
-          
+
           <div className="controls-content">
             {/* Selector de Layout */}
             <div className="control-group">
@@ -338,14 +378,17 @@ function GraphVisualization() {
                 onChange={(e) => setCurrentLayout(e.target.value)}
                 className="control-select"
               >
-                {AVAILABLE_LAYOUTS.map(layout => (
+                {AVAILABLE_LAYOUTS.map((layout) => (
                   <option key={layout.value} value={layout.value}>
                     {layout.label}
                   </option>
                 ))}
               </select>
               <span className="control-description">
-                {AVAILABLE_LAYOUTS.find(l => l.value === currentLayout)?.description}
+                {
+                  AVAILABLE_LAYOUTS.find((l) => l.value === currentLayout)
+                    ?.description
+                }
               </span>
             </div>
 
@@ -361,7 +404,9 @@ function GraphVisualization() {
                 max="3.0"
                 step="0.1"
                 value={nodeSizeMultiplier}
-                onChange={(e) => setNodeSizeMultiplier(parseFloat(e.target.value))}
+                onChange={(e) =>
+                  setNodeSizeMultiplier(parseFloat(e.target.value))
+                }
                 className="control-slider"
               />
               <div className="slider-labels">
@@ -382,33 +427,64 @@ function GraphVisualization() {
                   <input
                     type="checkbox"
                     checked={nodeFilters.Person}
-                    onChange={(e) => setNodeFilters(prev => ({ ...prev, Person: e.target.checked }))}
+                    onChange={(e) =>
+                      setNodeFilters((prev) => ({
+                        ...prev,
+                        Person: e.target.checked,
+                      }))
+                    }
                   />
                   <span className="filter-label">
-                    <span className="filter-color" style={{ backgroundColor: NODE_COLORS.Person }}></span>
-                    Personas ({nodes.filter(n => n.labels?.includes('Person')).length})
+                    <span
+                      className="filter-color"
+                      style={{ backgroundColor: NODE_COLORS.Person }}
+                    ></span>
+                    Personas (
+                    {nodes.filter((n) => n.labels?.includes("Person")).length})
                   </span>
                 </label>
                 <label className="filter-checkbox">
                   <input
                     type="checkbox"
                     checked={nodeFilters.Organization}
-                    onChange={(e) => setNodeFilters(prev => ({ ...prev, Organization: e.target.checked }))}
+                    onChange={(e) =>
+                      setNodeFilters((prev) => ({
+                        ...prev,
+                        Organization: e.target.checked,
+                      }))
+                    }
                   />
                   <span className="filter-label">
-                    <span className="filter-color" style={{ backgroundColor: NODE_COLORS.Organization }}></span>
-                    Organizaciones ({nodes.filter(n => n.labels?.includes('Organization')).length})
+                    <span
+                      className="filter-color"
+                      style={{ backgroundColor: NODE_COLORS.Organization }}
+                    ></span>
+                    Organizaciones (
+                    {
+                      nodes.filter((n) => n.labels?.includes("Organization"))
+                        .length
+                    }
+                    )
                   </span>
                 </label>
                 <label className="filter-checkbox">
                   <input
                     type="checkbox"
                     checked={nodeFilters.Domain}
-                    onChange={(e) => setNodeFilters(prev => ({ ...prev, Domain: e.target.checked }))}
+                    onChange={(e) =>
+                      setNodeFilters((prev) => ({
+                        ...prev,
+                        Domain: e.target.checked,
+                      }))
+                    }
                   />
                   <span className="filter-label">
-                    <span className="filter-color" style={{ backgroundColor: NODE_COLORS.Domain }}></span>
-                    Dominios ({nodes.filter(n => n.labels?.includes('Domain')).length})
+                    <span
+                      className="filter-color"
+                      style={{ backgroundColor: NODE_COLORS.Domain }}
+                    ></span>
+                    Dominios (
+                    {nodes.filter((n) => n.labels?.includes("Domain")).length})
                   </span>
                 </label>
               </div>
@@ -422,7 +498,7 @@ function GraphVisualization() {
 
       {/* Botón para mostrar controles si están ocultos */}
       {!showControls && (
-        <button 
+        <button
           className="show-controls-btn"
           onClick={() => setShowControls(true)}
           aria-label="Mostrar controles"
@@ -453,4 +529,3 @@ function GraphVisualization() {
 }
 
 export default GraphVisualization;
-
diff --git a/src/app/ui/src/interactions.js b/src/app/ui/src/interactions.js
index 7e6a449..6afdff3 100644
--- a/src/app/ui/src/interactions.js
+++ b/src/app/ui/src/interactions.js
@@ -1,22 +1,26 @@
-import NVL from '@neo4j-nvl/base'
+import NVL from "@neo4j-nvl/base";
 import {
   ClickInteraction,
   DragNodeInteraction,
   HoverInteraction,
   PanInteraction,
-  ZoomInteraction
-} from '@neo4j-nvl/interaction-handlers'
+  ZoomInteraction,
+} from "@neo4j-nvl/interaction-handlers";
 
 export default (parentContainer) => {
-  const nodes = [{ id: '0' }, { id: '1' }]
-  const rels = [{ id: '10', from: '0', to: '1' }]
-  const myNvl = new NVL(parentContainer, nodes, rels)
+  const nodes = [{ id: "0" }, { id: "1" }];
+  const rels = [{ id: "10", from: "0", to: "1" }];
+  const myNvl = new NVL(parentContainer, nodes, rels, {
+    // Opciones de ForceDirected
+    enableCytoscape: true, // Auto-switch a CoseBilkent para grafos pequeños
+    enableVerlet: true, // Usar nuevo motor de física (recomendado)
+    intelWorkaround: false, // Solo activar si hay problemas con GPUs Intel
+  });
+  new ZoomInteraction(myNvl);
+  new PanInteraction(myNvl);
+  new DragNodeInteraction(myNvl);
+  new ClickInteraction(myNvl, { selectOnClick: true });
+  new HoverInteraction(myNvl, { drawShadowOnHover: true });
 
-  new ZoomInteraction(myNvl)
-  new PanInteraction(myNvl)
-  new DragNodeInteraction(myNvl)
-  new ClickInteraction(myNvl, { selectOnClick: true })
-  new HoverInteraction(myNvl, { drawShadowOnHover: true })
-
-  return myNvl
-}
\ No newline at end of file
+  return myNvl;
+};
