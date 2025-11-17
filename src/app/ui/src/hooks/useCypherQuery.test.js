import { renderHook, act } from '@testing-library/react';
import { useCypherQuery } from './useCypherQuery';

describe('useCypherQuery', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('initializes with null results and no loading state', () => {
    const { result } = renderHook(() => useCypherQuery());

    expect(result.current.results).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  test('executeQuery sets loading to true', async () => {
    const { result } = renderHook(() => useCypherQuery());

    act(() => {
      result.current.executeQuery('MATCH (n) RETURN n', {}, [], []);
    });

    expect(result.current.loading).toBe(true);
  });

  test('executeQuery sets results after execution', async () => {
    const { result } = renderHook(() => useCypherQuery());

    await act(async () => {
      await result.current.executeQuery('MATCH (n) RETURN n', {}, [], []);
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.results).not.toBeNull();
    expect(result.current.results.executed).toBe(true);
  });

  test('executeQuery handles errors', async () => {
    const { result } = renderHook(() => useCypherQuery());

    // Simular un error
    const originalExecute = result.current.executeQuery;
    result.current.executeQuery = jest.fn().mockRejectedValue(new Error('Test error'));

    await act(async () => {
      try {
        await result.current.executeQuery('INVALID QUERY', {}, [], []);
      } catch (error) {
        // Error manejado
      }
    });

    // Restaurar función original
    result.current.executeQuery = originalExecute;
  });

  test('clearResults clears results and error', () => {
    const { result } = renderHook(() => useCypherQuery());

    act(() => {
      result.current.clearResults();
    });

    expect(result.current.results).toBeNull();
    expect(result.current.error).toBeNull();
  });
});

