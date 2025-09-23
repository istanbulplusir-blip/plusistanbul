import { useState, useCallback } from 'react';

interface UseRetryOptions {
  maxAttempts?: number;
  delayMs?: number;
  backoffMultiplier?: number;
}

interface UseRetryReturn<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
  retryCount: number;
  execute: (fn: () => Promise<T>) => Promise<T>;
  reset: () => void;
}

export function useRetry<T>(options: UseRetryOptions = {}): UseRetryReturn<T> {
  const {
    maxAttempts = 3,
    delayMs = 1000,
    backoffMultiplier = 2
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const execute = useCallback(async (fn: () => Promise<T>): Promise<T> => {
    setIsLoading(true);
    setError(null);
    let lastError: Error;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        setRetryCount(attempt - 1);
        const result = await fn();
        setData(result);
        setIsLoading(false);
        return result;
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));
        setError(lastError);

        if (attempt === maxAttempts) {
          setIsLoading(false);
          throw lastError;
        }

        // Wait before retrying (with exponential backoff)
        const waitTime = delayMs * Math.pow(backoffMultiplier, attempt - 1);
        await delay(waitTime);
      }
    }

    setIsLoading(false);
    throw lastError!;
  }, [maxAttempts, delayMs, backoffMultiplier]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
    setRetryCount(0);
  }, []);

  return {
    data,
    error,
    isLoading,
    retryCount,
    execute,
    reset
  };
}

// Specialized retry hook for API calls
export function useApiRetry<T>(options: UseRetryOptions = {}) {
  const retry = useRetry<T>(options);

  const executeApiCall = useCallback(async (
    apiCall: () => Promise<T>,
    onSuccess?: (data: T) => void,
    onError?: (error: Error) => void
  ) => {
    try {
      const result = await retry.execute(apiCall);
      onSuccess?.(result);
      return result;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      onError?.(err);
      throw err;
    }
  }, [retry]);

  return {
    ...retry,
    executeApiCall
  };
}
