# 🚀 Guía Rápida: Levantar el Proyecto Localmente

Esta guía te ayudará a levantar la aplicación de visualización del grafo de conocimiento en tu máquina local.

## 📋 Requisitos Previos

- **Python 3.12+** con las dependencias del proyecto instaladas
- **Node.js 18+** y **npm** instalados
- **Credenciales de Neo4j** (ya configuradas en `.cursor/mcp.json`)

## 🎯 Pasos para Levantar el Proyecto

### Paso 1: Configurar Variables de Entorno (si es necesario)

Si no tienes un archivo `.env` en la raíz del proyecto, créalo con:

```env
NEO4J_URI=neo4j+s://87983fcb.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_QUANTUM_NETWORK_AURA=6LYXoE4Z5jrCwJVikRtk5TwcJNGn8C5UFiXu4YskEnY
```

> **Nota**: Las credenciales ya están en `.cursor/mcp.json`, pero el script Python las necesita en variables de entorno o en `.env`.

### Paso 2: Exportar Datos de Neo4j

Primero, necesitas exportar los datos del grafo de Neo4j a un archivo JSON que React pueda consumir:

```bash
# Desde la raíz del proyecto
python src/app/scripts/export_neo4j_data.py
```

Esto generará el archivo `src/app/ui/public/graph-data.json` con todos los datos del grafo.

**✅ Verificación**: Asegúrate de que el archivo se creó correctamente:
```bash
# En Windows PowerShell
Test-Path src/app/ui/public/graph-data.json

# En Linux/Mac
ls -la src/app/ui/public/graph-data.json
```

### Paso 3: Instalar Dependencias de Node.js

```bash
cd src/app/ui
npm install
```

### Paso 4: Levantar el Servidor de Desarrollo

```bash
# Asegúrate de estar en src/app/ui
npm start
```

Esto abrirá automáticamente tu navegador en `http://localhost:3000` y verás la visualización del grafo.

## 🔄 Flujo de Trabajo Completo

```bash
# 1. Desde la raíz del proyecto, exportar datos
python src/app/scripts/export_neo4j_data.py

# 2. Ir al directorio de la app React
cd src/app/ui

# 3. Instalar dependencias (solo la primera vez)
npm install

# 4. Levantar el servidor de desarrollo
npm start
```

## 🛠️ Comandos Útiles

### Actualizar Datos del Grafo

Si actualizas datos en Neo4j y quieres ver los cambios:

```bash
# Desde la raíz del proyecto
python src/app/scripts/export_neo4j_data.py

# Luego refresca el navegador (el servidor de desarrollo recargará automáticamente)
```

### Construir para Producción

```bash
cd src/app/ui
npm run build
```

Esto generará una carpeta `build/` con los archivos optimizados para producción.

## ❓ Troubleshooting

### Error: "No se puede encontrar el módulo 'neo4j'"

```bash
# Instala las dependencias de Python
uv sync
# o
pip install neo4j
```

### Error: "Cannot find module" en React

```bash
cd src/app/ui
rm -rf node_modules package-lock.json
npm install
```

### Error: "graph-data.json not found"

1. Verifica que ejecutaste el script de exportación
2. Verifica que el archivo existe en `src/app/ui/public/graph-data.json`
3. Verifica las credenciales de Neo4j en `.env` o variables de entorno

### El puerto 3000 está ocupado

El servidor te preguntará si quieres usar otro puerto, o puedes especificarlo:

```bash
PORT=3001 npm start
```

## 📁 Estructura de Archivos Importantes

```
src/app/
├── scripts/
│   └── export_neo4j_data.py    # Script para exportar datos de Neo4j
├── ui/
│   ├── public/
│   │   └── graph-data.json     # Datos exportados (generado)
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   └── GraphVisualization.js
│   │   └── hooks/
│   │       └── useGraphData.js
│   └── package.json
└── README.md                    # Este archivo
```

## 🎨 Características de la Aplicación

- **Visualización Interactiva**: Arrastra nodos, haz zoom, pan
- **Datos en Tiempo Real**: Carga datos desde Neo4j
- **Estadísticas**: Muestra conteo de nodos, relaciones y tipos
- **Interactividad**: Click, hover, y más eventos en nodos y relaciones

## 🔗 Próximos Pasos

Una vez que tengas la app corriendo localmente, puedes:
- Personalizar los estilos en `src/app/ui/src/components/GraphVisualization.css`
- Agregar más funcionalidades en los componentes
- Preparar el despliegue a GitHub Pages (ver `DEPLOYMENT.md`)

