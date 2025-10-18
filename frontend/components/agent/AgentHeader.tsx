'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useAuth } from '@/lib/contexts/AuthContext';
import { useLocale } from 'next-intl';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { 
  BellIcon, 
  UserCircleIcon, 
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';

export default function AgentHeader() {
  const t = useTranslations('agent');
  const { user, logout } = useAuth();
  const locale = useLocale();
  const isRTL = locale === 'fa';
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showUserMenu && !(event.target as Element).closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showUserMenu]);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 fixed top-0 left-0 right-0 z-40">
      <div className="px-4 sm:px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className={cn(
            "flex items-center",
            isRTL ? "space-x-reverse space-x-4" : "space-x-4"
          )}>
            <div className={cn(
              "flex items-center",
              isRTL ? "space-x-reverse space-x-3" : "space-x-3"
            )}>
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">A</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">
                  {t('dashboard.title')}
                </h1>
                <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  {t('dashboard.subtitle')}
                </p>
              </div>
            </div>
          </div>

          {/* Right Side */}
          <div className={cn(
            "flex items-center",
            isRTL ? "space-x-reverse space-x-2 sm:space-x-4" : "space-x-2 sm:space-x-4"
          )}>
            {/* Notifications */}
            <Button
              variant="ghost"
              size="sm"
              className="relative p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <BellIcon className="w-5 h-5" />
              <span className={cn(
                "absolute w-3 h-3 bg-red-500 rounded-full",
                isRTL ? "-top-1 -left-1" : "-top-1 -right-1"
              )}></span>
            </Button>

            {/* User Menu */}
            <div className="relative user-menu-container">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowUserMenu(!showUserMenu)}
                className={cn(
                  "flex items-center p-2 text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white",
                  isRTL ? "space-x-reverse space-x-2" : "space-x-2"
                )}
              >
                <UserCircleIcon className="w-5 h-5 sm:w-6 sm:h-6" />
                <span className="hidden sm:block text-sm font-medium truncate max-w-32">
                  {user?.first_name || user?.username}
                </span>
              </Button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <div className={cn(
                  "absolute mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50",
                  isRTL ? "left-0" : "right-0"
                )}>
                  <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {user?.first_name} {user?.last_name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                      {user?.email}
                    </p>
                    <p className="text-xs text-primary-600 dark:text-primary-400 font-medium">
                      Agent Code: {user?.id}
                    </p>
                  </div>
                  
                  <button className={cn(
                    "w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 flex items-center",
                    isRTL ? "space-x-reverse space-x-2 text-right" : "space-x-2 text-left"
                  )}>
                    <Cog6ToothIcon className="w-4 h-4 flex-shrink-0" />
                    <span>{'Settings'}</span>
                  </button>
                  
                  <button 
                    onClick={handleLogout}
                    className={cn(
                      "w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 flex items-center",
                      isRTL ? "space-x-reverse space-x-2 text-right" : "space-x-2 text-left"
                    )}
                  >
                    <ArrowRightOnRectangleIcon className="w-4 h-4 flex-shrink-0" />
                    <span>{'Logout'}</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
