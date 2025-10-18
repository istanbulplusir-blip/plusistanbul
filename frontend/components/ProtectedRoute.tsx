'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '../lib/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requiredRole?: 'agent' | 'admin' | 'user';
  redirectTo?: string;
}

export default function ProtectedRoute({ 
  children, 
  requireAuth = true,
  requiredRole,
  redirectTo = '/login' 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // Extract locale from pathname
  const locale = pathname.startsWith('/fa') ? 'fa' : 
                 pathname.startsWith('/tr') ? 'tr' : 'en';
  
  const prefix = locale === 'en' ? '' : `/${locale}`;

  useEffect(() => {
    if (!isLoading) {
      if (requireAuth && !isAuthenticated) {
        // Redirect to login if authentication is required but user is not authenticated
        // Include current path as redirect parameter so user returns after login
        const currentPath = pathname;
        router.push(`${prefix}${redirectTo}?redirect=${encodeURIComponent(currentPath)}`);
      } else if (requireAuth && isAuthenticated && requiredRole) {
        // Check if user has required role
        if (user?.role !== requiredRole) {
          // Redirect to unauthorized page or home
          router.push(`${prefix}/`);
        }
      } else if (!requireAuth && isAuthenticated) {
        // Redirect to home if user is authenticated but page doesn't require auth (like login/register)
        router.push(`${prefix}/`);
      }
    }
  }, [isAuthenticated, isLoading, requireAuth, requiredRole, user, redirectTo, router, prefix, pathname]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Show content if authentication and role requirements are met
  const hasRequiredAuth = requireAuth ? isAuthenticated : !isAuthenticated;
  const hasRequiredRole = requiredRole ? user?.role === requiredRole : true;
  
  if (hasRequiredAuth && hasRequiredRole) {
    return <>{children}</>;
  }

  // Return null while redirecting
  return null;
} 