'use client';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DollarSign, ChevronDown } from 'lucide-react';
import { useDropdown } from '@/contexts/DropdownContext';
import { useUnifiedCurrency } from '@/lib/contexts/UnifiedCurrencyContext';

const currencies = [
  { code: 'USD', symbol: '$', name: 'US Dollar', flag: '🇺🇸' },
  { code: 'EUR', symbol: '€', name: 'Euro', flag: '🇪🇺' },
  { code: 'TRY', symbol: '₺', name: 'Turkish Lira', flag: '🇹🇷' },
  { code: 'IRR', symbol: 'ریال', name: 'Iranian Rial', flag: '🇮🇷' },
];

interface CurrencySelectorProps {
  dropDirection?: 'up' | 'down' | 'auto';
}

export default function CurrencySelector({ dropDirection = 'auto' }: CurrencySelectorProps) {
  const { currency, setCurrency, isAgent, isLoading } = useUnifiedCurrency();
  const { openDropdown, setOpenDropdown } = useDropdown();
  const dropdownId = 'currency-selector';
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

  const handleCurrencyChange = (newCurrency: string) => {
    setCurrency(newCurrency);
    setOpenDropdown(null);
    
    // Show message for agents
    if (isAgent) {
      console.log('Currency changed for agent. This will be saved to your profile.');
    }
  };

  const toggleDropdown = () => {
    setOpenDropdown(isOpen ? null : dropdownId);
  };

  const currentCurrency = currencies.find(c => c.code === currency) || currencies[0];

  return (
    <div className="relative">
      <motion.button
        onClick={toggleDropdown}
        className="flex items-center gap-2 h-11 px-4 text-sm bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl hover:bg-white dark:hover:bg-gray-800 hover:border-primary-300 dark:hover:border-primary-600 transition-all duration-300 text-gray-700 dark:text-gray-300 shadow-sm hover:shadow-md group"
        whileHover={{ scale: 1.02, y: -1 }}
        whileTap={{ scale: 0.98 }}
      >
        <DollarSign className="w-4 h-4 text-primary-500 dark:text-primary-400 group-hover:text-primary-600 dark:group-hover:text-primary-300 transition-colors duration-300" />
        <span className="hidden sm:inline text-lg">{currentCurrency.flag}</span>
        <span className="hidden md:inline font-medium">{currentCurrency.symbol} {currentCurrency.code}</span>
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
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Select Currency</h3>
            </div>
            
            {currencies.map((curr, index) => (
              <motion.button
                key={curr.code}
                onClick={() => handleCurrencyChange(curr.code)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-sm text-left hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all duration-200 ${
                  currency === curr.code 
                    ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20' 
                    : 'text-gray-700 dark:text-gray-300'
                }`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: index * 0.05 }}
                whileHover={{ x: 5 }}
              >
                <span className="text-xl">{curr.flag}</span>
                <div className="flex flex-col">
                  <span className="font-medium">{curr.symbol} {curr.code}</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{curr.name}</span>
                </div>
                {currency === curr.code && (
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