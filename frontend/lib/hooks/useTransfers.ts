/**
 * SWR hooks for Transfer data management.
 * Updated to match backend implementation.
 */

import useSWR, { SWRConfiguration, mutate } from 'swr';

import * as transfersApi from '../api/transfers';
import { TransferLocation } from '../types/api';

// Transfer Routes
export const useTransferRoutes = (
  params?: {
    search?: string;
    origin?: string;
    destination?: string;
  },
  config?: SWRConfiguration
) => {
  const key = params ? ['transfer-routes', params] : 'transfer-routes';
  
  return useSWR<{ results: transfersApi.TransferRoute[] }>(
    key,
    () => transfersApi.getTransferRoutes(params),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Transfer Route by ID
export const useTransferRoute = (
  routeId: string,
  config?: SWRConfiguration
) => {
  return useSWR<transfersApi.TransferRoute>(
    routeId ? ['transfer-route', routeId] : null,
    () => transfersApi.getTransferRoute(routeId),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Transfer Pricing Calculation
export const useTransferPricing = (
  routeId: string | null,
  pricingRequest: transfersApi.TransferPriceCalculationRequest | null,
  config?: SWRConfiguration
) => {
  const key = routeId && pricingRequest ? `transfer-pricing-${routeId}-${JSON.stringify(pricingRequest)}` : null;
  
  return useSWR<transfersApi.TransferPriceCalculationResponse>(
    key,
    () => transfersApi.calculateTransferPrice(routeId!, pricingRequest!),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Transfer Mutations
export const useTransferMutations = () => {
  const addToCart = async (bookingData: transfersApi.TransferBookingRequest) => {
    try {
      const result = await transfersApi.addTransferToCart(bookingData);
      // Invalidate cart data
      mutate('cart');
      return { success: true, data: result };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error && error.message ? error.message : 'Failed to add to cart';
      return { success: false, error: errorMessage };
    }
  };

  return {
    addToCart
  };
};

// Legacy hooks for backward compatibility (to be removed)
export const useTransferLocations = (
  params?: {
    search?: string;
    city?: string;
    country?: string;
  },
  config?: SWRConfiguration
) => {
  console.warn('useTransferLocations is deprecated. Use useTransferRoutes instead.');
  return useSWR<TransferLocation[]>(
    'transfer-locations',
    async () => {
      const response = await transfersApi.getTransferLocations();
      return response.results;
    },
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useTransfers = (
  params?: unknown,
  config?: SWRConfiguration
) => {
  console.warn('useTransfers is deprecated. Use useTransferRoutes instead.');
  return useSWR<unknown>(
    'transfers',
    () => transfersApi.getTransfers(),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useTransferSearch = (
  searchParams?: { origin?: string; destination?: string; search?: string },
  config?: SWRConfiguration
) => {
  console.warn('useTransferSearch is deprecated. Use useTransferRoutes instead.');
  return useSWR<transfersApi.TransferRoute[]>(
    searchParams ? `transfer-search-${JSON.stringify(searchParams)}` : null,
    () => transfersApi.searchTransfers(searchParams || {}),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useTransferBySlug = (
  slug: string,
  config?: SWRConfiguration
) => {
  console.warn('useTransferBySlug is deprecated. Use useTransferRoute instead.');
  return useSWR<transfersApi.TransferRoute>(
    slug ? `transfer-${slug}` : null,
    () => transfersApi.getTransferBySlug(slug),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useTransferById = (
  id: string,
  config?: SWRConfiguration
) => {
  console.warn('useTransferById is deprecated. Use useTransferRoute instead.');
  return useSWR<transfersApi.TransferRoute>(
    id ? `transfer-${id}` : null,
    () => transfersApi.getTransferById(id),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useTransferSchedules = (
  transferId: string,
  config?: SWRConfiguration
) => {
  console.warn('useTransferSchedules is deprecated. Schedules are not used in transfer routes.');
  return useSWR<transfersApi.TransferSchedule[]>(
    transferId ? `transfer-schedules-${transferId}` : null,
    () => transfersApi.getTransferSchedules(transferId),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useTransferAvailability = (
  params: { route_id: string; date: string; vehicle_type?: string },
  config?: SWRConfiguration
) => {
  console.warn('useTransferAvailability is deprecated. Transfers are always available.');
  return useSWR<transfersApi.TransferAvailability>(
    params ? `transfer-availability-${JSON.stringify(params)}` : null,
    () => transfersApi.getTransferAvailability(params),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useTransferFilters = (config?: SWRConfiguration) => {
  console.warn('useTransferFilters is deprecated.');
  return useSWR<unknown>(
    'transfer-filters',
    () => transfersApi.getTransferFilters(),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useTransferStats = (
  _transferId: string,
  config?: SWRConfiguration
) => {
  console.warn('useTransferStats is deprecated.');
  return useSWR<unknown>(
    'transfer-stats',
    () => transfersApi.getTransferStats(),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useRouteByLocations = (
  pickupLocationId: string,
  dropoffLocationId: string,
  config?: SWRConfiguration
) => {
  console.warn('useRouteByLocations is deprecated. Use useTransferRoutes with origin/destination params.');
  return useSWR<transfersApi.TransferRoute | null>(
    pickupLocationId && dropoffLocationId ? `route-by-locations-${pickupLocationId}-${dropoffLocationId}` : null,
    () => transfersApi.getRouteByLocations({ origin: pickupLocationId, destination: dropoffLocationId }),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

export const useTransferBooking = () => {
  console.warn('useTransferBooking is deprecated. Use useTransferMutations instead.');
  return {
    bookTransfer: async (bookingData: transfersApi.TransferBookingRequest) => {
      return transfersApi.bookTransfer(bookingData);
    }
  };
};

export const useTransferSearchWithFilters = (searchParams?: { origin?: string; destination?: string; search?: string }) => {
  console.warn('useTransferSearchWithFilters is deprecated. Use useTransferRoutes instead.');
  return useTransferSearch(searchParams);
}; 

// Transfer Options
export const useTransferOptions = (
  routeId?: string,
  config?: SWRConfiguration
) => {
  return useSWR<transfersApi.TransferOption[]>(
    ['transfer-options', routeId || 'global'],
    async () => {
      const response = await transfersApi.getTransferOptions();
      return response;
    },
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
}; 