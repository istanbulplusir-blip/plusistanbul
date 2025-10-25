/**
 * Leaflet configuration for better mobile/iOS experience
 */

import L from 'leaflet';

/**
 * Configure Leaflet for iOS devices
 */
export function configureLeafletForIOS() {
  // Check if running on iOS
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);

  if (isIOS) {
    // Configure map options for iOS without modifying read-only properties
    L.Map.mergeOptions({
      tapTolerance: 20,
      touchZoom: true,
      bounceAtZoomLimits: false,
    });
  }
}

/**
 * Get map options optimized for mobile devices
 */
export function getMobileMapOptions() {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  const isIOSSafari = isIOS && /Safari/.test(navigator.userAgent);
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  return {
    zoomControl: false, // We'll use custom controls
    touchZoom: true,
    doubleClickZoom: false, // Prevent accidental zooms
    scrollWheelZoom: !isMobile, // Disable on mobile to prevent conflicts
    dragging: true,
    boxZoom: false,
    keyboard: false,
    attributionControl: true,
    zoomAnimation: true,
    fadeAnimation: true,
    markerZoomAnimation: true,
    // iOS Safari specific options
    tap: isIOSSafari,
    tapTolerance: isIOSSafari ? 20 : 15,
    // Enhanced touch handling for iOS
    ...(isIOSSafari && {
      preferCanvas: false,
      renderer: undefined, // Use default SVG renderer for better iOS compatibility
    })
  };
}

/**
 * Fix iOS-specific Leaflet issues
 */
export function applyIOSFixes() {
  // Prevent iOS from showing the magnifying glass on long press
  if (typeof document !== 'undefined') {
    const style = document.createElement('style');
    style.innerHTML = `
      .leaflet-container {
        -webkit-tap-highlight-color: transparent !important;
        -webkit-touch-callout: none !important;
        -webkit-user-select: none !important;
        user-select: none !important;
        touch-action: pan-y pinch-zoom !important;
      }
      
      .leaflet-container img {
        -webkit-user-drag: none !important;
        -webkit-touch-callout: none !important;
        pointer-events: none !important;
      }
      
      /* Enhanced iOS Safari touch handling */
      .leaflet-container * {
        -webkit-tap-highlight-color: transparent !important;
        -webkit-touch-callout: none !important;
      }
      
      /* Prevent zoom controls from flickering on iOS */
      .leaflet-control-zoom {
        touch-action: manipulation !important;
        -webkit-tap-highlight-color: transparent !important;
      }
      
      .leaflet-control-zoom a {
        touch-action: manipulation !important;
        -webkit-tap-highlight-color: transparent !important;
        min-width: 44px !important;
        min-height: 44px !important;
      }
      
      /* Improve marker touch targets for iOS */
      .leaflet-marker-icon {
        touch-action: manipulation !important;
        cursor: pointer !important;
        -webkit-tap-highlight-color: transparent !important;
        min-width: 44px !important;
        min-height: 44px !important;
      }
      
      /* Fix popup touch issues on iOS */
      .leaflet-popup {
        touch-action: auto !important;
        -webkit-tap-highlight-color: transparent !important;
      }
      
      /* iOS Safari specific map interaction fixes */
      @supports (-webkit-touch-callout: none) {
        .leaflet-container {
          -webkit-overflow-scrolling: touch !important;
        }
        
        .leaflet-interactive {
          touch-action: manipulation !important;
        }
        
        /* Force hardware acceleration on iOS */
        .leaflet-zoom-animated {
          -webkit-transform: translateZ(0) !important;
          transform: translateZ(0) !important;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

/**
 * Initialize Leaflet with mobile optimizations
 */
export function initializeLeafletForMobile() {
  if (typeof window !== 'undefined') {
    configureLeafletForIOS();
    applyIOSFixes();
  }
}
