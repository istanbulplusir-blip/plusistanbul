'use client'

import { useState, useEffect } from 'react'
import { FaChevronDown } from 'react-icons/fa'
import { useFAQ } from '../../hooks/useFAQ'
import { FAQ } from '../../types/faq'
import { useTranslations } from 'next-intl'
import { getFAQSettings, FAQSettings } from '@/lib/api/shared'

export default function FAQSection() {
  const t = useTranslations('home')
  const { faqs, loading, error, categories, selectedCategory, setSelectedCategory } = useFAQ()
  const [isRTL, setIsRTL] = useState(false)

  // API state for FAQ settings
  const [faqSettings, setFaqSettings] = useState<FAQSettings | null>(null)
  const [, setSettingsLoading] = useState(true)
  
  // Detect RTL language
  useEffect(() => {
    const htmlDir = document.documentElement.dir
    setIsRTL(htmlDir === 'rtl')
  }, [])

  // Fetch FAQ settings from API
  useEffect(() => {
    const fetchFAQSettings = async () => {
      try {
        setSettingsLoading(true)
        const settings = await getFAQSettings()
        setFaqSettings(settings)
      } catch (err) {
        console.error('Error fetching FAQ settings:', err)
      } finally {
        setSettingsLoading(false)
      }
    }

    fetchFAQSettings()
  }, [])
  const [activeAccordion, setActiveAccordion] = useState<string>('')
  const [showMoreFAQs, setShowMoreFAQs] = useState<Record<string, boolean>>({})
  const [showAllCategories, setShowAllCategories] = useState(false)
  const [showCategoriesSection, setShowCategoriesSection] = useState(false)

  
  const initialCount = 5
  const expandedCount = 10
  
  const getFAQsByCategory = (category: string | null) => {
    if (!category) return faqs
    return faqs.filter(faq => faq.category === category)
  }
  
  const getVisibleFAQs = (category: string | null) => {
    const categoryFAQs = getFAQsByCategory(category)
    const isExpanded = category ? showMoreFAQs[category] : false
    return isExpanded ? categoryFAQs.slice(0, expandedCount) : categoryFAQs.slice(0, initialCount)
  }
  
  const hasMoreFAQs = (category: string | null) => {
    const categoryFAQs = getFAQsByCategory(category)
    return categoryFAQs.length > initialCount
  }
  
  const canShowMore = (category: string | null) => {
    const categoryFAQs = getFAQsByCategory(category)
    return categoryFAQs.length > expandedCount
  }

  const toggleAccordion = (id: string) => {
    setActiveAccordion(activeAccordion === id ? '' : id)
  }

  const handleCategoryChange = (category: string | null) => {
    setSelectedCategory(category)
    setActiveAccordion('')
    setShowMoreFAQs({})
  }
  
  const toggleAllCategories = () => {
    setShowAllCategories(!showAllCategories)
  }
  
  const toggleCategoriesSection = () => {
    setShowCategoriesSection(!showCategoriesSection)
    // Reset other states when toggling categories section
    if (!showCategoriesSection) {
      setShowAllCategories(false)
    }
  }
  
  const toggleShowMoreFAQs = (category: string | null) => {
    if (!category) return
    
    setShowMoreFAQs(prev => ({
      ...prev,
      [category]: !prev[category]
    }))
  }
  
  const getCategoryInfo = (category: string) => {
    const categoryFAQs = faqs.filter(faq => faq.category === category)
    
    return {
      totalCount: categoryFAQs.length
    }
  }



  return (
    <section className="relative py-12 sm:py-16 lg:py-20 overflow-hidden">
      {/* Background - Modern gradient matching hero */}
      <div className="absolute inset-0 bg-gradient-to-br from-secondary-50/80 via-white to-primary-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900" />

      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(8)].map((_, i) => {
          // Deterministic positions for SSR consistency
          const positions = [
            { left: 69.54, top: 69.70 },
            { left: 7.79, top: 34.92 },
            { left: 15.06, top: 41.25 },
            { left: 23.23, top: 63.42 },
            { left: 60.79, top: 88.71 },
            { left: 41.47, top: 25.53 },
            { left: 66.41, top: 10.64 },
            { left: 10.81, top: 8.61 },
          ];

          const pos = positions[i] || { left: 50, top: 50 };

          return (
            <div
              key={i}
              className="absolute w-2 h-2 bg-primary-400/30 rounded-full animate-pulse"
              style={{
                left: `${pos.left}%`,
                top: `${pos.top}%`,
                animationDelay: `${(i * 0.625) % 5}s`,
                animationDuration: `${5 + (i * 0.25) % 2}s`,
              }}
            />
          );
        })}
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
                 {/* Header Section - Modern design */}
         <div className="text-center mb-12 sm:mb-16">
           {/* Badge with modern styling */}
           <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-primary-500/10 to-secondary-500/10 backdrop-blur-sm rounded-full border border-primary-200/50 dark:border-primary-700/50 mb-4">
             <span className="text-sm uppercase tracking-wider text-primary-600 dark:text-primary-400 font-semibold">
               Frequently Asked Questions
             </span>
           </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            {faqSettings?.title || t('faqTitle') || 'Frequently Asked Questions'}
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            {faqSettings?.subtitle || t('faqSubtitle') || 'Find answers to common questions about our tours, events, and travel services.'}
          </p>
         </div>

                                 {/* Category Section */}
        {categories.length > 0 && (
          <div className="flex flex-col items-center gap-6 mb-12">
            {/* Categories Toggle Button */}
            <button
              onClick={toggleCategoriesSection}
              className="group flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-all duration-300 hover:scale-105 active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 rounded-lg"
              aria-expanded={showCategoriesSection}
              aria-controls="categories-section"
            >
              <span className="transition-transform duration-300 group-hover:scale-110">
                {showCategoriesSection ? (
                  <>
                    <span className="hidden sm:inline">{t('faqHideCategories')}</span>
                    <span className="sm:hidden">{t('faqHide')}</span>
                    <span className="ml-1">({categories.length})</span>
                  </>
                ) : (
                  <>
                    <span className="hidden sm:inline">{t('faqShowCategories')}</span>
                    <span className="sm:hidden">{t('faqCategories')}</span>
                    <span className="ml-1">({categories.length})</span>
                  </>
                )}
              </span>
              <svg
                className={`w-4 h-4 transition-transform duration-300 ${
                  showCategoriesSection ? 'rotate-180' : 'rotate-0'
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Categories Content (Collapsible) */}
            <div className={`overflow-hidden transition-all duration-500 ease-in-out w-full ${
              showCategoriesSection ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
            }`} id="categories-section">
              <nav className="flex flex-col items-center gap-6" role="tablist" aria-label="FAQ categories">
                {/* Visible Categories */}
                <div className="flex flex-wrap justify-center gap-4">
                  {categories.slice(0, 4).map((category, index) => {
                    const categoryInfo = getCategoryInfo(category)
                    const isSelected = selectedCategory === category
                    
                    return (
                      <button
                        key={`${category}-${index}`}
                        onClick={() => handleCategoryChange(category)}
                        role="tab"
                        aria-selected={isSelected}
                        aria-controls={`category-${category}`}
                        className={`px-6 py-3 rounded-full font-semibold transition-all duration-500 hover:scale-105 active:scale-95 backdrop-blur-md border focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 ${
                          isSelected
                            ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg shadow-primary-500/50 border-primary-400'
                            : 'bg-white/20 dark:bg-gray-700/20 text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 border-white/30 dark:border-gray-600/30'
                        } animate-fade-in-up`}
                        style={{ animationDelay: `${0.3 + index * 0.1}s` }}
                      >
                        {category} ({categoryInfo.totalCount})
                      </button>
                    )
                  })}
                </div>

                {/* Hidden Categories (Collapsible) */}
                {categories.length > 4 && (
                  <div className={`overflow-hidden transition-all duration-500 ease-in-out ${
                    showAllCategories ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
                  }`}>
                    <div className="flex flex-wrap justify-center gap-4 pt-4">
                      {categories.slice(4).map((category, index) => {
                        const categoryInfo = getCategoryInfo(category)
                        const isSelected = selectedCategory === category
                        
                        return (
                          <button
                            key={`${category}-${index + 4}`}
                            onClick={() => handleCategoryChange(category)}
                            role="tab"
                            aria-selected={isSelected}
                            aria-controls={`category-${category}`}
                            className={`px-6 py-3 rounded-full font-semibold transition-all duration-500 hover:scale-105 active:scale-95 border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 ${
                              isSelected
                                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50 border-blue-400'
                                : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600 border-gray-200 dark:border-gray-600'
                            } animate-fade-in-up`}
                            style={{ animationDelay: `${0.1}s` }}
                          >
                            {category} ({categoryInfo.totalCount})
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}

                {/* Show More Categories Button */}
                {categories.length > 4 && (
                  <button
                    onClick={toggleAllCategories}
                    className="group flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-all duration-300 hover:scale-105 active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 rounded-lg"
                    aria-expanded={showAllCategories}
                    aria-controls="hidden-categories"
                  >
                    <span className="transition-transform duration-300 group-hover:scale-110">
                      {showAllCategories ? (
                        <>
                          <span className="hidden sm:inline">{t('faqHide')}</span>
                          <span className="sm:hidden">{t('faqHide')}</span>
                          <span className="ml-1">({categories.length - 4})</span>
                        </>
                      ) : (
                        <>
                          <span className="hidden sm:inline">{t('faqShow')}</span>
                          <span className="sm:hidden">{t('faqShow')}</span>
                          <span className="ml-1">+{categories.length - 4} {t('faqMore')}</span>
                        </>
                      )}
                    </span>
                    <svg
                      className={`w-4 h-4 transition-transform duration-300 ${
                        showAllCategories ? 'rotate-180' : 'rotate-0'
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                )}
              </nav>
            </div>
          </div>
        )}

        {/* FAQ Content */}
        <div className="max-w-4xl mx-auto">
                     {/* Loading State */}
           {loading && (
             <div className="text-center py-8 sm:py-12">
               <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
                 <span className="text-2xl sm:text-3xl">❓</span>
               </div>
               <p className="text-gray-500 dark:text-gray-400 text-base sm:text-lg">
                 {t('faqLoading')}
               </p>
             </div>
           )}

           {/* Error State */}
           {error && (
             <div className="text-center py-8 sm:py-12">
               <div className="w-16 h-16 sm:w-20 sm:h-20 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
                 <span className="text-2xl sm:text-3xl">⚠️</span>
               </div>
               <p className="text-red-500 dark:text-red-400 text-base sm:text-lg">
                 {error}
               </p>
             </div>
           )}

           {/* No FAQs State */}
           {!loading && !error && faqs.length === 0 && (
             <div className="text-center py-8 sm:py-12">
               <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
                 <span className="text-2xl sm:text-3xl">❓</span>
               </div>
               <p className="text-gray-500 dark:text-gray-400 text-base sm:text-lg">
                 {selectedCategory 
                   ? t('faqNoQuestionsInCategory', { category: selectedCategory })
                   : t('faqNoQuestions')
                 }
               </p>
             </div>
           )}

          {/* FAQ Content */}
          {!loading && !error && faqs.length > 0 && (
            <div>
                             {/* Category Header */}
               {selectedCategory && (
                 <div className="bg-gradient-to-r from-primary-50/20 to-secondary-50/20 dark:from-primary-900/20 dark:to-secondary-900/20 border border-primary-200/50 dark:border-primary-700/50 rounded-2xl p-4 sm:p-6 shadow-lg mb-6 sm:mb-8 backdrop-blur-sm">
                   <div className={`flex items-center justify-between ${
                     isRTL ? 'flex-row-reverse' : 'flex-row'
                   }`}>
                     <div className={`flex items-center gap-2 sm:gap-3 ${
                       isRTL ? 'flex-row-reverse' : 'flex-row'
                     }`}>
                       <div className="w-8 h-8 sm:w-10 sm:h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center">
                         <span className="text-indigo-600 dark:text-indigo-400 text-base sm:text-lg">📂</span>
                       </div>
                       <div className={isRTL ? 'text-right' : 'text-left'}>
                         <h3 className="text-lg sm:text-xl font-bold text-indigo-900 dark:text-indigo-100">
                           {t('faqCategoryHeader', { category: selectedCategory })}
                         </h3>
                         <p className="text-indigo-700 dark:text-indigo-300 text-xs sm:text-sm">
                           {t('faqCategorySubtitle')}
                         </p>
                       </div>
                     </div>
                     <span className="bg-indigo-600 text-white px-3 sm:px-4 py-1 sm:py-2 rounded-full text-xs sm:text-sm font-semibold">
                       {getFAQsByCategory(selectedCategory).length} {t('faqQuestions')}
                     </span>
                   </div>
                 </div>
               )}
              
              {/* Visible FAQs */}
              <div className="space-y-4">
                {getVisibleFAQs(selectedCategory).map((faq: FAQ) => (
                  <div
                    key={faq.id}
                    className="bg-white/20 dark:bg-gray-800/20 backdrop-blur-md rounded-2xl shadow-lg border border-white/30 dark:border-gray-700/30 overflow-hidden hover:shadow-xl hover:shadow-primary-500/25 transition-all duration-300 transform hover:scale-[1.01]"
                  >
                                         <button
                       onClick={() => toggleAccordion(faq.id)}
                       className={`w-full px-4 sm:px-6 lg:px-8 py-4 sm:py-6 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-300 group ${
                         isRTL ? 'flex-row-reverse' : 'flex-row'
                       }`}
                     >
                       <div className={`flex-1 ${isRTL ? 'text-right pr-2 sm:pr-4 lg:pr-8' : 'text-left pl-2 sm:pl-4 lg:pl-8'}`}>
                         <h4 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors duration-300">
                           {faq.question}
                         </h4>
                         <div className={`flex items-center gap-2 text-xs sm:text-sm text-gray-500 dark:text-gray-400 ${
                           isRTL ? 'flex-row-reverse' : 'flex-row'
                         }`}>
                           <span className="w-2 h-2 bg-primary-400 rounded-full"></span>
                           <span>{t('faqClickToView')}</span>
                         </div>
                       </div>
                                                                        <div className={`flex-shrink-0 ${isRTL ? 'ml-2 sm:ml-4 lg:ml-6' : 'mr-2 sm:mr-4 lg:mr-6'}`}>
                           <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 rounded-full flex items-center justify-center shadow-lg border border-primary-400 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25">
                             <FaChevronDown
                               className={`w-5 h-5 text-white transition-all duration-300 ${
                                 activeAccordion === faq.id ? 'rotate-180' : ''
                               }`}
                             />
                           </div>
                         </div>
                    </button>
                    
                                         <div
                       className={`overflow-hidden transition-all duration-500 ease-in-out ${
                         activeAccordion === faq.id ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
                       }`}
                     >
                       <div className={`px-4 sm:px-6 lg:px-8 pb-4 sm:pb-6 border-t border-gray-100 dark:border-gray-700`}>
                         <div className="pt-4 sm:pt-6">
                           <div className={`flex items-start gap-2 sm:gap-3 ${
                             isRTL ? 'flex-row-reverse' : 'flex-row'
                           }`}>
                             <div className={`w-5 h-5 sm:w-6 sm:h-6 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center flex-shrink-0 mt-1 ${
                               isRTL ? 'ml-2 sm:ml-3' : 'mr-2 sm:mr-3'
                             }`}>
                               <span className="text-green-600 dark:text-green-400 text-xs sm:text-sm">✓</span>
                             </div>
                             <p className={`text-gray-700 dark:text-gray-300 leading-relaxed text-sm sm:text-base ${
                               isRTL ? 'text-right' : 'text-left'
                             }`}>
                               {faq.answer}
                             </p>
                           </div>
                         </div>
                       </div>
                     </div>
                  </div>
                ))}
              </div>
              
                             {/* Show More/Less Button */}
               {hasMoreFAQs(selectedCategory) && (
                 <div className="text-center pt-6 sm:pt-8">
                                       <button
                      onClick={() => toggleShowMoreFAQs(selectedCategory)}
                      className="inline-flex items-center px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white font-semibold rounded-lg transition-all duration-300 hover:scale-105 active:scale-95 shadow-lg shadow-primary-500/50 hover:shadow-primary-600/50 border border-primary-400/50 backdrop-blur-md text-sm sm:text-base"
                    >
                     {showMoreFAQs[selectedCategory || ''] ? (
                       <>
                         <span>{t('faqShowLess')}</span>
                         <FaChevronDown className={`w-4 h-4 sm:w-5 sm:h-5 transform rotate-180 ${
                           isRTL ? 'ml-2 sm:ml-3' : 'mr-2 sm:mr-3'
                         }`} />
                       </>
                     ) : (
                       <>
                         <span>{t('faqShowMoreQuestions', { count: Math.min(getFAQsByCategory(selectedCategory).length - initialCount, expandedCount - initialCount) })}</span>
                         <FaChevronDown className={`w-4 h-4 sm:w-5 sm:h-5 ${
                           isRTL ? 'ml-2 sm:ml-3' : 'mr-2 sm:mr-3'
                         }`} />
                       </>
                     )}
                   </button>
                   
                   {/* FAQ Count Info */}
                   <div className="mt-3 sm:mt-4 text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                     <span className="bg-gray-100 dark:bg-gray-700 px-2 sm:px-3 py-1 sm:py-2 rounded-full">
                       {t('faqDisplaying', { visible: getVisibleFAQs(selectedCategory).length, total: getFAQsByCategory(selectedCategory).length })}
                     </span>
                     {canShowMore(selectedCategory) && showMoreFAQs[selectedCategory || ''] && (
                       <div className="mt-1 sm:mt-2 text-xs text-gray-400 dark:text-gray-500">
                         {t('faqMaxDisplayed', { max: expandedCount })}
                       </div>
                     )}
                   </div>
                 </div>
               )}
            </div>
          )}
        </div>
      </div>
    </section>
  )
} 