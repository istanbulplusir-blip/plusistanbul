/**
 * Final Testing and Validation Script for Static Pages Fix
 * Task 7: تست نهایی و اعتبارسنجی
 * 
 * This script performs comprehensive testing of:
 * - Privacy page in all languages (fa, en, tr)
 * - Terms page in all languages (fa, en, tr)
 * - Footer presence on all static pages
 * - Translation keys validation
 * - Dark/Light mode compatibility
 * - Responsive design
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes for console output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
};

// Test results storage
const testResults = {
    passed: 0,
    failed: 0,
    warnings: 0,
    tests: []
};

// Helper function to log test results
function logTest(testName, passed, message = '') {
    const status = passed ? `${colors.green}✓ PASS${colors.reset}` : `${colors.red}✗ FAIL${colors.reset}`;
    console.log(`${status} ${testName}`);
    if (message) {
        console.log(`  ${colors.cyan}→${colors.reset} ${message}`);
    }

    testResults.tests.push({ testName, passed, message });
    if (passed) {
        testResults.passed++;
    } else {
        testResults.failed++;
    }
}

function logWarning(message) {
    console.log(`${colors.yellow}⚠ WARNING${colors.reset} ${message}`);
    testResults.warnings++;
}

function logSection(title) {
    console.log(`\n${colors.bright}${colors.blue}═══ ${title} ═══${colors.reset}\n`);
}

// Test 1: Check translation files for privacy and terms keys
function testTranslationKeys() {
    logSection('Test 1: Translation Keys Validation');

    const languages = ['fa', 'en', 'tr'];
    const requiredSections = ['privacy', 'terms'];

    languages.forEach(lang => {
        const filePath = path.join(__dirname, 'frontend', 'messages', `${lang}.json`);

        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const translations = JSON.parse(content);

            requiredSections.forEach(section => {
                const hasSection = translations[section] !== undefined;
                logTest(
                    `${lang}.json has "${section}" section`,
                    hasSection,
                    hasSection ? `Found ${Object.keys(translations[section] || {}).length} keys` : 'Section missing'
                );

                if (hasSection) {
                    // Check for required sub-keys
                    const requiredKeys = ['title', 'description', 'content', 'cta'];
                    requiredKeys.forEach(key => {
                        const hasKey = translations[section][key] !== undefined;
                        logTest(
                            `${lang}.json "${section}.${key}" exists`,
                            hasKey,
                            hasKey ? 'Key found' : 'Key missing'
                        );
                    });
                }
            });
        } catch (error) {
            logTest(`Read ${lang}.json`, false, error.message);
        }
    });
}

// Test 2: Check Privacy page implementation
function testPrivacyPage() {
    logSection('Test 2: Privacy Page Implementation');

    const privacyPagePath = path.join(__dirname, 'frontend', 'app', '[locale]', 'privacy', 'page.tsx');

    try {
        const content = fs.readFileSync(privacyPagePath, 'utf8');

        // Check for required imports
        logTest(
            'Privacy page imports useTranslations',
            content.includes("import { useTranslations } from 'next-intl'"),
            'Translation hook imported'
        );

        logTest(
            'Privacy page imports StaticPageLayout',
            content.includes("import StaticPageLayout from"),
            'Layout component imported'
        );

        // Check for translation usage
        logTest(
            'Privacy page uses privacy translations',
            content.includes("useTranslations('privacy')"),
            'Privacy translation namespace used'
        );

        // Check for content sections
        const contentSections = [
            'dataCollection',
            'dataUsage',
            'dataSecurity',
            'userRights',
            'contact'
        ];

        contentSections.forEach(section => {
            logTest(
                `Privacy page has ${section} section`,
                content.includes(`content.${section}`),
                `Section ${section} implemented`
            );
        });

        // Check for dark mode support
        logTest(
            'Privacy page has dark mode classes',
            content.includes('dark:text-') || content.includes('dark:bg-'),
            'Dark mode styling present'
        );

    } catch (error) {
        logTest('Read Privacy page', false, error.message);
    }
}

// Test 3: Check Terms page implementation
function testTermsPage() {
    logSection('Test 3: Terms Page Implementation');

    const termsPagePath = path.join(__dirname, 'frontend', 'app', '[locale]', 'terms', 'page.tsx');

    try {
        const content = fs.readFileSync(termsPagePath, 'utf8');

        // Check for required imports
        logTest(
            'Terms page imports useTranslations',
            content.includes("import { useTranslations } from 'next-intl'"),
            'Translation hook imported'
        );

        logTest(
            'Terms page imports StaticPageLayout',
            content.includes("import StaticPageLayout from"),
            'Layout component imported'
        );

        // Check for translation usage
        logTest(
            'Terms page uses terms translations',
            content.includes("useTranslations('terms')"),
            'Terms translation namespace used'
        );

        // Check for content sections
        const contentSections = [
            'acceptance',
            'services',
            'bookingPolicy',
            'cancellationPolicy',
            'liability',
            'changes'
        ];

        contentSections.forEach(section => {
            logTest(
                `Terms page has ${section} section`,
                content.includes(`content.${section}`),
                `Section ${section} implemented`
            );
        });

        // Check for dark mode support
        logTest(
            'Terms page has dark mode classes',
            content.includes('dark:text-') || content.includes('dark:bg-'),
            'Dark mode styling present'
        );

    } catch (error) {
        logTest('Read Terms page', false, error.message);
    }
}

// Test 4: Check StaticPageLayout has Footer
function testStaticPageLayout() {
    logSection('Test 4: StaticPageLayout Footer Integration');

    const layoutPath = path.join(__dirname, 'frontend', 'components', 'common', 'StaticPageLayout.tsx');

    try {
        const content = fs.readFileSync(layoutPath, 'utf8');

        // Check for Footer import
        logTest(
            'StaticPageLayout imports Footer',
            content.includes("import Footer from"),
            'Footer component imported'
        );

        // Check for Footer rendering
        logTest(
            'StaticPageLayout renders Footer',
            content.includes('<Footer') || content.includes('{showFooter && <Footer'),
            'Footer component rendered'
        );

        // Check for showFooter prop
        logTest(
            'StaticPageLayout has showFooter prop',
            content.includes('showFooter'),
            'Optional showFooter prop available'
        );

        // Check for dark mode support in layout
        logTest(
            'StaticPageLayout has dark mode support',
            content.includes('dark:') || content.includes('bg-gradient'),
            'Dark mode styling present'
        );

    } catch (error) {
        logTest('Read StaticPageLayout', false, error.message);
    }
}

// Test 5: Check other static pages
function testOtherStaticPages() {
    logSection('Test 5: Other Static Pages Validation');

    const staticPages = [
        { name: 'FAQ', path: 'faq' },
        { name: 'About', path: 'about' },
        { name: 'Contact', path: 'contact' }
    ];

    staticPages.forEach(({ name, path: pagePath }) => {
        const fullPath = path.join(__dirname, 'frontend', 'app', '[locale]', pagePath, 'page.tsx');

        try {
            const content = fs.readFileSync(fullPath, 'utf8');

            logTest(
                `${name} page exists`,
                true,
                `File found at ${pagePath}/page.tsx`
            );

            // Check if it uses translations
            const usesTranslations = content.includes('useTranslations');
            if (usesTranslations) {
                logTest(
                    `${name} page uses translations`,
                    true,
                    'Translation hook found'
                );
            } else {
                logWarning(`${name} page might not use translations`);
            }

        } catch (error) {
            logTest(`${name} page exists`, false, `File not found: ${error.message}`);
        }
    });
}

// Test 6: Check for console errors patterns
function testForCommonErrors() {
    logSection('Test 6: Common Error Patterns Check');

    const filesToCheck = [
        'frontend/app/[locale]/privacy/page.tsx',
        'frontend/app/[locale]/terms/page.tsx',
        'frontend/components/common/StaticPageLayout.tsx'
    ];

    filesToCheck.forEach(filePath => {
        const fullPath = path.join(__dirname, filePath);

        try {
            const content = fs.readFileSync(fullPath, 'utf8');

            // Check for common issues
            const hasConsoleLog = content.includes('console.log') || content.includes('console.error');
            if (hasConsoleLog) {
                logWarning(`${filePath} contains console statements`);
            }

            // Check for TODO comments
            const hasTodo = content.includes('TODO') || content.includes('FIXME');
            if (hasTodo) {
                logWarning(`${filePath} contains TODO/FIXME comments`);
            }

            // Check for proper TypeScript
            const hasAnyType = content.match(/:\s*any/g);
            if (hasAnyType) {
                logWarning(`${filePath} uses 'any' type (${hasAnyType.length} occurrences)`);
            }

            logTest(
                `${path.basename(filePath)} code quality check`,
                !hasConsoleLog && !hasTodo,
                'No console logs or TODOs found'
            );

        } catch (error) {
            logTest(`Check ${filePath}`, false, error.message);
        }
    });
}

// Test 7: Responsive design check
function testResponsiveDesign() {
    logSection('Test 7: Responsive Design Validation');

    const filesToCheck = [
        'frontend/app/[locale]/privacy/page.tsx',
        'frontend/app/[locale]/terms/page.tsx'
    ];

    filesToCheck.forEach(filePath => {
        const fullPath = path.join(__dirname, filePath);

        try {
            const content = fs.readFileSync(fullPath, 'utf8');

            // Check for responsive classes
            const hasResponsiveClasses =
                content.includes('sm:') ||
                content.includes('md:') ||
                content.includes('lg:') ||
                content.includes('xl:');

            logTest(
                `${path.basename(filePath)} has responsive classes`,
                hasResponsiveClasses,
                hasResponsiveClasses ? 'Responsive breakpoints found' : 'No responsive classes detected'
            );

            // Check for mobile-first approach
            const hasMobileFirst = content.includes('max-w-') || content.includes('px-4');
            logTest(
                `${path.basename(filePath)} uses mobile-first approach`,
                hasMobileFirst,
                'Mobile-first utilities found'
            );

        } catch (error) {
            logTest(`Check responsive design in ${filePath}`, false, error.message);
        }
    });
}

// Test 8: UI/UX consistency check
function testUIConsistency() {
    logSection('Test 8: UI/UX Consistency Check');

    const pages = [
        'frontend/app/[locale]/privacy/page.tsx',
        'frontend/app/[locale]/terms/page.tsx',
        'frontend/app/[locale]/contact/page.tsx',
        'frontend/app/[locale]/about/page.tsx'
    ];

    const commonPatterns = {
        'Uses StaticPageLayout': 'StaticPageLayout',
        'Has icon decoration': 'Icon',
        'Has CTA section': 'showCTA',
        'Uses gradient backgrounds': 'bg-gradient',
        'Has proper spacing': 'mb-',
        'Uses consistent colors': 'text-gray-'
    };

    pages.forEach(pagePath => {
        const fullPath = path.join(__dirname, pagePath);
        const pageName = path.basename(path.dirname(pagePath));

        try {
            const content = fs.readFileSync(fullPath, 'utf8');

            Object.entries(commonPatterns).forEach(([testName, pattern]) => {
                const hasPattern = content.includes(pattern);
                logTest(
                    `${pageName} - ${testName}`,
                    hasPattern,
                    hasPattern ? 'Pattern found' : 'Pattern missing'
                );
            });

        } catch (error) {
            // Page might not exist, skip
            logWarning(`Could not check ${pageName}: ${error.message}`);
        }
    });
}

// Main test execution
function runAllTests() {
    console.log(`${colors.bright}${colors.cyan}`);
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║   Static Pages Fix - Final Testing & Validation Suite     ║');
    console.log('║   Task 7: تست نهایی و اعتبارسنجی                          ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log(colors.reset);

    // Run all test suites
    testTranslationKeys();
    testPrivacyPage();
    testTermsPage();
    testStaticPageLayout();
    testOtherStaticPages();
    testForCommonErrors();
    testResponsiveDesign();
    testUIConsistency();

    // Print summary
    logSection('Test Summary');
    console.log(`${colors.green}✓ Passed:${colors.reset}  ${testResults.passed}`);
    console.log(`${colors.red}✗ Failed:${colors.reset}  ${testResults.failed}`);
    console.log(`${colors.yellow}⚠ Warnings:${colors.reset} ${testResults.warnings}`);
    console.log(`${colors.cyan}Total Tests:${colors.reset} ${testResults.passed + testResults.failed}\n`);

    // Overall result
    if (testResults.failed === 0) {
        console.log(`${colors.bright}${colors.green}╔════════════════════════════════════════╗`);
        console.log(`║   ✓ ALL TESTS PASSED SUCCESSFULLY!    ║`);
        console.log(`╚════════════════════════════════════════╝${colors.reset}\n`);
    } else {
        console.log(`${colors.bright}${colors.red}╔════════════════════════════════════════╗`);
        console.log(`║   ✗ SOME TESTS FAILED - REVIEW NEEDED ║`);
        console.log(`╚════════════════════════════════════════╝${colors.reset}\n`);
    }

    // Manual testing checklist
    console.log(`${colors.bright}${colors.blue}Manual Testing Checklist:${colors.reset}`);
    console.log(`
${colors.cyan}1. Browser Testing:${colors.reset}
   □ Test Privacy page in Chrome, Firefox, Safari
   □ Test Terms page in Chrome, Firefox, Safari
   □ Check console for IntlError messages
   
${colors.cyan}2. Language Testing:${colors.reset}
   □ Test Privacy page in Persian (fa)
   □ Test Privacy page in English (en)
   □ Test Privacy page in Turkish (tr)
   □ Test Terms page in Persian (fa)
   □ Test Terms page in English (en)
   □ Test Terms page in Turkish (tr)
   
${colors.cyan}3. Footer Testing:${colors.reset}
   □ Verify Footer on Privacy page
   □ Verify Footer on Terms page
   □ Verify Footer on FAQ page
   □ Verify Footer on About page
   □ Verify Footer on Contact page
   
${colors.cyan}4. Theme Testing:${colors.reset}
   □ Test Privacy page in Light mode
   □ Test Privacy page in Dark mode
   □ Test Terms page in Light mode
   □ Test Terms page in Dark mode
   □ Check text readability in both modes
   □ Check background colors in both modes
   
${colors.cyan}5. Responsive Testing:${colors.reset}
   □ Test on Desktop (1920x1080)
   □ Test on Tablet (768x1024)
   □ Test on Mobile (375x667)
   □ Check layout breaks at different sizes
   
${colors.cyan}6. UI/UX Consistency:${colors.reset}
   □ Compare Privacy page with Contact page
   □ Compare Terms page with About page
   □ Check icon consistency
   □ Check spacing consistency
   □ Check color scheme consistency
   
${colors.cyan}7. Navigation Testing:${colors.reset}
   □ Test links in Footer
   □ Test CTA buttons
   □ Test language switcher
   □ Test back navigation
  `);

    return testResults.failed === 0 ? 0 : 1;
}

// Run tests
const exitCode = runAllTests();
process.exit(exitCode);
