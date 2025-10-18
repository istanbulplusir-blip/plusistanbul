// Design System - Breakpoint Tokens
export const breakpoints = {
  // Mobile-first breakpoints
  sm: '640px',   // Small devices (phones)
  md: '768px',   // Medium devices (tablets)
  lg: '1024px',  // Large devices (laptops)
  xl: '1280px',  // Extra large devices (desktops)
  '2xl': '1536px', // 2X large devices (large desktops)
  
  // Custom breakpoints for specific use cases
  mobile: '480px',    // Mobile phones
  tablet: '768px',    // Tablets
  laptop: '1024px',   // Laptops
  desktop: '1280px',  // Desktops
  wide: '1536px',     // Wide screens
  
  // Orientation breakpoints
  portrait: 'orientation: portrait',
  landscape: 'orientation: landscape',
  
  // Device-specific breakpoints
  device: {
    mobile: {
      min: '320px',
      max: '767px',
    },
    tablet: {
      min: '768px',
      max: '1023px',
    },
    desktop: {
      min: '1024px',
      max: '1279px',
    },
    wide: {
      min: '1280px',
      max: '1535px',
    },
    ultra: {
      min: '1536px',
    },
  },
  
  // Content breakpoints (for optimal reading)
  content: {
    narrow: '640px',   // Narrow content (mobile)
    standard: '768px', // Standard content (tablet)
    wide: '1024px',    // Wide content (desktop)
    full: '1280px',    // Full width content
  },
} as const;

export type BreakpointToken = typeof breakpoints;

// Utility functions for responsive design
export const responsive = {
  // Mobile-first media queries
  up: (breakpoint: keyof typeof breakpoints) => 
    `@media (min-width: ${breakpoints[breakpoint]})`,
  
  down: (breakpoint: keyof typeof breakpoints) => 
    `@media (max-width: ${breakpoints[breakpoint]})`,
  
  between: (min: keyof typeof breakpoints, max: keyof typeof breakpoints) => 
    `@media (min-width: ${breakpoints[min]}) and (max-width: ${breakpoints[max]})`,
  
  // Device-specific queries
  mobile: `@media (max-width: ${breakpoints.sm})`,
  tablet: `@media (min-width: ${breakpoints.md}) and (max-width: ${breakpoints.lg})`,
  desktop: `@media (min-width: ${breakpoints.lg})`,
  
  // Orientation queries
  portrait: `@media (orientation: portrait)`,
  landscape: `@media (orientation: landscape)`,
  
  // High DPI displays
  retina: `@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)`,
  
  // Reduced motion
  reducedMotion: `@media (prefers-reduced-motion: reduce)`,
  
  // Dark mode preference
  darkMode: `@media (prefers-color-scheme: dark)`,
  
  // Print styles
  print: `@media print`,
} as const; 