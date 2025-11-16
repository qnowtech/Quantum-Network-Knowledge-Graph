# Knowledge Graph React

Landing page minimalista para visualizar grafos de conocimiento con Neo4j.

## Tecnologías Esenciales

- **React 18**: Framework
- **Neo4j NVL**: Visualización de grafos
- **Neo4j NDL**: Componentes UI

## Comandos

### Instalar y ejecutar
```bash
npm install
npm start
```

Abre http://localhost:3000

### Producción
```bash
npm run build
```

## Estructura

```
ui/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── GraphVisualization.js    # Grafo interactivo
│   │   └── GraphVisualization.css
│   ├── data/
│   │   └── mockData.js              # Datos del grafo
│   ├── App.js
│   ├── App.css
│   └── index.js
└── package.json
```

## Personalizar Datos

Edita `src/data/mockData.js` para cambiar nodos y relaciones del grafo.

