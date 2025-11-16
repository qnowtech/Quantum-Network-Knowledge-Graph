# Script rápido para levantar el proyecto en desarrollo (Windows PowerShell)
# Ejecuta: .\src\app\start-dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Iniciando proyecto de visualización del grafo..." -ForegroundColor Cyan
Write-Host ""

# Paso 1: Exportar datos de Neo4j
Write-Host "📊 Paso 1/3: Exportando datos de Neo4j..." -ForegroundColor Yellow
$exportScript = Join-Path $PSScriptRoot "scripts" "export_neo4j_data.py"
try {
    python $exportScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al exportar datos. Verifica las credenciales de Neo4j." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "💡 Asegúrate de tener Python instalado y las dependencias del proyecto." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Datos exportados correctamente" -ForegroundColor Green
Write-Host ""

# Paso 2: Verificar/instalar dependencias de Node.js
$uiPath = Join-Path $PSScriptRoot "ui"
$nodeModulesPath = Join-Path $uiPath "node_modules"

if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "📦 Paso 2/3: Instalando dependencias de Node.js..." -ForegroundColor Yellow
    Set-Location $uiPath
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al instalar dependencias de Node.js" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencias de Node.js ya instaladas" -ForegroundColor Green
}
Write-Host ""

# Paso 3: Levantar servidor de desarrollo
Write-Host "🌐 Paso 3/3: Levantando servidor de desarrollo..." -ForegroundColor Yellow
Write-Host ""
Write-Host "La aplicación se abrirá automáticamente en http://localhost:3000" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

Set-Location $uiPath
npm start

