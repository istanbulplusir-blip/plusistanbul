import { Suspense } from 'react'
import Link from 'next/link'
import Banner from '../../../components/common/Banner'
import SiteSettings from '../../../components/common/SiteSettings'
import ImageOptimizationStats from '../../../components/common/ImageOptimizationStats'

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  )
}

export default function ContentDemoPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            🎉 Content Management System Demo
          </h1>
          <p className="text-xl opacity-90 max-w-3xl mx-auto">
            نمایش کامل سیستم مدیریت محتوای Peykan Tourism - همه داده‌ها از backend API دریافت می‌شود
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Hero Slides Section */}
        <section className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              🎠 Hero Slides from API
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              اسلایدرهای هیرو که از backend API دریافت می‌شوند
            </p>
          </div>
          <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-8 text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              اسلایدرهای هیرو در بخش Hero اصلی نمایش داده می‌شوند
            </p>
            <Link
              href="/"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              مشاهده در صفحه اصلی ←
            </Link>
          </div>
        </section>

        {/* Banners Section */}
        <section className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              📢 Dynamic Banners
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              بنرهای داینامیک با قابلیت targeting مختلف
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Homepage Top Banners */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                🏠 Homepage Top
              </h3>
              <Suspense fallback={<LoadingSpinner />}>
                <Banner position="top" page="home" />
              </Suspense>
            </div>

            {/* Homepage Bottom Banners */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                🏠 Homepage Bottom
              </h3>
              <Suspense fallback={<LoadingSpinner />}>
                <Banner position="bottom" page="home" />
              </Suspense>
            </div>

            {/* Sidebar Banners */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                📱 Sidebar
              </h3>
              <Suspense fallback={<LoadingSpinner />}>
                <Banner position="sidebar" page="home" />
              </Suspense>
            </div>

            {/* Tour Detail Banners */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                🏔️ Tour Detail
              </h3>
              <Suspense fallback={<LoadingSpinner />}>
                <Banner position="middle" page="tour" />
              </Suspense>
            </div>

            {/* Event Detail Banners */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                🎭 Event Detail
              </h3>
              <Suspense fallback={<LoadingSpinner />}>
                <Banner position="middle" page="event" />
              </Suspense>
            </div>

            {/* Seasonal Banners */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                ❄️ Seasonal
              </h3>
              <Suspense fallback={<LoadingSpinner />}>
                <Banner position="popup" page="seasonal" />
              </Suspense>
            </div>
          </div>
        </section>

        {/* Site Settings Section */}
        <section className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              ⚙️ Site Settings
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              تنظیمات کلی سایت از backend
            </p>
          </div>

          <Suspense fallback={<LoadingSpinner />}>
            <SiteSettings />
          </Suspense>
        </section>

        {/* Image Optimization Stats */}
        <section className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              📊 Image Optimization Analytics
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              آمار بهینه‌سازی تصاویر و compression ratios
            </p>
          </div>

          <Suspense fallback={<LoadingSpinner />}>
            <ImageOptimizationStats />
          </Suspense>
        </section>

        {/* API Endpoints Info */}
        <section className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              🌐 API Endpoints
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              لیست کامل APIهای استفاده شده
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                🎠 Hero Slides
              </h3>
              <div className="space-y-2 text-sm">
                <div className="font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  GET /api/v1/shared/hero-slides/active/
                </div>
                <div className="font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  POST /api/v1/shared/hero-slides/{'{id}'}/track_click/
                </div>
                <div className="font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  POST /api/v1/shared/hero-slides/{'{id}'}/track_view/
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                📢 Banners
              </h3>
              <div className="space-y-2 text-sm">
                <div className="font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  GET /api/v1/shared/banners/active/
                </div>
                <div className="font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  POST /api/v1/shared/banners/{'{id}'}/track_click/
                </div>
                <div className="font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  POST /api/v1/shared/banners/{'{id}'}/track_view/
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                ⚙️ Site Settings
              </h3>
              <div className="space-y-2 text-sm">
                <div className="font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  GET /api/v1/shared/site-settings/
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                📊 Image Optimization
              </h3>
              <div className="space-y-2 text-sm">
                <div className="font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  GET /api/v1/shared/image-optimization/
                </div>
                <div className="font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  POST /api/v1/shared/image-optimization/{'{id}'}/optimize/
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Navigation */}
        <section className="text-center mt-16">
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-8">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              🏠 بازگشت به صفحه اصلی
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              برای مشاهده اسلایدرهای هیرو و بنرها در صفحه اصلی کلیک کنید
            </p>
            <Link
              href="/"
              className="inline-flex items-center px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-lg font-semibold"
            >
              مشاهده صفحه اصلی ←
            </Link>
          </div>
        </section>
      </div>
    </div>
  )
}
