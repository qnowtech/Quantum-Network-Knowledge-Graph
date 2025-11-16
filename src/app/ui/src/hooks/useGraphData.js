import { useState, useEffect } from 'react';

/**
 * Hook personalizado para cargar datos del grafo desde el archivo JSON.
 * 
 * El archivo graph-data.json se genera mediante el script export_neo4j_data.py
 * y debe estar en la carpeta public/ para que React pueda accederlo.
 * 
 * @returns {Object} { nodes, relationships, stats, loading, error }
 */
export function useGraphData() {
  const [data, setData] = useState({
    nodes: [],
    relationships: [],
    stats: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadGraphData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Cargar datos desde el archivo JSON en public/
        // En desarrollo, usar ruta absoluta desde la raíz
        // En producción, usar process.env.PUBLIC_URL si está configurado
        let jsonPath = '/graph-data.json';
        
        // Si estamos en desarrollo (sin PUBLIC_URL), usar ruta absoluta
        // Si estamos en producción con homepage configurado, usar PUBLIC_URL
        if (process.env.PUBLIC_URL && process.env.PUBLIC_URL !== '') {
          jsonPath = `${process.env.PUBLIC_URL}/graph-data.json`;
        }
        
        const response = await fetch(jsonPath);
        
        if (!response.ok) {
          throw new Error(`Error al cargar datos: ${response.status} ${response.statusText}`);
        }
        
        const graphData = await response.json();
        
        setData({
          nodes: graphData.nodes || [],
          relationships: graphData.relationships || [],
          stats: graphData.stats || null
        });
      } catch (err) {
        console.error('Error cargando datos del grafo:', err);
        setError(err.message);
        // En caso de error, usar datos vacíos para evitar crashes
        setData({
          nodes: [],
          relationships: [],
          stats: null
        });
      } finally {
        setLoading(false);
      }
    };

    loadGraphData();
  }, []);

  return {
    nodes: data.nodes,
    relationships: data.relationships,
    stats: data.stats,
    loading,
    error
  };
}

