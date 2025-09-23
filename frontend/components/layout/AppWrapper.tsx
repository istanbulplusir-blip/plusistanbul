'use client';

import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import Navbar from '../Navbar';
import SupportButton from '../common/SupportButton';

interface AppWrapperProps {
  children: ReactNode;
}

export default function AppWrapper({ children }: AppWrapperProps) {
  const pathname = usePathname();
  const isAgentPage = pathname?.includes('/agent');

  // For agent pages, render children directly without AppWrapper structure
  if (isAgentPage) {
    return <>{children}</>;
  }

  // For main site pages, use the full AppWrapper structure
  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-gray-900 transition-colors duration-300">
      <Navbar />
      
      <main className="flex-1 transition-all duration-300">
        {children}
      </main>
      
      <SupportButton />
    </div>
  );
}
