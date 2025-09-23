import { useState, useEffect } from 'react';

/**
 * Custom hook to prevent hydration mismatches
 * Returns true only after the component has mounted on the client
 */
export function useHydration() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return mounted;
}

/**
 * Custom hook to safely access persisted state
 * Prevents hydration mismatches with Zustand persist
 */
export function usePersistedState<T>(selector: () => T, defaultValue: T): T {
  const [state, setState] = useState<T>(defaultValue);
  const mounted = useHydration();

  useEffect(() => {
    if (mounted) {
      setState(selector());
    }
  }, [mounted, selector]);

  return mounted ? state : defaultValue;
}
