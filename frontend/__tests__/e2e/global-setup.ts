import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use;
  
  console.log('🚀 Starting global setup for E2E tests...');
  
  // Launch browser for setup
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Test if the application is running
    console.log(`📡 Testing connection to ${baseURL}...`);
    await page.goto(baseURL!);
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check if the application is accessible
    const title = await page.title();
    console.log(`✅ Application is running. Page title: ${title}`);
    
    // You can add more setup tasks here, such as:
    // - Creating test data
    // - Setting up test users
    // - Configuring test environment
    // - Clearing test database
    
    console.log('✅ Global setup completed successfully');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;
