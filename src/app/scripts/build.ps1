# Script de build completo para GitHub Pages (PowerShell)
# Este script:
# 1. Exporta datos de Neo4j
# 2. Construye la aplicación React
# 3. Prepara el build para GitHub Pages

$ErrorActionPreference = "Stop"

Write-Host "🚀 Iniciando proceso de build para GitHub Pages..." -ForegroundColor Cyan

# Ir al directorio de la app React
$uiPath = Join-Path $PSScriptRoot ".." "ui"
Set-Location $uiPath

# Paso 1: Exportar datos de Neo4j
Write-Host "📊 Exportando datos de Neo4j..." -ForegroundColor Yellow
$exportScript = Join-Path $PSScriptRoot "export_neo4j_data.py"
python $exportScript

# Verificar que el archivo se generó correctamente
$jsonPath = Join-Path $uiPath "public" "graph-data.json"
if (-not (Test-Path $jsonPath)) {
    Write-Host "❌ Error: No se pudo generar graph-data.json" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Datos exportados correctamente" -ForegroundColor Green

# Paso 2: Instalar dependencias si es necesario
$nodeModulesPath = Join-Path $uiPath "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "📦 Instalando dependencias de Node.js..." -ForegroundColor Yellow
    npm install
}

# Paso 3: Construir la aplicación React
Write-Host "🔨 Construyendo aplicación React..." -ForegroundColor Yellow
npm run build

Write-Host "✅ Build completado exitosamente!" -ForegroundColor Green
Write-Host "📁 Los archivos están en: src/app/ui/build/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para desplegar a GitHub Pages, ejecuta:" -ForegroundColor Yellow
Write-Host "  cd src/app/ui && npm run deploy" -ForegroundColor White

