'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { login } from '../../../lib/api/auth';
import { useAuth } from '../../../lib/contexts/AuthContext';
import ProtectedRoute from '../../../components/ProtectedRoute';
import GoogleSignInButton from '../../../components/auth/GoogleSignInButton';
import { Eye, EyeOff, Mail, Lock, LogIn, ArrowRight, Sparkles, AlertCircle, CheckCircle } from 'lucide-react';
import type { User as UserType } from '../../../lib/types/api';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const t = useTranslations('auth');
  const { login: authLogin, mergeGuestCart } = useAuth();

  // Get locale from current path
  const locale = typeof window !== 'undefined' ?
    window.location.pathname.split('/')[1] || 'en' : 'en';

  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });

  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Get redirect URL from query params
  const redirect = searchParams.get('redirect') || '/cart';

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.username || !formData.password) {
      setError(t('pleaseFillAllFields'));
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await login({
        username: formData.username,
        password: formData.password
      });

      const responseData = response as {
        data: {
          requires_email_verification?: boolean;
          email?: string;
          success?: boolean;
          user?: unknown;
          tokens?: unknown;
          message?: string;
        }
      };

      if (responseData.data.requires_email_verification) {
        // Redirect to email verification page with email if available
        if (responseData.data.email) {
          router.push(`/verify-email?email=${encodeURIComponent(responseData.data.email)}`);
        } else {
          // If email is not available in response, use the username as it might be an email
          router.push(`/verify-email?email=${encodeURIComponent(formData.username)}`);
        }
        return;
      }

      if (responseData.data.success) {
        // Check if both user and tokens are available
        if (responseData.data.user && responseData.data.tokens) {
          // Use AuthContext to handle login
          authLogin(responseData.data.user as UserType, responseData.data.tokens as { access: string; refresh: string });

          // Handle cart merge with overbooking validation
          const mergeResult = await mergeGuestCart();
          if (!mergeResult.success) {
            if (mergeResult.conflicts) {
              // Show overbooking conflicts
              setError(`${mergeResult.message}\n\n${t('conflictsDetected')}:\n${mergeResult.conflicts?.map((conflict: unknown) => {
                const c = conflict as { product_title?: string; message?: string };
                return `- ${c.product_title}: ${c.message}`;
              }).join('\n')}`);

              // Redirect to orders page after delay
              setTimeout(() => {
                router.push(`/${locale}/orders`);
              }, 3000);
              return;
            } else {
              // Show other merge errors
              setError(mergeResult.message || t('cartMergeError'));
            }
          } else {
            setSuccess(t('loginSuccess') + (mergeResult.message ? ` ${mergeResult.message}` : ''));
          }

          // Check for pending transfer booking
          const pendingBookingData = localStorage.getItem('pendingTransferBooking');
          if (pendingBookingData) {
            try {
              const bookingData = JSON.parse(pendingBookingData);
              // Check if booking is not too old (within 1 hour)
              const isBookingValid = Date.now() - bookingData.timestamp < 60 * 60 * 1000;

              if (isBookingValid) {
                // Store booking data for completion
                localStorage.setItem('completeTransferBooking', JSON.stringify(bookingData));
                localStorage.removeItem('pendingTransferBooking');

                // Redirect to the original booking page
                setTimeout(() => {
                  router.push(bookingData.returnUrl || `/${locale}/transfers/booking`);
                }, 1000);
                return;
              } else {
                // Remove expired booking data
                localStorage.removeItem('pendingTransferBooking');
              }
            } catch (error) {
              console.error('Error parsing pending booking data:', error);
              localStorage.removeItem('pendingTransferBooking');
            }
          }

          // Guest cart is automatically merged in AuthContext.login()
          // Redirect to cart after successful login
          setTimeout(() => {
            router.push(redirect || `/${locale}/cart`);
          }, 500);
        } else {
          setError(t('loginError'));
        }
      } else {
        setError(responseData.data.message || t('loginError'));
      }

    } catch (err: unknown) {
      console.error('Login error:', err);
      const errorMessage = err instanceof Error && 'response' in err && err.response && typeof err.response === 'object' && 'data' in err.response && err.response.data && typeof err.response.data === 'object' && 'message' in err.response.data && typeof err.response.data.message === 'string'
        ? err.response.data.message
        : err instanceof Error && 'response' in err && err.response && typeof err.response === 'object' && 'data' in err.response && err.response.data && typeof err.response.data === 'object' && 'error' in err.response.data && typeof err.response.data.error === 'string'
          ? err.response.data.error
          : t('loginError');
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ProtectedRoute requireAuth={false}>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <motion.div
          className="max-w-md w-full"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header */}
          <motion.div
            className="text-center mb-8"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <motion.div
              className="relative inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl mb-6 shadow-lg"
              animate={{ y: [0, -3, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
              <LogIn className="w-10 h-10 text-white" />
              <Sparkles className="absolute -top-1 -right-1 w-5 h-5 text-yellow-300 opacity-80" />
            </motion.div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-3">
              {t('loginTitle')}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              {t('loginSubtitle')}
            </p>
          </motion.div>

          {/* Login Form */}
          <motion.div
            className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-8"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username/Email Field */}
              <motion.div
                className="space-y-3"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <label htmlFor="username" className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  {t('usernameOrEmail')}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    required
                    className="w-full pl-12 pr-4 py-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 shadow-sm hover:shadow-md"
                    placeholder={t('enterUsernameOrEmail')}
                    disabled={isLoading}
                  />
                </div>
              </motion.div>

              {/* Password Field */}
              <motion.div
                className="space-y-3"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  {t('password')}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    className="w-full pl-12 pr-12 py-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 shadow-sm hover:shadow-md"
                    placeholder={t('enterPassword')}
                    disabled={isLoading}
                  />
                  <motion.button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-primary-500 transition-colors duration-300"
                    disabled={isLoading}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </motion.button>
                </div>
              </motion.div>

              {/* Error/Success Messages */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    className="p-4 bg-red-50/80 dark:bg-red-900/20 backdrop-blur-sm border border-red-200/50 dark:border-red-700/50 rounded-xl"
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                      <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {success && (
                  <motion.div
                    className="p-4 bg-green-50/80 dark:bg-green-900/20 backdrop-blur-sm border border-green-200/50 dark:border-green-700/50 rounded-xl"
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                      <p className="text-green-600 dark:text-green-400 text-sm">{success}</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={isLoading}
                className="w-full h-14 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white font-semibold rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 shadow-lg hover:shadow-glow"
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 }}
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    <span>{t('loggingIn')}</span>
                  </>
                ) : (
                  <>
                    <span>{t('loginButton')}</span>
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </motion.button>

              {/* Divider */}
              <div className="flex items-center my-6">
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>
                <span className="px-3 text-xs text-gray-500 dark:text-gray-400 bg-white/80 dark:bg-gray-800/80 rounded-full">{t('or')}</span>
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>
              </div>

              {/* Google Sign-In */}
              <motion.div
                className="mt-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.6 }}
              >
                <GoogleSignInButton
                  onError={(msg) => setError(msg)}
                  onSuccessRedirect={(path) => router.push(`/${locale}${path}`)}
                />
              </motion.div>

              {/* Links */}
              <motion.div
                className="mt-8 space-y-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.7 }}
              >
                <div className="text-center">
                  <Link
                    href="/forgot-password"
                    className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium transition-colors duration-300 hover:underline"
                  >
                    {t('forgotPassword')}
                  </Link>
                </div>
                <div className="text-center">
                  <Link
                    href="/register"
                    className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-medium transition-colors duration-300"
                  >
                    {t('noAccount')} <span className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 hover:underline">{t('registerNow')}</span>
                  </Link>
                </div>
              </motion.div>
            </form>
          </motion.div>
        </motion.div>
      </div>
    </ProtectedRoute>
  );
} 