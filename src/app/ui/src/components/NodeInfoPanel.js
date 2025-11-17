import React from 'react';
import './NodeInfoPanel.css';

/**
 * Panel lateral que muestra información detallada de un nodo seleccionado
 */
function NodeInfoPanel({ node, relationships, allNodes, onClose }) {
  if (!node) return null;

  // Encontrar todas las relaciones que involucran este nodo
  const nodeRelationships = relationships.filter(
    rel => rel.from === node.id || rel.to === node.id
  );

  // Encontrar los nodos relacionados
  const relatedNodes = nodeRelationships.map(rel => {
    const relatedNodeId = rel.from === node.id ? rel.to : rel.from;
    const relatedNode = allNodes.find(n => n.id === relatedNodeId);
    return {
      node: relatedNode,
      relationship: rel,
      direction: rel.from === node.id ? 'outgoing' : 'incoming'
    };
  }).filter(item => item.node); // Filtrar nodos que no existen

  return (
    <div className="node-info-panel">
      <div className="panel-header">
        <h3>Información del Nodo</h3>
        <button className="close-button" onClick={onClose} aria-label="Cerrar">
          ×
        </button>
      </div>
      
      <div className="panel-content">
        {/* Información básica del nodo */}
        <div className="node-basic-info">
          <h4 className="node-title">{node.caption}</h4>
          <div className="node-labels">
            {node.labels && node.labels.map((label, idx) => (
              <span key={idx} className="node-label">{label}</span>
            ))}
          </div>
          {node.degree !== undefined && (
            <div className="node-degree">
              <span className="degree-label">Degree (Conexiones):</span>
              <span className="degree-value">{node.degree}</span>
            </div>
          )}
        </div>

        {/* Propiedades del nodo */}
        {node.properties && Object.keys(node.properties).length > 0 && (
          <div className="node-properties">
            <h5>Propiedades</h5>
            <div className="properties-list">
              {Object.entries(node.properties).map(([key, value]) => (
                <div key={key} className="property-item">
                  <span className="property-key">{key}:</span>
                  <span className="property-value">
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Resumen de relaciones por tipo */}
        <div className="relationships-summary">
          <h5>Resumen de Relaciones</h5>
          <div className="summary-stats">
            {(() => {
              const relTypes = {};
              nodeRelationships.forEach(rel => {
                relTypes[rel.type] = (relTypes[rel.type] || 0) + 1;
              });
              return Object.entries(relTypes).map(([type, count]) => (
                <div key={type} className="summary-item">
                  <span className="summary-type">{type}:</span>
                  <span className="summary-count">{count}</span>
                </div>
              ));
            })()}
          </div>
        </div>

        {/* Relaciones */}
        <div className="node-relationships">
          <h5>
            Relaciones Detalladas ({nodeRelationships.length})
          </h5>
          {relatedNodes.length > 0 ? (
            <div className="relationships-list">
              {relatedNodes.map((item, idx) => (
                <div key={idx} className="relationship-item">
                  <div className="relationship-type">
                    {item.direction === 'outgoing' ? '→' : '←'} {item.relationship.type}
                  </div>
                  <div className="related-node">
                    {item.node.caption}
                    <span className="related-node-label">
                      ({item.node.labels?.[0] || 'Node'})
                    </span>
                  </div>
                  {item.relationship.properties && 
                   Object.keys(item.relationship.properties).length > 0 && (
                    <div className="relationship-props">
                      {Object.entries(item.relationship.properties).map(([key, value]) => (
                        <span key={key} className="rel-prop">
                          {key}: {String(value)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="no-relationships">Este nodo no tiene relaciones</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default NodeInfoPanel;

