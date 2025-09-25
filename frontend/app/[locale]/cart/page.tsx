'use client';

import React, { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { motion, AnimatePresence } from 'framer-motion';
import { useCart } from '../../../lib/hooks/useCart';
import { useAuth } from '../../../lib/contexts/AuthContext';
import { useCustomerData } from '../../../lib/hooks/useCustomerData';
import { useToast } from '../../../components/Toast';
import { 
  ShoppingCart, 
  Trash2, 
  AlertCircle,
  Clock,
  Calendar,
  Users,
  MapPin,
  ArrowRight,
  Home,
  Package,
  Ticket,
  Truck,
  Sparkles,
  Star,
  User
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { CartItem } from '../../../lib/contexts/UnifiedCartContext';
import OptimizedImage from '@/components/common/OptimizedImage';
import { getImageUrl } from '@/lib/utils';

export default function CartPage() {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const t = useTranslations('Cart');
  const { items, totalItems, currency, subtotal, feesTotal, taxTotal, grandTotal, removeItem, clearCart, refreshCart, limits } = useCart();
  const { isAuthenticated, user } = useAuth();
  const { } = useCustomerData();
  const { addToast } = useToast();
  
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isRemoving, setIsRemoving] = useState<string | null>(null);

  // Toast helper function
  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    addToast({
      title: type === 'error' ? 'خطا' : type === 'success' ? 'موفقیت' : 'اطلاعات',
      message: message,
      type: type
    });
  };

  const handleRemoveItem = async (itemId: string) => {
    setIsRemoving(itemId);
    try {
      const result = await removeItem(itemId);
      if (result.success) {
        showToast('آیتم از سبد خرید حذف شد', 'success');
        await refreshCart();
      } else {
        showToast(result.error || 'خطا در حذف آیتم', 'error');
      }
    } catch {
      showToast('خطا در حذف آیتم. لطفاً دوباره تلاش کنید.', 'error');
    } finally {
      setIsRemoving(null);
    }
  };

  const handleClearCart = async () => {
    setIsRefreshing(true);
    try {
      const result = await clearCart();
      if (result.success) {
        showToast('سبد خرید پاک شد', 'success');
        setShowClearConfirm(false);
      } else {
        showToast(result.error || 'خطا در پاک کردن سبد خرید', 'error');
      }
    } catch {
      showToast('خطا در پاک کردن سبد خرید. لطفاً دوباره تلاش کنید.', 'error');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleCheckout = () => {
    if (totalItems === 0) return;
    // Add redirect parameter to checkout URL so user returns to cart after login/register
    router.push(`/${locale}/checkout?redirect=/${locale}/cart`);
  };

  const handleContinueShopping = () => {
    router.push(`/${locale}`);
  };

  const handleBackToHome = () => {
    router.push(`/${locale}`);
  };

  const getProductTypeIcon = (productType: string) => {
    switch (productType) {
      case 'tour':
        return <Package className="h-4 w-4" />;
      case 'event':
        return <Ticket className="h-4 w-4" />;
      case 'transfer':
        return <Truck className="h-4 w-4" />;
      default:
        return <Package className="h-4 w-4" />;
    }
  };

  const getProductTypeLabel = (productType: string) => {
    switch (productType) {
      case 'tour':
        return t('tour');
      case 'event':
        return t('event');
      case 'transfer':
        return t('transfer');
      default:
        return productType;
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat(locale === 'fa' ? 'fa-IR' : locale === 'tr' ? 'tr-TR' : 'en-US').format(price);
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString(locale === 'fa' ? 'fa-IR' : locale === 'tr' ? 'tr-TR' : 'en-US');
  };

  if (totalItems === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
        <motion.div 
          className="max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="text-center mb-12">
            <motion.div 
              className="mx-auto h-20 w-20 sm:h-24 sm:w-24 bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-full flex items-center justify-center mb-6 shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              whileHover={{ scale: 1.05, rotate: 5 }}
            >
              <ShoppingCart className="h-10 w-10 sm:h-12 sm:w-12 text-primary-500 dark:text-primary-400" />
            </motion.div>
            
            <motion.h1 
              className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              {t('cartTitle')}
            </motion.h1>
            
            <motion.p 
              className="text-base sm:text-lg text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              {t('emptyCartDescription')}
            </motion.p>
            
            <motion.div 
              className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center max-w-md mx-auto"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              <motion.div
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="flex-1"
              >
                <Button
                  onClick={handleContinueShopping}
                  className="w-full bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-6 sm:px-8 py-3 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-glow"
                >
                  <Home className="h-4 w-4 sm:h-5 sm:w-5 mr-2" />
                  {t('startShopping')}
                </Button>
              </motion.div>
              
              <motion.div
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="flex-1"
              >
                <Button
                  onClick={handleBackToHome}
                  variant="outline"
                  className="w-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 text-gray-700 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-800 px-6 sm:px-8 py-3 rounded-xl font-semibold transition-all duration-300 shadow-sm hover:shadow-md"
                >
                  {t('backToHome')}
                </Button>
              </motion.div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-6 sm:py-8 px-4 sm:px-6 lg:px-8">
      <motion.div 
        className="max-w-7xl mx-auto"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <motion.div 
          className="mb-6 sm:mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-6">
            <div className="flex items-center gap-3">
              <motion.div 
                className="h-10 w-10 sm:h-12 sm:w-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center shadow-lg"
                whileHover={{ scale: 1.05, rotate: 5 }}
                animate={{ y: [0, -2, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <ShoppingCart className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                  {t('cartTitle')}
                </h1>
                <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <Sparkles className="h-4 w-4 text-primary-500" />
                  {totalItems} {t('items')} {t('inCart')}
                </p>
                
                {/* User Limits Display */}
                <div className="mt-2 flex items-center gap-2 text-xs text-blue-600 dark:text-blue-400">
                  <User className="h-3 w-3" />
                  <span>{limits.userType === 'guest' ? 'کاربر مهمان' : 'کاربر عادی'}</span>
                  <span>•</span>
                  <span>{totalItems}/{limits.maxItems} آیتم</span>
                  <span>•</span>
                  <span>${grandTotal}/${limits.maxTotal}</span>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
              <motion.div
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  onClick={handleContinueShopping}
                  variant="outline"
                  className="w-full sm:w-auto bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 text-gray-700 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-800 px-4 py-2 rounded-xl font-medium transition-all duration-300 shadow-sm hover:shadow-md"
                >
                  {t('continueShopping')}
                </Button>
              </motion.div>
              
              <motion.div
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  onClick={() => setShowClearConfirm(true)}
                  variant="outline"
                  className="w-full sm:w-auto bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-red-200/50 dark:border-red-700/50 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 px-4 py-2 rounded-xl font-medium transition-all duration-300 shadow-sm hover:shadow-md"
                  disabled={isRefreshing}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  {t('clearCart')}
                </Button>
              </motion.div>
            </div>
          </div>
        </motion.div>

        {/* Guest User Limits Warning */}
        {!isAuthenticated && (
          <motion.div 
            className="mb-6 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200/50 dark:border-amber-700/50 rounded-2xl p-4 sm:p-6 backdrop-blur-xl"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-amber-500 rounded-full flex items-center justify-center">
                  <AlertCircle className="h-4 w-4 text-white" />
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-amber-800 dark:text-amber-200 mb-2">
                  محدودیت‌های کاربر مهمان
                </h3>
                <div className="text-sm text-amber-700 dark:text-amber-300 space-y-1">
                  <p>• حداکثر 5 آیتم در سبد خرید</p>
                  <p>• حداکثر 1000 دلار ارزش کل سبد</p>
                  <p>• برای رزرو و تکمیل سفارش نیاز به ثبت‌نام است</p>
                </div>
                <div className="mt-3">
                  <Button
                    onClick={() => router.push(`/${locale}/register?redirect=/${locale}/cart`)}
                    className="bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    ثبت‌نام کنید
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* User Status Information */}
        <motion.div 
          className="mb-6"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  isAuthenticated 
                    ? 'bg-green-100 dark:bg-green-900/30' 
                    : 'bg-yellow-100 dark:bg-yellow-900/30'
                }`}>
                  <User className={`h-4 w-4 ${
                    isAuthenticated 
                      ? 'text-green-600 dark:text-green-400' 
                      : 'text-yellow-600 dark:text-yellow-400'
                  }`} />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {isAuthenticated ? 'کاربر احراز هویت شده' : 'کاربر مهمان'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {isAuthenticated 
                      ? `ایمیل: ${user?.email || 'نامشخص'}` 
                      : 'برای ذخیره سبد خرید، لطفاً وارد شوید'
                    }
                  </p>
                </div>
              </div>
              {!isAuthenticated && (
                <Button
                  onClick={() => router.push(`/${locale}/login?redirect=/${locale}/cart`)}
                  className="px-4 py-2 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700 transition-colors"
                >
                  ورود / ثبت نام
                </Button>
              )}
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            <AnimatePresence>
              {items.map((item: CartItem, index) => (
                <motion.div 
                  key={item.id} 
                  className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-4 sm:p-6 transition-all duration-300 hover:shadow-glow"
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -20, scale: 0.95 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  whileHover={{ y: -2, scale: 1.01 }}
                  layout
                >
                <div className="flex flex-col gap-4">
                  {/* Mobile: Image and Price Row */}
                  <div className="flex sm:hidden items-start gap-3">
                    <motion.div 
                      className="flex-shrink-0"
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="relative overflow-hidden rounded-lg shadow-md">
                        <OptimizedImage
                          src={getImageUrl(item.image) || '/images/placeholder-car.jpg'}
                          alt={item.title || item.product_title || 'Product'}
                          width={80}
                          height={80}
                          className="w-16 h-16 object-cover"
                          fallbackSrc="/images/tour-image.jpg"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300" />
                      </div>
                    </motion.div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1 line-clamp-2">
                        {item.title || item.product_title}
                      </h3>
                      <div className="flex items-center justify-between">
                        <motion.span 
                          className="flex items-center gap-1.5 px-2 py-1 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 text-primary-700 dark:text-primary-300 rounded-full border border-primary-200/50 dark:border-primary-700/50 text-xs"
                          whileHover={{ scale: 1.05 }}
                          transition={{ duration: 0.2 }}
                        >
                          {getProductTypeIcon(item.product_type)}
                          <span className="font-medium">{getProductTypeLabel(item.product_type)}</span>
                        </motion.span>
                        
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          transition={{ duration: 0.2 }}
                          className="bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-xl px-4 py-3 border border-primary-200/50 dark:border-primary-700/50 shadow-md"
                        >
                          <p className="text-lg font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                            {formatPrice(item.total_price)} {currency}
                          </p>
                        </motion.div>
                      </div>
                    </div>
                  </div>

                  {/* Mobile: Additional Info Badges */}
                  <div className="sm:hidden">
                    <div className="flex flex-wrap items-center gap-2 text-sm">
                      {item.product_type === 'tour' && item.booking_data?.schedule_id && (
                        <motion.span 
                          className="flex items-center gap-1 px-2 py-1 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 text-green-700 dark:text-green-300 rounded-full border border-green-200/50 dark:border-green-700/50"
                          whileHover={{ scale: 1.05 }}
                          transition={{ duration: 0.2 }}
                        >
                          <Clock className="h-3 w-3" />
                          <span className="font-medium text-xs">{t('scheduled')}</span>
                        </motion.span>
                      )}
                      
                      {item.booking_date && (
                        <motion.span 
                          className="flex items-center gap-1 px-2 py-1 bg-gradient-to-r from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 text-purple-700 dark:text-purple-300 rounded-full border border-purple-200/50 dark:border-purple-700/50"
                          whileHover={{ scale: 1.05 }}
                          transition={{ duration: 0.2 }}
                        >
                          <Calendar className="h-3 w-3" />
                          <span className="font-medium text-xs">{formatDate(item.booking_date)}</span>
                        </motion.span>
                      )}
                    </div>
                  </div>

                  {/* Desktop: Original Layout */}
                  <div className="hidden sm:flex items-start gap-4">
                    <motion.div 
                      className="flex-shrink-0"
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="relative overflow-hidden rounded-xl shadow-md">
                        <OptimizedImage
                          src={getImageUrl(item.image) || '/images/placeholder-car.jpg'}
                          alt={item.title || item.product_title || 'Product'}
                          width={120}
                          height={120}
                          className="w-20 h-20 lg:w-24 lg:h-24 object-cover"
                          fallbackSrc="/images/tour-image.jpg"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300" />
                      </div>
                    </motion.div>
              
                    {/* Desktop Product Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-3">
                        <div className="flex-1 min-w-0">
                          <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                            {item.title || item.product_title}
                          </h3>
                          
                          {/* Product Type & Info */}
                          <div className="flex flex-wrap items-center gap-2 text-sm mb-3">
                            <motion.span 
                              className="flex items-center gap-1.5 px-2.5 py-1 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 text-primary-700 dark:text-primary-300 rounded-full border border-primary-200/50 dark:border-primary-700/50"
                              whileHover={{ scale: 1.05 }}
                              transition={{ duration: 0.2 }}
                            >
                              {getProductTypeIcon(item.product_type)}
                              <span className="font-medium text-xs sm:text-sm">{getProductTypeLabel(item.product_type)}</span>
                            </motion.span>
                          
                          {item.product_type === 'tour' && item.booking_data?.schedule_id && (
                            <motion.span 
                              className="flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 text-green-700 dark:text-green-300 rounded-full border border-green-200/50 dark:border-green-700/50"
                              whileHover={{ scale: 1.05 }}
                              transition={{ duration: 0.2 }}
                            >
                              <Clock className="h-3 w-3 sm:h-4 sm:w-4" />
                              <span className="font-medium text-xs sm:text-sm">{t('scheduled')}</span>
                            </motion.span>
                          )}
                          
                          {item.booking_date && (
                            <motion.span 
                              className="flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 text-purple-700 dark:text-purple-300 rounded-full border border-purple-200/50 dark:border-purple-700/50"
                              whileHover={{ scale: 1.05 }}
                              transition={{ duration: 0.2 }}
                            >
                              <Calendar className="h-3 w-3 sm:h-4 sm:w-4" />
                              <span className="font-medium text-xs sm:text-sm">{formatDate(item.booking_date)}</span>
                            </motion.span>
                          )}
                        </div>

                        {/* Additional Details */}
                        {item.product_type === 'tour' && item.booking_data?.participants && (
                          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                            <span className="flex items-center gap-1">
                              <Users className="h-4 w-4" />
                              {Object.values(item.booking_data.participants).reduce((sum: number, count: number) => sum + count, 0)} {t('participants')}
                            </span>
                          </div>
                        )}

                        {item.product_type === 'transfer' && item.booking_data?.special_requests && (
                          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                            <span className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              {item.booking_data.special_requests}
                            </span>
                          </div>
                        )}
                      </div>
                      
                          {/* Desktop Price */}
                          <div className="text-right ml-4 flex-shrink-0">
                            <motion.div
                              whileHover={{ scale: 1.05 }}
                              transition={{ duration: 0.2 }}
                              className="bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-xl px-5 py-4 border border-primary-200/50 dark:border-primary-700/50 shadow-lg"
                            >
                              <p className="text-xl lg:text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                                {formatPrice(item.total_price)} {currency}
                              </p>
                              <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-end gap-1 mt-1">
                                <Star className="h-4 w-4 text-primary-500" />
                                {t('perItem')}
                              </p>
                            </motion.div>
                          </div>

                        {/* Desktop Additional Details */}

                        {item.product_type === 'transfer' && item.booking_data?.special_requests && (
                          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                            <span className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              {item.booking_data.special_requests}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                    <div className="flex items-center justify-center sm:justify-between gap-3 pt-4 border-t border-gray-200/50 dark:border-gray-700/50">
                      <motion.div
                        className="flex items-center gap-3"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: 0.2 }}
                      >
                        {/* Quantity Badge */}
                        <motion.span 
                          className="text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700/50 px-3 py-2 rounded-lg border border-gray-200/50 dark:border-gray-600/50 flex items-center gap-1"
                          whileHover={{ scale: 1.05 }}
                          transition={{ duration: 0.2 }}
                        >
                          <Users className="h-4 w-4 text-primary-500" />
                          {t('quantity')}: <span className="font-bold text-primary-600 dark:text-primary-400">{item.quantity}</span>
                        </motion.span>
                        
                        {/* Remove Button */}
                        <motion.div
                          whileHover={{ scale: 1.02, y: -1 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <Button
                            onClick={() => handleRemoveItem(item.id)}
                            disabled={isRemoving === item.id}
                            variant="ghost"
                            className="bg-red-50/80 dark:bg-red-900/20 text-red-600 hover:text-red-700 hover:bg-red-100 dark:text-red-400 dark:hover:bg-red-900/30 px-3 py-2 rounded-lg font-medium transition-all duration-300 border border-red-200/50 dark:border-red-700/50 flex items-center gap-2"
                          >
                            <Trash2 className="h-4 w-4" />
                            <span className="hidden sm:inline">{isRemoving === item.id ? t('processing') : t('removeItem')}</span>
                          </Button>
                        </motion.div>
                      </motion.div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Cart Summary */}
          <div className="lg:col-span-1">
            <motion.div 
              className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-4 sm:p-6 sticky top-4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <motion.h3 
                className="text-lg font-semibold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-6 flex items-center gap-2"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.4 }}
              >
                <motion.div
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                >
                  <ShoppingCart className="h-5 w-5 text-primary-500" />
                </motion.div>
                {t('cartSummary')}
              </motion.h3>
              
              <motion.div 
                className="space-y-3 mb-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.5 }}
              >
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 py-2">
                  <span className="font-medium">{t('subtotal')}</span>
                  <span className="font-semibold">{formatPrice(subtotal)} {currency}</span>
                </div>
                
                {feesTotal > 0 && (
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 py-2">
                    <span className="font-medium">{t('fees')}</span>
                    <span className="font-semibold">{formatPrice(feesTotal)} {currency}</span>
                  </div>
                )}
                
                {taxTotal > 0 && (
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 py-2">
                    <span className="font-medium">{t('tax')}</span>
                    <span className="font-semibold">{formatPrice(taxTotal)} {currency}</span>
                  </div>
                )}
                
                <div className="border-t border-gray-200/50 dark:border-gray-700/50 pt-4 mt-4">
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-bold text-gray-900 dark:text-white">{t('total')}</span>
                    <motion.span 
                      className="text-xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.2 }}
                    >
                      {formatPrice(grandTotal)} {currency}
                    </motion.span>
                  </div>
                </div>
              </motion.div>
              
              <motion.div
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.6 }}
              >
                <Button
                  onClick={handleCheckout}
                  disabled={totalItems === 0 || isRefreshing}
                  className="w-full bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white py-3 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-glow"
                >
                  {isRefreshing ? t('processing') : t('proceedToCheckout')}
                  <motion.div
                    animate={{ x: [0, 4, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 2 }}
                  >
                    <ArrowRight className="h-5 w-5" />
                  </motion.div>
                </Button>
              </motion.div>
              
              {!isAuthenticated && (
                <motion.p 
                  className="text-sm text-gray-500 dark:text-gray-400 text-center mt-4 flex items-center justify-center gap-1"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.3, delay: 0.7 }}
                >
                  <AlertCircle className="h-4 w-4" />
                  {t('loginRequiredForCheckout')}
                </motion.p>
              )}
            </motion.div>
          </div>
        </div>

        {/* Clear Cart Confirmation Modal */}
        <AnimatePresence>
          {showClearConfirm && (
            <motion.div 
              className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setShowClearConfirm(false)}
            >
              <motion.div 
                className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl p-6 max-w-md w-full shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50"
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                transition={{ duration: 0.3 }}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center gap-3 mb-4">
                  <motion.div 
                    className="h-12 w-12 bg-gradient-to-br from-red-100 to-red-200 dark:from-red-900/20 dark:to-red-800/20 rounded-full flex items-center justify-center border border-red-200/50 dark:border-red-700/50"
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <AlertCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
                  </motion.div>
                  <h3 className="text-lg font-semibold bg-gradient-to-r from-red-600 to-red-700 bg-clip-text text-transparent">
                    {t('clearCartConfirmTitle')}
                  </h3>
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                  {t('clearCartConfirmMessage')}
                </p>
                
                <div className="flex flex-col sm:flex-row gap-3 justify-end">
                  <motion.div
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex-1 sm:flex-none"
                  >
                    <Button
                      onClick={() => setShowClearConfirm(false)}
                      variant="outline"
                      className="w-full sm:w-auto bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-600/50 text-gray-700 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-800 px-6 py-2 rounded-xl font-medium transition-all duration-300"
                    >
                      {t('cancel')}
                    </Button>
                  </motion.div>
                  
                  <motion.div
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex-1 sm:flex-none"
                  >
                    <Button
                      onClick={handleClearCart}
                      variant="destructive"
                      disabled={isRefreshing}
                      className="w-full sm:w-auto bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-6 py-2 rounded-xl font-medium transition-all duration-300 shadow-lg hover:shadow-glow"
                    >
                      {isRefreshing ? t('clearing') : t('clearCart')}
                    </Button>
                  </motion.div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
} 