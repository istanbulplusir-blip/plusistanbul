/**
 * Utility functions for currency handling and formatting
 */

export interface CurrencyInfo {
  code: string;
  symbol: string;
  name: string;
  locale: string;
}

export const SUPPORTED_CURRENCIES: Record<string, CurrencyInfo> = {
  USD: { code: 'USD', symbol: '$', name: 'US Dollar', locale: 'en-US' },
  EUR: { code: 'EUR', symbol: '€', name: 'Euro', locale: 'en-EU' },
  IRR: { code: 'IRR', symbol: 'ریال', name: 'Iranian Rial', locale: 'fa-IR' },
  TRY: { code: 'TRY', symbol: '₺', name: 'Turkish Lira', locale: 'tr-TR' },
};

/**
 * Format price with proper currency formatting
 */
export function formatPrice(
  amount: number, 
  currency: string = 'USD', 
  locale?: string
): string {
  const currencyInfo = SUPPORTED_CURRENCIES[currency];
  if (!currencyInfo) {
    return `${currency} ${amount.toFixed(2)}`;
  }

  try {
    // Special handling for Iranian Rial
    if (currency === 'IRR') {
      const formattedAmount = new Intl.NumberFormat('fa-IR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(amount);
      return `${formattedAmount} ${currencyInfo.symbol}`;
    }

    // Standard currency formatting
    return new Intl.NumberFormat(currencyInfo.locale, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  } catch (error) {
    console.warn('Currency formatting error:', error);
    return `${currencyInfo.symbol}${amount.toFixed(2)}`;
  }
}

/**
 * Format price for agent display with conversion info
 */
export function formatAgentPrice(
  amount: number,
  currency: string,
  originalCurrency?: string,
  conversionApplied?: boolean
): string {
  const formatted = formatPrice(amount, currency);
  
  if (conversionApplied && originalCurrency && originalCurrency !== currency) {
    return `${formatted} (converted from ${originalCurrency})`;
  }
  
  return formatted;
}

/**
 * Get currency symbol
 */
export function getCurrencySymbol(currency: string): string {
  return SUPPORTED_CURRENCIES[currency]?.symbol || currency;
}

/**
 * Get currency name
 */
export function getCurrencyName(currency: string): string {
  return SUPPORTED_CURRENCIES[currency]?.name || currency;
}

/**
 * Check if currency is supported
 */
export function isSupportedCurrency(currency: string): boolean {
  return currency in SUPPORTED_CURRENCIES;
}

/**
 * Convert amount between currencies (mock implementation)
 * In real app, this would call the backend conversion service
 */
export async function convertCurrency(
  amount: number,
  fromCurrency: string,
  toCurrency: string
): Promise<number> {
  if (fromCurrency === toCurrency) {
    return amount;
  }

  // Mock conversion rates - in real app, fetch from backend
  const rates: Record<string, number> = {
    'USD': 1.0,
    'EUR': 0.85,
    'IRR': 420000,
    'TRY': 15.5,
  };

  const fromRate = rates[fromCurrency] || 1;
  const toRate = rates[toCurrency] || 1;

  return (amount / fromRate) * toRate;
}
