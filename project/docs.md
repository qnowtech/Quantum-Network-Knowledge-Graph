# Quantum Network Knowledge Graph

## Máxima del Proyecto

**La máxima de este grafo de conocimiento es poder crear representaciones semánticas de valor de grafos de conocimiento asociados a la computación cuántica.**

## Propósito

Este proyecto tiene como objetivo construir un pipeline ETL (Extract, Transform, Load) para la creación de un grafo de conocimiento en Neo4j que represente el ecosistema de computación cuántica en LATAM. El grafo permitirá:

1. **Mapear el ecosistema**: Empresas, investigadores, estudiantes y profesionales vinculados a la computación cuántica
2. **Facilitar conexiones estratégicas**: Conectar investigadores y sus áreas de investigación con problemas empresariales específicos
3. **Generar valor semántico**: Crear representaciones estructuradas que permitan descubrir colaboraciones potenciales, temas de investigación en común y oportunidades de networking
4. **Orientar esfuerzos**: Proporcionar un mapa visual y consultable para orientar conversaciones, colaboraciones y estrategias en el ecosistema cuántico

## Modelo de Conocimiento

### Entidades Principales

El grafo modelará las siguientes entidades:

- **Persona**: Investigadores, estudiantes, profesionales y miembros de la comunidad cuántica
- **Organización**: Empresas, universidades, startups, instituciones de investigación
- **Dominio**: Áreas de interés en computación cuántica (ej: "Investigación académica", "Casos de uso en Finanzas", "Desarrollo de software / algoritmos", etc.). Los dominios facilitan encontrar personas con intereses en común para iniciar conversaciones.
- **Problema**: Desafíos y necesidades empresariales que pueden ser abordados con computación cuántica (futuro)
- **Tópico**: Áreas de investigación, tecnologías, casos de uso y temas de interés en computación cuántica (futuro, para enriquecimiento con NER)

### Patrón de Referencia: DOC-PAGE-CHUNK-ENTITY

### Relaciones Clave

Las relaciones que conectan las entidades incluyen:

- `(Persona)-[:TRABAJA_EN]->(Organización)`: Relación laboral entre persona y organización
- `(Persona)-[:HAS_INTEREST]->(Dominio)`: **Relación principal para facilitar conversaciones**. Conecta personas con sus áreas de interés en computación cuántica. Permite encontrar personas con intereses en común.
- `(Persona)-[:TIENE_EXPERIENCIA_EN]->(Dominio)`: Indica que la persona tiene experiencia práctica en ese dominio (solo para experiencia 'active' o 'exploration')
- `(Organización)-[:TIENE_PROBLEMA]->(Problema)` (futuro)
- `(Problema)-[:PUEDE_RESOLVERSE_CON]->(Dominio)` (futuro)
- `(Persona)-[:CONECTADO_CON]->(Persona)` (red de LinkedIn, futuro)
- `(Organización)-[:COLABORA_CON]->(Organización)` (futuro)

## Fuentes de Datos

### Fuente Primaria: CSV de Registro de Eventos

El archivo `data/quantum_network.csv` contiene información inicial de participantes en eventos de computación cuántica, incluyendo:

- Información básica: Nombre completo, correo electrónico
- Afiliación: Organización/Empresa, Cargo/Rol, Sector
- Intereses: Áreas de interés en computación cuántica
- Experiencia: Nivel de experiencia con tecnologías cuánticas
- LinkedIn: URLs de perfiles (parcialmente completado)

### Fuente Secundaria: LinkedIn (Scraping)

Para enriquecer el grafo, se realizará scraping de perfiles de LinkedIn para obtener:

- **Skills y tecnologías**: Competencias técnicas específicas
- **Experiencia laboral**: Historial profesional detallado
- **Educación**: Formación académica
- **Publicaciones**: Artículos y contenido compartido
- **Conexiones**: Red de contactos profesionales (consideraciones éticas aplican)

## Consideraciones Éticas

Antes de implementar el scraping y procesamiento de datos, se debe evaluar:

1. **Consentimiento**: ¿Tiene sentido enmascarar inicialmente la información para realizar un uso adecuado de los datos?
2. **Privacidad**: Respeto a los términos de servicio de LinkedIn y políticas de privacidad
3. **Uso responsable**: Los datos deben utilizarse exclusivamente para facilitar networking y colaboración legítima en el ecosistema cuántico
4. **Transparencia**: Los participantes deben estar informados sobre el uso de sus datos

## Casos de Uso y Consultas Objetivo

**Propósito principal: Facilitar conversaciones y networking en el ecosistema cuántico**

El grafo permitirá realizar consultas como:

- **Encontrar personas con intereses en común**: "¿Quiénes tienen interés en 'Desarrollo de software / algoritmos'?" - Para iniciar conversaciones sobre temas compartidos
- **Descubrir personas con experiencia en un dominio específico**: "¿Quiénes tienen experiencia activa en 'Hardware cuántico'?" - Para conectar con expertos
- **Mapear el ecosistema por organización**: "¿Qué personas trabajan en IBM y qué dominios les interesan?" - Para entender el perfil de una organización
- **Identificar oportunidades de colaboración**: "¿Qué personas de diferentes organizaciones comparten intereses en 'Casos de uso en Finanzas'?" - Para facilitar networking estratégico
- **Visualizar el ecosistema completo**: Ver el mapa completo de personas, organizaciones y dominios para orientar conversaciones y estrategias de networking

## Proceso ETL

El pipeline ETL seguirá las siguientes etapas (a desarrollar en detalle):

1. **Extract**:

   - Carga de datos CSV + Scraping de LinkedIn (con Selenium y Python)
2. **Transform**:

   - Limpieza y normalización de datos
   - Extracción de entidades (NER)
   - Identificación de relaciones
3. **Load**:

   - Inserción en Neo4j
   - Creación de índices y constraints
   - Validación de integridad del grafo
