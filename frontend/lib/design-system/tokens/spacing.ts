// Design System - Spacing Tokens
export const spacing = {
  // Base spacing units (4px grid system)
  0: '0px',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
  32: '8rem',     // 128px
  40: '10rem',    // 160px
  48: '12rem',    // 192px
  56: '14rem',    // 224px
  64: '16rem',    // 256px
  
  // Component-specific spacing
  component: {
    // Button spacing
    button: {
      padding: {
        sm: '0.5rem 1rem',    // 8px 16px
        md: '0.75rem 1.5rem', // 12px 24px
        lg: '1rem 2rem',      // 16px 32px
        xl: '1.25rem 2.5rem', // 20px 40px
      },
      gap: '0.5rem', // 8px
    },
    
    // Card spacing
    card: {
      padding: {
        sm: '1rem',     // 16px
        md: '1.5rem',   // 24px
        lg: '2rem',     // 32px
        xl: '2.5rem',   // 40px
      },
      gap: '1rem', // 16px
    },
    
    // Form spacing
    form: {
      padding: {
        sm: '0.75rem',  // 12px
        md: '1rem',     // 16px
        lg: '1.25rem',  // 20px
      },
      gap: '0.75rem', // 12px
      margin: '1.5rem', // 24px
    },
    
    // Navigation spacing
    nav: {
      padding: {
        sm: '0.5rem',   // 8px
        md: '0.75rem',  // 12px
        lg: '1rem',     // 16px
      },
      gap: '1rem', // 16px
    },
    
    // Modal spacing
    modal: {
      padding: {
        sm: '1.5rem',   // 24px
        md: '2rem',     // 32px
        lg: '2.5rem',   // 40px
      },
      gap: '1.5rem', // 24px
    },
  },
  
  // Layout spacing
  layout: {
    // Section spacing
    section: {
      padding: {
        sm: '2rem 0',     // 32px 0
        md: '3rem 0',     // 48px 0
        lg: '4rem 0',     // 64px 0
        xl: '5rem 0',     // 80px 0
      },
      margin: {
        sm: '2rem 0',     // 32px 0
        md: '3rem 0',     // 48px 0
        lg: '4rem 0',     // 64px 0
        xl: '5rem 0',     // 80px 0
      },
    },
    
    // Container spacing
    container: {
      padding: {
        sm: '1rem',       // 16px
        md: '1.5rem',     // 24px
        lg: '2rem',       // 32px
        xl: '2.5rem',     // 40px
      },
      maxWidth: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px',
      },
    },
    
    // Grid spacing
    grid: {
      gap: {
        sm: '1rem',       // 16px
        md: '1.5rem',     // 24px
        lg: '2rem',       // 32px
        xl: '2.5rem',     // 40px
      },
    },
  },
  
  // Responsive spacing
  responsive: {
    // Mobile-first spacing
    mobile: {
      padding: '1rem',
      margin: '1rem',
      gap: '0.75rem',
    },
    
    // Tablet spacing
    tablet: {
      padding: '1.5rem',
      margin: '1.5rem',
      gap: '1rem',
    },
    
    // Desktop spacing
    desktop: {
      padding: '2rem',
      margin: '2rem',
      gap: '1.5rem',
    },
    
    // Large desktop spacing
    large: {
      padding: '2.5rem',
      margin: '2.5rem',
      gap: '2rem',
    },
  },
} as const;

export type SpacingToken = typeof spacing; 