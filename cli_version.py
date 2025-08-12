#!/usr/bin/env python3
"""
Twitter Automation CLI Version
For running on Linux servers without GUI
"""

import sys
import os
import json
import time
import random
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Import required modules
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Error: Missing required module - {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


class ProfileManager:
    """Class to manage Chrome profiles"""
    
    def __init__(self):
        self.app_state_dir = Path("app/state")
        self.app_state_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_file = self.app_state_dir / "profiles.json"
        self.profiles = self.load_profiles()
    
    def load_profiles(self) -> Dict[str, Dict]:
        """Load saved profiles from JSON file"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profiles: {e}")
                return {}
        return {}
    
    def save_profiles(self):
        """Save profiles to JSON file"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def add_profile(self, profile_name: str, profile_path: str) -> bool:
        """Add a new profile"""
        if profile_name in self.profiles:
            return False
        
        self.profiles[profile_name] = {
            "name": profile_name,
            "path": profile_path,
            "created": datetime.now().isoformat(),
            "last_used": None
        }
        self.save_profiles()
        return True
    
    def get_profile(self, profile_name: str) -> Optional[Dict]:
        """Get profile by name"""
        return self.profiles.get(profile_name)
    
    def get_all_profiles(self) -> List[str]:
        """Get list of all profile names"""
        return list(self.profiles.keys())
    
    def update_last_used(self, profile_name: str):
        """Update last used timestamp for profile"""
        if profile_name in self.profiles:
            self.profiles[profile_name]["last_used"] = datetime.now().isoformat()
            self.save_profiles()
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile"""
        if profile_name in self.profiles:
            del self.profiles[profile_name]
            self.save_profiles()
            return True
        return False


class TweetScraper:
    """Class to scrape tweet content using Chrome profile"""
    
    def __init__(self, profile_name: str = None):
        self.profile_name = profile_name
        self.driver = None
    
    def setup_driver(self, profile_name: str = None, use_gui: bool = False, display: str = ":1"):
        """Setup Chrome driver with profile"""
        if profile_name:
            self.profile_name = profile_name
            
        if not self.profile_name:
            raise ValueError("Profile name is required")
            
        try:
            chrome_options = Options()
            
            # Set up user data directory - use absolute path for Linux
            if os.name == 'posix':  # Linux
                profile_dir = os.path.expanduser(f"~/.config/chrome_profiles/{self.profile_name}")
            else:  # Windows/Other
                profile_dir = f"chrome-data/{self.profile_name}"
            
            os.makedirs(profile_dir, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={os.path.abspath(profile_dir)}")
            
            # VNC support for Linux
            if os.name == 'posix' and use_gui:
                print(f"Setting up Chrome in GUI mode for VNC display {display}")
                os.environ["DISPLAY"] = display
                # Don't use headless mode for VNC
            else:
                # Enable JavaScript and improve compatibility
                chrome_options.add_argument("--enable-javascript")
                chrome_options.add_argument("--enable-scripts")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--allow-running-insecure-content")
            
            # Common options for both modes
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            
            # Only set debugging port if not in GUI mode
            if not use_gui:
                chrome_options.add_argument("--remote-debugging-port=9222")
            
            # Additional options for better automation and stealth
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            
            # Set user agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Experimental options for stealth
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.media_stream": 2,
            })
            
            # Try to use system ChromeDriver on Linux
            if os.name == 'posix':
                try:
                    print("Using system ChromeDriver on Linux...")
                    service = Service('/usr/local/bin/chromedriver')
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    print("System ChromeDriver initialized successfully")
                except Exception as e:
                    print(f"System ChromeDriver failed: {e}")
                    # Fallback to webdriver-manager
                    try:
                        print("Falling back to webdriver-manager...")
                        service = Service(ChromeDriverManager().install())
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        print("ChromeDriver downloaded and initialized successfully")
                    except Exception as e2:
                        print(f"All ChromeDriver attempts failed: {e2}")
                        return False
            else:
                # Non-Linux: Use webdriver-manager first
                try:
                    print("Attempting to download ChromeDriver...")
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    print("ChromeDriver downloaded and initialized successfully")
                except Exception as e:
                    print(f"webdriver-manager failed: {e}")
                    # Fallback: try to use system ChromeDriver
                    try:
                        print("Trying system ChromeDriver...")
                        self.driver = webdriver.Chrome(options=chrome_options)
                        print("System ChromeDriver initialized successfully")
                    except Exception as e2:
                        print(f"System ChromeDriver failed: {e2}")
                        # Last resort: try without service
                        try:
                            print("Trying ChromeDriver without service...")
                            self.driver = webdriver.Chrome(options=chrome_options)
                            print("ChromeDriver initialized without service")
                        except Exception as e3:
                            print(f"All ChromeDriver attempts failed: {e3}")
                            return False
            
            if self.driver:
                # Execute stealth scripts to avoid detection (not needed in GUI mode)
                if not use_gui:
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
                    self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
                    self.driver.execute_script("window.chrome = {runtime: {}}")
                    print("Chrome driver initialized successfully with stealth options")
                else:
                    print("Chrome driver initialized successfully in GUI mode")
                return True
            else:
                print("Failed to initialize Chrome driver")
                return False
                
        except Exception as e:
            print(f"Failed to setup Chrome driver: {str(e)}")
            return False
    
    def scrape_tweet_content(self, tweet_url: str) -> Optional[str]:
        """Scrape tweet content from URL using Chrome profile or fallback to requests"""
        # Try Chrome-based scraping first
        if self.driver or self.setup_driver():
            try:
                content = self._scrape_with_chrome(tweet_url)
                if content:
                    return content
                else:
                    print("Chrome scraping returned no content, trying requests fallback...")
            except Exception as e:
                print(f"Chrome scraping failed: {e}")
        
        # Fallback to requests-based scraping
        try:
            content = self._scrape_with_requests(tweet_url)
            if content:
                return content
            else:
                print("Requests fallback also failed - X (Twitter) may require JavaScript or login")
                return None
        except Exception as e:
            print(f"Requests scraping also failed: {e}")
            return None
    
    def _scrape_with_chrome(self, tweet_url: str) -> Optional[str]:
        """Scrape tweet content using Chrome"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Scraping with Chrome (attempt {attempt + 1}): {tweet_url}")
                self.driver.get(tweet_url)
                
                # Wait for page to load and check for JavaScript detection
                time.sleep(2)
                
                # Check if we're on a JavaScript detection page
                page_source = self.driver.page_source.lower()
                if "javascript" in page_source and ("disabled" in page_source or "not available" in page_source):
                    print("Detected JavaScript detection page, waiting for redirect...")
                    # Wait longer for potential redirect
                    time.sleep(5)
                    
                    # Try to refresh the page
                    self.driver.refresh()
                    time.sleep(3)
                
                # Wait for tweet content to load with multiple possible selectors
                tweet_found = False
                for selector in ['[data-testid="tweet"]', 'article[data-testid="tweet"]', '[data-testid="tweetText"]']:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        tweet_found = True
                        break
                    except TimeoutException:
                        continue
                
                if not tweet_found:
                    print("Tweet content not found, waiting longer...")
                    time.sleep(5)
                
                # Additional wait for content to fully load
                time.sleep(3)
                
                # Try to find tweet text content with multiple selectors
                tweet_text = None
                
                # Look for tweet text in various possible selectors (matching main.py)
                selectors = [
                    'div[data-testid="tweetText"]',
                    'div[lang]',
                    '.tweet-text',
                    '[data-testid="tweet"] div[lang]',
                    'article[data-testid="tweet"] div[lang]',
                    '[data-testid="tweet"] span[lang]',
                    'div[data-testid="tweet"] span',
                    'article div[lang]',
                    '[data-testid="tweetText"]',
                    '[data-testid="tweet"] [lang]',
                    '[data-testid="tweet"] div[dir="auto"]',
                    'article[data-testid="tweet"] div[dir="auto"]',
                    'div[data-testid="tweet"] div[dir="auto"]',
                    'span[data-testid="tweetText"]'
                ]
                
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            for element in elements:
                                text = element.text.strip()
                                if text and len(text) > 10:  # Ensure we have meaningful content
                                    tweet_text = text
                                    break
                            if tweet_text:
                                break
                    except Exception:
                        continue
                
                if tweet_text:
                    # Normalize the content to a single line
                    normalized_content = self._normalize_tweet_content(tweet_text)
                    print(f"Successfully scraped tweet content: {normalized_content[:100]}...")
                    return normalized_content
                else:
                    # If no text found, try to wait a bit more and retry
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed: No content found, retrying...")
                        time.sleep(3)
                        continue
                    else:
                        print("No tweet content found after all attempts")
                        return None
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(3)
                    continue
                else:
                    print(f"Error scraping with Chrome: {e}")
                    return None
        
        return None
    
    def _scrape_with_requests(self, tweet_url: str) -> Optional[str]:
        """Fallback scraping using requests"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Scraping with requests (attempt {attempt + 1}): {tweet_url}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                }
                
                response = requests.get(tweet_url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Check if we got a JavaScript detection page
                content_lower = response.text.lower()
                if "javascript" in content_lower and ("disabled" in content_lower or "not available" in content_lower):
                    print("Requests fallback detected JavaScript block - X (Twitter) requires JavaScript")
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed: JavaScript required, retrying...")
                        time.sleep(2)
                        continue
                    else:
                        print("All attempts failed: X (Twitter) requires JavaScript for content access")
                        return None
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find tweet text content
                tweet_text = None
                
                # Look for tweet text in various possible selectors (matching main.py)
                selectors = [
                    'div[data-testid="tweetText"]',
                    'div[lang]',
                    '.tweet-text',
                    '[data-testid="tweet"] div[lang]',
                    'article[data-testid="tweet"] div[lang]',
                    '[data-testid="tweet"] span[lang]',
                    'div[data-testid="tweet"] span',
                    'article div[lang]',
                    '[data-testid="tweetText"]',
                    '[lang]',
                    'div[dir="auto"]',
                    'p',
                    'span'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        for element in elements:
                            text = element.get_text(strip=True)
                            if text and len(text) > 10:  # Ensure we have meaningful content
                                tweet_text = text
                                break
                        if tweet_text:
                            break
                
                if tweet_text:
                    # Normalize the content to a single line
                    normalized_content = self._normalize_tweet_content(tweet_text)
                    print(f"Successfully scraped tweet content (requests): {normalized_content[:100]}...")
                    return normalized_content
                elif attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: No content found, retrying...")
                    time.sleep(2)
                    continue
                else:
                    print("No tweet content found with requests after all attempts")
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    print(f"Error scraping with requests: {e}")
                    return None
        
        return None
    
    def _normalize_tweet_content(self, content: str) -> str:
        """Normalize tweet content to single line"""
        if not content:
            return ""
        # Split by any whitespace and rejoin with single spaces
        return ' '.join(content.split())
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing driver: {e}")


class TwitterAutomation:
    """Class to perform Twitter automation (like, retweet, reply)"""
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.driver = None
    
    def setup_driver(self):
        """Setup Chrome driver with profile"""
        try:
            chrome_options = Options()
            
            # Set up user data directory
            profile_dir = f"chrome-data/{self.profile_name}"
            os.makedirs(profile_dir, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={os.path.abspath(profile_dir)}")
            
            # Enable JavaScript and improve compatibility
            chrome_options.add_argument("--enable-javascript")
            chrome_options.add_argument("--enable-scripts")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Additional options for better automation and stealth
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--remote-debugging-port=9223")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            
            # Set user agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Experimental options for stealth
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.media_stream": 2,
            })
            
            # Try to use webdriver-manager to get the correct ChromeDriver
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                print("Attempting to download ChromeDriver...")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("ChromeDriver downloaded and initialized successfully")
            except Exception as e:
                print(f"webdriver-manager failed: {e}")
                # Fallback: try to use system ChromeDriver
                try:
                    print("Trying system ChromeDriver...")
                    self.driver = webdriver.Chrome(options=chrome_options)
                    print("System ChromeDriver initialized successfully")
                except Exception as e2:
                    print(f"System ChromeDriver failed: {e2}")
                    # Last resort: try without service
                    try:
                        print("Trying ChromeDriver without service...")
                        self.driver = webdriver.Chrome(options=chrome_options)
                        print("ChromeDriver initialized without service")
                    except Exception as e3:
                        print(f"All ChromeDriver attempts failed: {e3}")
                        return False
            
            if self.driver:
                # Execute stealth scripts to avoid detection
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
                self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
                self.driver.execute_script("window.chrome = {runtime: {}}")
                print("Chrome driver initialized successfully with stealth options")
                return True
            else:
                print("Failed to initialize Chrome driver")
                return False
                
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            return False
    
    def process_tweet(self, tweet_url: str, reply_comment: str, actions: Dict[str, bool], max_retries: int = 3) -> bool:
        """Process a single tweet with selected actions and retries"""
        for attempt in range(max_retries):
            try:
                self.driver.get(tweet_url)
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
                )
                
                # Perform actions based on checkboxes
                success = True
                if actions.get('like', False):
                    if not self.like_tweet():
                        success = False
                        
                if actions.get('retweet', False):
                    if not self.retweet_tweet():
                        success = False
                        
                if actions.get('reply', False) and reply_comment:
                    if not self.reply_to_tweet(reply_comment):
                        success = False
                
                if success:
                    return True
                elif attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                    continue
                else:
                    return False
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {str(e)}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    print(f"Error processing tweet: {str(e)}")
                    return False
        
        return False
    
    def like_tweet(self):
        """Like the current tweet"""
        try:
            like_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="like"]'))
            )
            like_button.click()
            print("✓ Liked tweet")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Failed to like tweet: {str(e)}")
            return False
    
    def retweet_tweet(self):
        """Retweet the current tweet"""
        try:
            retweet_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="retweet"]'))
            )
            retweet_button.click()
            
            # Click the retweet confirm button
            confirm_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="retweetConfirm"]'))
            )
            confirm_button.click()
            
            print("✓ Retweeted")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Failed to retweet: {str(e)}")
            return False
    
    def reply_to_tweet(self, comment: str):
        """Reply to the current tweet"""
        try:
            reply_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="reply"]'))
            )
            reply_button.click()
            
            # Find and fill the reply text area
            reply_textarea = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            reply_textarea.clear()
            reply_textarea.send_keys(comment)
            
            # Click reply button
            reply_submit = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
            )
            reply_submit.click()
            
            print(f"✓ Replied: {comment[:50]}...")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Failed to reply: {str(e)}")
            return False
    
    def log_to_file(self, filename: str, message: str):
        """Log message to file with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing driver: {e}")


class TwitterAutomationCLI:
    """Main CLI class for Twitter automation"""
    
    def __init__(self):
        self.profile_manager = ProfileManager()
    
    def list_profiles(self):
        """List all saved profiles"""
        profiles = self.profile_manager.get_all_profiles()
        if profiles:
            print("Saved profiles:")
            for profile in profiles:
                profile_data = self.profile_manager.get_profile(profile)
                created = profile_data.get('created', 'Unknown')
                last_used = profile_data.get('last_used', 'Never')
                print(f"  - {profile} (Created: {created}, Last used: {last_used})")
        else:
            print("No saved profiles found.")
    
    def create_profile(self, profile_name: str):
        """Create a new profile with full Chrome profile structure"""
        if not profile_name:
            print("Error: Profile name is required")
            return False
        
        profile_path = f"chrome-data/{profile_name}"
        
        # Create the full Chrome profile directory structure
        try:
            import os
            import json
            from datetime import datetime
            
            # Create main profile directory
            os.makedirs(profile_path, exist_ok=True)
            
            # Create Chrome profile subdirectories
            chrome_dirs = [
                "Default",
                "Default/Cookies-journal",
                "Default/Code Cache",
                "Default/Code Cache/js",
                "Default/Code Cache/wasm",
                "Default/GPUCache",
                "Default/IndexedDB",
                "Default/Local Storage",
                "Default/Network",
                "Default/Session Storage",
                "Default/Service Worker",
                "Default/Storage",
                "Default/WebStorage",
                "Default/WebStorage/000003.log",
                "Default/WebStorage/000003.ldb",
                "Default/WebStorage/CURRENT",
                "Default/WebStorage/LOCK",
                "Default/WebStorage/LOG",
                "Default/WebStorage/MANIFEST-000001",
                "GrShaderCache",
                "ShaderCache",
                "GPUCache",
                "Local State",
                "Preferences",
                "Secure Preferences",
                "Web Data",
                "Web Data-journal"
            ]
            
            for dir_path in chrome_dirs:
                full_path = os.path.join(profile_path, dir_path)
                if dir_path.endswith('/'):
                    os.makedirs(full_path, exist_ok=True)
                else:
                    # Create directory for files
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    # Create empty files for important Chrome files
                    if any(file in dir_path for file in ['Local State', 'Preferences', 'Secure Preferences', 'Web Data']):
                        if not os.path.exists(full_path):
                            with open(full_path, 'w') as f:
                                if 'Preferences' in dir_path:
                                    # Basic Chrome preferences
                                    prefs = {
                                        "profile": {
                                            "name": profile_name,
                                            "created": datetime.now().isoformat()
                                        },
                                        "browser": {
                                            "window_placement": {
                                                "maximized": True
                                            }
                                        },
                                        "session": {
                                            "restore_on_startup": 4
                                        }
                                    }
                                    json.dump(prefs, f, indent=2)
                                elif 'Local State' in dir_path:
                                    # Basic local state
                                    local_state = {
                                        "browser": {
                                            "profile": {
                                                "name": profile_name
                                            }
                                        },
                                        "user_experience_metrics": {
                                            "stability": {
                                                "exited_cleanly": True
                                            }
                                        }
                                    }
                                    json.dump(local_state, f, indent=2)
                                else:
                                    # Empty file for other important files
                                    f.write("")
            
            # Create a profile info file
            profile_info = {
                "name": profile_name,
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "description": f"Chrome profile for {profile_name}",
                "path": os.path.abspath(profile_path)
            }
            
            with open(os.path.join(profile_path, "profile_info.json"), 'w') as f:
                json.dump(profile_info, f, indent=2)
            
            # Add to profile manager
            if self.profile_manager.add_profile(profile_name, profile_path):
                print(f"✅ Profile '{profile_name}' created successfully")
                print(f"📁 Profile directory: {os.path.abspath(profile_path)}")
                print(f"🎯 To launch this profile in VNC:")
                print(f"   ./launch_chrome_vnc.sh {profile_name}")
                print(f"   or")
                print(f"   ./run_cli.sh --launch-browser {profile_name}")
                return True
            else:
                print(f"Error: Profile '{profile_name}' already exists")
                return False
                
        except Exception as e:
            print(f"Error creating profile: {e}")
            return False
    
    def delete_profile(self, profile_name: str):
        """Delete a profile"""
        if not profile_name:
            print("Error: Profile name is required")
            return False
        
        if self.profile_manager.delete_profile(profile_name):
            # Also delete the profile directory
            profile_dir = f"chrome-data/{profile_name}"
            if os.path.exists(profile_dir):
                import shutil
                try:
                    shutil.rmtree(profile_dir)
                    print(f"Profile directory '{profile_dir}' deleted")
                except Exception as e:
                    print(f"Warning: Could not delete profile directory: {e}")
            
            print(f"Profile '{profile_name}' deleted successfully")
            return True
        else:
            print(f"Error: Profile '{profile_name}' not found")
            return False
    
    def launch_profile_browser(self, profile_name: str):
        """Launch Chrome browser for a profile with VNC support"""
        if not profile_name:
            print("Error: Profile name is required")
            return False
        
        profile_dir = f"chrome-data/{profile_name}"
        if not os.path.exists(profile_dir):
            print(f"Error: Profile directory '{profile_dir}' not found")
            print(f"Please create the profile first: ./run_cli.sh --create-profile {profile_name}")
            return False
        
        try:
            import subprocess
            import platform
            
            # Check if VNC is running (Linux only)
            vnc_running = False
            if platform.system() == "Linux":
                try:
                    result = subprocess.run(['pgrep', '-f', 'vncserver.*:1'], capture_output=True, text=True)
                    vnc_running = result.returncode == 0
                except Exception:
                    pass
            
            # Chrome command for different platforms
            if platform.system() == "Linux":
                chrome_cmd = "google-chrome"
            elif platform.system() == "Darwin":  # macOS
                chrome_cmd = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            else:  # Windows
                chrome_cmd = "chrome"
            
            # Set up Chrome options for VNC
            chrome_options = [
                chrome_cmd,
                f"--user-data-dir={os.path.abspath(profile_dir)}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-notifications",
                "--start-maximized",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            
            # Add VNC-specific options if VNC is running
            if vnc_running and platform.system() == "Linux":
                os.environ["DISPLAY"] = ":1"
                print(f"🖥️  VNC detected - launching Chrome in GUI mode on display :1")
                chrome_options.extend([
                    "--disable-gpu-sandbox",
                    "--disable-software-rasterizer"
                ])
            elif platform.system() == "Linux":
                print(f"⚠️  VNC not detected - launching Chrome in headless mode")
                chrome_options.append("--headless")
            
            # Launch Chrome
            print(f"🚀 Launching Chrome with profile: {profile_name}")
            print(f"📁 Profile directory: {os.path.abspath(profile_dir)}")
            
            # Launch in background
            process = subprocess.Popen(
                chrome_options,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid if platform.system() == "Linux" else None
            )
            
            print(f"✅ Chrome launched successfully with PID: {process.pid}")
            
            if vnc_running and platform.system() == "Linux":
                print(f"🎯 Chrome should now be visible in your VNC viewer")
                # Get server IP for VNC connection
                try:
                    import socket
                    hostname = socket.gethostname()
                    ip_address = socket.gethostbyname(hostname)
                    print(f"🔗 VNC Connection: {ip_address}:5901")
                except:
                    print(f"🔗 VNC Connection: localhost:5901")
                print(f"📺 Display: :1")
            else:
                print(f"💡 To view Chrome in VNC, start VNC first:")
                print(f"   vncserver :1 -geometry 1920x1080 -depth 24")
                print(f"   Then run: ./launch_chrome_vnc.sh {profile_name}")
            
            return True
            
        except Exception as e:
            print(f"Error launching Chrome browser: {e}")
            return False
    
    def scrape_tweets(self, profile_name: str, tweet_links_file: str, output_file: str = "scraped_tweets.txt", max_retries: int = 3):
        """Scrape tweets from file"""
        if not profile_name:
            print("Error: Profile name is required")
            return False
        
        if not os.path.exists(tweet_links_file):
            print(f"Error: Tweet links file '{tweet_links_file}' not found")
            return False
        
        # Read tweet links
        with open(tweet_links_file, 'r', encoding='utf-8') as f:
            tweet_links = [line.strip() for line in f if line.strip()]
        
        if not tweet_links:
            print("Error: No tweet links found in file")
            return False
        
        print(f"Found {len(tweet_links)} tweet links to scrape")
        
        # Initialize scraper
        scraper = TweetScraper(profile_name)
        chrome_available = scraper.setup_driver()
        
        if chrome_available:
            print("Chrome driver initialized successfully")
        else:
            print("Chrome driver failed - using fallback requests-based scraping")
        
        # Scrape tweets
        scraped_content = []
        failed_links = []
        
        for i, link in enumerate(tweet_links, 1):
            print(f"Scraping tweet {i}/{len(tweet_links)}: {link}")
            
            # Try scraping with retries
            content = self._scrape_with_retries(scraper, link, max_retries)
            
            if content:
                scraped_content.append(content)
                print(f"✓ Successfully scraped tweet {i}")
            else:
                failed_links.append(link)
                print(f"✗ Failed to scrape tweet {i}")
            
            # Random delay between tweets
            if i < len(tweet_links):
                delay = random.randint(3, 5)
                print(f"Waiting {delay} seconds...")
                time.sleep(delay)
        
        # Save scraped content
        with open(output_file, 'w', encoding='utf-8') as f:
            for content in scraped_content:
                f.write(f"{content}\n")
        
        print(f"\nScraping completed!")
        print(f"Successfully scraped: {len(scraped_content)} tweets")
        print(f"Failed: {len(failed_links)} tweets")
        print(f"Results saved to: {output_file}")
        
        if failed_links:
            print("\nFailed links:")
            for link in failed_links:
                print(f"  - {link}")
        
        scraper.cleanup()
        return True
    
    def _scrape_with_retries(self, scraper: TweetScraper, link: str, max_retries: int = 3) -> Optional[str]:
        """Scrape with retry logic"""
        for attempt in range(max_retries):
            try:
                content = scraper.scrape_tweet_content(link)
                if content and content.strip():
                    return content
                elif attempt < max_retries - 1:
                    print(f"  Attempt {attempt + 1} failed: No content found, retrying...")
                    time.sleep(2)
                    continue
                else:
                    print(f"  All attempts failed: No content found")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  Attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    print(f"  All attempts failed: {e}")
        
        return None
    
    def run_automation(self, profile_name: str, tweet_links_file: str, reply_comments_file: str = None,
                      actions: Dict[str, bool] = None, min_wait: int = 5, max_wait: int = 15, max_retries: int = 3):
        """Run Twitter automation"""
        if not profile_name:
            print("Error: Profile name is required")
            return False
        
        if not os.path.exists(tweet_links_file):
            print(f"Error: Tweet links file '{tweet_links_file}' not found")
            return False
        
        # Read tweet links
        with open(tweet_links_file, 'r', encoding='utf-8') as f:
            tweet_links = [line.strip() for line in f if line.strip()]
        
        if not tweet_links:
            print("Error: No tweet links found in file")
            return False
        
        # Read reply comments if provided
        reply_comments = []
        if reply_comments_file and os.path.exists(reply_comments_file):
            with open(reply_comments_file, 'r', encoding='utf-8') as f:
                reply_comments = [line.strip() for line in f if line.strip()]
        
        # Default actions if none provided
        if not actions:
            actions = {'like': True, 'retweet': False, 'reply': False}
        
        print(f"Starting Twitter automation with profile: {profile_name}")
        print(f"Tweet links: {len(tweet_links)}")
        print(f"Reply comments: {len(reply_comments)}")
        print(f"Actions: {actions}")
        print(f"Wait time: {min_wait}-{max_wait} seconds")
        print(f"Max retries: {max_retries}")
        
        # Initialize automation
        automation = TwitterAutomation(profile_name)
        if not automation.setup_driver():
            print("Failed to initialize Chrome driver")
            return False
        
        # Randomize tweet order
        tweet_indices = list(range(len(tweet_links)))
        random.shuffle(tweet_indices)
        
        success_count = 0
        failure_count = 0
        
        try:
            for i, tweet_idx in enumerate(tweet_indices):
                tweet_url = tweet_links[tweet_idx]
                reply_comment = reply_comments[tweet_idx] if tweet_idx < len(reply_comments) else ""
                
                print(f"\nProcessing tweet {i+1}/{len(tweet_links)}: {tweet_url}")
                
                try:
                    success = automation.process_tweet(tweet_url, reply_comment, actions, max_retries)
                    
                    if success:
                        success_count += 1
                        automation.log_to_file("success_log.txt", f"SUCCESS: {tweet_url}")
                        print("✓ Tweet processed successfully")
                    else:
                        failure_count += 1
                        automation.log_to_file("failure_log.txt", f"FAILURE: {tweet_url}")
                        print("✗ Tweet processing failed")
                        
                except Exception as e:
                    failure_count += 1
                    automation.log_to_file("failure_log.txt", f"ERROR: {tweet_url} - {str(e)}")
                    print(f"✗ Error processing tweet: {str(e)}")
                
                # Random wait between tweets
                if i < len(tweet_links) - 1:
                    wait_time = random.randint(min_wait, max_wait)
                    print(f"Waiting {wait_time} seconds before next tweet...")
                    time.sleep(wait_time)
            
            print(f"\nAutomation completed!")
            print(f"Success: {success_count}, Failures: {failure_count}")
            
        except KeyboardInterrupt:
            print("\nAutomation interrupted by user")
        except Exception as e:
            print(f"\nAutomation error: {str(e)}")
        finally:
            automation.cleanup()
        
        return True


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Twitter Automation CLI')
    parser.add_argument('--list-profiles', action='store_true', help='List all saved profiles')
    parser.add_argument('--create-profile', type=str, help='Create a new profile')
    parser.add_argument('--delete-profile', type=str, help='Delete a profile')
    parser.add_argument('--scrape', action='store_true', help='Scrape tweets')
    parser.add_argument('--automate', action='store_true', help='Run automation')
    parser.add_argument('--launch-browser', type=str, help='Launch Chrome browser for a profile')
    parser.add_argument('--profile', type=str, help='Profile name to use')
    parser.add_argument('--tweet-links', type=str, default='tweet_links.txt', help='File containing tweet links')
    parser.add_argument('--reply-comments', type=str, help='File containing reply comments')
    parser.add_argument('--output', type=str, default='scraped_tweets.txt', help='Output file for scraped content')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum retries for each operation')
    parser.add_argument('--like', action='store_true', help='Like tweets')
    parser.add_argument('--retweet', action='store_true', help='Retweet tweets')
    parser.add_argument('--reply', action='store_true', help='Reply to tweets')
    parser.add_argument('--min-wait', type=int, default=5, help='Minimum wait time between tweets (seconds)')
    parser.add_argument('--max-wait', type=int, default=15, help='Maximum wait time between tweets (seconds)')
    
    args = parser.parse_args()
    
    cli = TwitterAutomationCLI()
    
    if args.list_profiles:
        cli.list_profiles()
    elif args.create_profile:
        cli.create_profile(args.create_profile)
    elif args.delete_profile:
        cli.delete_profile(args.delete_profile)
    elif args.scrape:
        if not args.profile:
            print("Error: --profile is required for scraping")
            sys.exit(1)
        cli.scrape_tweets(args.profile, args.tweet_links, args.output, args.max_retries)
    elif args.automate:
        if not args.profile:
            print("Error: --profile is required for automation")
            sys.exit(1)
        actions = {
            'like': args.like,
            'retweet': args.retweet,
            'reply': args.reply
        }
        cli.run_automation(args.profile, args.tweet_links, args.reply_comments, 
                          actions, args.min_wait, args.max_wait, args.max_retries)
    elif args.launch_browser:
        cli.launch_profile_browser(args.launch_browser)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
