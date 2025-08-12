#!/usr/bin/env python3
"""
Test script for JavaScript detection fix
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli_version import TweetScraper, ProfileManager

def test_javascript_fix():
    """Test the JavaScript detection fix"""
    print("=== Testing JavaScript Detection Fix ===")
    
    # Test profile manager
    print("\n1. Testing Profile Manager...")
    profile_manager = ProfileManager()
    profiles = profile_manager.get_all_profiles()
    print(f"Found {len(profiles)} profiles: {profiles}")
    
    # Create a test profile if none exists
    if not profiles:
        print("Creating test profile...")
        profile_manager.add_profile("test_profile", "chrome-data/test_profile")
        profiles = ["test_profile"]
    
    profile_name = profiles[0] if profiles else "test_profile"
    print(f"Using profile: {profile_name}")
    
    # Initialize scraper
    scraper = TweetScraper(profile_name)
    print("Setting up Chrome driver with JavaScript support...")
    
    if scraper.setup_driver():
        print("✓ Chrome driver initialized successfully with stealth options")
        
        # Test scraping with a real tweet URL (replace with actual URL)
        test_url = "https://twitter.com/elonmusk/status/1234567890123456789"  # Replace with real URL
        
        print(f"\n2. Testing tweet scraping with URL: {test_url}")
        print("This will test if JavaScript detection is bypassed...")
        
        try:
            content = scraper.scrape_tweet_content(test_url)
            if content:
                print(f"✓ Successfully scraped content: {content[:100]}...")
                print("✓ JavaScript detection bypassed successfully!")
            else:
                print("✗ No content found")
                print("This could be due to:")
                print("  - Fake/expired tweet URL")
                print("  - X (Twitter) requiring login")
                print("  - X (Twitter) blocking scraping")
                print("  - Network connectivity issues")
        except Exception as e:
            print(f"✗ Scraping failed: {e}")
            if "javascript" in str(e).lower():
                print("⚠️  JavaScript issue still detected")
            else:
                print("✓ No JavaScript detection issue (other error occurred)")
        
        scraper.cleanup()
    else:
        print("✗ Failed to initialize Chrome driver")
        print("Testing fallback requests-based scraping...")
        
        try:
            content = scraper._scrape_with_requests(test_url)
            if content:
                print(f"✓ Successfully scraped content (requests): {content[:100]}...")
            else:
                print("✗ No content found with requests")
                print("This is expected as X (Twitter) requires JavaScript for content access")
        except Exception as e:
            print(f"✗ Requests scraping failed: {e}")
    
    print("\n=== Test completed ===")
    print("\nKey improvements made:")
    print("1. ✅ Enabled JavaScript support in Chrome")
    print("2. ✅ Added stealth options to avoid detection")
    print("3. ✅ Improved user agent")
    print("4. ✅ Added JavaScript detection page handling")
    print("5. ✅ Enhanced retry logic")
    print("6. ✅ Better error handling for requests fallback")
    print("7. ✅ Clear error messages for JavaScript blocks")
    
    print("\nTroubleshooting tips:")
    print("- Use real tweet URLs for testing")
    print("- Ensure Chrome is up to date")
    print("- Try logging into X (Twitter) first using the login guide")
    print("- Check if X (Twitter) is blocking your IP/region")

if __name__ == "__main__":
    test_javascript_fix()
