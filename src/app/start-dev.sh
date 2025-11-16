#!/bin/bash
# Script rápido para levantar el proyecto en desarrollo (Linux/Mac)
# Ejecuta: ./src/app/start-dev.sh

set -e

echo "🚀 Iniciando proyecto de visualización del grafo..."
echo ""

# Paso 1: Exportar datos de Neo4j
echo "📊 Paso 1/3: Exportando datos de Neo4j..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORT_SCRIPT="$SCRIPT_DIR/scripts/export_neo4j_data.py"

if ! python "$EXPORT_SCRIPT"; then
    echo "❌ Error al exportar datos. Verifica las credenciales de Neo4j."
    exit 1
fi

echo "✅ Datos exportados correctamente"
echo ""

# Paso 2: Verificar/instalar dependencias de Node.js
UI_PATH="$SCRIPT_DIR/ui"
NODE_MODULES="$UI_PATH/node_modules"

if [ ! -d "$NODE_MODULES" ]; then
    echo "📦 Paso 2/3: Instalando dependencias de Node.js..."
    cd "$UI_PATH"
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error al instalar dependencias de Node.js"
        exit 1
    fi
    echo "✅ Dependencias instaladas"
else
    echo "✅ Dependencias de Node.js ya instaladas"
fi
echo ""

# Paso 3: Levantar servidor de desarrollo
echo "🌐 Paso 3/3: Levantando servidor de desarrollo..."
echo ""
echo "La aplicación se abrirá automáticamente en http://localhost:3000"
echo "Presiona Ctrl+C para detener el servidor"
echo ""

cd "$UI_PATH"
npm start

