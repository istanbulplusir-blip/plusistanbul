/**
 * Centralized limit validation service for frontend
 * Provides consistent limit checking across all components
 */

export interface LimitSettings {
  cartMaxItemsGuest: number;
  cartMaxTotalGuest: number;
  cartMaxItemsUser: number;
  cartMaxTotalUser: number;
  orderMaxPendingPerUser: number;
}

export interface ValidationResult {
  isValid: boolean;
  errorMessage?: string;
  errorCode?: string;
}

export class LimitValidationService {
  private static settings: LimitSettings = {
    cartMaxItemsGuest: 3,
    cartMaxTotalGuest: 500,
    cartMaxItemsUser: 10,
    cartMaxTotalUser: 5000,
    orderMaxPendingPerUser: 3,
  };

  /**
   * Update settings from backend
   */
  static updateSettings(settings: Partial<LimitSettings>): void {
    this.settings = { ...this.settings, ...settings };
  }

  /**
   * Get current settings
   */
  static getSettings(): LimitSettings {
    return { ...this.settings };
  }

  /**
   * Validate cart limits
   */
  static validateCartLimits(
    isAuthenticated: boolean,
    currentItems: number,
    currentTotal: number,
    newItemTotal: number = 0
  ): ValidationResult {
    const settings = this.getSettings();
    
    if (isAuthenticated) {
      // Authenticated user limits
      if (currentItems >= settings.cartMaxItemsUser) {
        return {
          isValid: false,
          errorMessage: `You can add maximum ${settings.cartMaxItemsUser} items to cart.`,
          errorCode: 'CART_ITEMS_LIMIT_EXCEEDED'
        };
      }
      
      if (currentTotal + newItemTotal > settings.cartMaxTotalUser) {
        return {
          isValid: false,
          errorMessage: `Cart total cannot exceed $${settings.cartMaxTotalUser}.`,
          errorCode: 'CART_TOTAL_LIMIT_EXCEEDED'
        };
      }
    } else {
      // Guest user limits
      if (currentItems >= settings.cartMaxItemsGuest) {
        return {
          isValid: false,
          errorMessage: `Guest users can add maximum ${settings.cartMaxItemsGuest} items to cart. Please register to add more items.`,
          errorCode: 'GUEST_CART_ITEMS_LIMIT_EXCEEDED'
        };
      }
      
      if (currentTotal + newItemTotal > settings.cartMaxTotalGuest) {
        return {
          isValid: false,
          errorMessage: `Guest cart total cannot exceed $${settings.cartMaxTotalGuest}. Please register to add more items.`,
          errorCode: 'GUEST_CART_TOTAL_LIMIT_EXCEEDED'
        };
      }
    }

    return { isValid: true };
  }

  /**
   * Validate merge limits
   */
  static validateMergeLimits(
    userCartItems: number,
    userCartTotal: number,
    guestCartItems: number,
    guestCartTotal: number
  ): ValidationResult {
    const settings = this.getSettings();

    // Check if merge would exceed user limits
    if (userCartItems + guestCartItems > settings.cartMaxItemsUser) {
      return {
        isValid: false,
        errorMessage: `Cannot merge: would exceed maximum ${settings.cartMaxItemsUser} items limit.`,
        errorCode: 'MERGE_LIMIT_EXCEEDED'
      };
    }

    if (userCartTotal + guestCartTotal > settings.cartMaxTotalUser) {
      return {
        isValid: false,
        errorMessage: `Cannot merge: would exceed maximum $${settings.cartMaxTotalUser} total limit.`,
        errorCode: 'MERGE_TOTAL_EXCEEDED'
      };
    }

    // Check if guest cart itself exceeds guest limits
    if (guestCartItems > settings.cartMaxItemsGuest) {
      return {
        isValid: false,
        errorMessage: `Guest cart exceeds maximum ${settings.cartMaxItemsGuest} items limit.`,
        errorCode: 'GUEST_CART_LIMIT_EXCEEDED'
      };
    }

    if (guestCartTotal > settings.cartMaxTotalGuest) {
      return {
        isValid: false,
        errorMessage: `Guest cart exceeds maximum $${settings.cartMaxTotalGuest} total limit.`,
        errorCode: 'GUEST_CART_TOTAL_EXCEEDED'
      };
    }

    return { isValid: true };
  }

  /**
   * Validate participant limits for tours
   */
  static validateParticipantLimits(
    participants: { adult: number; child: number; infant: number },
    tourLimits: { minParticipants: number; maxParticipants: number }
  ): ValidationResult {
    const totalParticipants = participants.adult + participants.child + participants.infant;

    // Check minimum participants
    if (totalParticipants < tourLimits.minParticipants) {
      return {
        isValid: false,
        errorMessage: `Minimum ${tourLimits.minParticipants} participants required.`,
        errorCode: 'MIN_PARTICIPANTS_REQUIRED'
      };
    }

    // Check maximum participants
    if (totalParticipants > tourLimits.maxParticipants) {
      return {
        isValid: false,
        errorMessage: `Maximum ${tourLimits.maxParticipants} participants allowed.`,
        errorCode: 'MAX_PARTICIPANTS_EXCEEDED'
      };
    }

    // Check infant limit
    if (participants.infant > 2) {
      return {
        isValid: false,
        errorMessage: 'Maximum 2 infants allowed.',
        errorCode: 'MAX_INFANTS_EXCEEDED'
      };
    }

    // Check adult + child combination
    const adultChildTotal = participants.adult + participants.child;
    const maxAdultChild = tourLimits.maxParticipants - participants.infant;
    if (adultChildTotal > maxAdultChild) {
      return {
        isValid: false,
        errorMessage: `Adult + child combination cannot exceed ${maxAdultChild} (considering ${participants.infant} infants).`,
        errorCode: 'ADULT_CHILD_COMBINATION_EXCEEDED'
      };
    }

    return { isValid: true };
  }

  /**
   * Validate option quantity limits
   */
  static validateOptionLimits(
    optionId: string,
    quantity: number,
    maxQuantity?: number
  ): ValidationResult {
    if (maxQuantity && quantity > maxQuantity) {
      return {
        isValid: false,
        errorMessage: `Option quantity cannot exceed ${maxQuantity}.`,
        errorCode: 'OPTION_QUANTITY_EXCEEDED'
      };
    }

    return { isValid: true };
  }

  /**
   * Get limit display text
   */
  static getLimitDisplayText(isAuthenticated: boolean): string {
    const settings = this.getSettings();
    
    if (isAuthenticated) {
      return `${settings.cartMaxItemsUser} items • $${settings.cartMaxTotalUser} max`;
    } else {
      return `${settings.cartMaxItemsGuest} items • $${settings.cartMaxTotalGuest} max`;
    }
  }
}
