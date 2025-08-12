#!/usr/bin/env python3
"""
Test script for the Linux scraper
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli_version import TweetScraper, ProfileManager

def test_scraper():
    """Test the scraper functionality"""
    print("=== Testing Linux Scraper ===")
    
    # Test profile manager
    print("\n1. Testing Profile Manager...")
    profile_manager = ProfileManager()
    profiles = profile_manager.get_all_profiles()
    print(f"Found {len(profiles)} profiles: {profiles}")
    
    # Test scraper with a sample tweet
    print("\n2. Testing Scraper...")
    test_url = "https://twitter.com/elonmusk/status/1234567890123456789"  # Replace with a real tweet URL
    
    # Create a test profile if none exists
    if not profiles:
        print("Creating test profile...")
        profile_manager.add_profile("test_profile", "chrome-data/test_profile")
        profiles = ["test_profile"]
    
    profile_name = profiles[0] if profiles else "test_profile"
    print(f"Using profile: {profile_name}")
    
    # Initialize scraper
    scraper = TweetScraper(profile_name)
    print("Setting up Chrome driver...")
    
    if scraper.setup_driver():
        print("✓ Chrome driver initialized successfully")
        
        # Test scraping (this will likely fail with the fake URL, but should show the process)
        print(f"\n3. Testing tweet scraping with URL: {test_url}")
        try:
            content = scraper.scrape_tweet_content(test_url)
            if content:
                print(f"✓ Successfully scraped content: {content[:100]}...")
            else:
                print("✗ No content found (expected with fake URL)")
        except Exception as e:
            print(f"✗ Scraping failed: {e}")
        
        scraper.cleanup()
    else:
        print("✗ Failed to initialize Chrome driver")
        print("Testing fallback requests-based scraping...")
        
        try:
            content = scraper._scrape_with_requests(test_url)
            if content:
                print(f"✓ Successfully scraped content (requests): {content[:100]}...")
            else:
                print("✗ No content found with requests (expected with fake URL)")
        except Exception as e:
            print(f"✗ Requests scraping failed: {e}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_scraper()
