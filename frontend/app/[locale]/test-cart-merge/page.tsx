'use client';

import React, { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
// import { useTranslations } from 'next-intl';
import { useAuth } from '../../../lib/contexts/AuthContext';
import { useCart } from '../../../lib/hooks/useCart';
import { useCustomerData } from '../../../lib/hooks/useCustomerData';
import { Button } from '@/components/ui/Button';
import { 
  ShoppingCart, 
  User, 
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';

export default function TestCartMergePage() {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  // const t = useTranslations('test');
  
  const { user, isAuthenticated } = useAuth();
  const { items, totalItems, refreshCart } = useCart();
  const { customerData, getGuestSessionInfo, logCartMergeAttempt } = useCustomerData();
  
  const [testResults, setTestResults] = useState<Array<{
    test: string;
    status: 'success' | 'error';
    data: unknown;
    message: string;
  }>>([]);
  const [isRunningTest, setIsRunningTest] = useState(false);

  const runCartMergeTest = async () => {
    setIsRunningTest(true);
    setTestResults([]);
    
    const results = [];
    
    // Test 1: Guest Session Info
    try {
      const sessionInfo = getGuestSessionInfo();
      results.push({
        test: 'Guest Session Info',
        status: 'success' as const,
        data: sessionInfo,
        message: 'Session info retrieved successfully'
      });
    } catch (error) {
      results.push({
        test: 'Guest Session Info',
        status: 'error' as const,
        data: null,
        message: `Error: ${error}`
      });
    }
    
    // Test 2: Customer Data Loading
    try {
      results.push({
        test: 'Customer Data Loading',
        status: 'success' as const,
        data: customerData,
        message: `Customer data loaded for ${isAuthenticated ? 'authenticated' : 'guest'} user`
      });
    } catch (error) {
      results.push({
        test: 'Customer Data Loading',
        status: 'error' as const,
        data: null,
        message: `Error: ${error}`
      });
    }
    
    // Test 3: Cart Merge Logging
    try {
      const sessionInfo = getGuestSessionInfo();
      logCartMergeAttempt(sessionInfo, true, 'Test merge attempt');
      results.push({
        test: 'Cart Merge Logging',
        status: 'success' as const,
        data: { sessionInfo, isAuthenticated },
        message: 'Cart merge attempt logged successfully'
      });
    } catch (error) {
      results.push({
        test: 'Cart Merge Logging',
        status: 'error' as const,
        data: null,
        message: `Error: ${error}`
      });
    }
    
    // Test 4: Cart Data
    try {
      await refreshCart();
      results.push({
        test: 'Cart Data',
        status: 'success' as const,
        data: { items: items.length, totalItems },
        message: `Cart has ${totalItems} items`
      });
    } catch (error) {
      results.push({
        test: 'Cart Data',
        status: 'error' as const,
        data: null,
        message: `Error: ${error}`
      });
    }
    
    setTestResults(results);
    setIsRunningTest(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            تست عملکرد مرج سبد خرید
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            این صفحه برای تست عملکرد مرج سبد خرید و همگام‌سازی داده‌های کاربر طراحی شده است.
          </p>
        </div>

        {/* User Status */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <User className="h-5 w-5" />
            وضعیت کاربر
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">وضعیت احراز هویت:</p>
              <p className={`font-medium ${isAuthenticated ? 'text-green-600' : 'text-yellow-600'}`}>
                {isAuthenticated ? 'احراز هویت شده' : 'کاربر مهمان'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">ایمیل:</p>
              <p className="font-medium text-gray-900 dark:text-white">
                {user?.email || 'نامشخص'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">تعداد آیتم‌های سبد:</p>
              <p className="font-medium text-gray-900 dark:text-white">
                {totalItems}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">داده‌های مشتری:</p>
              <p className="font-medium text-gray-900 dark:text-white">
                {customerData ? 'بارگذاری شده' : 'بارگذاری نشده'}
              </p>
            </div>
          </div>
        </div>

        {/* Test Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <ShoppingCart className="h-5 w-5" />
            اجرای تست‌ها
          </h2>
          <div className="flex gap-4">
            <Button
              onClick={runCartMergeTest}
              disabled={isRunningTest}
              className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg disabled:opacity-50"
            >
              {isRunningTest ? 'در حال اجرا...' : 'اجرای تست‌ها'}
            </Button>
            <Button
              onClick={() => router.push(`/${locale}/cart`)}
              variant="outline"
              className="px-6 py-2 rounded-lg"
            >
              مشاهده سبد خرید
            </Button>
          </div>
        </div>

        {/* Test Results */}
        {testResults.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              نتایج تست‌ها
            </h2>
            <div className="space-y-4">
              {testResults.map((result, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${
                    result.status === 'success'
                      ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                      : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {result.status === 'success' ? (
                      <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {result.test}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {result.message}
                      </p>
                      {result.data !== null && (
                        <pre className="text-xs bg-gray-100 dark:bg-gray-700 p-2 rounded mt-2 overflow-x-auto">
                          {JSON.stringify(result.data as Record<string, unknown>, null, 2)}
                        </pre>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-6 mt-8">
          <h2 className="text-xl font-semibold text-blue-900 dark:text-blue-100 mb-4 flex items-center gap-2">
            <Info className="h-5 w-5" />
            راهنمای تست
          </h2>
          <div className="space-y-2 text-blue-800 dark:text-blue-200">
            <p>1. به عنوان کاربر مهمان، محصولی به سبد اضافه کنید</p>
            <p>2. وارد شوید یا ثبت‌نام کنید</p>
            <p>3. به صفحه سبد خرید بروید و مرج سبد را بررسی کنید</p>
            <p>4. به صفحه چک‌اوت بروید و اطلاعات مشتری را بررسی کنید</p>
            <p>5. سفارش را تکمیل کنید و بررسی کنید که اطلاعات در پروفایل ذخیره شده</p>
          </div>
        </div>
      </div>
    </div>
  );
}
