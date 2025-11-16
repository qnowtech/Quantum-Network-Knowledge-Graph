#!/bin/bash
# Script de build completo para GitHub Pages
# Este script:
# 1. Exporta datos de Neo4j
# 2. Construye la aplicación React
# 3. Prepara el build para GitHub Pages

set -e  # Salir si hay algún error

echo "🚀 Iniciando proceso de build para GitHub Pages..."

# Ir al directorio de la app React
cd "$(dirname "$0")/../ui"

# Paso 1: Exportar datos de Neo4j
echo "📊 Exportando datos de Neo4j..."
python ../../app/scripts/export_neo4j_data.py

# Verificar que el archivo se generó correctamente
if [ ! -f "public/graph-data.json" ]; then
    echo "❌ Error: No se pudo generar graph-data.json"
    exit 1
fi

echo "✅ Datos exportados correctamente"

# Paso 2: Instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias de Node.js..."
    npm install
fi

# Paso 3: Construir la aplicación React
echo "🔨 Construyendo aplicación React..."
npm run build

echo "✅ Build completado exitosamente!"
echo "📁 Los archivos están en: src/app/ui/build/"
echo ""
echo "Para desplegar a GitHub Pages, ejecuta:"
echo "  cd src/app/ui && npm run deploy"

