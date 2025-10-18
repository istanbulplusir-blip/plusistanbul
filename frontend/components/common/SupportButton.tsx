'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageCircle } from 'lucide-react';
import { useTranslations } from 'next-intl';
import SupportModal from './SupportModal';

export default function SupportButton() {
  const t = useTranslations('support');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <>
      {/* Modern Floating WhatsApp Button */}
      <motion.button
        onClick={openModal}
        className="fixed bottom-6 right-6 z-40 w-16 h-16 bg-green-500 hover:bg-green-600 text-white rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center justify-center group"
        whileHover={{ scale: 1.1, y: -2 }}
        whileTap={{ scale: 0.95 }}
        initial={{ opacity: 0, scale: 0.8, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 1 }}
      >
        <MessageCircle className="w-7 h-7" />
        
        {/* Pulse Animation */}
        <motion.div
          className="absolute inset-0 bg-green-400 rounded-full"
          animate={{ scale: [1, 1.2, 1], opacity: [0.7, 0, 0.7] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
        
        {/* Tooltip */}
        <motion.div
          className="absolute right-20 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-sm px-3 py-2 rounded-lg whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-300 shadow-lg"
          initial={{ opacity: 0, x: 10 }}
          whileHover={{ opacity: 1, x: 0 }}
        >
          {t('buttonTooltip')}
          <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-gray-900 transform rotate-45 translate-x-1"></div>
        </motion.div>
      </motion.button>

      {/* Modern Chat Popup Modal */}
      <SupportModal isOpen={isModalOpen} onClose={closeModal} />
    </>
  );
}
