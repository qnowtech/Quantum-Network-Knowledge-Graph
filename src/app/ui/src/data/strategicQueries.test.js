import { STRATEGIC_QUERIES } from './strategicQueries';

describe('STRATEGIC_QUERIES', () => {
  test('contains all 7 queries from README', () => {
    expect(STRATEGIC_QUERIES).toHaveLength(7);
  });

  test('each query has required fields', () => {
    STRATEGIC_QUERIES.forEach(query => {
      expect(query).toHaveProperty('id');
      expect(query).toHaveProperty('title');
      expect(query).toHaveProperty('question');
      expect(query).toHaveProperty('cypher');
      expect(query).toHaveProperty('parameters');
      expect(query).toHaveProperty('description');
      
      expect(typeof query.id).toBe('string');
      expect(typeof query.title).toBe('string');
      expect(typeof query.question).toBe('string');
      expect(typeof query.cypher).toBe('string');
      expect(typeof query.description).toBe('string');
      expect(typeof query.parameters).toBe('object');
    });
  });

  test('query IDs are unique', () => {
    const ids = STRATEGIC_QUERIES.map(q => q.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });

  test('query IDs are sequential', () => {
    const ids = STRATEGIC_QUERIES.map(q => q.id).sort();
    expect(ids).toEqual(['1', '2', '3', '4', '5', '6', '7']);
  });

  test('queries with requiresInput have inputLabel and inputPlaceholder', () => {
    const queriesWithInput = STRATEGIC_QUERIES.filter(q => q.requiresInput);
    
    queriesWithInput.forEach(query => {
      expect(query).toHaveProperty('inputLabel');
      expect(query).toHaveProperty('inputPlaceholder');
      expect(typeof query.inputLabel).toBe('string');
      expect(typeof query.inputPlaceholder).toBe('string');
    });
  });

  test('query #3 requires input (email)', () => {
    const query3 = STRATEGIC_QUERIES.find(q => q.id === '3');
    expect(query3).toBeDefined();
    expect(query3.requiresInput).toBe(true);
    expect(query3.inputLabel).toBe('Email address');
    expect(query3.parameters).toHaveProperty('email');
  });

  test('all Cypher queries are valid strings', () => {
    STRATEGIC_QUERIES.forEach(query => {
      expect(query.cypher.length).toBeGreaterThan(0);
      expect(query.cypher).toContain('MATCH');
      expect(query.cypher).toContain('RETURN');
    });
  });

  test('queries have meaningful descriptions', () => {
    STRATEGIC_QUERIES.forEach(query => {
      expect(query.description.length).toBeGreaterThan(20);
    });
  });
});

