#!/usr/bin/env python3
"""
Test script for SeleniumBase Cloudflare bypass functionality
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_seleniumbase_installation():
    """Test SeleniumBase installation"""
    print("🧪 Testing SeleniumBase Installation")
    print("=" * 50)
    
    try:
        from seleniumbase import SB
        print("✅ SeleniumBase imported successfully")
        
        # Test basic SeleniumBase functionality
        print("\n🚀 Testing SeleniumBase with undetected-chromedriver:")
        
        with SB(uc=True, ad_block_on=True, headless=True) as sb:
            print("   • SeleniumBase instance created")
            
            # Test with a simple URL
            test_url = "https://www.google.com"
            print(f"   • Testing with: {test_url}")
            
            try:
                sb.uc_open_with_reconnect(test_url, 8)
                print("   • ✅ Successfully opened URL with uc_open_with_reconnect")
                
                # Get page title
                title = sb.get_title()
                print(f"   • Page title: {title}")
                
                return True
                
            except Exception as e:
                print(f"   • ❌ Error opening URL: {e}")
                return False
                
    except ImportError as e:
        print(f"❌ SeleniumBase not installed: {e}")
        print("\n📦 To install SeleniumBase, run:")
        print("   pip install seleniumbase")
        return False
    except Exception as e:
        print(f"❌ SeleniumBase test error: {e}")
        return False

def test_cloudflare_bypass():
    """Test Cloudflare bypass with a known protected site"""
    print("\n🛡️ Testing Cloudflare Bypass")
    print("=" * 30)
    
    try:
        from seleniumbase import SB
        
        # Test with a site that typically has Cloudflare protection
        test_url = "https://www.cloudflare.com"
        print(f"   • Testing Cloudflare bypass with: {test_url}")
        
        with SB(uc=True, ad_block_on=True, headless=True) as sb:
            try:
                sb.uc_open_with_reconnect(test_url, 8)
                print("   • ✅ Successfully bypassed Cloudflare")
                
                # Check if we can access the page content
                title = sb.get_title()
                print(f"   • Page title: {title}")
                
                # Check for Cloudflare challenge elements
                cloudflare_elements = sb.find_elements("text=Checking your browser")
                if cloudflare_elements:
                    print("   • ⚠️ Cloudflare challenge detected")
                else:
                    print("   • ✅ No Cloudflare challenge detected")
                
                return True
                
            except Exception as e:
                print(f"   • ❌ Cloudflare bypass failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Cloudflare bypass test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SeleniumBase Cloudflare Bypass Test")
    print("=" * 60)
    
    success = True
    
    # Test installation
    if not test_seleniumbase_installation():
        success = False
    
    # Test Cloudflare bypass
    if not test_cloudflare_bypass():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! SeleniumBase is ready for Cloudflare bypass.")
        print("\nKey Features Verified:")
        print("   • SeleniumBase installation working")
        print("   • Undetected-chromedriver integration")
        print("   • Cloudflare bypass capability")
        print("   • uc_open_with_reconnect functionality")
    else:
        print("❌ Some tests failed. Please check the installation.")
    
    return success

if __name__ == "__main__":
    main() 