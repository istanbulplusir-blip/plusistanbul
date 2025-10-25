/**
 * Tests for Leaflet mobile configuration
 */

import { getMobileMapOptions, configureLeafletForIOS } from '../leafletConfig';

// Mock navigator
const mockNavigator = (userAgent: string) => {
    Object.defineProperty(window.navigator, 'userAgent', {
        value: userAgent,
        configurable: true,
    });
};

describe('leafletConfig', () => {
    describe('getMobileMapOptions', () => {
        it('should return mobile-optimized options for iOS', () => {
            mockNavigator('Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)');
            const options = getMobileMapOptions();

            expect(options.zoomControl).toBe(false);
            expect(options.tap).toBe(true);
            expect(options.tapTolerance).toBe(20); // Higher for iOS
            expect(options.touchZoom).toBe(true);
            expect(options.doubleClickZoom).toBe(false);
        });

        it('should return mobile-optimized options for Android', () => {
            mockNavigator('Mozilla/5.0 (Linux; Android 10)');
            const options = getMobileMapOptions();

            expect(options.zoomControl).toBe(false);
            expect(options.tap).toBe(true);
            expect(options.tapTolerance).toBe(15); // Standard for Android
            expect(options.touchZoom).toBe(true);
        });

        it('should return desktop-optimized options', () => {
            mockNavigator('Mozilla/5.0 (Windows NT 10.0; Win64; x64)');
            const options = getMobileMapOptions();

            expect(options.scrollWheelZoom).toBe(true);
        });
    });

    describe('configureLeafletForIOS', () => {
        it('should configure Leaflet for iOS devices', () => {
            mockNavigator('Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)');

            // This test would need to mock L.Browser and L.Map
            // For now, we just ensure it doesn't throw
            expect(() => configureLeafletForIOS()).not.toThrow();
        });
    });
});
