# Guía de Despliegue a GitHub Pages

Esta guía explica cómo desplegar la aplicación de visualización del grafo de conocimiento a GitHub Pages.

## 📋 Requisitos Previos

1. **Python 3.12+** con las dependencias del proyecto instaladas
2. **Node.js** y **npm** instalados
3. **Credenciales de Neo4j** configuradas en `.env` o variables de entorno
4. **Repositorio de GitHub** configurado

## 🔧 Configuración Inicial

### 1. Configurar Variables de Entorno

Asegúrate de tener un archivo `.env` en la raíz del proyecto con:

```env
NEO4J_URI=neo4j+s://87983fcb.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_QUANTUM_NETWORK_AURA=tu_contraseña_aqui
```

### 2. Actualizar Homepage en package.json

Edita `src/app/ui/package.json` y actualiza la línea `homepage` con tu usuario/organización de GitHub:

```json
"homepage": "https://TU_USUARIO.github.io/Quantum-Network-Knowledge-Graph"
```

### 3. Instalar Dependencias

```bash
# Instalar dependencias de Python (si no están instaladas)
uv sync

# Instalar dependencias de Node.js
cd src/app/ui
npm install
```

## 🚀 Proceso de Despliegue

### Opción 1: Despliegue Manual

#### Paso 1: Exportar Datos de Neo4j

```bash
# Desde la raíz del proyecto
python src/app/scripts/export_neo4j_data.py
```

Esto generará `src/app/ui/public/graph-data.json` con todos los datos del grafo.

#### Paso 2: Construir la Aplicación

```bash
cd src/app/ui
npm run build
```

#### Paso 3: Desplegar a GitHub Pages

```bash
# Instalar gh-pages si no está instalado
npm install --save-dev gh-pages

# Desplegar
npm run deploy
```

### Opción 2: Usar Scripts de Build

#### En Windows (PowerShell):

```powershell
.\src\app\scripts\build.ps1
cd src/app/ui
npm run deploy
```

#### En Linux/Mac:

```bash
chmod +x src/app/scripts/build.sh
./src/app/scripts/build.sh
cd src/app/ui
npm run deploy
```

## 🔄 Actualización Automática con GitHub Actions

Para automatizar el despliegue cada vez que se actualicen los datos, puedes crear un workflow de GitHub Actions.

### Crear `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:  # Permite ejecución manual

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install Python dependencies
        run: |
          pip install uv
          uv sync
      
      - name: Export Neo4j data
        env:
          NEO4J_URI: ${{ secrets.NEO4J_URI }}
          NEO4J_USER: ${{ secrets.NEO4J_USER }}
          NEO4J_QUANTUM_NETWORK_AURA: ${{ secrets.NEO4J_QUANTUM_NETWORK_AURA }}
        run: |
          python src/app/scripts/export_neo4j_data.py
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dir: src/app/ui
      
      - name: Install Node dependencies
        working-directory: src/app/ui
        run: npm ci
      
      - name: Build React app
        working-directory: src/app/ui
        run: npm run build
        env:
          CI: false
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: src/app/ui/build
```

### Configurar Secrets en GitHub:

1. Ve a **Settings** → **Secrets and variables** → **Actions**
2. Agrega los siguientes secrets:
   - `NEO4J_URI`
   - `NEO4J_USER`
   - `NEO4J_QUANTUM_NETWORK_AURA`

## 📝 Notas Importantes

### Datos Estáticos

- GitHub Pages solo sirve archivos estáticos
- Los datos se exportan en tiempo de build, no en tiempo de ejecución
- Para actualizar los datos, necesitas ejecutar el script de exportación y hacer un nuevo build

### Estructura de Archivos

```
src/app/
├── scripts/
│   ├── export_neo4j_data.py  # Script de exportación
│   ├── build.sh               # Script de build (Linux/Mac)
│   └── build.ps1              # Script de build (Windows)
└── ui/
    ├── public/
    │   └── graph-data.json    # Datos exportados (generado)
    ├── build/                  # Build de producción (generado)
    └── package.json
```

### Troubleshooting

#### Error: "No se pudo generar graph-data.json"

- Verifica que las credenciales de Neo4j estén correctas
- Asegúrate de que el script puede conectarse a Neo4j
- Revisa los logs del script para más detalles

#### Error: "Module not found" en React

- Ejecuta `npm install` en `src/app/ui`
- Verifica que todas las dependencias estén instaladas

#### Error al desplegar con gh-pages

- Verifica que la URL en `homepage` de `package.json` sea correcta
- Asegúrate de tener permisos de escritura en el repositorio
- Revisa que la rama `gh-pages` no esté protegida

## 🔗 Enlaces Útiles

- [Documentación de GitHub Pages](https://docs.github.com/en/pages)
- [gh-pages npm package](https://www.npmjs.com/package/gh-pages)
- [React Deployment](https://create-react-app.dev/docs/deployment/)

