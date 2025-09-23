'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Shield, AlertCircle, CheckCircle, Sparkles } from 'lucide-react';
import { useTranslations } from 'next-intl';

interface OTPModalProps {
  isOpen: boolean;
  onClose: () => void;
  onVerify: (otpCode: string) => Promise<void>;
  field: string;
  newValue: string;
  message: string;
  isLoading?: boolean;
}

export default function OTPModal({
  isOpen,
  onClose,
  onVerify,
  field,
  newValue,
  message
}: OTPModalProps) {
  const t = useTranslations('auth');
  const [otpCode, setOtpCode] = useState('');
  const [error, setError] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setOtpCode('');
      setError('');
      setIsVerifying(false);
    }
  }, [isOpen]);

  const handleVerify = async () => {
    if (!otpCode.trim()) {
      setError(t('otpRequired'));
      return;
    }

    if (otpCode.length !== 6) {
      setError(t('otpInvalidLength'));
      return;
    }

    setIsVerifying(true);
    setError('');

    try {
      await onVerify(otpCode);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : t('otpVerificationError');
      setError(errorMessage);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleVerify();
    }
  };

  const getFieldLabel = (field: string) => {
    switch (field) {
      case 'email':
        return t('fieldEmail');
      case 'phone_number':
        return t('fieldPhoneNumber');
      case 'first_name':
        return t('fieldFirstName');
      case 'last_name':
        return t('fieldLastName');
      default:
        return field;
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm flex items-center justify-center z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          <motion.div 
            className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 max-w-md w-full mx-4"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            {/* Header */}
            <div className="relative p-6 border-b border-gray-200/50 dark:border-gray-700/50">
              <motion.button
                onClick={onClose}
                className="absolute top-4 right-4 w-8 h-8 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full flex items-center justify-center transition-all duration-300"
                disabled={isVerifying}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              </motion.button>
              
              <div className="flex items-center gap-4">
                <motion.div 
                  className="relative w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center shadow-lg"
                  animate={{ y: [0, -2, 0] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                >
                  <Shield className="w-6 h-6 text-white" />
                  <Sparkles className="absolute -top-1 -right-1 w-3 h-3 text-yellow-300 opacity-80" />
                </motion.div>
                <div>
                  <h3 className="text-lg font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                    {t('otpConfirmChange', { field: getFieldLabel(field) })}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {t('otpSecurityMessage')}
                  </p>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* Message */}
              <motion.div 
                className="mb-6 p-4 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border border-primary-200/50 dark:border-primary-700/50 rounded-xl"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-primary-600 dark:text-primary-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm text-primary-800 dark:text-primary-200 font-medium mb-1">
                      {message}
                    </p>
                    <p className="text-xs text-primary-600 dark:text-primary-400">
                      {t('otpCodeSentTo', { field: field === 'email' ? t('fieldEmail') : t('fieldPhoneNumber') })}
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Field Info */}
              <motion.div 
                className="mb-6 p-4 bg-gray-50/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {t('otpNewValue', { field: getFieldLabel(field) })}
                  </span>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {newValue}
                  </span>
                </div>
              </motion.div>

              {/* OTP Input */}
              <motion.div 
                className="mb-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.3 }}
              >
                <label htmlFor="otp" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  {t('otpEnterCode')}
                </label>
                <input
                  type="text"
                  id="otp"
                  value={otpCode}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                    setOtpCode(value);
                    if (error) setError('');
                  }}
                  onKeyPress={handleKeyPress}
                  placeholder="000000"
                  className="w-full px-4 py-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-center text-xl font-mono tracking-widest shadow-sm hover:shadow-md transition-all duration-300"
                  maxLength={6}
                  disabled={isVerifying}
                />
              </motion.div>

              {/* Error Message */}
              <AnimatePresence>
                {error && (
                  <motion.div 
                    className="mb-6 p-4 bg-red-50/80 dark:bg-red-900/20 backdrop-blur-sm border border-red-200/50 dark:border-red-700/50 rounded-xl"
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                      <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Actions */}
              <motion.div 
                className="flex gap-3"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.4 }}
              >
                <motion.button
                  onClick={onClose}
                  disabled={isVerifying}
                  className="flex-1 h-12 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 hover:bg-white dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-xl transition-all duration-300 disabled:opacity-50 shadow-sm hover:shadow-md"
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {t('otpCancel')}
                </motion.button>
                <motion.button
                  onClick={handleVerify}
                  disabled={isVerifying || !otpCode.trim()}
                  className="flex-1 h-12 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white rounded-xl transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg hover:shadow-glow"
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isVerifying ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      {t('otpVerifying')}
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      {t('otpConfirm')}
                    </>
                  )}
                </motion.button>
              </motion.div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
} 