# Tests End-to-End de la API

Este documento describe los tests end-to-end para validar que la API FastAPI funciona correctamente y se integra con la UI.

## Ejecutar los Tests

### Todos los tests de la API:

```bash
pytest tests/test_api_end_to_end.py -v
```

### Test específico:

```bash
pytest tests/test_api_end_to_end.py::TestAPIEndToEnd::test_health_check -v
```

### Con cobertura:

```bash
pytest tests/test_api_end_to_end.py --cov=src.api --cov-report=html
```

## Tests Incluidos

### TestAPIEndToEnd

- `test_health_check`: Valida que el endpoint de health check funciona
- `test_root_endpoint`: Valida que el endpoint raíz funciona
- `test_query_execute_with_mock`: Valida ejecución de queries con mock de Neo4j
- `test_query_execute_empty_query`: Valida que queries vacías son rechazadas
- `test_query_execute_with_parameters`: Valida manejo de parámetros
- `test_query_response_format`: Valida formato de respuesta
- `test_cors_headers`: Valida configuración CORS
- `test_error_handling`: Valida manejo de errores

### TestUIIntegration

- `test_query_response_compatible_with_ui`: Valida compatibilidad con formato UI
- `test_strategic_queries_format`: Valida queries estratégicas del README

### TestRealNeo4jIntegration

- `test_real_neo4j_connection`: Test con Neo4j real (requiere conexión)
- `test_real_query_execution`: Test ejecutando query real (requiere conexión)

**Nota**: Los tests con Neo4j real están deshabilitados por defecto. Para ejecutarlos:

```bash
SKIP_REAL_NEO4J_TESTS=false pytest tests/test_api_end_to_end.py::TestRealNeo4jIntegration -v
```

## Validaciones

Los tests validan:

1. ✅ La API FastAPI está funcionando
2. ✅ Los endpoints responden correctamente
3. ✅ Las queries Cypher se ejecutan (con mock)
4. ✅ Los resultados se formatean correctamente
5. ✅ El formato es compatible con la UI
6. ✅ Los errores se manejan apropiadamente
7. ✅ CORS está configurado correctamente

## Mock de Neo4j

Los tests usan mocks de Neo4j para no requerir una conexión real durante el desarrollo. El mock simula:

- Driver de Neo4j
- Sesiones
- Resultados de queries
- Registros con datos de ejemplo

## Integración con UI

El test `test_query_response_compatible_with_ui` valida que el formato de respuesta de la API es compatible con el formato esperado por `useCypherQuery.js` en React.

Formato esperado:
```javascript
{
  success: true,
  data: [...],
  columns: [...],
  recordsCount: 2,
  executionTime: 123.45,
  query: "...",
  parameters: {...}
}
```

