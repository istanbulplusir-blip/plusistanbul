'use client';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, ChevronDown } from 'lucide-react';
import { useDropdown } from '@/contexts/DropdownContext';
import { useUnifiedLanguage } from '@/lib/contexts/UnifiedLanguageContext';

const languages = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'fa', label: 'فارسی', flag: '🇮🇷' },
  { code: 'tr', label: 'Türkçe', flag: '🇹🇷' },
];

interface LanguageSwitcherProps {
  dropDirection?: 'up' | 'down' | 'auto';
}

export default function LanguageSwitcher({ dropDirection = 'auto' }: LanguageSwitcherProps) {
  const { language, changeLanguageAndNavigate, isAgent, isLoading } = useUnifiedLanguage();
  const { openDropdown, setOpenDropdown } = useDropdown();
  const dropdownId = 'language-switcher';
  const isOpen = openDropdown === dropdownId;
  
  // Check if we're in mobile view
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Determine dropdown direction
  const shouldDropUp = dropDirection === 'up' || (dropDirection === 'auto' && isMobile);

  const handleLanguageChange = (newLocale: string) => {
    changeLanguageAndNavigate(newLocale);
    setOpenDropdown(null);
    
    // Show message for agents
    if (isAgent) {
      console.log('Language changed for agent. This will be saved to your profile.');
    }
  };

  const toggleDropdown = () => {
    setOpenDropdown(isOpen ? null : dropdownId);
  };

  const currentLanguage = languages.find(lang => lang.code === language) || languages[0];

  return (
    <div className="relative">
      <motion.button
        onClick={toggleDropdown}
        className="flex items-center gap-2 h-11 px-4 text-sm bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl hover:bg-white dark:hover:bg-gray-800 hover:border-primary-300 dark:hover:border-primary-600 transition-all duration-300 text-gray-700 dark:text-gray-300 shadow-sm hover:shadow-md group"
        whileHover={{ scale: 1.02, y: -1 }}
        whileTap={{ scale: 0.98 }}
      >
        <Globe className="w-4 h-4 text-primary-500 dark:text-primary-400 group-hover:text-primary-600 dark:group-hover:text-primary-300 transition-colors duration-300" />
        <span className="hidden sm:inline text-lg">{currentLanguage.flag}</span>
        <span className="hidden md:inline font-medium">{currentLanguage.code.toUpperCase()}</span>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="w-4 h-4 text-gray-400 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors duration-300" />
        </motion.div>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            className={`absolute right-0 w-56 bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 py-3 z-50 ${
              shouldDropUp ? 'bottom-full mb-3' : 'top-full mt-3'
            }`}
            initial={{ 
              opacity: 0, 
              y: shouldDropUp ? 10 : -10, 
              scale: 0.95 
            }}
            animate={{ 
              opacity: 1, 
              y: 0, 
              scale: 1 
            }}
            exit={{ 
              opacity: 0, 
              y: shouldDropUp ? 10 : -10, 
              scale: 0.95 
            }}
            transition={{ duration: 0.2 }}
          >
            <div className="px-4 py-2 border-b border-gray-100 dark:border-gray-700 mb-2">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Select Language</h3>
            </div>
            
            {languages.map((lang, index) => (
              <motion.button
                key={lang.code}
                onClick={() => handleLanguageChange(lang.code)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-sm text-left hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all duration-200 ${
                  language === lang.code 
                    ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20' 
                    : 'text-gray-700 dark:text-gray-300'
                }`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: index * 0.05 }}
                whileHover={{ x: 5 }}
              >
                <span className="text-xl">{lang.flag}</span>
                <span className="font-medium">{lang.label}</span>
                {language === lang.code && (
                  <motion.span 
                    className="ml-auto text-primary-600 dark:text-primary-400"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  >
                    ✓
                  </motion.span>
                )}
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Click outside to close */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setOpenDropdown(null)}
        />
      )}
    </div>
  );
} 