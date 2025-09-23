export type NormalizedPriceBreakdown = {
  base_price: number;
  modifiers: {
    outbound_surcharge?: number;
    return_surcharge?: number;
    round_trip_discount?: number;
    price_modifier?: number;
  };
  options_total: number;
  fees_total: number;
  taxes_total: number;
  subtotal: number;
  final_price: number;
  currency: string;
  timestamp?: string;
};

const toNumber = (v: unknown, fallback = 0): number => {
  const n = typeof v === 'string' ? parseFloat(v) : typeof v === 'number' ? v : NaN;
  return Number.isFinite(n) ? n : fallback;
};

export function normalizeEventPricing(raw: unknown, fallbackCurrency = 'USD'): NormalizedPriceBreakdown {
  const pb = (raw && typeof raw === 'object' && raw !== null && 'price_breakdown' in raw ? raw.price_breakdown : raw) ?? {};
  const typedPb = pb as Record<string, unknown>;
  const base = toNumber(typedPb.base_price);
  const options = toNumber(typedPb.options_total);
  const fees = toNumber(typedPb.fees_total);
  const taxes = toNumber(typedPb.taxes_total);
  const pm = toNumber(typedPb.price_modifier);
  const subtotal = toNumber(typedPb.subtotal, base + options + fees + taxes + pm);
  const final_price = toNumber(typedPb.final_price, subtotal);
  const currency = String(typedPb.currency || (raw && typeof raw === 'object' && raw !== null && 'currency' in raw ? raw.currency : fallbackCurrency));
  return {
    base_price: base,
    modifiers: { price_modifier: pm },
    options_total: options,
    fees_total: fees,
    taxes_total: taxes,
    subtotal,
    final_price,
    currency,
    timestamp: (raw && typeof raw === 'object' && raw !== null && 'calculation_timestamp' in raw ? raw.calculation_timestamp as string : undefined),
  };
}

export function normalizeTransferPricing(raw: unknown, fallbackCurrency = 'USD'): NormalizedPriceBreakdown {
  const pb = (raw && typeof raw === 'object' && raw !== null && 'price_breakdown' in raw ? raw.price_breakdown : raw) ?? {};
  const typedPb = pb as Record<string, unknown>;
  const base = toNumber(typedPb.base_price);
  const outS = toNumber(typedPb.outbound_surcharge);
  const retS = toNumber(typedPb.return_surcharge);
  const options = toNumber(typedPb.options_total);
  const rtd = toNumber(typedPb.round_trip_discount);
  
  // Use backend's calculated values directly instead of manual calculation
  const subtotal = toNumber(typedPb.subtotal) || toNumber(typedPb.final_price);
  const final_price = toNumber(typedPb.final_price);
  
  const currency = String(typedPb.currency || fallbackCurrency);
  return {
    base_price: base,
    modifiers: {
      outbound_surcharge: outS,
      return_surcharge: retS,
      round_trip_discount: rtd,
    },
    options_total: options,
    fees_total: toNumber(typedPb.fees_total),
    taxes_total: toNumber(typedPb.taxes_total),
    subtotal,
    final_price,
    currency,
    timestamp: (raw && typeof raw === 'object' && raw !== null && 'calculation_timestamp' in raw ? raw.calculation_timestamp as string : undefined),
  };
}

export function normalizeFromCartItem(cartItem: unknown, fallbackCurrency = 'USD'): NormalizedPriceBreakdown {
  const typedCartItem = cartItem as Record<string, unknown>;
  // Use specific normalization for transfers if pricing_breakdown is available
  if (typedCartItem.product_type === 'transfer' && typedCartItem.pricing_breakdown) {
    return normalizeTransferPricing(typedCartItem.pricing_breakdown, fallbackCurrency);
  }
  
  // Use specific normalization for events if pricing_breakdown is available
  if (typedCartItem.product_type === 'event' && typedCartItem.pricing_breakdown) {
    return normalizeEventPricing(typedCartItem.pricing_breakdown, fallbackCurrency);
  }
  
  // Best-effort derivation from cart line for other cases
  const unit = toNumber(typedCartItem.unit_price);
  const options = toNumber(typedCartItem.options_total);
  const total = toNumber(typedCartItem.total_price, unit + options);
  const currency = String(typedCartItem.currency || fallbackCurrency);
  return {
    base_price: unit,
    modifiers: {} as Record<string, never>,
    options_total: options,
    fees_total: 0,
    taxes_total: 0,
    subtotal: total,
    final_price: total,
    currency,
    timestamp: (typedCartItem.updated_at as string) || (typedCartItem.created_at as string),
  };
}


