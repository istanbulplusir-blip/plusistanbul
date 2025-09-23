'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FaImage, FaCheckCircle, FaClock, FaExclamationTriangle } from 'react-icons/fa'

interface ImageOptimizationRecord {
  id: string
  image_type: string
  original_size: number
  optimized_size_desktop: number
  optimized_size_tablet: number
  optimized_size_mobile: number
  optimization_completed: boolean
  compression_ratio: number
  created_at: string
}

export default function ImageOptimizationStats() {
  const [stats, setStats] = useState<ImageOptimizationRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const response = await fetch('http://localhost:8000/api/v1/shared/image-optimization/')
        if (!response.ok) {
          throw new Error('Failed to fetch image optimization stats')
        }
        const data = await response.json()
        setStats(data.results || [])
        console.log('Fetched image optimization stats:', data.results)
      } catch (err) {
        console.error('Error fetching image optimization stats:', err)
        setError('Failed to load image optimization statistics')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getImageTypeIcon = (type: string) => {
    switch (type) {
      case 'hero': return '🎠'
      case 'tour': return '🏔️'
      case 'event': return '🎭'
      case 'banner': return '📢'
      case 'gallery': return '🖼️'
      case 'profile': return '👤'
      default: return '🖼️'
    }
  }

  const getImageTypeLabel = (type: string) => {
    switch (type) {
      case 'hero': return 'Hero Images'
      case 'tour': return 'Tour Images'
      case 'event': return 'Event Images'
      case 'banner': return 'Banner Images'
      case 'gallery': return 'Gallery Images'
      case 'profile': return 'Profile Images'
      default: return type
    }
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="text-center text-red-600 dark:text-red-400">
          <FaExclamationTriangle className="mx-auto mb-2 text-2xl" />
          {error}
        </div>
      </div>
    )
  }

  const totalOptimizedSize = stats.reduce((sum, stat) =>
    sum + stat.optimized_size_desktop + stat.optimized_size_tablet + stat.optimized_size_mobile, 0
  )
  const averageCompression = stats.length > 0
    ? stats.reduce((sum, stat) => sum + Math.abs(stat.compression_ratio), 0) / stats.length
    : 0
  const completedCount = stats.filter(stat => stat.optimization_completed).length

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
          <FaImage className="text-blue-600 dark:text-blue-400 text-xl" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Image Optimization Statistics
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Real-time image compression analytics
          </p>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-4 rounded-lg"
        >
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {stats.length}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Total Images
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 p-4 rounded-lg"
        >
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {completedCount}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Optimized
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 p-4 rounded-lg"
        >
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {averageCompression.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Avg Compression
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 p-4 rounded-lg"
        >
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {formatBytes(totalOptimizedSize)}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Saved Space
          </div>
        </motion.div>
      </div>

      {/* Detailed Stats */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900 dark:text-white mb-3">
          Image Details
        </h4>

        {stats.map((stat, index) => (
          <motion.div
            key={stat.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
          >
            <div className="flex items-center gap-3">
              <div className="text-2xl">
                {getImageTypeIcon(stat.image_type)}
              </div>
              <div>
                <div className="font-medium text-gray-900 dark:text-white">
                  {getImageTypeLabel(stat.image_type)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Original: {formatBytes(stat.original_size)}
                </div>
              </div>
            </div>

            <div className="text-right">
              <div className="flex items-center gap-2">
                {stat.optimization_completed ? (
                  <FaCheckCircle className="text-green-500" />
                ) : (
                  <FaClock className="text-yellow-500" />
                )}
                <span className={`text-sm font-medium ${
                  stat.optimization_completed
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-yellow-600 dark:text-yellow-400'
                }`}>
                  {Math.abs(stat.compression_ratio).toFixed(1)}%
                </span>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {stat.optimization_completed ? 'Completed' : 'Processing'}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {stats.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <FaImage className="mx-auto mb-2 text-3xl opacity-50" />
          No image optimization data available
        </div>
      )}
    </div>
  )
}
