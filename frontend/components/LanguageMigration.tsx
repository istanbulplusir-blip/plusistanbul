'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

/**
 * Component to migrate users from old language preferences to default 'fa'
 * This runs once per user and clears any non-fa language preferences from localStorage
 */
export default function LanguageMigration() {
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        // Only run migration once
        const migrationDone = localStorage.getItem('lang_migration_v1_done');

        if (!migrationDone) {
            const storedLang = localStorage.getItem('language');

            // If user has a non-fa language stored, clear it and redirect to fa
            if (storedLang && storedLang !== 'fa') {
                console.log('[Language Migration] Clearing old language preference:', storedLang);
                localStorage.removeItem('language');

                // Get current locale from URL
                const currentLocale = pathname.split('/')[1];

                // If currently on en or tr, redirect to fa
                if (currentLocale === 'en' || currentLocale === 'tr') {
                    const newPath = pathname.replace(`/${currentLocale}/`, '/fa/');
                    console.log('[Language Migration] Redirecting to:', newPath);
                    router.replace(newPath);
                }
            }

            // Mark migration as done
            localStorage.setItem('lang_migration_v1_done', 'true');
            console.log('[Language Migration] Migration completed');
        }
    }, [pathname, router]);

    // This component doesn't render anything
    return null;
}
