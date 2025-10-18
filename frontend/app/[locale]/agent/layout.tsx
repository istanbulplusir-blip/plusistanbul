'use client';

import { ReactNode } from 'react';
import { useLocale } from 'next-intl';
import AgentSidebar from '@/components/agent/AgentSidebar';
import AgentHeader from '@/components/agent/AgentHeader';
import ProtectedRoute from '@/components/ProtectedRoute';
import { cn } from '@/lib/utils';

interface AgentLayoutProps {
  children: ReactNode;
}

export default function AgentLayout({ children }: AgentLayoutProps) {
  const locale = useLocale();
  const isRTL = locale === 'fa';

  return (
    <ProtectedRoute requiredRole="agent">
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Agent Header */}
        <AgentHeader />
        
        {/* Sidebar */}
        <AgentSidebar />
        
        {/* Main Content */}
        <main className={cn(
          "transition-all duration-300",
          // Desktop sidebar spacing
          "lg:ml-64",
          // RTL adjustments
          isRTL && "lg:ml-0 lg:mr-64",
          // Top spacing - account for fixed agent header on all screen sizes
          "pt-20"
        )}>
          <div className="p-4 sm:p-6">
            {children}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
