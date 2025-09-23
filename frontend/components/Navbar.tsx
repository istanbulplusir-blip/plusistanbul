'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useTranslations, useLocale } from 'next-intl';
import { motion, AnimatePresence } from 'framer-motion';
import LanguageSwitcher from './LanguageSwitcher';
import CurrencySelector from './CurrencySelector';
import { 
  User, 
  ShoppingCart, 
  LogOut, 
  Heart, 
  Package, 
  Menu, 
  X, 
  Sun, 
  Moon
} from 'lucide-react';
import Image from 'next/image';
import { useAuth } from '../lib/contexts/AuthContext';
import { useTheme } from '../lib/contexts/ThemeContext';
import LoginQuickModal from './auth/LoginQuickModal';
import { useCart } from '../lib/hooks/useCart';
import { DropdownProvider } from '@/contexts/DropdownContext';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const t = useTranslations('common');
  const navT = useTranslations('navigation');
  const locale = useLocale();
  const { user, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { totalItems } = useCart();
  
  
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [showQuickLogin, setShowQuickLogin] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [cartRotate, setCartRotate] = useState(false);
  
  const prefix = `/${locale}`;

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      setShowUserMenu(false);
      router.push(`${prefix}/login`);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      if (showUserMenu) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showUserMenu]);

  // Previous totalItems to detect changes
  const [prevTotalItems, setPrevTotalItems] = useState(totalItems);
  
  useEffect(() => {
    if (totalItems > prevTotalItems && totalItems > 0) {
      setCartRotate(true);
      const timer = setTimeout(() => setCartRotate(false), 600);
      setPrevTotalItems(totalItems);
      return () => clearTimeout(timer);
    }
    setPrevTotalItems(totalItems);
  }, [totalItems, prevTotalItems]);

  const navItems = [
    { href: `${prefix}/`, label: navT('home'), icon: null },
    { href: `${prefix}/tours`, label: navT('tours'), icon: null },
    { href: `${prefix}/events`, label: navT('events'), icon: null },
    { href: `${prefix}/transfers/booking`, label: navT('transfers'), icon: null },
    { href: `${prefix}/car-rentals`, label: navT('carRentals'), icon: null },
    { href: `${prefix}/contact`, label: navT('contact'), icon: null },
  ];

  const isActive = (href: string) => {
    if (href === `${prefix}/`) {
      return pathname === `${prefix}/` || pathname === `${prefix}`;
    }
    return pathname.includes(href.replace(prefix, ''));
  };

  return (
    <DropdownProvider>
      <motion.nav 
        className={`sticky top-0 z-50 transition-all duration-300 ${
          isScrolled 
            ? 'bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl shadow-lg border-b border-gray-200/50 dark:border-gray-800/50' 
            : 'bg-white/95 dark:bg-gray-950/95 backdrop-blur-md shadow-sm border-b border-gray-200/30 dark:border-gray-800/30'
        }`}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <motion.div 
              className="flex items-center gap-3"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              <div className="flex items-center gap-3">
                <motion.div 
                  className="relative w-18 h-18 sm:w-14 sm:h-14 rounded-2xl flex items-center justify-center shadow-lg hover:shadow-glow transition-all duration-300 group overflow-hidden"
                  whileHover={{ rotate: 5, scale: 1.1 }}
                  animate={{ y: [0, -2, 0] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                >
                  <Image
                    src="/logo.png"
                    alt="Peykan Tourism Logo"
                    width={100}
                    height={100}
                    className="w-20 h-20 sm:w-16 sm:h-16 object-contain"
                    quality={100}
                    priority
                  />
                  <div className="absolute inset-0 bg-gradient-to-br from-primary-400/20 to-secondary-400/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </motion.div>
                <div className="flex flex-col">
                  <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent font-display">
                    Peykan
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 -mt-0.5">
                    Tourism & Travel
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item, index) => (
                <motion.div
                  key={item.href}
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Link 
                    href={item.href}
                    className={`relative px-3 md:px-4 py-2 rounded-xl font-medium transition-all duration-300 group text-sm md:text-base ${
                      isActive(item.href)
                        ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20'
                        : 'text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                    }`}
                    style={{ position: 'relative' }}
                  >
                    {item.label}
                    {isActive(item.href) && (
                      <motion.div
                        className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"
                        layoutId="activeTab"
                        initial={false}
                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                        style={{ position: 'absolute' }}
                      />
                    )}
                    <div className="absolute inset-0 bg-gradient-to-r from-primary-500/10 to-secondary-500/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  </Link>
                </motion.div>
              ))}
            </div>

                                      {/* Desktop Right Side */}
             <div className="hidden md:flex items-center gap-2">
               {/* Dark Mode Toggle */}
               <motion.button 
                 className="h-11 px-3 md:px-4 text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-300 rounded-xl hover:bg-primary-50 dark:hover:bg-primary-900/20 hover:shadow-md flex items-center justify-center"
                 onClick={toggleTheme}
                 title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
                 whileHover={{ scale: 1.05, rotate: 180 }}
                 whileTap={{ scale: 0.95 }}
                 transition={{ duration: 0.3 }}
                 initial={{ opacity: 0, scale: 0.8 }}
                 animate={{ opacity: 1, scale: 1 }}
               >
                 {theme === 'light' ? (
                   <Moon className="w-5 h-5" />
                 ) : (
                   <Sun className="w-5 h-5" />
                 )}
               </motion.button>

               {/* Currency Selector */}
               <motion.div
                 initial={{ opacity: 0, scale: 0.8 }}
                 animate={{ opacity: 1, scale: 1 }}
                 transition={{ duration: 0.3, delay: 0.2 }}
               >
                 <CurrencySelector />
               </motion.div>

               <motion.div
                 initial={{ opacity: 0, scale: 0.8 }}
                 animate={{ opacity: 1, scale: 1 }}
                 transition={{ duration: 0.3, delay: 0.3 }}
               >
                 <LanguageSwitcher />
               </motion.div>
              
                             {/* Cart */}
               <motion.div
                 initial={{ opacity: 0, scale: 0.8 }}
                 animate={{ opacity: 1, scale: 1 }}
                 transition={{ duration: 0.3, delay: 0.4 }}
               >
                 <Link 
                   href={`${prefix}/cart`}
                   className="relative group"
                 >
                   <motion.button
                     className="relative h-11 px-3 md:px-4 text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-300 rounded-xl hover:bg-primary-50 dark:hover:bg-primary-900/20 hover:shadow-md flex items-center justify-center focus:outline-none focus:ring-0"
                     whileHover={{ scale: 1.05, rotate: 180 }}
                     whileTap={{ scale: 0.95 }}
                     animate={{ rotate: cartRotate ? 360 : 0 }}
                     transition={{ duration: 0.3 }}
                   >
                     <ShoppingCart className="w-5 h-5" />
                     {totalItems > 0 && (
                       <motion.span 
                         className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold shadow-lg"
                         initial={{ scale: 0 }}
                         animate={{ scale: 1 }}
                         transition={{ type: "spring", stiffness: 500, damping: 30 }}
                       >
                         {totalItems}
                       </motion.span>
                     )}
                   </motion.button>
                 </Link>
               </motion.div>

              {/* Authentication */}
              {isAuthenticated && user ? (
                <motion.div 
                  className="relative"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: 0.5 }}
                >
                  <motion.button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowUserMenu(!showUserMenu);
                    }}
                    className="flex items-center gap-3 text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-300 p-3 rounded-xl hover:bg-primary-50 dark:hover:bg-primary-900/20 hover:shadow-md group"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="relative">
                      <div className="w-10 h-10 bg-gradient-to-br from-primary-100 to-secondary-100 dark:from-primary-900 to-secondary-900 rounded-full flex items-center justify-center shadow-md group-hover:shadow-glow transition-all duration-300">
                        <User className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                      </div>
                      <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white dark:border-gray-800" />
                    </div>
                    <span className="text-sm font-medium">
                      {user.first_name} {user.last_name}
                    </span>
                  </motion.button>

                  {/* User Dropdown Menu */}
                  <AnimatePresence>
                    {showUserMenu && (
                      <motion.div
                        className="absolute right-0 mt-3 w-64 bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 py-3 z-50"
                        initial={{ opacity: 0, y: -10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -10, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {user.first_name} {user.last_name}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{user.email}</p>
                        </div>
                        
                        <div className="py-2">
                          <Link
                            href={`${prefix}/profile`}
                            className="flex items-center gap-3 px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all duration-200 rounded-lg mx-2"
                            onClick={() => setShowUserMenu(false)}
                          >
                            <User className="w-4 h-4" />
                            {t('profile')}
                          </Link>
                          
                          <Link
                            href={`${prefix}/orders`}
                            className="flex items-center gap-3 px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all duration-200 rounded-lg mx-2"
                            onClick={() => setShowUserMenu(false)}
                          >
                            <Package className="w-4 h-4" />
                            {t('orders')}
                          </Link>
                          
                          <Link
                            href={`${prefix}/wishlist`}
                            className="flex items-center gap-3 px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all duration-200 rounded-lg mx-2"
                            onClick={() => setShowUserMenu(false)}
                          >
                            <Heart className="w-4 h-4" />
                            {t('wishlist')}
                          </Link>
                        </div>
                        
                        <div className="border-t border-gray-100 dark:border-gray-700 mt-2 pt-2">
                          <button
                            onClick={handleLogout}
                            className="flex items-center gap-3 px-4 py-3 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-200 rounded-lg mx-2 w-full text-left"
                          >
                            <LogOut className="w-4 h-4" />
                            {t('logout')}
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ) : (
                <motion.div 
                  className="flex items-center gap-3"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: 0.5 }}
                >
                                     <button 
                     onClick={() => setShowQuickLogin(true)}
                     className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-300 font-medium h-11 px-3 md:px-4 rounded-xl hover:bg-primary-50 dark:hover:bg-primary-900/20 flex items-center justify-center text-sm md:text-base"
                   >
                     {t('login')}
                   </button>
                  <Link 
                    href={`${prefix}/register`}
                    className="group"
                  >
                                         <motion.div
                       className="bg-gradient-to-r from-accent-500 to-primary-500 hover:from-accent-600 hover:to-primary-600 text-white h-11 px-4 md:px-6 rounded-xl transition-all duration-300 font-medium shadow-lg hover:shadow-glow flex items-center justify-center text-sm md:text-base"
                       whileHover={{ scale: 1.05, y: -2 }}
                       whileTap={{ scale: 0.95 }}
                     >
                      {t('register')}
                    </motion.div>
                  </Link>
                </motion.div>
              )}
            </div>

                         {/* Mobile Menu Button */}
             <motion.button 
               onClick={() => setShowMobileMenu(!showMobileMenu)}
               className="md:hidden h-11 px-4 text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-300 rounded-xl hover:bg-primary-50 dark:hover:bg-primary-900/20 flex items-center justify-center"
               whileHover={{ scale: 1.05 }}
               whileTap={{ scale: 0.95 }}
             >
              {showMobileMenu ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </motion.button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {showMobileMenu && (
            <motion.div 
              className="md:hidden border-t border-gray-200/50 dark:border-gray-800/50 bg-white/95 dark:bg-gray-950/95 backdrop-blur-xl fixed left-0 right-0 z-40 max-h-[calc(100vh-80px)] overflow-y-auto"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
            >
              <div className="px-4 py-4 space-y-3">
                {/* Mobile Settings - Moved to top for better accessibility */}
                <motion.div 
                  className="pb-3 border-b border-gray-200/50 dark:border-gray-800/50"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700 dark:text-gray-300 font-medium text-sm">{t('settings')}</span>
                    <div className="flex items-center gap-1">
                      <button 
                        className="p-2 text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-300 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20"
                        onClick={toggleTheme}
                        title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
                      >
                        {theme === 'light' ? (
                          <Moon className="w-4 h-4" />
                        ) : (
                          <Sun className="w-4 h-4" />
                        )}
                      </button>
                      <div className="scale-90">
                        <CurrencySelector dropDirection="down" />
                      </div>
                      <div className="scale-90">
                        <LanguageSwitcher dropDirection="down" />
                      </div>
                    </div>
                  </div>
                </motion.div>

                {/* Mobile Navigation Links */}
                <div className="space-y-2">
                  {navItems.map((item, index) => (
                    <motion.div
                      key={item.href}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <Link 
                        href={item.href} 
                        className={`block text-base font-medium transition-all duration-300 p-2.5 rounded-lg ${
                          isActive(item.href)
                            ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20' 
                            : 'text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                        }`}
                        onClick={() => setShowMobileMenu(false)}
                      >
                        {item.label}
                      </Link>
                    </motion.div>
                  ))}
                </div>

                {/* Mobile Cart */}
                <motion.div 
                  className="pt-3 border-t border-gray-200/50 dark:border-gray-800/50"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                >
                  <motion.div
                    animate={{ rotate: cartRotate ? 360 : 0 }}
                    transition={{ duration: 0.3 }}
                    whileHover={{ scale: 1.05, rotate: 180 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Link 
                      href={`${prefix}/cart`}
                      className="flex items-center justify-between text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-300 rounded-xl hover:bg-primary-50 dark:hover:bg-primary-900/20 hover:shadow-md px-4 py-4 focus:outline-none focus:ring-0"
                      onClick={() => setShowMobileMenu(false)}
                    >
                      <div className="flex items-center gap-3">
                        <ShoppingCart className="w-5 h-5" />
                        <span className="font-medium">{t('cart')}</span>
                      </div>
                      {totalItems > 0 && (
                        <span className="bg-red-500 text-white text-sm rounded-full w-6 h-6 flex items-center justify-center font-bold shadow-lg">
                          {totalItems}
                        </span>
                      )}
                    </Link>
                  </motion.div>
                </motion.div>

                {/* Mobile Authentication */}
                <motion.div 
                  className="pt-3 border-t border-gray-200/50 dark:border-gray-800/50"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 }}
                >
                  {isAuthenticated && user ? (
                    <div className="space-y-2">
                      {/* User Info */}
                      <div className="flex items-center gap-3 p-3 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-lg">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-100 to-secondary-100 dark:from-primary-900 to-secondary-900 rounded-full flex items-center justify-center shadow-md">
                          <User className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {user.first_name} {user.last_name}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{user.email}</p>
                        </div>
                      </div>
                      
                      {/* User Menu Links */}
                      <Link
                        href={`${prefix}/profile`}
                        className="flex items-center gap-3 p-2.5 text-gray-700 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-all duration-300"
                        onClick={() => setShowMobileMenu(false)}
                      >
                        <User className="w-5 h-5" />
                        <span className="font-medium">{t('profile')}</span>
                      </Link>
                      
                      <Link
                        href={`${prefix}/orders`}
                        className="flex items-center gap-3 p-2.5 text-gray-700 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-all duration-300"
                        onClick={() => setShowMobileMenu(false)}
                      >
                        <Package className="w-5 h-5" />
                        <span className="font-medium">{t('orders')}</span>
                      </Link>
                      
                      <Link
                        href={`${prefix}/wishlist`}
                        className="flex items-center gap-3 p-2.5 text-gray-700 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-all duration-300"
                        onClick={() => setShowMobileMenu(false)}
                      >
                        <Heart className="w-5 h-5" />
                        <span className="font-medium">{t('wishlist')}</span>
                      </Link>
                      
                      <button
                        onClick={() => {
                          handleLogout();
                          setShowMobileMenu(false);
                        }}
                        className="flex items-center gap-3 p-2.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all duration-300 w-full text-left"
                      >
                        <LogOut className="w-5 h-5" />
                        <span className="font-medium">{t('logout')}</span>
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Link 
                        href={`${prefix}/login`} 
                        className="block text-center bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 px-4 py-3 rounded-lg transition-all duration-300 font-medium"
                        onClick={() => setShowMobileMenu(false)}
                      >
                        {t('login')}
                      </Link>
                      <Link 
                        href={`${prefix}/register`} 
                        className="block text-center bg-gradient-to-r from-accent-500 to-primary-500 hover:from-accent-600 hover:to-primary-600 text-white px-4 py-3 rounded-lg transition-all duration-300 font-medium shadow-lg"
                        onClick={() => setShowMobileMenu(false)}
                      >
                        {t('register')}
                      </Link>
                    </div>
                  )}
                </motion.div>


              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.nav>

      {/* Quick Login Modal */}
      <LoginQuickModal
        isOpen={showQuickLogin}
        onClose={() => setShowQuickLogin(false)}
        onError={(msg) => console.error('Quick login error:', msg)}
      />
    </DropdownProvider>
  );
} 