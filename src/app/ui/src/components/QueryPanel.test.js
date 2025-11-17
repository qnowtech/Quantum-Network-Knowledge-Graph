import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import QueryPanel from './QueryPanel';
import { STRATEGIC_QUERIES } from '../data/strategicQueries';

// Mock del hook useCypherQuery
jest.mock('../hooks/useCypherQuery', () => ({
  useCypherQuery: () => ({
    executeQuery: jest.fn().mockResolvedValue(),
    results: null,
    loading: false,
    error: null,
    clearResults: jest.fn()
  })
}));

describe('QueryPanel', () => {
  const mockNodes = [
    { id: '1', labels: ['Person'], properties: { name: 'Test Person' } }
  ];
  const mockRelationships = [
    { id: '1', from: '1', to: '2', type: 'WORKS_AT' }
  ];
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders query panel with header', () => {
    render(
      <QueryPanel
        nodes={mockNodes}
        relationships={mockRelationships}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Queries Estratégicas')).toBeInTheDocument();
    expect(screen.getByLabelText('Cerrar')).toBeInTheDocument();
  });

  test('displays list of available queries', () => {
    render(
      <QueryPanel
        nodes={mockNodes}
        relationships={mockRelationships}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Selecciona una Query')).toBeInTheDocument();
    
    // Verificar que se muestran todas las queries
    STRATEGIC_QUERIES.forEach(query => {
      expect(screen.getByText(query.title)).toBeInTheDocument();
    });
  });

  test('allows selecting a query', () => {
    render(
      <QueryPanel
        nodes={mockNodes}
        relationships={mockRelationships}
        onClose={mockOnClose}
      />
    );

    const firstQuery = screen.getByText(STRATEGIC_QUERIES[0].title);
    fireEvent.click(firstQuery);

    // Verificar que se muestra la pregunta de la query seleccionada
    expect(screen.getByText(STRATEGIC_QUERIES[0].question)).toBeInTheDocument();
  });

  test('displays query details when a query is selected', () => {
    render(
      <QueryPanel
        nodes={mockNodes}
        relationships={mockRelationships}
        onClose={mockOnClose}
      />
    );

    const firstQuery = screen.getByText(STRATEGIC_QUERIES[0].title);
    fireEvent.click(firstQuery);

    expect(screen.getByText('Pregunta:')).toBeInTheDocument();
    expect(screen.getByText('Query Cypher:')).toBeInTheDocument();
    expect(screen.getByText('▶️ Ejecutar Query')).toBeInTheDocument();
  });

  test('shows input field for queries that require input', () => {
    render(
      <QueryPanel
        nodes={mockNodes}
        relationships={mockRelationships}
        onClose={mockOnClose}
      />
    );

    // Buscar la query que requiere input (query #3)
    const queryWithInput = STRATEGIC_QUERIES.find(q => q.requiresInput);
    if (queryWithInput) {
      const queryItem = screen.getByText(queryWithInput.title);
      fireEvent.click(queryItem);

      expect(screen.getByLabelText(new RegExp(queryWithInput.inputLabel || 'Parámetro requerido'))).toBeInTheDocument();
    }
  });

  test('calls onClose when close button is clicked', () => {
    render(
      <QueryPanel
        nodes={mockNodes}
        relationships={mockRelationships}
        onClose={mockOnClose}
      />
    );

    const closeButton = screen.getByLabelText('Cerrar');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('displays copy button for Cypher query', () => {
    render(
      <QueryPanel
        nodes={mockNodes}
        relationships={mockRelationships}
        onClose={mockOnClose}
      />
    );

    const firstQuery = screen.getByText(STRATEGIC_QUERIES[0].title);
    fireEvent.click(firstQuery);

    const copyButton = screen.getByText('📋 Copiar');
    expect(copyButton).toBeInTheDocument();
  });

  test('copies query to clipboard when copy button is clicked', async () => {
    // Mock clipboard API
    const mockWriteText = jest.fn().mockResolvedValue();
    global.navigator.clipboard = {
      writeText: mockWriteText
    };

    render(
      <QueryPanel
        nodes={mockNodes}
        relationships={mockRelationships}
        onClose={mockOnClose}
      />
    );

    const firstQuery = screen.getByText(STRATEGIC_QUERIES[0].title);
    fireEvent.click(firstQuery);

    const copyButton = screen.getByText('📋 Copiar');
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(mockWriteText).toHaveBeenCalledWith(STRATEGIC_QUERIES[0].cypher);
    });
  });
});

