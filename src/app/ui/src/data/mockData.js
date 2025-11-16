// Datos mockeados del grafo de conocimiento
export const mockNodes = [
  { 
    id: '1', 
    caption: 'React',
    labels: ['Technology'],
    properties: { 
      type: 'Framework',
      year: 2013,
      category: 'Frontend'
    }
  },
  { 
    id: '2', 
    caption: 'GraphQL',
    labels: ['Technology'],
    properties: { 
      type: 'Query Language',
      year: 2015,
      category: 'API'
    }
  },
  { 
    id: '3', 
    caption: 'Neo4j',
    labels: ['Database'],
    properties: { 
      type: 'Graph Database',
      year: 2007,
      category: 'Backend'
    }
  },
  { 
    id: '4', 
    caption: 'JavaScript',
    labels: ['Language'],
    properties: { 
      type: 'Programming Language',
      year: 1995,
      category: 'General Purpose'
    }
  },
  { 
    id: '5', 
    caption: 'Apollo Client',
    labels: ['Technology'],
    properties: { 
      type: 'Library',
      year: 2016,
      category: 'GraphQL Client'
    }
  }
];

export const mockRelationships = [
  { 
    id: 'r1', 
    from: '1', 
    to: '4',
    type: 'USES',
    caption: 'USES'
  },
  { 
    id: 'r2', 
    from: '5', 
    to: '2',
    type: 'IMPLEMENTS',
    caption: 'IMPLEMENTS'
  },
  { 
    id: 'r3', 
    from: '1', 
    to: '5',
    type: 'INTEGRATES_WITH',
    caption: 'INTEGRATES_WITH'
  },
  { 
    id: 'r4', 
    from: '2', 
    to: '3',
    type: 'QUERIES',
    caption: 'QUERIES'
  },
  { 
    id: 'r5', 
    from: '4', 
    to: '2',
    type: 'SUPPORTS',
    caption: 'SUPPORTS'
  }
];

// Datos para tabla
export const mockTableData = mockNodes.map(node => ({
  name: node.caption,
  type: node.properties.type,
  year: node.properties.year,
  category: node.properties.category
}));

// Estadísticas del grafo
export const mockStats = {
  totalNodes: mockNodes.length,
  totalRelationships: mockRelationships.length,
  nodeTypes: [...new Set(mockNodes.map(n => n.labels[0]))],
  relationshipTypes: [...new Set(mockRelationships.map(r => r.type))]
};


