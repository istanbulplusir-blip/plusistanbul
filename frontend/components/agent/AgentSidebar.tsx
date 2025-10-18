'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useLocale, useTranslations } from 'next-intl';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import {
  HomeIcon,
  ChartBarIcon,
  UserGroupIcon,
  ShoppingBagIcon,
  CurrencyDollarIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  PlusIcon,
  CalendarDaysIcon,
  TruckIcon,
  TicketIcon,
  Bars3Icon,
} from '@heroicons/react/24/outline';

const navigation = [
  {
    name: 'dashboard',
    href: '/agent',
    icon: HomeIcon,
  },
  {
    name: 'analytics',
    href: '/agent/analytics',
    icon: ChartBarIcon,
  },
  {
    name: 'customers',
    href: '/agent/customers',
    icon: UserGroupIcon,
  },
  {
    name: 'orders',
    href: '/agent/orders',
    icon: ShoppingBagIcon,
  },
  {
    name: 'commissions',
    href: '/agent/commissions',
    icon: CurrencyDollarIcon,
  },
  {
    name: 'reports',
    href: '/agent/reports',
    icon: DocumentTextIcon,
  },
  {
    name: 'settings',
    href: '/agent/settings',
    icon: Cog6ToothIcon,
  },
];

const bookingMenu = [
  {
    name: 'book_tour',
    href: '/agent/book/tour',
    icon: CalendarDaysIcon,
  },
  {
    name: 'book_transfer',
    href: '/agent/book/transfer',
    icon: TruckIcon,
  },
  {
    name: 'book_car',
    href: '/agent/book/car-rental',
    icon: TruckIcon,
  },
  {
    name: 'book_event',
    href: '/agent/book/event',
    icon: TicketIcon,
  },
];

export default function AgentSidebar() {
  const pathname = usePathname();
  const locale = useLocale();
  const t = useTranslations('agent.sidebar');
  const isRTL = locale === 'fa';
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Close mobile sidebar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isMobileOpen && !(event.target as Element).closest('.sidebar-container')) {
        setIsMobileOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isMobileOpen]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isMobileOpen) {
        setIsMobileOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isMobileOpen]);

  return (
    <>
      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" />
      )}

      {/* Sidebar */}
      <div className={cn(
        "sidebar-container fixed z-30 bg-white dark:bg-gray-800 shadow-lg border-r border-gray-200 dark:border-gray-700 transition-all duration-300",
        // Positioning - start below header
        "top-20 bottom-0",
        // Desktop behavior
        "hidden lg:block",
        isCollapsed ? "w-16" : "w-64",
        // RTL positioning
        isRTL ? "right-0 border-l border-r-0" : "left-0",
        // Mobile behavior
        isMobileOpen && "block w-64"
      )}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className={cn(
            "flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700",
            isRTL ? "flex-row-reverse" : "flex-row"
          )}>
            {(!isCollapsed || isMobileOpen) && (
              <div className={cn(
                "flex items-center",
                isRTL ? "space-x-reverse space-x-3" : "space-x-3"
              )}>
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">A</span>
                </div>
                <span className="text-lg font-semibold text-gray-900 dark:text-white">
                  {'Agent Panel'}
                </span>
              </div>
            )}
            <button
              onClick={() => {
                if (window.innerWidth < 1024) {
                  setIsMobileOpen(false);
                } else {
                  setIsCollapsed(!isCollapsed);
                }
              }}
              className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <div className="w-4 h-4">
                <div className={cn(
                  "w-full h-0.5 bg-gray-600 dark:bg-gray-300 transition-all duration-300",
                  isCollapsed ? "rotate-45 translate-y-1" : "rotate-0"
                )}></div>
                <div className={cn(
                  "w-full h-0.5 bg-gray-600 dark:bg-gray-300 mt-1 transition-all duration-300",
                  isCollapsed ? "-rotate-45 -translate-y-1" : "rotate-0"
                )}></div>
              </div>
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {/* Main Navigation */}
            <div className="space-y-1">
              <div className={cn(
                "text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3",
                (isCollapsed && !isMobileOpen) && "hidden"
              )}>
                {'Main Menu'}
              </div>
              
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => {
                      if (window.innerWidth < 1024) {
                        setIsMobileOpen(false);
                      }
                    }}
                    className={cn(
                      "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                      isRTL ? "space-x-reverse space-x-3" : "space-x-3",
                      isActive
                        ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400"
                        : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                    )}
                  >
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                    {(!isCollapsed || isMobileOpen) && (
                      <span className={cn(
                        "truncate",
                        isRTL ? "text-right" : "text-left"
                      )}>
                        {t(item.name)}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>

            {/* Booking Menu */}
            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <div className={cn(
                "text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3",
                (isCollapsed && !isMobileOpen) && "hidden"
              )}>
                {'Quick Booking'}
              </div>
              
              <div className="space-y-1">
                {bookingMenu.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      onClick={() => {
                        if (window.innerWidth < 1024) {
                          setIsMobileOpen(false);
                        }
                      }}
                      className={cn(
                        "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                        isRTL ? "space-x-reverse space-x-3" : "space-x-3",
                        isActive
                          ? "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400"
                          : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                      )}
                    >
                      <item.icon className="w-5 h-5 flex-shrink-0" />
                      {(!isCollapsed || isMobileOpen) && (
                        <span className={cn(
                          "truncate",
                          isRTL ? "text-right" : "text-left"
                        )}>
                          {t(item.name)}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          </nav>

          {/* Quick Actions */}
          {(!isCollapsed || isMobileOpen) && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <Link
                href="/agent/book/tour"
                onClick={() => {
                  if (window.innerWidth < 1024) {
                    setIsMobileOpen(false);
                  }
                }}
                className={cn(
                  "flex items-center justify-center w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors",
                  isRTL ? "space-x-reverse space-x-2" : "space-x-2"
                )}
              >
                <PlusIcon className="w-4 h-4" />
                <span className="text-sm font-medium">{'Quick Book'}</span>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className={cn(
          "lg:hidden fixed top-4 z-50 p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700",
          isRTL ? "right-4" : "left-4"
        )}
      >
        <Bars3Icon className="w-6 h-6 text-gray-600 dark:text-gray-300" />
      </button>
    </>
  );
}
