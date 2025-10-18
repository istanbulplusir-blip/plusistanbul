// UI Constants for Transfers Booking System
// This file contains consistent Tailwind CSS classes for the entire transfers booking system

export const UI_CLASSES = {
  // Layout & Containers
  container: 'space-y-6',
  card: 'bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6',
  cardLarge: 'bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8',
  cardSticky: 'bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 sticky top-8',
  
  // Headers
  pageHeader: 'bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6',
  sectionHeader: 'bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6',
  
  // Typography
  title: 'text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2',
  subtitle: 'text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2',
  sectionTitle: 'text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4',
  description: 'text-gray-600 dark:text-gray-400',
  smallText: 'text-sm text-gray-600 dark:text-gray-400',
  caption: 'text-xs text-gray-500 dark:text-gray-400',
  
  // Buttons
  buttonPrimary: 'px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2',
  buttonSecondary: 'px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2',
  buttonSmall: 'px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors',
  buttonDisabled: 'px-6 py-3 bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 rounded-lg cursor-not-allowed flex items-center gap-2',
  
  // Form Elements
  input: 'w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100',
  label: 'block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2',
  select: 'w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100',
  
  // Status & Badges
  badgeSuccess: 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200',
  badgeWarning: 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200',
  badgeInfo: 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200',
  badgeError: 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200',
  badgePurple: 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200',
  
  // Grid & Layout
  grid1: 'grid grid-cols-1 gap-4',
  grid2: 'grid grid-cols-1 md:grid-cols-2 gap-4',
  grid3: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4',
  
  // Spacing
  spaceY: 'space-y-4',
  spaceY6: 'space-y-6',
  spaceY8: 'space-y-8',
  
  // Borders & Dividers
  borderTop: 'border-t border-gray-200 dark:border-gray-600',
  borderBottom: 'border-b border-gray-200 dark:border-gray-600',
  
  // Interactive Elements
  cardInteractive: 'p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md',
  cardSelected: 'border-blue-500 bg-blue-50 dark:bg-blue-900/20',
  cardUnselected: 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-700',
  
  // Loading & States
  loadingSpinner: 'animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 dark:border-blue-400 mx-auto',
  loadingSpinnerSmall: 'animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 dark:border-blue-400',
  
  // Icons
  iconLarge: 'w-16 h-16',
  iconMedium: 'w-8 h-8',
  iconSmall: 'w-4 h-4',
  iconTiny: 'w-5 h-5',
  
  // Colors
  textPrimary: 'text-gray-900 dark:text-gray-100',
  textSecondary: 'text-gray-600 dark:text-gray-400',
  textMuted: 'text-gray-500 dark:text-gray-400',
  textAccent: 'text-blue-600 dark:text-blue-400',
  
  // Backgrounds
  bgPrimary: 'bg-white dark:bg-gray-800',
  bgSecondary: 'bg-gray-50 dark:bg-gray-700',
  bgAccent: 'bg-blue-50 dark:bg-blue-900/20',
  bgSuccess: 'bg-green-50 dark:bg-green-900/20',
  bgWarning: 'bg-orange-50 dark:bg-orange-900/20',
  bgError: 'bg-red-50 dark:bg-red-900/20',
  
  // Shadows
  shadow: 'shadow-sm',
  shadowHover: 'hover:shadow-md',
  
  // Transitions
  transition: 'transition-colors',
  transitionAll: 'transition-all',
  
  // Flexbox
  flexCenter: 'flex items-center justify-center',
  flexBetween: 'flex items-center justify-between',
  flexStart: 'flex items-start',
  flexEnd: 'flex items-end',
  
  // Text Alignment
  textCenter: 'text-center',
  textLeft: 'text-left',
  textRight: 'text-right',
  
  // Margins & Padding
  marginTop: 'mt-4',
  marginBottom: 'mb-4',
  marginTopLarge: 'mt-8',
  marginBottomLarge: 'mb-8',
  padding: 'p-4',
  paddingLarge: 'p-6',
  paddingExtraLarge: 'p-8',
} as const;

// Specific component classes
export const COMPONENT_CLASSES = {
  // Route Selection
  routeCard: `${UI_CLASSES.cardInteractive} ${UI_CLASSES.cardUnselected}`,
  routeCardSelected: `${UI_CLASSES.cardInteractive} ${UI_CLASSES.cardSelected}`,
  
  // Vehicle Selection
  vehicleCard: `${UI_CLASSES.cardInteractive} ${UI_CLASSES.cardUnselected}`,
  vehicleCardSelected: `${UI_CLASSES.cardInteractive} ${UI_CLASSES.cardSelected}`,
  
  // Form Sections
  formSection: `${UI_CLASSES.card} ${UI_CLASSES.spaceY6}`,
  formField: `${UI_CLASSES.spaceY}`,
  
  // Navigation
  navigationContainer: `${UI_CLASSES.card} ${UI_CLASSES.flexBetween}`,
  
  // Summary
  summaryContainer: `${UI_CLASSES.cardSticky}`,
  summarySection: `${UI_CLASSES.spaceY} ${UI_CLASSES.borderBottom} pb-4`,
  
  // Error States
  errorContainer: 'bg-red-50 border border-red-200 rounded-lg p-4',
  errorText: 'text-red-700',
  
  // Success States
  successContainer: 'bg-green-50 border border-green-200 rounded-lg p-4',
  successText: 'text-green-700',
  
  // Info States
  infoContainer: 'bg-blue-50 border border-blue-200 rounded-lg p-4',
  infoText: 'text-blue-700',
} as const;

// Responsive breakpoints
export const RESPONSIVE = {
  mobile: 'sm:',
  tablet: 'md:',
  desktop: 'lg:',
  large: 'xl:',
} as const;

// Animation classes
export const ANIMATIONS = {
  fadeIn: 'animate-fade-in',
  slideIn: 'animate-slide-in',
  slideUp: 'animate-slide-up',
  scaleIn: 'animate-scale-in',
} as const;
