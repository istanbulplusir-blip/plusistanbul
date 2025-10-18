'use client';

import { useLocale, useTranslations } from 'next-intl';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { X, LogIn, UserPlus, Sparkles } from 'lucide-react';
import GoogleSignInButton from './GoogleSignInButton';

type Props = {
  isOpen: boolean;
  onClose: () => void;
  onError?: (msg: string) => void;
};

export default function LoginQuickModal({ isOpen, onClose, onError }: Props) {
  const locale = useLocale();
  const t = useTranslations('auth');
  const prefix = locale === 'en' ? '' : `/${locale}`;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70 backdrop-blur-sm p-4" 
          onClick={onClose}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          <motion.div
            className="w-full max-w-md bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-6"
            onClick={(e) => e.stopPropagation()}
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            {/* Header */}
            <div className="relative mb-6 text-center">
              <motion.button
                onClick={onClose}
                className="absolute -top-2 -right-2 w-8 h-8 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full flex items-center justify-center transition-all duration-300"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              </motion.button>
              
              <motion.div
                className="relative inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl mb-4 shadow-lg"
                animate={{ y: [0, -2, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              >
                <LogIn className="w-8 h-8 text-white" />
                <Sparkles className="absolute -top-1 -right-1 w-4 h-4 text-yellow-300 opacity-80" />
              </motion.div>
              
              <h3 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-2">
                {t('quickLogin')}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {t('quickLoginDesc')}
              </p>
            </div>

            {/* Google Sign In */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <GoogleSignInButton
                onError={onError}
                onSuccessRedirect={(path) => {
                  window.location.href = `${prefix}${path}`;
                }}
              />
            </motion.div>

            {/* Divider */}
            <div className="flex items-center my-6">
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>
              <span className="px-3 text-xs text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-full">{t('or')}</span>
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>
            </div>

            {/* Action Buttons */}
            <motion.div 
              className="flex items-center gap-3"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <Link
                href={`${prefix}/login`}
                className="flex-1 group"
                onClick={onClose}
              >
                <motion.div
                  className="h-12 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 hover:bg-white dark:hover:bg-gray-800 hover:border-primary-300 dark:hover:border-primary-600 text-gray-700 dark:text-gray-300 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-sm hover:shadow-md"
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <LogIn className="w-4 h-4 text-primary-500 dark:text-primary-400 group-hover:text-primary-600 dark:group-hover:text-primary-300 transition-colors duration-300" />
                  <span className="font-medium">{t('loginPage')}</span>
                </motion.div>
              </Link>
              
              <Link
                href={`${prefix}/register`}
                className="flex-1 group"
                onClick={onClose}
              >
                <motion.div
                  className="h-12 bg-gradient-to-r from-accent-500 to-primary-500 hover:from-accent-600 hover:to-primary-600 text-white rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-glow"
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <UserPlus className="w-4 h-4" />
                  <span className="font-medium">{t('signUp')}</span>
                </motion.div>
              </Link>
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}


