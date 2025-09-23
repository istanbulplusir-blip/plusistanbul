'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface DropdownContextType {
  openDropdown: string | null;
  setOpenDropdown: (id: string | null) => void;
  closeAllDropdowns: () => void;
}

const DropdownContext = createContext<DropdownContextType | undefined>(undefined);

export const useDropdown = () => {
  const context = useContext(DropdownContext);
  if (context === undefined) {
    throw new Error('useDropdown must be used within a DropdownProvider');
  }
  return context;
};

interface DropdownProviderProps {
  children: ReactNode;
}

export const DropdownProvider: React.FC<DropdownProviderProps> = ({ children }) => {
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  const closeAllDropdowns = () => {
    setOpenDropdown(null);
  };

  return (
    <DropdownContext.Provider value={{ openDropdown, setOpenDropdown, closeAllDropdowns }}>
      {children}
    </DropdownContext.Provider>
  );
};
