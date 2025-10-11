#!/usr/bin/env python3
"""
Google OAuth Production Verification Script

This script verifies that Google OAuth is properly configured
in the production environment without requiring database access.
"""

import os
import sys
import requests
from urllib.parse import urljoin

# Production configuration
PRODUCTION_CONFIG = {
    'base_url': 'https://peykantravelistanbul.com',
    'api_base': 'https://peykantravelistanbul.com/api/v1',
    'google_auth_endpoint': '/auth/social/google/',
    'expected_client_id': '728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com',
    'test_pages': [
        '/en/login',
        '/en/register',
        '/tr/login',
        '/tr/register',
        '/fa/login',
        '/fa/register'
    ]
}

def log(message, status='info'):
    """Log message with status indicator."""
    prefix = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }.get(status, 'ℹ️')
    print(f"{prefix} {message}")

def test_production_site_accessibility():
    """Test if the production site is accessible."""
    log("Testing production site accessibility...")
    
    try:
        response = requests.get(PRODUCTION_CONFIG['base_url'], timeout=10)
        if response.status_code == 200:
            log("Production site is accessible", 'success')
            return True
        else:
            log(f"Production site returned status {response.status_code}", 'error')
            return False
    except requests.RequestException as e:
        log(f"Cannot access production site: {e}", 'error')
        return False

def test_google_oauth_endpoint():
    """Test Google OAuth API endpoint."""
    log("Testing Google OAuth API endpoint...")
    
    endpoint_url = PRODUCTION_CONFIG['api_base'] + PRODUCTION_CONFIG['google_auth_endpoint']
    
    try:
        # Test OPTIONS request (CORS preflight)
        options_response = requests.options(
            endpoint_url,
            headers={
                'Origin': PRODUCTION_CONFIG['base_url'],
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        
        cors_ok = options_response.status_code in [200, 204]
        
        # Test POST request with empty body (should return 400)
        post_response = requests.post(
            endpoint_url,
            json={},
            headers={
                'Content-Type': 'application/json',
                'Origin': PRODUCTION_CONFIG['base_url']
            },
            timeout=10
        )
        
        endpoint_ok = post_response.status_code == 400
        
        if cors_ok and endpoint_ok:
            log("Google OAuth endpoint is properly configured", 'success')
            log(f"Endpoint URL: {endpoint_url}")
            return True
        else:
            log("Google OAuth endpoint configuration issues:", 'error')
            log(f"  CORS OK: {cors_ok} (status: {options_response.status_code})")
            log(f"  Endpoint OK: {endpoint_ok} (status: {post_response.status_code})")
            return False
            
    except requests.RequestException as e:
        log(f"Cannot access Google OAuth endpoint: {e}", 'error')
        return False

def test_frontend_pages():
    """Test if frontend pages are accessible and contain Google OAuth setup."""
    log("Testing frontend pages for Google OAuth setup...")
    
    results = {}
    
    for page in PRODUCTION_CONFIG['test_pages']:
        page_url = PRODUCTION_CONFIG['base_url'] + page
        
        try:
            response = requests.get(page_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for Google OAuth indicators
                has_google_script = 'accounts.google.com/gsi/client' in content
                has_client_id = PRODUCTION_CONFIG['expected_client_id'] in content
                has_google_button_component = 'GoogleSignInButton' in content or 'google-signin' in content.lower()
                
                results[page] = {
                    'accessible': True,
                    'has_google_script': has_google_script,
                    'has_client_id': has_client_id,
                    'has_google_button': has_google_button_component
                }
                
                if has_google_script and has_client_id:
                    log(f"Page {page}: Google OAuth properly configured", 'success')
                else:
                    log(f"Page {page}: Missing Google OAuth configuration", 'warning')
                    if not has_google_script:
                        log(f"  Missing Google script reference")
                    if not has_client_id:
                        log(f"  Missing client ID in build")
                        
            else:
                results[page] = {'accessible': False, 'status_code': response.status_code}
                log(f"Page {page}: Not accessible (status: {response.status_code})", 'error')
                
        except requests.RequestException as e:
            results[page] = {'accessible': False, 'error': str(e)}
            log(f"Page {page}: Request failed - {e}", 'error')
    
    return results

def test_google_services_accessibility():
    """Test if Google OAuth services are accessible."""
    log("Testing Google OAuth services accessibility...")
    
    google_endpoints = [
        'https://accounts.google.com/gsi/client',
        'https://accounts.google.com/.well-known/openid_configuration'
    ]
    
    all_accessible = True
    
    for endpoint in google_endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                log(f"Google service accessible: {endpoint}", 'success')
            else:
                log(f"Google service issue: {endpoint} (status: {response.status_code})", 'warning')
                all_accessible = False
        except requests.RequestException as e:
            log(f"Cannot access Google service: {endpoint} - {e}", 'error')
            all_accessible = False
    
    return all_accessible

def generate_verification_report(site_ok, endpoint_ok, pages_results, google_services_ok):
    """Generate comprehensive verification report."""
    print("\n" + "="*60)
    print("📊 GOOGLE OAUTH PRODUCTION VERIFICATION REPORT")
    print("="*60)
    
    print(f"\n1. Production Site: {'✅ ACCESSIBLE' if site_ok else '❌ NOT ACCESSIBLE'}")
    print(f"2. OAuth Endpoint: {'✅ CONFIGURED' if endpoint_ok else '❌ ISSUES'}")
    print(f"3. Google Services: {'✅ ACCESSIBLE' if google_services_ok else '❌ ISSUES'}")
    
    print("\n4. Frontend Pages:")
    accessible_pages = 0
    configured_pages = 0
    
    for page, result in pages_results.items():
        if result.get('accessible'):
            accessible_pages += 1
            if result.get('has_google_script') and result.get('has_client_id'):
                configured_pages += 1
                status = "✅ CONFIGURED"
            else:
                status = "⚠️ PARTIAL"
        else:
            status = "❌ NOT ACCESSIBLE"
        
        print(f"   {page}: {status}")
    
    print(f"\n5. Summary:")
    print(f"   Pages Accessible: {accessible_pages}/{len(PRODUCTION_CONFIG['test_pages'])}")
    print(f"   Pages Configured: {configured_pages}/{len(PRODUCTION_CONFIG['test_pages'])}")
    
    # Overall assessment
    overall_ok = (site_ok and endpoint_ok and google_services_ok and 
                  configured_pages >= len(PRODUCTION_CONFIG['test_pages']) // 2)
    
    print(f"\n6. Overall Status: {'✅ READY FOR TESTING' if overall_ok else '❌ NEEDS ATTENTION'}")
    
    if overall_ok:
        print("\n🎉 Google OAuth appears to be properly configured!")
        print("   Ready for end-to-end testing with real user authentication.")
    else:
        print("\n⚠️ Issues detected that may affect Google OAuth functionality:")
        if not site_ok:
            print("   - Production site not accessible")
        if not endpoint_ok:
            print("   - OAuth API endpoint issues")
        if not google_services_ok:
            print("   - Google services not accessible")
        if configured_pages < len(PRODUCTION_CONFIG['test_pages']) // 2:
            print("   - Frontend pages missing OAuth configuration")
    
    print(f"\n📅 Verification completed at: {requests.utils.default_headers()}")
    print("="*60)
    
    return overall_ok

def main():
    """Run all verification tests."""
    print("🚀 Starting Google OAuth Production Verification...\n")
    
    try:
        # Run verification tests
        site_ok = test_production_site_accessibility()
        endpoint_ok = test_google_oauth_endpoint()
        pages_results = test_frontend_pages()
        google_services_ok = test_google_services_accessibility()
        
        # Generate report
        overall_ok = generate_verification_report(
            site_ok, endpoint_ok, pages_results, google_services_ok
        )
        
        # Exit with appropriate code
        sys.exit(0 if overall_ok else 1)
        
    except KeyboardInterrupt:
        log("Verification interrupted by user", 'warning')
        sys.exit(1)
    except Exception as e:
        log(f"Verification failed with error: {e}", 'error')
        sys.exit(1)

if __name__ == '__main__':
    main()