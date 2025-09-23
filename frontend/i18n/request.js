import { getRequestConfig } from 'next-intl/server';
import { locales, defaultLocale } from './config.js';

export default getRequestConfig(async ({ locale }) => {
  // Validate that the incoming `locale` parameter is valid
  if (!locale || !locales.includes(locale)) {
    locale = defaultLocale;
  }

  // Load messages dynamically with error handling
  let messages;
  try {
    messages = (await import(`../messages/${locale}.json`)).default;
  } catch (error) {
    console.error(`Failed to load messages for locale ${locale}:`, error);
    // Fallback to default locale
    messages = (await import(`../messages/${defaultLocale}.json`)).default;
  }

  return {
    locale,
    messages,
    timeZone: 'Asia/Tehran'
  };
});
