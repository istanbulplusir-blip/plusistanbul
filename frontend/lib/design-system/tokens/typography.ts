// Design System - Typography Tokens
export const typography = {
  // Font Families
  fontFamily: {
    sans: ['Inter', 'Vazirmatn', 'ui-sans-serif', 'system-ui', 'sans-serif'],
    serif: ['ui-serif', 'Georgia', 'Cambria', 'serif'],
    mono: ['ui-monospace', 'SFMono-Regular', 'Monaco', 'Consolas', 'monospace'],
  },
  
  // Font Sizes
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
    '6xl': '3.75rem',  // 60px
    '7xl': '4.5rem',   // 72px
    '8xl': '6rem',     // 96px
    '9xl': '8rem',     // 128px
  },
  
  // Font Weights
  fontWeight: {
    thin: '100',
    extralight: '200',
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
    black: '900',
  },
  
  // Line Heights
  lineHeight: {
    none: '1',
    tight: '1.25',
    snug: '1.375',
    normal: '1.5',
    relaxed: '1.625',
    loose: '2',
  },
  
  // Letter Spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0em',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
  
  // Text Styles (Predefined combinations)
  textStyles: {
    // Headings
    h1: {
      fontSize: '2.25rem', // 4xl
      fontWeight: '700',
      lineHeight: '1.2',
      letterSpacing: '-0.025em',
    },
    h2: {
      fontSize: '1.875rem', // 3xl
      fontWeight: '600',
      lineHeight: '1.3',
      letterSpacing: '-0.025em',
    },
    h3: {
      fontSize: '1.5rem', // 2xl
      fontWeight: '600',
      lineHeight: '1.4',
      letterSpacing: '-0.025em',
    },
    h4: {
      fontSize: '1.25rem', // xl
      fontWeight: '600',
      lineHeight: '1.4',
      letterSpacing: '-0.025em',
    },
    h5: {
      fontSize: '1.125rem', // lg
      fontWeight: '600',
      lineHeight: '1.4',
      letterSpacing: '-0.025em',
    },
    h6: {
      fontSize: '1rem', // base
      fontWeight: '600',
      lineHeight: '1.4',
      letterSpacing: '-0.025em',
    },
    
    // Body Text
    body: {
      fontSize: '1rem', // base
      fontWeight: '400',
      lineHeight: '1.6',
      letterSpacing: '0em',
    },
    bodyLarge: {
      fontSize: '1.125rem', // lg
      fontWeight: '400',
      lineHeight: '1.6',
      letterSpacing: '0em',
    },
    bodySmall: {
      fontSize: '0.875rem', // sm
      fontWeight: '400',
      lineHeight: '1.5',
      letterSpacing: '0em',
    },
    
    // Caption
    caption: {
      fontSize: '0.75rem', // xs
      fontWeight: '400',
      lineHeight: '1.4',
      letterSpacing: '0.025em',
    },
    
    // Button Text
    button: {
      fontSize: '0.875rem', // sm
      fontWeight: '500',
      lineHeight: '1.4',
      letterSpacing: '0.025em',
    },
    buttonLarge: {
      fontSize: '1rem', // base
      fontWeight: '500',
      lineHeight: '1.4',
      letterSpacing: '0.025em',
    },
  },
} as const;

export type TypographyToken = typeof typography; 