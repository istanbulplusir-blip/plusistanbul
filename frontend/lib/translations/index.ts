export { fa } from './fa';
export { en } from './en';

// Default language
export const defaultLanguage = 'fa';

// Language detection helper
export const getLanguage = (): string => {
  if (typeof window !== 'undefined') {
    // Check localStorage first
    const stored = localStorage.getItem('language');
    if (stored) return stored;
    
    // Check browser language
    const browserLang = navigator.language.split('-')[0];
    if (browserLang === 'fa' || browserLang === 'ar') return 'fa';
    if (browserLang === 'tr') return 'tr';
    return 'en';
  }
  return defaultLanguage;
};

// Translation helper
export const t = async (key: string, lang: string = defaultLanguage): Promise<string> => {
  try {
    const keys = key.split('.');
    let value: Record<string, unknown> = {};
    
    if (lang === 'fa') {
      const { fa: faTranslations } = await import('./fa');
      value = faTranslations;
    } else if (lang === 'en') {
      const { en: enTranslations } = await import('./en');
      value = enTranslations;
    }
    
    for (const k of keys) {
      value = value?.[k] as Record<string, unknown>;
    }
    
    return (typeof value === 'string' ? value : key);
  } catch {
    return key;
  }
};

// Get translations object based on language
export const getTranslations = (lang: string = defaultLanguage) => {
  if (lang === 'fa') {
    return import('./fa').then(m => m.fa);
  } else if (lang === 'en') {
    return import('./en').then(m => m.en);
  }
  return import('./fa').then(m => m.fa); // fallback to Persian
};
