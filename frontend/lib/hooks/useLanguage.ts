import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { getTranslations, getLanguage } from '../translations';
import { fa } from '../translations/fa';

export const useLanguage = () => {
  const params = useParams();
  const [currentLang, setCurrentLang] = useState<string>('fa');
  const [translations, setTranslations] = useState(fa);

  useEffect(() => {
    const loadTranslations = async () => {
      // Get language from URL params
      const langFromUrl = params?.locale as string;
      if (langFromUrl && ['fa', 'en', 'tr'].includes(langFromUrl)) {
        setCurrentLang(langFromUrl);
        const trans = await getTranslations(langFromUrl);
        setTranslations(trans);
      } else {
        // Fallback to browser language or stored preference
        const detectedLang = getLanguage();
        setCurrentLang(detectedLang);
        const trans = await getTranslations(detectedLang);
        setTranslations(trans);
      }
    };

    loadTranslations();
  }, [params?.locale]);

  const changeLanguage = async (lang: string) => {
    if (['fa', 'en', 'tr'].includes(lang)) {
      setCurrentLang(lang);
      const trans = await getTranslations(lang);
      setTranslations(trans);
      if (typeof window !== 'undefined') {
        localStorage.setItem('language', lang);
      }
    }
  };

  return {
    currentLang,
    translations,
    changeLanguage,
    isRTL: currentLang === 'fa'
  };
};
