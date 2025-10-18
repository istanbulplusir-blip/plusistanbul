'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from './AuthContext';

interface UnifiedLanguageContextType {
  language: string;
  setLanguage: (language: string) => void;
  isAgent: boolean;
  agentLanguage?: string;
  isLoading: boolean;
  changeLanguageAndNavigate: (newLanguage: string) => void;
}

const UnifiedLanguageContext = createContext<UnifiedLanguageContextType | undefined>(undefined);

export const useUnifiedLanguage = () => {
  const context = useContext(UnifiedLanguageContext);
  if (context === undefined) {
    throw new Error('useUnifiedLanguage must be used within a UnifiedLanguageProvider');
  }
  return context;
};

interface UnifiedLanguageProviderProps {
  children: React.ReactNode;
}

export const UnifiedLanguageProvider: React.FC<UnifiedLanguageProviderProps> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [language, setLanguageState] = useState<string>('fa');
  const [isLoading, setIsLoading] = useState(true);

  // Determine if user is an agent
  const isAgent = isAuthenticated && user?.role === 'agent';
  const agentLanguage = isAgent ? user?.preferred_language : undefined;

  // Load initial language
  useEffect(() => {
    const loadInitialLanguage = () => {
      try {
        // Get current language from URL
        const currentLocale = pathname.split('/')[1];
        if (['fa', 'en', 'tr'].includes(currentLocale)) {
          setLanguageState(currentLocale);
          console.log('Using URL language:', currentLocale);
        } else if (isAgent && agentLanguage) {
          // For agents, use their preferred language from database
          setLanguageState(agentLanguage);
          console.log('Using agent preferred language:', agentLanguage);
        } else {
          // For regular users, use localStorage or default
          const storedLanguage = localStorage.getItem('language');
          if (storedLanguage && ['fa', 'en', 'tr'].includes(storedLanguage)) {
            setLanguageState(storedLanguage);
            console.log('Using stored language:', storedLanguage);
          } else {
            setLanguageState('fa');
            console.log('Using default language: fa');
          }
        }
      } catch (error) {
        console.error('Error loading initial language:', error);
        setLanguageState('fa');
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialLanguage();
  }, [pathname, isAgent, agentLanguage]);

  // Update language state when URL changes
  useEffect(() => {
    const currentLocale = pathname.split('/')[1];
    if (['fa', 'en', 'tr'].includes(currentLocale) && currentLocale !== language) {
      setLanguageState(currentLocale);
      console.log('Language state updated from URL:', currentLocale);
    }
  }, [pathname, language]);

  // Change language and navigate
  const changeLanguageAndNavigate = useCallback((newLanguage: string) => {
    if (!['fa', 'en', 'tr'].includes(newLanguage)) {
      console.warn('Invalid language:', newLanguage);
      return;
    }

    setLanguageState(newLanguage);
    
    // Store in localStorage for non-agents
    if (!isAgent) {
      localStorage.setItem('language', newLanguage);
      console.log('Stored language in localStorage:', newLanguage);
    }

    // Navigate to new language URL
    let pathWithoutLocale = pathname;
    
    // Remove the current locale prefix from the pathname
    // Handle different URL patterns: /fa/agent/settings/, /en/agent/settings/, etc.
    const localePattern = /^\/([a-z]{2})(\/.*)?$/;
    const match = pathname.match(localePattern);
    
    if (match) {
      // Extract the path without locale
      pathWithoutLocale = match[2] || '/';
    } else {
      // If no locale found, use the full pathname
      pathWithoutLocale = pathname;
    }
    
    // Ensure we have a valid path
    if (pathWithoutLocale === '') {
      pathWithoutLocale = '/';
    }
    
    // Create the new path with the new locale prefix
    const newPath = `/${newLanguage}${pathWithoutLocale}`;
    
    console.log('Navigating to:', newPath);
    router.push(newPath);
  }, [pathname, router, isAgent]);

  // Set language function (without navigation)
  const setLanguage = useCallback((newLanguage: string) => {
    if (!['fa', 'en', 'tr'].includes(newLanguage)) {
      console.warn('Invalid language:', newLanguage);
      return;
    }

    setLanguageState(newLanguage);
    
    // Store in localStorage for non-agents
    if (!isAgent) {
      localStorage.setItem('language', newLanguage);
      console.log('Stored language in localStorage:', newLanguage);
    }
    
    console.log('Language changed to:', newLanguage);
  }, [isAgent]);

  // Update language when agent's preferred language changes
  useEffect(() => {
    if (isAgent && agentLanguage && agentLanguage !== language) {
      setLanguageState(agentLanguage);
      console.log('Updated language from agent settings:', agentLanguage);
    }
  }, [isAgent, agentLanguage, language]);

  const value: UnifiedLanguageContextType = {
    language,
    setLanguage,
    isAgent,
    agentLanguage,
    isLoading,
    changeLanguageAndNavigate,
  };

  return (
    <UnifiedLanguageContext.Provider value={value}>
      {children}
    </UnifiedLanguageContext.Provider>
  );
};
