import { useState, useCallback, useEffect } from 'react';

interface UseTouchInteractionReturn {
  touchedCard: string | null;
  isVisible: (cardId: string) => boolean;
  handleTouchStart: (cardId: string) => void;
  handleTouchEnd: (cardId: string) => void;
}

export const useTouchInteraction = (): UseTouchInteractionReturn => {
  const [touchedCard, setTouchedCard] = useState<string | null>(null);
  const [touchTimeout, setTouchTimeout] = useState<NodeJS.Timeout | null>(null);

  // Handle touch start - toggle card visibility
  const handleTouchStart = useCallback((cardId: string) => {
    if (touchTimeout) {
      clearTimeout(touchTimeout);
    }
    
    if (touchedCard === cardId) {
      // If already touched, toggle off
      setTouchedCard(null);
    } else {
      // Set new touched card
      setTouchedCard(cardId);
    }
  }, [touchedCard, touchTimeout]);

  // Handle touch end - auto-hide after delay
  const handleTouchEnd = useCallback(() => {
    // Add a small delay before hiding to allow user to see the content
    const timeout = setTimeout(() => {
      setTouchedCard(null);
    }, 2000); // Show for 2 seconds after touch
    
    setTouchTimeout(timeout);
  }, []);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (touchTimeout) {
        clearTimeout(touchTimeout);
      }
    };
  }, [touchTimeout]);

  // Determine if content should be visible
  const isVisible = useCallback((cardId: string) => {
    return touchedCard === cardId;
  }, [touchedCard]);

  return {
    touchedCard,
    isVisible,
    handleTouchStart,
    handleTouchEnd
  };
};
