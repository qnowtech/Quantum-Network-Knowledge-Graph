import React, { useState } from 'react';
import { useCypherQuery } from '../hooks/useCypherQuery';
import { STRATEGIC_QUERIES } from '../data/strategicQueries';
import './QueryPanel.css';

/**
 * Panel para mostrar y ejecutar queries estratégicas del README
 */
function QueryPanel({ nodes = [], relationships = [], onClose }) {
  const [selectedQuery, setSelectedQuery] = useState(null);
  const [inputValues, setInputValues] = useState({});
  const { executeQuery, results, loading, error, clearResults } = useCypherQuery();

  const handleQuerySelect = (query) => {
    setSelectedQuery(query);
    clearResults();
    // Inicializar valores de entrada si la query los requiere
    if (query.requiresInput) {
      setInputValues(prev => ({
        ...prev,
        [query.id]: query.parameters[Object.keys(query.parameters)[0]] || ''
      }));
    }
  };

  const handleExecute = async () => {
    if (!selectedQuery) return;

    // Preparar parámetros
    const parameters = { ...selectedQuery.parameters };
    if (selectedQuery.requiresInput) {
      const inputKey = Object.keys(parameters)[0];
      parameters[inputKey] = inputValues[selectedQuery.id] || '';
    }

    await executeQuery(selectedQuery.cypher, parameters, nodes, relationships);
  };

  const handleInputChange = (queryId, value) => {
    setInputValues(prev => ({
      ...prev,
      [queryId]: value
    }));
  };

  return (
    <div className="query-panel">
      <div className="query-panel-header">
        <h3>Queries Estratégicas</h3>
        <button className="close-button" onClick={onClose} aria-label="Cerrar">
          ×
        </button>
      </div>

      <div className="query-panel-content">
        {/* Lista de queries disponibles */}
        <div className="queries-list">
          <h4>Selecciona una Query</h4>
          {STRATEGIC_QUERIES.map(query => (
            <div
              key={query.id}
              className={`query-item ${selectedQuery?.id === query.id ? 'active' : ''}`}
              onClick={() => handleQuerySelect(query)}
            >
              <div className="query-item-header">
                <span className="query-number">{query.id}</span>
                <h5>{query.title}</h5>
              </div>
              <p className="query-description">{query.description}</p>
            </div>
          ))}
        </div>

        {/* Detalles de la query seleccionada */}
        {selectedQuery && (
          <div className="query-details">
            <div className="query-question">
              <h4>Pregunta:</h4>
              <p className="question-text">{selectedQuery.question}</p>
            </div>

            {/* Input para queries que requieren parámetros */}
            {selectedQuery.requiresInput && (
              <div className="query-input">
                <label htmlFor={`input-${selectedQuery.id}`}>
                  {selectedQuery.inputLabel || 'Parámetro requerido'}:
                </label>
                <input
                  id={`input-${selectedQuery.id}`}
                  type="text"
                  value={inputValues[selectedQuery.id] || ''}
                  onChange={(e) => handleInputChange(selectedQuery.id, e.target.value)}
                  placeholder={selectedQuery.inputPlaceholder || 'Ingresa el valor...'}
                  className="query-parameter-input"
                />
              </div>
            )}

            {/* Query Cypher */}
            <div className="query-cypher">
              <div className="cypher-header">
                <h4>Query Cypher:</h4>
                <button
                  className="copy-button"
                  onClick={() => {
                    navigator.clipboard.writeText(selectedQuery.cypher);
                  }}
                  title="Copiar query"
                >
                  📋 Copiar
                </button>
              </div>
              <pre className="cypher-code">
                <code>{selectedQuery.cypher}</code>
              </pre>
            </div>

            {/* Botón de ejecución */}
            <div className="query-actions">
              <button
                className="execute-button"
                onClick={handleExecute}
                disabled={loading || (selectedQuery.requiresInput && !inputValues[selectedQuery.id])}
              >
                {loading ? '⏳ Ejecutando...' : '▶️ Ejecutar Query'}
              </button>
            </div>

            {/* Resultados */}
            {error && (
              <div className="query-error">
                <h4>❌ Error:</h4>
                <p>{error}</p>
              </div>
            )}

            {results && (
              <div className="query-results">
                <div className="results-header">
                  <h4>📊 Resultados:</h4>
                  <button
                    className="clear-button"
                    onClick={clearResults}
                    title="Limpiar resultados"
                  >
                    ✕
                  </button>
                </div>
                <div className="results-content">
                  {/* Estadísticas de ejecución */}
                  <div className="result-stats">
                    <span className="stat-item">
                      <strong>{results.recordsCount || 0}</strong> registros
                    </span>
                    {results.executionTime && (
                      <span className="stat-item">
                        <strong>{(results.executionTime / 1000).toFixed(2)}s</strong> tiempo
                      </span>
                    )}
                    {results.success !== undefined && (
                      <span className={`stat-item ${results.success ? 'success' : 'error'}`}>
                        {results.success ? '✅' : '❌'} {results.success ? 'Éxito' : 'Error'}
                      </span>
                    )}
                  </div>

                  {/* Tabla de resultados */}
                  {results.data && results.data.length > 0 ? (
                    <div className="results-table-container">
                      <table className="results-table">
                        <thead>
                          <tr>
                            {results.columns && results.columns.map((col, idx) => (
                              <th key={idx}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {results.data.map((row, rowIdx) => (
                            <tr key={rowIdx}>
                              {results.columns && results.columns.map((col, colIdx) => (
                                <td key={colIdx}>
                                  {Array.isArray(row[col]) 
                                    ? row[col].join(', ') 
                                    : typeof row[col] === 'object' && row[col] !== null
                                    ? JSON.stringify(row[col])
                                    : String(row[col] ?? '')}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="results-empty">
                      <p>No se encontraron resultados para esta query.</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default QueryPanel;

