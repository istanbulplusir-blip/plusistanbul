/**
 * Utility functions for agent-related operations
 */

import { AgentCommission } from '@/lib/types/api';

/**
 * Format commission amount for display
 */
export const formatCommissionAmount = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format commission status for display
 */
export const formatCommissionStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: 'Pending',
    approved: 'Approved',
    paid: 'Paid',
    rejected: 'Rejected',
    cancelled: 'Cancelled',
  };
  
  return statusMap[status] || status;
};

/**
 * Get color class for commission status
 */
export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    pending: 'text-yellow-600 bg-yellow-100',
    approved: 'text-blue-600 bg-blue-100',
    paid: 'text-green-600 bg-green-100',
    rejected: 'text-red-600 bg-red-100',
    cancelled: 'text-gray-600 bg-gray-100',
  };
  
  return colorMap[status] || 'text-gray-600 bg-gray-100';
};

/**
 * Calculate total commission amount
 */
export const calculateTotalCommission = (commissions: AgentCommission[]): number => {
  return commissions.reduce((total, commission) => {
    return total + commission.commission_amount;
  }, 0);
};

/**
 * Calculate commission by status
 */
export const calculateCommissionByStatus = (commissions: AgentCommission[], status: string): number => {
  return commissions
    .filter(commission => commission.status === status)
    .reduce((total, commission) => total + commission.commission_amount, 0);
};

/**
 * Format date for display
 */
export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Format currency amount
 */
export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format customer tier for display
 */
export const formatCustomerTier = (tier: string): string => {
  const tierMap: Record<string, string> = {
    bronze: 'Bronze',
    silver: 'Silver',
    gold: 'Gold',
    platinum: 'Platinum',
  };
  
  return tierMap[tier] || tier;
};

/**
 * Format customer status for display
 */
export const formatCustomerStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    active: 'Active',
    inactive: 'Inactive',
    suspended: 'Suspended',
  };
  
  return statusMap[status] || status;
};

/**
 * Get color class for customer tier
 */
export const getTierColor = (tier: string): string => {
  const colorMap: Record<string, string> = {
    bronze: 'text-orange-600 bg-orange-100',
    silver: 'text-gray-600 bg-gray-100',
    gold: 'text-yellow-600 bg-yellow-100',
    platinum: 'text-purple-600 bg-purple-100',
  };
  
  return colorMap[tier] || 'text-gray-600 bg-gray-100';
};

/**
 * Get color class for customer status
 */
export const getCustomerStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    active: 'text-green-600 bg-green-100',
    inactive: 'text-gray-600 bg-gray-100',
    suspended: 'text-red-600 bg-red-100',
  };
  
  return colorMap[status] || 'text-gray-600 bg-gray-100';
};
