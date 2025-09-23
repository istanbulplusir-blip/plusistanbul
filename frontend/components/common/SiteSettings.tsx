'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Image from 'next/image'
import { FaCog, FaGlobe, FaPhone, FaEnvelope, FaImage, FaTools, FaSearch } from 'react-icons/fa'
import { getSiteSettings, SiteSettings as SiteSettingsType } from '@/lib/api/shared'

export default function SiteSettingsDisplay() {
  const [settings, setSettings] = useState<SiteSettingsType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true)
        const data = await getSiteSettings()
        setSettings(data)
        console.log('Fetched site settings:', data)
      } catch (err) {
        console.error('Error fetching site settings:', err)
        setError('Failed to load site settings')
      } finally {
        setLoading(false)
      }
    }

    fetchSettings()
  }, [])

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error || !settings) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="text-center text-red-600 dark:text-red-400">
          <FaCog className="mx-auto mb-2 text-2xl" />
          {error || 'No site settings available'}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
          <FaCog className="text-blue-600 dark:text-blue-400 text-xl" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Site Settings
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Global configuration from backend
          </p>
        </div>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Basic Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-4 rounded-lg"
        >
          <div className="flex items-center gap-2 mb-2">
            <FaGlobe className="text-blue-600 dark:text-blue-400" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Site Name
            </span>
          </div>
          <div className="text-lg font-semibold text-gray-900 dark:text-white">
            {settings.site_name}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 p-4 rounded-lg"
        >
          <div className="flex items-center gap-2 mb-2">
            <FaGlobe className="text-green-600 dark:text-green-400" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Default Language
            </span>
          </div>
          <div className="text-lg font-semibold text-gray-900 dark:text-white uppercase">
            {settings.default_language}
          </div>
        </motion.div>

        {/* Contact Info */}
        {settings.default_phone && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 p-4 rounded-lg"
          >
            <div className="flex items-center gap-2 mb-2">
              <FaPhone className="text-purple-600 dark:text-purple-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Default Phone
              </span>
            </div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white font-mono">
              {settings.default_phone}
            </div>
          </motion.div>
        )}

        {settings.default_email && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-br from-pink-50 to-pink-100 dark:from-pink-900/20 dark:to-pink-800/20 p-4 rounded-lg"
          >
            <div className="flex items-center gap-2 mb-2">
              <FaEnvelope className="text-pink-600 dark:text-pink-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Default Email
              </span>
            </div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white break-all">
              {settings.default_email}
            </div>
          </motion.div>
        )}

        {/* Maintenance Mode */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className={`p-4 rounded-lg ${
            settings.maintenance_mode
              ? 'bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20'
              : 'bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20'
          }`}
        >
          <div className="flex items-center gap-2 mb-2">
            <FaTools className={`${
              settings.maintenance_mode
                ? 'text-red-600 dark:text-red-400'
                : 'text-green-600 dark:text-green-400'
            }`} />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Maintenance Mode
            </span>
          </div>
          <div className={`text-lg font-semibold ${
            settings.maintenance_mode
              ? 'text-red-600 dark:text-red-400'
              : 'text-green-600 dark:text-green-400'
          }`}>
            {settings.maintenance_mode ? 'ENABLED' : 'DISABLED'}
          </div>
          {settings.maintenance_mode && settings.maintenance_message && (
              <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              &ldquo;{settings.maintenance_message}&rdquo;
            </div>
          )}
        </motion.div>

        {/* SEO Defaults */}
        {(settings.default_meta_title || settings.default_meta_description) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900/20 dark:to-indigo-800/20 p-4 rounded-lg md:col-span-2"
          >
            <div className="flex items-center gap-2 mb-2">
              <FaSearch className="text-indigo-600 dark:text-indigo-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                SEO Defaults
              </span>
            </div>
            {settings.default_meta_title && (
              <div className="mb-2">
                <div className="text-sm text-gray-600 dark:text-gray-400">Title:</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {settings.default_meta_title}
                </div>
              </div>
            )}
            {settings.default_meta_description && (
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Description:</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {settings.default_meta_description}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Default Images */}
      {(settings.default_hero_image || settings.default_tour_image || settings.default_event_image) && (
        <div className="mt-6">
          <h4 className="font-medium text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <FaImage className="text-gray-600 dark:text-gray-400" />
            Default Images
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {settings.default_hero_image && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 }}
                className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg text-center"
              >
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Hero Image
                </div>
                <Image
                  src={settings.default_hero_image_url || '/media/defaults/no-image.png'}
                  alt="Default Hero"
                  width={300}
                  height={80}
                  className="w-full h-20 object-cover rounded"
                />
              </motion.div>
            )}

            {settings.default_tour_image && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7 }}
                className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg text-center"
              >
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tour Image
                </div>
                <Image
                  src={settings.default_tour_image_url || '/media/defaults/tour-default.png'}
                  alt="Default Tour"
                  width={300}
                  height={80}
                  className="w-full h-20 object-cover rounded"
                />
              </motion.div>
            )}

            {settings.default_event_image && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8 }}
                className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg text-center"
              >
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Event Image
                </div>
                <Image
                  src={settings.default_event_image_url || '/media/defaults/event-default.png'}
                  alt="Default Event"
                  width={300}
                  height={80}
                  className="w-full h-20 object-cover rounded"
                />
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* Description */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Description:</strong> {settings.site_description}
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-500 mt-2">
          Last updated: {new Date(settings.updated_at).toLocaleString()}
        </div>
      </div>
    </div>
  )
}
