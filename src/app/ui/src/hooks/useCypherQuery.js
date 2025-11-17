import { useState, useCallback } from 'react';

/**
 * Hook para ejecutar queries Cypher contra Neo4j
 * 
 * Por ahora simula la ejecución usando los datos del grafo cargado.
 * En el futuro, esto puede conectarse a un endpoint backend que ejecute
 * queries reales contra Neo4j.
 * 
 * @returns {Object} { executeQuery, results, loading, error }
 */
export function useCypherQuery() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Ejecuta una query Cypher contra Neo4j a través del backend API
   * 
   * @param {string} cypherQuery - La query Cypher a ejecutar
   * @param {Object} parameters - Parámetros para la query
   * @param {Array} nodes - Nodos del grafo (no usado, mantenido por compatibilidad)
   * @param {Array} relationships - Relaciones del grafo (no usado, mantenido por compatibilidad)
   */
  const executeQuery = useCallback(async (cypherQuery, parameters = {}, nodes = [], relationships = []) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Determinar la URL del API (desarrollo o producción)
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      
      // Ejecutar query contra el backend
      const response = await fetch(`${apiUrl}/api/query/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cypher: cypherQuery,
          parameters: parameters
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Formatear resultados para el componente
      const formattedResults = {
        success: data.success,
        data: data.data,
        columns: data.columns,
        recordsCount: data.records_count,
        executionTime: data.execution_time_ms,
        query: cypherQuery,
        parameters: parameters
      };

      setResults(formattedResults);
    } catch (err) {
      console.error('Error ejecutando query:', err);
      setError(err.message || 'Error al ejecutar la query');
      setResults(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  return {
    executeQuery,
    results,
    loading,
    error,
    clearResults
  };
}

