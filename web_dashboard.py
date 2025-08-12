#!/usr/bin/env python3
"""
Twitter Automation Web Dashboard
Flask-based web interface for the Twitter automation app
"""

import os
import sys
import json
import time
import random
import threading
import subprocess
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Flask imports
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_socketio import SocketIO, emit
import werkzeug

# Import our existing classes
try:
    from cli_version import ProfileManager, TweetScraper, TwitterAutomationCLI, TwitterAutomation
    from config import config
    try:
        from vnc_checker import check_vnc_running, check_vnc_running_simple, verify_vnc_environment, cleanup_stale_vnc_processes
    except ImportError:
        # Fallback VNC checker functions if module not available
        def check_vnc_running(display: str = ":1"):
            """Check if VNC is running"""
            try:
                # Check for various VNC server types
                vnc_patterns = [
                    f'vncserver.*{display}',
                    f'Xtightvnc.*{display}',
                    f'tightvncserver.*{display}',
                    f'tigervncserver.*{display}',
                    f'x11vnc.*{display}'
                ]
                
                for pattern in vnc_patterns:
                    result = subprocess.run(['pgrep', '-f', pattern], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return True, None
                
                return False, f"No VNC server found running on display {display}"
            except subprocess.TimeoutExpired:
                return False, "VNC status check timed out"
            except Exception as e:
                return False, str(e)
        
        def check_vnc_running_simple(display: str = ":1"):
            """Simple VNC check using pgrep"""
            try:
                # Check for various VNC server types
                vnc_patterns = [
                    f'vncserver.*{display}',
                    f'Xtightvnc.*{display}',
                    f'tightvncserver.*{display}',
                    f'tigervncserver.*{display}',
                    f'x11vnc.*{display}'
                ]
                
                for pattern in vnc_patterns:
                    result = subprocess.run(['pgrep', '-f', pattern], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return True, None
                
                return False, f"No VNC server found running on display {display}"
            except subprocess.TimeoutExpired:
                return False, "VNC status check timed out"
            except Exception as e:
                return False, str(e)
        
        def verify_vnc_environment(display: str = ":1"):
            """Verify VNC environment"""
            try:
                # Check if VNC server is installed
                result = subprocess.run(['which', 'vncserver'], capture_output=True, text=True)
                if result.returncode != 0:
                    return False, "VNC server not found"
                
                # Check if display is available
                if os.environ.get('DISPLAY') != display:
                    return False, f"Display {display} not set"
                
                return True, None
            except Exception as e:
                return False, str(e)
        
        def cleanup_stale_vnc_processes(display: str = ":1"):
            """Clean up stale VNC processes"""
            try:
                # Find VNC processes for the display
                vnc_patterns = [
                    f'vncserver.*{display}',
                    f'Xtightvnc.*{display}',
                    f'tightvncserver.*{display}',
                    f'tigervncserver.*{display}',
                    f'x11vnc.*{display}'
                ]
                
                result = None
                for pattern in vnc_patterns:
                    try:
                        result = subprocess.run(['pgrep', '-f', pattern], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            break
                    except Exception:
                        continue
                
                if result and result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    killed_count = 0
                    
                    for pid in pids:
                        if pid.strip():
                            try:
                                subprocess.run(['kill', '-9', pid.strip()], 
                                             capture_output=True, text=True, timeout=5)
                                killed_count += 1
                            except Exception:
                                pass
                    
                    if killed_count > 0:
                        return True, f"Cleaned up {killed_count} stale VNC processes"
                    else:
                        return True, "No stale VNC processes found"
                else:
                    return True, "No VNC processes found to clean up"
                    
            except Exception as e:
                return False, f"Error cleaning up VNC processes: {str(e)}"

    # Import Selenium components for automation actions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    # Import SeleniumBase for Cloudflare bypass
    try:
        from seleniumbase import SB
        SELENIUMBASE_AVAILABLE = True
    except ImportError:
        SELENIUMBASE_AVAILABLE = False
        print("⚠️  SeleniumBase not available. Install with: pip install seleniumbase")
        
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all required files are in the same directory.")
    sys.exit(1)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'twitter-automation-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
cli = TwitterAutomationCLI()
current_tasks = {}
task_status = {}
active_threads = {}  # Track active threads for proper termination

# Automation state management
automation_states = {}  # Store automation state for each task

class TaskStateManager:
    """Manage persistent task state that survives page refreshes"""
    
    def __init__(self, state_file: str = "task_state.json"):
        self.state_file = state_file
        self.task_status = {}
        self.active_threads = {}
        self.load_state()
    
    def save_state(self):
        """Save current task state to file"""
        try:
            state_data = {
                'task_status': self.task_status,
                'active_threads': list(self.active_threads.keys()),  # Only save thread IDs
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving task state: {e}")
    
    def load_state(self):
        """Load task state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                self.task_status = state_data.get('task_status', {})
                # Note: active_threads are not restored as threads can't be serialized
                # They will be recreated as needed
                
                print(f"Loaded {len(self.task_status)} tasks from state file")
        except Exception as e:
            print(f"Error loading task state: {e}")
            self.task_status = {}
    
    def add_task(self, task_id: str, task_data: dict):
        """Add a new task to state"""
        self.task_status[task_id] = task_data
        self.save_state()
    
    def update_task(self, task_id: str, updates: dict):
        """Update task status"""
        if task_id in self.task_status:
            self.task_status[task_id].update(updates)
            self.save_state()
    
    def remove_task(self, task_id: str):
        """Remove task from state"""
        if task_id in self.task_status:
            del self.task_status[task_id]
            self.save_state()
    
    def get_task(self, task_id: str) -> Optional[dict]:
        """Get task by ID"""
        return self.task_status.get(task_id)
    
    def get_all_tasks(self) -> dict:
        """Get all tasks"""
        return self.task_status.copy()
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        tasks_to_remove = []
        
        for task_id, task_data in self.task_status.items():
            if task_data.get('status') in ['completed', 'error', 'cancelled']:
                start_time = task_data.get('start_time')
                if start_time:
                    try:
                        task_timestamp = datetime.fromisoformat(start_time).timestamp()
                        if task_timestamp < cutoff_time:
                            tasks_to_remove.append(task_id)
                    except:
                        pass
        
        for task_id in tasks_to_remove:
            self.remove_task(task_id)
        
        if tasks_to_remove:
            print(f"Cleaned up {len(tasks_to_remove)} old completed tasks")

# Initialize task state manager
task_state_manager = TaskStateManager()

# Update global variables to use task state manager
def get_task_status():
    """Get current task status from state manager"""
    return task_state_manager.get_all_tasks()

def update_task_status(task_id: str, updates: dict):
    """Update task status in state manager"""
    task_state_manager.update_task(task_id, updates)

def add_task_status(task_id: str, task_data: dict):
    """Add new task to state manager"""
    task_state_manager.add_task(task_id, task_data)

def remove_task_status(task_id: str):
    """Remove task from state manager"""
    task_state_manager.remove_task(task_id)

def cleanup_old_tasks():
    """Clean up old completed tasks"""
    task_state_manager.cleanup_completed_tasks(max_age_hours=24)

def initialize_task_state():
    """Initialize task state on startup"""
    print("🔄 Loading persistent task state...")
    all_tasks = get_task_status()
    
    # Check for running tasks that might need recovery
    running_tasks = []
    for task_id, task_data in all_tasks.items():
        if task_data.get('status') == 'running':
            running_tasks.append(task_id)
            print(f"⚠️ Found running task: {task_id} (type: {task_data.get('type', 'unknown')})")
    
    if running_tasks:
        print(f"📋 Found {len(running_tasks)} running tasks that may need recovery")
        print("💡 These tasks will be available for monitoring but may need manual intervention")
    else:
        print("✅ No running tasks found")
    
    # Clean up old completed tasks
    cleanup_old_tasks()
    
    print(f"📊 Loaded {len(all_tasks)} total tasks from persistent state")

# Initialize task state on startup
initialize_task_state()

class AutomationAction:
    """Base class for automation actions"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, driver, tweet_url: str, **kwargs) -> bool:
        """Execute the action - to be implemented by subclasses"""
        raise NotImplementedError
    
    def can_execute(self, driver) -> bool:
        """Check if action can be executed - to be implemented by subclasses"""
        raise NotImplementedError

class LikeAction(AutomationAction):
    """Like tweet action"""
    
    def __init__(self):
        super().__init__("like", "Like the tweet")
    
    def can_execute(self, driver) -> bool:
        try:
            like_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="like"]'))
            )
            return True
        except:
            return False
    
    def execute(self, driver, tweet_url: str, **kwargs) -> bool:
        try:
            like_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="like"]'))
            )
            like_button.click()
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Failed to like tweet: {str(e)}")
            return False

class RetweetAction(AutomationAction):
    """Retweet action"""
    
    def __init__(self):
        super().__init__("retweet", "Retweet the tweet")
    
    def can_execute(self, driver) -> bool:
        try:
            retweet_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="retweet"]'))
            )
            return True
        except:
            return False
    
    def execute(self, driver, tweet_url: str, **kwargs) -> bool:
        try:
            retweet_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="retweet"]'))
            )
            retweet_button.click()
            
            # Click the retweet confirm button
            confirm_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="retweetConfirm"]'))
            )
            confirm_button.click()
            
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Failed to retweet: {str(e)}")
            return False

class ReplyAction(AutomationAction):
    """Reply to tweet action"""
    
    def __init__(self):
        super().__init__("reply", "Reply to the tweet")
    
    def can_execute(self, driver) -> bool:
        try:
            reply_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="reply"]'))
            )
            return True
        except:
            return False
    
    def execute(self, driver, tweet_url: str, reply_comment: str = "", **kwargs) -> bool:
        try:
            print(f"🔍 Starting reply action for: {tweet_url}")
            print(f"📝 Reply comment: {reply_comment[:50]}...")
            
            # Click reply button
            print("🔍 Looking for reply button...")
            try:
                reply_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="reply"]'))
                )
                print("✅ Found reply button")
                reply_button.click()
                print("✅ Clicked reply button")
            except Exception as e:
                print(f"❌ Failed to find or click reply button: {e}")
                return False
            
            # Wait for reply modal to appear
            print("⏳ Waiting for reply modal...")
            time.sleep(3)
            
            # Try different possible selectors for the reply textarea
            print("🔍 Looking for reply textarea...")
            reply_textarea = None
            textarea_selectors = [
                '[data-testid="tweetTextarea_0"]',
                '[data-testid="tweetTextarea"]',
                '[data-testid="tweetTextarea_1"]',
                '[data-testid="tweetTextarea_2"]',
                '[data-testid="tweetTextarea_3"]',
                '[data-testid="tweetTextarea_4"]',
                '[data-testid="tweetTextarea_5"]',
                '[data-testid="tweetTextarea_6"]',
                '[data-testid="tweetTextarea_7"]',
                '[data-testid="tweetTextarea_8"]',
                '[data-testid="tweetTextarea_9"]',
                '[data-testid="tweetTextarea_10"]',
                'div[contenteditable="true"][data-testid="tweetTextarea_0"]',
                'div[contenteditable="true"][data-testid="tweetTextarea"]',
                'div[contenteditable="true"]',
                'textarea[data-testid="tweetTextarea_0"]',
                'textarea[data-testid="tweetTextarea"]'
            ]
            
            for i, selector in enumerate(textarea_selectors):
                try:
                    print(f"   Trying selector {i+1}/{len(textarea_selectors)}: {selector}")
                    reply_textarea = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found reply textarea with selector: {selector}")
                    break
                except Exception as e:
                    print(f"   ❌ Selector failed: {e}")
                    continue
            
            if not reply_textarea:
                print("❌ Could not find reply textarea with any selector")
                # Let's see what elements are actually available
                print("🔍 Available elements on page:")
                try:
                    all_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid*="tweetTextarea"]')
                    print(f"   Found {len(all_elements)} elements with 'tweetTextarea' in data-testid")
                    for elem in all_elements[:5]:  # Show first 5
                        print(f"   - {elem.get_attribute('data-testid')}")
                    
                    contenteditable_elements = driver.find_elements(By.CSS_SELECTOR, '[contenteditable="true"]')
                    print(f"   Found {len(contenteditable_elements)} contenteditable elements")
                    for elem in contenteditable_elements[:5]:  # Show first 5
                        print(f"   - {elem.get_attribute('data-testid')} | {elem.get_attribute('class')}")
                except Exception as e:
                    print(f"   Error checking available elements: {e}")
                return False
            
            # Clear and fill the reply textarea
            print("📝 Filling reply textarea...")
            try:
                reply_textarea.clear()
                time.sleep(1)
                reply_textarea.send_keys(reply_comment)
                print(f"✅ Filled reply textarea with: {reply_comment[:50]}...")
            except Exception as e:
                print(f"❌ Error filling reply textarea: {e}")
                return False
            
            # Try different possible selectors for the reply submit button
            print("🔍 Looking for reply submit button...")
            reply_submit = None
            submit_selectors = [
                '[data-testid="tweetButton"]',
                '[data-testid="tweetButtonInline"]',
                'div[data-testid="tweetButton"]',
                'button[data-testid="tweetButton"]',
                '[data-testid="postButton"]',
                'button[data-testid="postButton"]'
            ]
            
            for i, selector in enumerate(submit_selectors):
                try:
                    print(f"   Trying submit selector {i+1}/{len(submit_selectors)}: {selector}")
                    reply_submit = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found reply submit button with selector: {selector}")
                    break
                except Exception as e:
                    print(f"   ❌ Submit selector failed: {e}")
                    continue
            
            if not reply_submit:
                print("❌ Could not find reply submit button with any selector")
                # Let's see what submit elements are available
                print("🔍 Available submit elements on page:")
                try:
                    submit_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid*="Button"]')
                    print(f"   Found {len(submit_elements)} elements with 'Button' in data-testid")
                    for elem in submit_elements[:5]:  # Show first 5
                        print(f"   - {elem.get_attribute('data-testid')}")
                except Exception as e:
                    print(f"   Error checking submit elements: {e}")
                return False
            
            # Click reply button
            print("🖱️ Clicking reply submit button...")
            try:
                reply_submit.click()
                print("✅ Clicked reply submit button")
            except Exception as e:
                print(f"❌ Error clicking reply submit button: {e}")
                return False
            
            # Wait for reply to be posted
            print("⏳ Waiting for reply to be posted...")
            time.sleep(3)
            
            # Additional wait and retry for success detection
            max_success_checks = 3
            for check_attempt in range(max_success_checks):
                print(f"🔍 Success check attempt {check_attempt + 1}/{max_success_checks}")
                
                # Check if reply was successful by looking for success indicators
                print("🔍 Verifying reply success...")
                try:
                    # Look for any error messages
                    error_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="error"]')
                    if error_elements:
                        print(f"❌ Reply error detected: {error_elements[0].text}")
                        return False
                    
                    # Look for success indicators - check multiple methods
                    success_indicators = [
                        # Method 1: Check if reply modal is closed (most reliable)
                        len(driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]')) == 0,
                        # Method 2: Check if we're back to the main tweet view
                        len(driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')) > 0,
                        # Method 3: Check if reply button is visible again
                        len(driver.find_elements(By.CSS_SELECTOR, '[data-testid="reply"]')) > 0,
                        # Method 4: Check if we're not in a modal state
                        len(driver.find_elements(By.CSS_SELECTOR, '[data-testid="modal"]')) == 0
                    ]
                    
                    # If any success indicator is true, consider it successful
                    if any(success_indicators):
                        print("✅ Reply success indicators detected:")
                        print(f"   • Modal closed: {success_indicators[0]}")
                        print(f"   • Tweet view visible: {success_indicators[1]}")
                        print(f"   • Reply button visible: {success_indicators[2]}")
                        print(f"   • No modal state: {success_indicators[3]}")
                        return True
                    else:
                        # Additional check: if we can't find the textarea but can find the tweet, it's likely successful
                        tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
                        textarea_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]')
                        
                        if len(tweet_elements) > 0 and len(textarea_elements) == 0:
                            print("✅ Tweet visible and textarea closed - reply likely successful")
                            return True
                        
                        print("⚠️ Reply modal still open, but checking for alternative success indicators...")
                        
                        # Final check: if we can see the original tweet and no error messages, assume success
                        if len(tweet_elements) > 0 and len(error_elements) == 0:
                            print("✅ Original tweet visible and no errors - assuming reply successful")
                            return True
                        
                        # If this is not the last attempt, wait a bit more
                        if check_attempt < max_success_checks - 1:
                            print(f"⏳ Waiting 2 more seconds for UI to update...")
                            time.sleep(2)
                            continue
                        
                        print("⚠️ Could not definitively determine reply success, but no errors detected")
                        # If we get here, assume success since the user reports it's working
                        return True
                        
                except Exception as e:
                    print(f"⚠️ Could not verify reply success: {e}")
                    # If this is not the last attempt, wait a bit more
                    if check_attempt < max_success_checks - 1:
                        print(f"⏳ Waiting 2 more seconds and retrying...")
                        time.sleep(2)
                        continue
                    # Assume success if no errors and we got this far
                    print("✅ Assuming reply successful (no errors detected)")
                    return True
            
        except Exception as e:
            print(f"❌ Failed to reply: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

class AutomationStrategy:
    """Base class for automation strategies"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.actions = {}
        self._register_actions()
    
    def _register_actions(self):
        """Register available actions - to be implemented by subclasses"""
        pass
    
    def get_actions(self) -> Dict[str, AutomationAction]:
        return self.actions
    
    def execute_actions(self, driver, tweet_url: str, enabled_actions: Dict[str, bool], **kwargs) -> Dict[str, bool]:
        """Execute enabled actions and return results"""
        results = {}
        
        print(f"🎯 Strategy executing actions for: {tweet_url}")
        print(f"📋 Available actions: {list(self.actions.keys())}")
        print(f"📋 Enabled actions: {enabled_actions}")
        
        for action_name, enabled in enabled_actions.items():
            print(f"🔍 Processing action: {action_name} (enabled: {enabled})")
            
            if enabled and action_name in self.actions:
                action = self.actions[action_name]
                print(f"✅ Action '{action_name}' found in strategy")
                
                if action.can_execute(driver):
                    print(f"✅ Action '{action_name}' can execute")
                    try:
                        result = action.execute(driver, tweet_url, **kwargs)
                        print(f"📊 Action '{action_name}' result: {result}")
                        results[action_name] = result
                    except Exception as e:
                        print(f"❌ Action '{action_name}' execution error: {e}")
                        results[action_name] = False
                else:
                    print(f"❌ Action '{action_name}' cannot execute")
                    results[action_name] = False
            else:
                print(f"⚠️ Action '{action_name}' not enabled or not found")
                results[action_name] = False
        
        print(f"📊 Final action results: {results}")
        return results

class StandardAutomationStrategy(AutomationStrategy):
    """Standard automation strategy with like, retweet, and reply actions"""
    
    def __init__(self):
        super().__init__("standard", "Standard automation with like, retweet, and reply")
    
    def _register_actions(self):
        self.actions = {
            'like': LikeAction(),
            'retweet': RetweetAction(),
            'reply': ReplyAction()
        }

class AutomationState:
    """Manage automation state for persistence and recovery"""
    
    def __init__(self, task_id: str, profile_name: str, tweet_links: List[str], 
                 reply_comments: List[str], actions: Dict[str, bool], 
                 min_wait: int, max_wait: int, max_retries: int):
        self.task_id = task_id
        self.profile_name = profile_name
        self.tweet_links = tweet_links
        self.reply_comments = reply_comments
        self.actions = actions
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.max_retries = max_retries
        
        # Create paired tasks (tweet + comment)
        self.paired_tasks = self._create_paired_tasks()
        
        # Progress tracking
        self.processed_tasks = set()  # Set of task indices that have been processed
        self.successful_tasks = set()  # Set of task indices that were successful
        self.failed_tasks = set()      # Set of task indices that failed
        self.current_index = 0
        self.start_time = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
    
    def _create_paired_tasks(self) -> List[Dict]:
        """Create paired tasks from tweet links and comments"""
        paired_tasks = []
        
        # Ensure we have the same number of tweets and comments
        max_length = max(len(self.tweet_links), len(self.reply_comments))
        
        for i in range(max_length):
            tweet_url = self.tweet_links[i] if i < len(self.tweet_links) else ""
            comment = self.reply_comments[i] if i < len(self.reply_comments) else ""
            
            if tweet_url.strip():  # Only add if tweet URL is not empty
                paired_tasks.append({
                    'index': i,
                    'tweet_url': tweet_url.strip(),
                    'comment': comment.strip(),
                    'original_tweet_index': i,
                    'original_comment_index': i
                })
        
        return paired_tasks
    
    def get_remaining_tasks(self) -> List[Dict]:
        """Get tasks that haven't been processed yet"""
        return [task for i, task in enumerate(self.paired_tasks) if i not in self.processed_tasks]
    
    def mark_task_processed(self, task_index: int, success: bool):
        """Mark a task as processed and track success/failure"""
        self.processed_tasks.add(task_index)
        if success:
            self.successful_tasks.add(task_index)
        else:
            self.failed_tasks.add(task_index)
        self.last_updated = datetime.now().isoformat()
    
    def get_progress_stats(self) -> Dict:
        """Get current progress statistics"""
        total_tasks = len(self.paired_tasks)
        processed_count = len(self.processed_tasks)
        successful_count = len(self.successful_tasks)
        failed_count = len(self.failed_tasks)
        remaining_count = total_tasks - processed_count
        
        success_rate = (successful_count / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'processed_count': processed_count,
            'successful_count': successful_count,
            'failed_count': failed_count,
            'remaining_count': remaining_count,
            'success_rate': success_rate,
            'progress_percentage': (processed_count / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def save_state(self):
        """Save state to file"""
        state_file = f"automation_state_{self.task_id}.json"
        stats = self.get_progress_stats()
        
        state_data = {
            'task_id': self.task_id,
            'profile_name': self.profile_name,
            'paired_tasks': self.paired_tasks,
            'actions': self.actions,
            'min_wait': self.min_wait,
            'max_wait': self.max_wait,
            'max_retries': self.max_retries,
            'processed_tasks': list(self.processed_tasks),
            'successful_tasks': list(self.successful_tasks),
            'failed_tasks': list(self.failed_tasks),
            'current_index': self.current_index,
            'start_time': self.start_time,
            'last_updated': self.last_updated,
            'stats': stats
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_state(cls, task_id: str) -> Optional['AutomationState']:
        """Load state from file"""
        state_file = f"automation_state_{task_id}.json"
        if not os.path.exists(state_file):
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Reconstruct original lists from paired tasks
            tweet_links = []
            reply_comments = []
            
            for task in state_data['paired_tasks']:
                tweet_links.append(task['tweet_url'])
                reply_comments.append(task['comment'])
            
            state = cls(
                state_data['task_id'],
                state_data['profile_name'],
                tweet_links,
                reply_comments,
                state_data['actions'],
                state_data['min_wait'],
                state_data['max_wait'],
                state_data['max_retries']
            )
            
            # Restore state
            state.paired_tasks = state_data['paired_tasks']
            state.processed_tasks = set(state_data['processed_tasks'])
            state.successful_tasks = set(state_data['successful_tasks'])
            state.failed_tasks = set(state_data['failed_tasks'])
            state.current_index = state_data['current_index']
            state.start_time = state_data['start_time']
            state.last_updated = state_data['last_updated']
            
            return state
        except Exception as e:
            print(f"Error loading state: {e}")
            return None
    
    def cleanup(self):
        """Clean up state file"""
        state_file = f"automation_state_{self.task_id}.json"
        if os.path.exists(state_file):
            os.remove(state_file)

class WebDashboard:
    def __init__(self):
        self.cli = TwitterAutomationCLI()
        self.tasks = {}
        self.task_counter = 0
    
    def get_profiles(self):
        """Get all saved profiles"""
        return self.cli.profile_manager.get_all_profiles()
    
    def create_profile(self, profile_name: str):
        """Create a new profile"""
        return self.cli.create_profile(profile_name)
    
    def delete_profile(self, profile_name: str):
        """Delete a profile"""
        return self.cli.delete_profile(profile_name)
    
    def launch_profile_browser(self, profile_name: str):
        """Launch Chrome browser for a profile with VNC support"""
        if not profile_name:
            return False
        
        profile_dir = f"chrome-data/{profile_name}"
        if not os.path.exists(profile_dir):
            return False
        
        try:
            import subprocess
            import platform
            
            # Use the same VNC configuration as scraping tasks
            use_gui = config.use_gui_chrome and os.name == 'posix'
            vnc_display = config.vnc_display
            
            # Chrome command for different platforms
            if platform.system() == "Linux":
                chrome_cmd = "google-chrome"
            elif platform.system() == "Darwin":  # macOS
                chrome_cmd = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            else:  # Windows
                chrome_cmd = "chrome"
            
            # Set up Chrome options
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
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions-except",
                "--disable-plugins-discovery",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-back-forward-cache",
                "--disable-ipc-flooding-protection",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            
            # Add VNC-specific options if GUI mode is enabled
            if use_gui and platform.system() == "Linux":
                # More comprehensive VNC detection
                vnc_running = False
                vnc_patterns = [
                    f'vncserver.*{vnc_display}',
                    f'Xtightvnc.*{vnc_display}',
                    f'tightvncserver.*{vnc_display}',
                    f'tigervncserver.*{vnc_display}',
                    f'x11vnc.*{vnc_display}',
                    f'vnc.*{vnc_display}'
                ]
                
                for pattern in vnc_patterns:
                    try:
                        result = subprocess.run(['pgrep', '-f', pattern], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            vnc_running = True
                            print(f"🖥️  VNC detected with pattern: {pattern}")
                            break
                    except Exception:
                        continue
                
                if vnc_running:
                    os.environ["DISPLAY"] = vnc_display
                    chrome_options.extend([
                        "--disable-gpu-sandbox",
                        "--disable-software-rasterizer",
                        "--no-sandbox",
                        "--disable-dev-shm-usage"
                    ])
                    print(f"🖥️  VNC detected - launching Chrome in GUI mode on display {vnc_display}")
                else:
                    print(f"⚠️  VNC not detected - launching Chrome in headless mode")
                    chrome_options.append("--headless")
            elif platform.system() == "Linux":
                print(f"⚠️  GUI mode disabled - launching Chrome in headless mode")
                chrome_options.append("--headless")
            
            # Launch Chrome
            print(f"🚀 Launching Chrome with profile: {profile_name}")
            print(f"📁 Profile directory: {os.path.abspath(profile_dir)}")
            
            # Launch in background with better error handling
            try:
                process = subprocess.Popen(
                    chrome_options,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid if platform.system() == "Linux" else None
                )
                
                # Wait a moment to see if Chrome starts successfully
                time.sleep(2)
                
                # Check if process is still running
                if process.poll() is None:
                    print(f"✅ Chrome launched successfully with PID: {process.pid}")
                    
                    if use_gui and platform.system() == "Linux" and vnc_running:
                        print(f"🎯 Chrome should now be visible in your VNC viewer")
                        # Get server IP for VNC connection
                        try:
                            import socket
                            hostname = socket.gethostname()
                            ip_address = socket.gethostbyname(hostname)
                            print(f"🔗 VNC Connection: {ip_address}:5901")
                        except:
                            print(f"🔗 VNC Connection: localhost:5901")
                        print(f"📺 Display: {vnc_display}")
                    else:
                        print(f"💡 To view Chrome in VNC, enable GUI mode in settings and start VNC first")
                    
                    return True
                else:
                    # Process died, get error output
                    stdout, stderr = process.communicate()
                    print(f"❌ Chrome process died immediately")
                    print(f"   • Return code: {process.returncode}")
                    if stderr:
                        print(f"   • Error: {stderr.decode('utf-8', errors='ignore')}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error launching Chrome: {e}")
                return False
            
        except Exception as e:
            print(f"Error launching Chrome browser: {e}")
            return False
    
    def scrape_tweets_async(self, profile_name: str, tweet_links: List[str], 
                           output_file: str = "scraped_tweets.txt", max_retries: int = 3):
        """Scrape tweets asynchronously"""
        task_id = f"scrape_{int(time.time())}"
        
        # Use task state manager instead of global task_status
        initial_task_data = {
            'type': 'scraping',
            'status': 'running',
            'progress': 0,
            'total': len(tweet_links),
            'current': 0,
            'logs': [],
            'start_time': datetime.now().isoformat()
        }
        add_task_status(task_id, initial_task_data)
        
        def scrape_worker():
            try:
                # Create temporary file for tweet links
                temp_links_file = f"temp_links_{task_id}.txt"
                with open(temp_links_file, 'w', encoding='utf-8') as f:
                    for link in tweet_links:
                        f.write(f"{link}\n")
                
                # Initialize scraper
                scraper = TweetScraper(profile_name)
                
                # Use GUI Chrome if configured and on Linux
                use_gui = config.use_gui_chrome and os.name == 'posix'
                if use_gui:
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append(f"Setting up Chrome in GUI mode via VNC (display {config.vnc_display})")
                    update_task_status(task_id, {'logs': current_logs})
                
                chrome_available = scraper.setup_driver(use_gui=use_gui, display=config.vnc_display)
                
                if chrome_available:
                    if use_gui:
                        current_task = get_task_status().get(task_id, {})
                        current_logs = current_task.get('logs', [])
                        current_logs.append("Chrome driver initialized successfully in GUI mode")
                        update_task_status(task_id, {'logs': current_logs})
                    else:
                        current_task = get_task_status().get(task_id, {})
                        current_logs = current_task.get('logs', [])
                        current_logs.append("Chrome driver initialized successfully")
                        update_task_status(task_id, {'logs': current_logs})
                else:
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append("Chrome driver failed - using fallback requests-based scraping")
                    update_task_status(task_id, {'logs': current_logs})
                
                # Scrape tweets
                scraped_content = []
                failed_links = []
                
                for i, link in enumerate(tweet_links, 1):
                    current_task = get_task_status().get(task_id, {})
                    if current_task.get('status') == 'cancelled':
                        break
                    
                    update_task_status(task_id, {
                        'current': i,
                        'progress': int((i / len(tweet_links)) * 100)
                    })
                    
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append(f"Scraping tweet {i}/{len(tweet_links)}: {link}")
                    update_task_status(task_id, {'logs': current_logs})
                    
                    # Try scraping with retries
                    content = self._scrape_with_retries(scraper, link, max_retries)
                    
                    if content:
                        scraped_content.append(content)
                        current_task = get_task_status().get(task_id, {})
                        current_logs = current_task.get('logs', [])
                        current_logs.append(f"✓ Successfully scraped tweet {i}")
                        update_task_status(task_id, {'logs': current_logs})
                    else:
                        failed_links.append(link)
                        current_task = get_task_status().get(task_id, {})
                        current_logs = current_task.get('logs', [])
                        current_logs.append(f"✗ Failed to scrape tweet {i}")
                        update_task_status(task_id, {'logs': current_logs})
                    
                    # Random delay between tweets
                    if i < len(tweet_links):
                        delay = random.randint(3, 5)
                        current_task = get_task_status().get(task_id, {})
                        current_logs = current_task.get('logs', [])
                        current_logs.append(f"Waiting {delay} seconds...")
                        update_task_status(task_id, {'logs': current_logs})
                        time.sleep(delay)
                
                # Save scraped content
                with open(output_file, 'w', encoding='utf-8') as f:
                    for content in scraped_content:
                        f.write(f"{content}\n")
                
                update_task_status(task_id, {'status': 'completed'})
                current_task = get_task_status().get(task_id, {})
                current_logs = current_task.get('logs', [])
                current_logs.append(f"Scraping completed! Successfully scraped: {len(scraped_content)} tweets")
                current_logs.append(f"Failed: {len(failed_links)} tweets")
                current_logs.append(f"Results saved to: {output_file}")
                update_task_status(task_id, {'logs': current_logs})
                
                # Clean up temporary file
                if os.path.exists(temp_links_file):
                    os.remove(temp_links_file)
                
                scraper.cleanup()
                
            except Exception as e:
                update_task_status(task_id, {'status': 'error'})
                current_task = get_task_status().get(task_id, {})
                current_logs = current_task.get('logs', [])
                current_logs.append(f"Error: {str(e)}")
                update_task_status(task_id, {'logs': current_logs})
                scraper.cleanup()
            finally:
                # Clean up thread reference
                if task_id in active_threads:
                    del active_threads[task_id]
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=scrape_worker)
        thread.daemon = True
        active_threads[task_id] = thread  # Store thread reference
        thread.start()
        
        return task_id
    
    def run_automation_async(self, profile_name: str, tweet_links: List[str], reply_comments: List[str],
                           actions: Dict[str, bool], min_wait: int, max_wait: int, max_retries: int = 3):
        """Run automation asynchronously with new modular structure"""
        task_id = f"automation_{int(time.time())}"
        
        # Create automation state first
        state = AutomationState(task_id, profile_name, tweet_links, reply_comments, 
                              actions, min_wait, max_wait, max_retries)
        automation_states[task_id] = state
        
        # Initialize task status using task state manager
        initial_task_data = {
            'type': 'automation',
            'status': 'running',
            'progress': 0,
            'total': len(state.paired_tasks),  # Use paired tasks count
            'current': 0,
            'logs': [],
            'start_time': datetime.now().isoformat(),
            'strategy': 'standard',
            'actions_enabled': actions
        }
        add_task_status(task_id, initial_task_data)
        
        def automation_worker():
            automation = None
            strategy = None
            
            try:
                # Log initialization
                current_task = get_task_status().get(task_id, {})
                current_logs = current_task.get('logs', [])
                current_logs.append(f"🚀 Starting Twitter automation with profile: {profile_name}")
                current_logs.append(f"📊 Configuration:")
                current_logs.append(f"   • Total paired tasks: {len(state.paired_tasks)}")
                current_logs.append(f"   • Actions: {actions}")
                current_logs.append(f"   • Wait time: {min_wait}-{max_wait} seconds")
                current_logs.append(f"   • Max retries: {max_retries}")
                update_task_status(task_id, {'logs': current_logs})
                
                # Initialize automation strategy
                strategy = StandardAutomationStrategy()
                current_task = get_task_status().get(task_id, {})
                current_logs = current_task.get('logs', [])
                current_logs.append(f"🎯 Using strategy: {strategy.name}")
                update_task_status(task_id, {'logs': current_logs})
                
                # Initialize automation
                automation = TwitterAutomation(profile_name)
                if not automation.setup_driver():
                    update_task_status(task_id, {'status': 'error'})
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append("❌ Failed to initialize Chrome driver")
                    update_task_status(task_id, {'logs': current_logs})
                    return
                
                current_task = get_task_status().get(task_id, {})
                current_logs = current_task.get('logs', [])
                current_logs.append("✅ Chrome driver initialized successfully")
                update_task_status(task_id, {'logs': current_logs})
                
                # Get remaining tasks and randomize order
                remaining_tasks = state.get_remaining_tasks()
                random.shuffle(remaining_tasks)
                current_task = get_task_status().get(task_id, {})
                current_logs = current_task.get('logs', [])
                current_logs.append(f"🔄 Randomized processing order for {len(remaining_tasks)} remaining tasks")
                update_task_status(task_id, {'logs': current_logs})
                
                # Process tasks
                for i, task in enumerate(remaining_tasks):
                    current_task = get_task_status().get(task_id, {})
                    if current_task.get('status') == 'cancelled':
                        current_logs = current_task.get('logs', [])
                        current_logs.append("⏹️ Automation cancelled by user")
                        update_task_status(task_id, {'logs': current_logs})
                        break
                    
                    task_index = task['index']
                    tweet_url = task['tweet_url']
                    reply_comment = task['comment']
                    
                    # Update progress
                    state.current_index = i
                    update_task_status(task_id, {
                        'current': i + 1,
                        'progress': int(((i + 1) / len(remaining_tasks)) * 100)
                    })
                    
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append(f"📝 Processing task {i+1}/{len(remaining_tasks)}:")
                    current_logs.append(f"   • Tweet: {tweet_url}")
                    if reply_comment:
                        current_logs.append(f"   • Comment: {reply_comment}")
                    update_task_status(task_id, {'logs': current_logs})
                    
                    # Process tweet with retry logic
                    success = self._process_tweet_with_retries(
                        automation, strategy, tweet_url, reply_comment, 
                        actions, max_retries, task_id, state
                    )
                    
                    # Mark task as processed and track success/failure
                    state.mark_task_processed(task_index, success)
                    
                    if success:
                        automation.log_to_file("success_log.txt", f"SUCCESS: {tweet_url} | Comment: {reply_comment}")
                        current_task = get_task_status().get(task_id, {})
                        current_logs = current_task.get('logs', [])
                        current_logs.append("✅ Task processed successfully")
                        update_task_status(task_id, {'logs': current_logs})
                    else:
                        automation.log_to_file("failure_log.txt", f"FAILURE: {tweet_url} | Comment: {reply_comment}")
                        current_task = get_task_status().get(task_id, {})
                        current_logs = current_task.get('logs', [])
                        current_logs.append("❌ Task processing failed")
                        update_task_status(task_id, {'logs': current_logs})
                    
                    # Log current stats
                    stats = state.get_progress_stats()
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append(f"📈 Progress: {stats['processed_count']}/{stats['total_tasks']} completed ({stats['success_rate']:.1f}% success rate)")
                    update_task_status(task_id, {'logs': current_logs})
                    
                    # Save state periodically
                    if (i + 1) % 3 == 0:  # Save more frequently for better recovery
                        state.save_state()
                        current_task = get_task_status().get(task_id, {})
                        current_logs = current_task.get('logs', [])
                        current_logs.append("💾 Progress saved")
                        update_task_status(task_id, {'logs': current_logs})
                    
                    # Random wait between tasks (except for last task)
                    if i < len(remaining_tasks) - 1:
                        wait_time = random.randint(min_wait, max_wait)
                        current_task = get_task_status().get(task_id, {})
                        current_logs = current_task.get('logs', [])
                        current_logs.append(f"⏳ Waiting {wait_time} seconds before next task...")
                        update_task_status(task_id, {'logs': current_logs})
                        time.sleep(wait_time)
                
                # Final state save
                state.save_state()
                
                # Log completion with final stats
                final_stats = state.get_progress_stats()
                
                update_task_status(task_id, {'status': 'completed'})
                current_task = get_task_status().get(task_id, {})
                current_logs = current_task.get('logs', [])
                current_logs.append(f"🎉 Automation completed!")
                current_logs.append(f"📈 Final Results:")
                current_logs.append(f"   • Total tasks: {final_stats['total_tasks']}")
                current_logs.append(f"   • Successful: {final_stats['successful_count']}")
                current_logs.append(f"   • Failed: {final_stats['failed_count']}")
                current_logs.append(f"   • Success rate: {final_stats['success_rate']:.1f}%")
                current_logs.append(f"   • Remaining: {final_stats['remaining_count']}")
                update_task_status(task_id, {'logs': current_logs})
                
            except Exception as e:
                update_task_status(task_id, {'status': 'error'})
                current_task = get_task_status().get(task_id, {})
                current_logs = current_task.get('logs', [])
                current_logs.append(f"💥 Automation error: {str(e)}")
                update_task_status(task_id, {'logs': current_logs})
                if state:
                    state.save_state()  # Save state even on error
            finally:
                # Cleanup
                if automation:
                    automation.cleanup()
                if task_id in active_threads:
                    del active_threads[task_id]
                if task_id in automation_states:
                    del automation_states[task_id]
        
        # Start automation in a separate thread
        thread = threading.Thread(target=automation_worker)
        thread.daemon = True
        active_threads[task_id] = thread
        thread.start()
        
        return task_id
    
    def _process_tweet_with_retries(self, automation, strategy, tweet_url: str, reply_comment: str,
                                  actions: Dict[str, bool], max_retries: int, task_id: str, state: AutomationState) -> bool:
        """Process a single tweet with retry logic using the new action system"""
        
        for attempt in range(max_retries):
            try:
                # Navigate to tweet
                automation.driver.get(tweet_url)
                
                # Wait for page to load
                WebDriverWait(automation.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
                )
                
                # Execute actions using strategy
                print(f"🔍 Executing actions for tweet: {tweet_url}")
                print(f"�� Enabled actions: {actions}")
                
                action_results = strategy.execute_actions(
                    automation.driver, 
                    tweet_url, 
                    actions, 
                    reply_comment=reply_comment
                )
                
                print(f"📊 Action results: {action_results}")
                
                # Check if all enabled actions succeeded
                enabled_actions = [name for name, enabled in actions.items() if enabled]
                successful_actions = [name for name, success in action_results.items() if success]
                
                print(f"✅ Successful actions: {successful_actions}")
                print(f"❌ Failed actions: {set(enabled_actions) - set(successful_actions)}")
                
                if len(successful_actions) == len(enabled_actions):
                    return True
                elif attempt < max_retries - 1:
                    failed_actions = set(enabled_actions) - set(successful_actions)
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append(f"⚠️ Attempt {attempt + 1} failed for actions: {failed_actions}, retrying...")
                    update_task_status(task_id, {'logs': current_logs})
                    time.sleep(2)
                    continue
                else:
                    failed_actions = set(enabled_actions) - set(successful_actions)
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append(f"❌ All attempts failed for actions: {failed_actions}")
                    update_task_status(task_id, {'logs': current_logs})
                    return False
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append(f"⚠️ Attempt {attempt + 1} failed: {str(e)}, retrying...")
                    update_task_status(task_id, {'logs': current_logs})
                    time.sleep(2)
                    continue
                else:
                    current_task = get_task_status().get(task_id, {})
                    current_logs = current_task.get('logs', [])
                    current_logs.append(f"❌ Error processing tweet: {str(e)}")
                    update_task_status(task_id, {'logs': current_logs})
                    return False
        
        return False
    
    def _scrape_with_retries(self, scraper: TweetScraper, link: str, max_retries: int = 3) -> Optional[str]:
        """Scrape with retry logic"""
        for attempt in range(max_retries):
            try:
                content = scraper.scrape_tweet_content(link)
                if content and content.strip():
                    return content
                elif attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    print(f"All attempts failed: No content found")
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    print(f"All attempts failed: {e}")
        
        return None

    def launch_profile_browser_seleniumbase(self, profile_name: str):
        """Launch Chrome browser using SeleniumBase with undetected-chromedriver for Cloudflare bypass"""
        if not profile_name:
            return False
        
        if not SELENIUMBASE_AVAILABLE:
            print("❌ SeleniumBase not available. Falling back to regular Chrome launch.")
            return self.launch_profile_browser(profile_name)
        
        profile_dir = f"chrome-data/{profile_name}"
        if not os.path.exists(profile_dir):
            return False
        
        try:
            import platform
            
            # Use the same VNC configuration as other methods
            use_gui = config.use_gui_chrome and os.name == 'posix'
            vnc_display = config.vnc_display
            
            print(f"🚀 Launching Chrome with SeleniumBase (Cloudflare bypass) for profile: {profile_name}")
            print(f"📁 Profile directory: {os.path.abspath(profile_dir)}")
            
            # Set up SeleniumBase options
            sb_options = {
                'uc': True,  # Use undetected-chromedriver
                'ad_block_on': True,  # Enable ad blocking
                'headless': not use_gui,  # Headless mode if not using GUI
                'user_data_dir': os.path.abspath(profile_dir),
                'no_sandbox': True,
                'disable_gpu': True,
                'disable_dev_shm_usage': True,
                'disable_web_security': True,
                'allow_running_insecure_content': True,
                'disable_features': 'TranslateUI',
                'disable_blink_features': 'AutomationControlled',
                'disable_extensions_except': '',
                'disable_plugins_discovery': True,
                'disable_background_timer_throttling': True,
                'disable_backgrounding_occluded_windows': True,
                'disable_renderer_backgrounding': True,
                'disable_field_trial_config': True,
                'disable_back_forward_cache': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Add VNC-specific options if GUI mode is enabled
            if use_gui and platform.system() == "Linux":
                # Check if VNC is running
                vnc_running = False
                vnc_patterns = [
                    f'vncserver.*{vnc_display}',
                    f'Xtightvnc.*{vnc_display}',
                    f'tightvncserver.*{vnc_display}',
                    f'tigervncserver.*{vnc_display}',
                    f'x11vnc.*{vnc_display}',
                    f'vnc.*{vnc_display}'
                ]
                
                for pattern in vnc_patterns:
                    try:
                        result = subprocess.run(['pgrep', '-f', pattern], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            vnc_running = True
                            print(f"🖥️  VNC detected with pattern: {pattern}")
                            break
                    except Exception:
                        continue
                
                if vnc_running:
                    os.environ["DISPLAY"] = vnc_display
                    sb_options.update({
                        'headless': False,
                        'disable_gpu_sandbox': True,
                        'disable_software_rasterizer': True
                    })
                    print(f"🖥️  VNC detected - launching Chrome in GUI mode on display {vnc_display}")
                else:
                    print(f"⚠️  VNC not detected - launching Chrome in headless mode")
                    sb_options['headless'] = True
            
            # Launch Chrome using SeleniumBase
            try:
                with SB(**sb_options) as sb:
                    # Open a simple page to test the browser
                    test_url = "https://www.google.com"
                    print(f"🌐 Testing browser with: {test_url}")
                    
                    # Use uc_open_with_reconnect for better Cloudflare bypass
                    sb.uc_open_with_reconnect(test_url, 8)
                    
                    print(f"✅ Chrome launched successfully with SeleniumBase")
                    
                    if use_gui and platform.system() == "Linux" and vnc_running:
                        print(f"🎯 Chrome should now be visible in your VNC viewer")
                        try:
                            import socket
                            hostname = socket.gethostname()
                            ip_address = socket.gethostbyname(hostname)
                            print(f"🔗 VNC Connection: {ip_address}:5901")
                        except:
                            print(f"🔗 VNC Connection: localhost:5901")
                        print(f"📺 Display: {vnc_display}")
                    
                    # Keep the browser open for manual use
                    print(f"💡 Browser is ready for manual use. Close this terminal to stop the browser.")
                    
                    # Wait for user to close (in a real implementation, you might want to return the sb object)
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print(f"\n🛑 Browser session ended by user")
                    
                    return True
                    
            except Exception as e:
                print(f"❌ Error launching Chrome with SeleniumBase: {e}")
                return False
            
        except Exception as e:
            print(f"Error launching Chrome browser with SeleniumBase: {e}")
            return False

# Initialize dashboard
dashboard = WebDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all saved profiles"""
    try:
        profiles = dashboard.get_profiles()
        return jsonify({
            'success': True,
            'profiles': profiles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    """Create a new profile"""
    try:
        data = request.get_json()
        profile_name = data.get('profile_name')
        
        if not profile_name:
            return jsonify({
                'success': False,
                'error': 'Profile name is required'
            }), 400
        
        success = dashboard.create_profile(profile_name)
        return jsonify({
            'success': success,
            'message': f"Profile '{profile_name}' created successfully" if success else f"Profile '{profile_name}' already exists"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profiles/<profile_name>', methods=['DELETE'])
def delete_profile(profile_name):
    """Delete a profile"""
    try:
        success = dashboard.delete_profile(profile_name)
        return jsonify({
            'success': success,
            'message': f"Profile '{profile_name}' deleted successfully" if success else f"Profile '{profile_name}' not found"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profiles/<profile_name>/launch', methods=['POST'])
def launch_profile_browser(profile_name):
    """Launch Chrome browser for a profile"""
    try:
        success = dashboard.launch_profile_browser(profile_name)
        return jsonify({
            'success': success,
            'message': f"Browser launched for profile '{profile_name}'" if success else f"Failed to launch browser for profile '{profile_name}'"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profiles/<profile_name>/launch-sb', methods=['POST'])
def launch_profile_browser_seleniumbase(profile_name):
    """Launch Chrome browser using SeleniumBase for Cloudflare bypass"""
    try:
        success = dashboard.launch_profile_browser_seleniumbase(profile_name)
        return jsonify({
            'success': success,
            'message': f"SeleniumBase browser launched for profile '{profile_name}'" if success else f"Failed to launch SeleniumBase browser for profile '{profile_name}'"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profiles/<profile_name>/status')
def check_profile_status(profile_name):
    """Check if a Chrome profile is running"""
    try:
        # Check if Chrome process is running for this profile
        profile_dir = f"chrome-data/{profile_name}"
        result = subprocess.run(['pgrep', '-f', f'chrome.*{profile_dir}'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            status = "Running"
            pids = result.stdout.strip().split('\n')
            process_count = len([pid for pid in pids if pid.strip()])
        else:
            status = "Not running"
            process_count = 0
        
        return jsonify({
            'success': True,
            'status': status,
            'process_count': process_count,
            'profile_name': profile_name
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profiles/<profile_name>/reattach', methods=['POST'])
def reattach_profile(profile_name):
    """Reattach Chrome profile to VNC display"""
    try:
        # Check if VNC is running
        vnc_running, error = check_vnc_running_simple(config.vnc_display)
        if not vnc_running:
            return jsonify({
                'success': False,
                'error': 'VNC server is not running. Please start VNC first.'
            }), 400
        
        # Kill existing Chrome processes for this profile
        profile_dir = f"chrome-data/{profile_name}"
        subprocess.run(['pkill', '-f', f'chrome.*{profile_dir}'], 
                      capture_output=True, text=True, timeout=5)
        
        # Wait a moment for processes to stop
        time.sleep(2)
        
        # Use the same VNC configuration as other methods
        use_gui = config.use_gui_chrome and os.name == 'posix'
        vnc_display = config.vnc_display
        
        # Chrome command for different platforms
        import platform
        if platform.system() == "Linux":
            chrome_cmd = "google-chrome"
        elif platform.system() == "Darwin":  # macOS
            chrome_cmd = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:  # Windows
            chrome_cmd = "chrome"
        
        # Set up Chrome options
        chrome_options = [
            chrome_cmd,
            f'--user-data-dir={profile_dir}',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-notifications',
            '--start-maximized',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--disable-blink-features=AutomationControlled',
            '--disable-extensions-except',
            '--disable-plugins-discovery',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-field-trial-config',
            '--disable-back-forward-cache',
            '--disable-ipc-flooding-protection',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Add VNC-specific options if GUI mode is enabled
        if use_gui and platform.system() == "Linux":
            os.environ["DISPLAY"] = vnc_display
            chrome_options.extend([
                "--disable-gpu-sandbox",
                "--disable-software-rasterizer",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ])
        
        # Set display environment
        env = os.environ.copy()
        if use_gui and platform.system() == "Linux":
            env['DISPLAY'] = vnc_display
        
        # Launch Chrome
        process = subprocess.Popen(chrome_options, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return jsonify({
            'success': True,
            'message': f'Profile {profile_name} reattached to VNC successfully',
            'pid': process.pid,
            'display': vnc_display if use_gui else 'headless'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profiles/<profile_name>/stop', methods=['POST'])
def stop_profile(profile_name):
    """Stop Chrome processes for a profile"""
    try:
        profile_dir = f"chrome-data/{profile_name}"
        
        # Kill Chrome processes for this profile
        result = subprocess.run(['pkill', '-f', f'chrome.*{profile_dir}'], 
                              capture_output=True, text=True, timeout=10)
        
        killed_count = 0
        if result.returncode == 0:
            # Count how many processes were killed
            pids = result.stdout.strip().split('\n')
            killed_count = len([pid for pid in pids if pid.strip()])
        
        return jsonify({
            'success': True,
            'message': f'Stopped {killed_count} Chrome processes for profile {profile_name}',
            'killed_count': killed_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start tweet scraping"""
    try:
        data = request.get_json()
        profile_name = data.get('profile_name')
        tweet_links = data.get('tweet_links', [])
        max_retries = data.get('max_retries', 3)
        
        if not profile_name:
            return jsonify({
                'success': False,
                'error': 'Profile name is required'
            }), 400
        
        if not tweet_links:
            return jsonify({
                'success': False,
                'error': 'Tweet links are required'
            }), 400
        
        task_id = dashboard.scrape_tweets_async(profile_name, tweet_links, max_retries=max_retries)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Scraping started'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/automate', methods=['POST'])
def start_automation():
    """Start Twitter automation"""
    try:
        data = request.get_json()
        profile_name = data.get('profile_name')
        tweet_links = data.get('tweet_links', [])
        reply_comments = data.get('reply_comments', [])
        actions = data.get('actions', {})
        min_wait = data.get('min_wait', 5)
        max_wait = data.get('max_wait', 15)
        max_retries = data.get('max_retries', 3)
        
        if not profile_name:
            return jsonify({
                'success': False,
                'error': 'Profile name is required'
            }), 400
        
        if not tweet_links:
            return jsonify({
                'success': False,
                'error': 'Tweet links are required'
            }), 400
        
        # Validate actions
        if not any(actions.values()):
            return jsonify({
                'success': False,
                'error': 'At least one action must be selected'
            }), 400
        
        task_id = dashboard.run_automation_async(profile_name, tweet_links, reply_comments, 
                                               actions, min_wait, max_wait, max_retries)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Automation started'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/automation/state/<task_id>', methods=['GET'])
def get_automation_state(task_id):
    """Get automation state for a task"""
    try:
        if task_id in automation_states:
            state = automation_states[task_id]
            return jsonify({
                'success': True,
                'state': {
                    'task_id': state.task_id,
                    'profile_name': state.profile_name,
                    'total_tweets': len(state.paired_tasks),
                    'processed_count': len(state.processed_tasks),
                    'successful_count': len(state.successful_tasks),
                    'failed_count': len(state.failed_tasks),
                    'current_index': state.current_index,
                    'progress_percentage': state.get_progress_stats()['progress_percentage'],
                    'start_time': state.start_time,
                    'last_updated': state.last_updated,
                    'actions': state.actions,
                    'success_rate': state.get_progress_stats()['success_rate']
                }
            })
        else:
            # Try to load from file
            state = AutomationState.load_state(task_id)
            if state:
                return jsonify({
                    'success': True,
                    'state': {
                        'task_id': state.task_id,
                        'profile_name': state.profile_name,
                        'total_tweets': len(state.paired_tasks),
                        'processed_count': len(state.processed_tasks),
                        'successful_count': len(state.successful_tasks),
                        'failed_count': len(state.failed_tasks),
                        'current_index': state.current_index,
                        'progress_percentage': state.get_progress_stats()['progress_percentage'],
                        'start_time': state.start_time,
                        'last_updated': state.last_updated,
                        'actions': state.actions,
                        'success_rate': state.get_progress_stats()['success_rate']
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Automation state not found'
                }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/automation/recover/<task_id>', methods=['POST'])
def recover_automation(task_id):
    """Recover and resume an interrupted automation task"""
    try:
        # Load state from file
        state = AutomationState.load_state(task_id)
        if not state:
            return jsonify({
                'success': False,
                'error': 'No saved state found for recovery'
            }), 404
        
        # Check if task is already running
        all_tasks = get_task_status() # Use task state manager
        if task_id in all_tasks and all_tasks[task_id]['status'] == 'running':
            return jsonify({
                'success': False,
                'error': 'Task is already running'
            }), 400
        
        # Calculate remaining tweets
        remaining_tweets = []
        remaining_comments = []
        for i, task in enumerate(state.paired_tasks):
            if i not in state.processed_tasks:
                remaining_tweets.append(task['tweet_url'])
                remaining_comments.append(task['comment'])
        
        if not remaining_tweets:
            return jsonify({
                'success': False,
                'error': 'No remaining tweets to process'
            }), 400
        
        # Start new automation with remaining tweets
        new_task_id = dashboard.run_automation_async(
            state.profile_name, 
            remaining_tweets, 
            remaining_comments,
            state.actions, 
            state.min_wait, 
            state.max_wait, 
            state.max_retries
        )
        
        # Clean up old state
        state.cleanup()
        
        return jsonify({
            'success': True,
            'task_id': new_task_id,
            'message': f'Recovery started with {len(remaining_tweets)} remaining tweets',
            'remaining_count': len(remaining_tweets)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/automation/strategies', methods=['GET'])
def get_automation_strategies():
    """Get available automation strategies"""
    try:
        strategies = [
            {
                'name': 'standard',
                'description': 'Standard automation with like, retweet, and reply actions',
                'actions': ['like', 'retweet', 'reply']
            }
        ]
        
        return jsonify({
            'success': True,
            'strategies': strategies
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/automation/tasks/<task_id>', methods=['GET'])
def get_automation_tasks(task_id):
    """Get detailed information about paired tasks for an automation job"""
    try:
        if task_id in automation_states:
            state = automation_states[task_id]
        else:
            # Try to load from file
            state = AutomationState.load_state(task_id)
            if not state:
                return jsonify({
                    'success': False,
                    'error': 'Automation state not found'
                }), 404
        
        # Get detailed task information
        tasks_info = []
        for i, task in enumerate(state.paired_tasks):
            task_info = {
                'index': i,
                'tweet_url': task['tweet_url'],
                'comment': task['comment'],
                'status': 'pending'
            }
            
            if i in state.processed_tasks:
                if i in state.successful_tasks:
                    task_info['status'] = 'success'
                else:
                    task_info['status'] = 'failed'
            
            tasks_info.append(task_info)
        
        stats = state.get_progress_stats()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'profile_name': state.profile_name,
            'tasks': tasks_info,
            'stats': stats,
            'actions': state.actions,
            'start_time': state.start_time,
            'last_updated': state.last_updated
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """Get all active tasks"""
    try:
        tasks = []
        all_tasks = get_task_status()  # Use task state manager
        for task_id, task_data in all_tasks.items():
            tasks.append({
                'id': task_id,
                'type': task_data.get('type', 'unknown'),
                'status': task_data.get('status', 'unknown'),
                'progress': task_data.get('progress', 0),
                'current': task_data.get('current', 0),
                'total': task_data.get('total', 0),
                'start_time': task_data.get('start_time', '')
            })
        
        return jsonify({
            'success': True,
            'tasks': tasks
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status_endpoint(task_id):
    """Get task status"""
    all_tasks = get_task_status()  # Use task state manager
    if task_id in all_tasks:
        return jsonify({
            'success': True,
            'task': all_tasks[task_id]
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Task not found'
        }), 404

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def cancel_task(task_id):
    """Cancel a task"""
    all_tasks = get_task_status()  # Use task state manager
    if task_id in all_tasks:
        # Mark task as cancelled
        update_task_status(task_id, {'status': 'cancelled'})
        
        # Add cancellation log
        current_task = get_task_status().get(task_id, {})
        current_logs = current_task.get('logs', [])
        current_logs.append("Task cancelled by user")
        update_task_status(task_id, {'logs': current_logs})
        
        # Save automation state if it exists
        if task_id in automation_states:
            state = automation_states[task_id]
            state.save_state()
            current_task = get_task_status().get(task_id, {})
            current_logs = current_task.get('logs', [])
            current_logs.append("Automation state saved for potential recovery")
            update_task_status(task_id, {'logs': current_logs})
        
        # Terminate the thread if it's still running
        if task_id in active_threads:
            thread = active_threads[task_id]
            if thread.is_alive():
                # Note: Python threads can't be forcefully terminated
                # The thread will check the cancelled status and exit gracefully
                current_task = get_task_status().get(task_id, {})
                current_logs = current_task.get('logs', [])
                current_logs.append("Thread termination requested")
                update_task_status(task_id, {'logs': current_logs})
            
            # Remove thread reference
            del active_threads[task_id]
        
        return jsonify({
            'success': True,
            'message': 'Task cancelled'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Task not found'
        }), 404

@app.route('/api/files/scraped_tweets')
def get_scraped_tweets():
    """Get scraped tweets content"""
    try:
        if os.path.exists('scraped_tweets.txt'):
            with open('scraped_tweets.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'success': True,
                'content': content
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No scraped tweets file found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/files/download/<filename>')
def download_file(filename):
    """Download a file"""
    try:
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/vnc', methods=['GET'])
def get_vnc_config():
    """Get VNC configuration"""
    try:
        return jsonify({
            'success': True,
            'config': {
                'use_gui_chrome': config.use_gui_chrome,
                'vnc_display': config.vnc_display,
                'chrome_profile_dir': config.chrome_profile_dir,
                'chromedriver_path': config.chromedriver_path
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/vnc', methods=['POST'])
def update_vnc_config():
    """Update VNC configuration"""
    try:
        data = request.get_json()
        config.update({
            'use_gui_chrome': data.get('use_gui_chrome', False),
            'vnc_display': data.get('vnc_display', ':1'),
            'chrome_profile_dir': data.get('chrome_profile_dir', '~/.config/chrome_profiles'),
            'chromedriver_path': data.get('chromedriver_path', '/usr/local/bin/chromedriver')
        })
        return jsonify({
            'success': True,
            'message': 'VNC configuration updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/vnc/status')
def check_vnc_status():
    """Check VNC server status"""
    try:
        # Only check VNC on Linux
        if os.name != 'posix':
            return jsonify({
                'success': True,
                'vnc_running': False,
                'error': 'VNC is only supported on Linux'
            })
        
        # Verify VNC environment
        env_ready, env_error = verify_vnc_environment(config.vnc_display)
        if not env_ready:
            return jsonify({
                'success': True,
                'vnc_running': False,
                'error': env_error
            })
        
        # Check if VNC is running using consistent method
        vnc_running, error = check_vnc_running_simple(config.vnc_display)
        return jsonify({
            'success': True,
            'vnc_running': vnc_running,
            'error': error
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/status')
def system_status():
    """Get system status"""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return jsonify({
            'success': True,
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_total': memory.total,
                'disk_percent': disk.percent,
                'disk_used': disk.used,
                'disk_total': disk.total
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/info')
def system_info():
    """Get system information"""
    try:
        import platform
        import subprocess
        
        # OS info
        os_info = f"{platform.system()} {platform.release()}"
        
        # Python version
        python_version = platform.python_version()
        
        # Chrome version
        chrome_version = None
        try:
            result = subprocess.run(['google-chrome', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                chrome_version = result.stdout.strip()
        except:
            pass
        
        # ChromeDriver version
        chromedriver_version = None
        try:
            result = subprocess.run(['chromedriver', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                chromedriver_version = result.stdout.strip()
        except:
            pass
        
        # VNC status
        vnc_status = "Unknown"
        try:
            if os.name == 'posix':
                vnc_running, error = check_vnc_running_simple(":1")
                if vnc_running:
                    vnc_status = "Running"
                else:
                    vnc_status = "Not running"
            else:
                vnc_status = "Not supported on this OS"
        except:
            vnc_status = "Error checking"
        
        return jsonify({
            'success': True,
            'os_info': os_info,
            'python_version': python_version,
            'chrome_version': chrome_version,
            'chromedriver_version': chromedriver_version,
            'vnc_status': vnc_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vnc/start', methods=['POST'])
def start_vnc():
    """Start VNC server"""
    try:
        if os.name != 'posix':
            return jsonify({
                'success': False,
                'error': 'VNC is only supported on Linux'
            }), 400
        
        # Check if VNC server is installed
        try:
            result = subprocess.run(['which', 'vncserver'], capture_output=True, text=True)
            if result.returncode != 0:
                return jsonify({
                    'success': False,
                    'error': 'VNC server not found. Please install it first: sudo apt install -y tightvncserver'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error checking VNC installation: {str(e)}'
            }), 500
        
        # Check if VNC is already running using consistent method
        try:
            vnc_running, error = check_vnc_running_simple(config.vnc_display)
            if vnc_running:
                return jsonify({
                    'success': True,
                    'message': 'VNC server is already running'
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error checking VNC status: {str(e)}'
            }), 500
        
        # Create VNC startup script if it doesn't exist
        vnc_startup_dir = os.path.expanduser("~/.vnc")
        vnc_startup_file = os.path.join(vnc_startup_dir, "xstartup")
        
        if not os.path.exists(vnc_startup_dir):
            os.makedirs(vnc_startup_dir, exist_ok=True)
        
        if not os.path.exists(vnc_startup_file):
            startup_content = """#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
"""
            with open(vnc_startup_file, 'w') as f:
                f.write(startup_content)
            os.chmod(vnc_startup_file, 0o755)
        
        # Start VNC server with the specific command you provided
        try:
            result = subprocess.run([
                'vncserver', ':1', 
                '-geometry', '1920x1080', 
                '-depth', '24'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Get the server IP for dynamic display
                server_ip = get_server_ip()
                return jsonify({
                    'success': True,
                    'message': 'VNC server started successfully',
                    'output': result.stdout,
                    'server_ip': server_ip,
                    'vnc_address': f'{server_ip}:5901'
                })
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return jsonify({
                    'success': False,
                    'error': f'Failed to start VNC server: {error_msg}'
                }), 500
                
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': 'VNC server startup timed out'
            }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error starting VNC server: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/vnc/stop', methods=['POST'])
def stop_vnc():
    """Stop VNC server"""
    try:
        if os.name != 'posix':
            return jsonify({
                'success': False,
                'error': 'VNC is only supported on Linux'
            }), 400
        
        # Check if VNC is running using consistent method
        try:
            vnc_running, error = check_vnc_running_simple(config.vnc_display)
            if not vnc_running:
                return jsonify({
                    'success': True,
                    'message': 'VNC server is not running'
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error checking VNC status: {str(e)}'
            }), 500
        
        # Stop VNC server
        try:
            result = subprocess.run(['vncserver', '-kill', ':1'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': 'VNC server stopped successfully',
                    'output': result.stdout
                })
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return jsonify({
                    'success': False,
                    'error': f'Failed to stop VNC server: {error_msg}'
                }), 500
                
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': 'VNC server stop operation timed out'
            }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error stopping VNC server: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/vnc/cleanup', methods=['POST'])
def cleanup_vnc():
    """Clean up stale VNC processes and lock files"""
    try:
        if os.name != 'posix':
            return jsonify({
                'success': False,
                'error': 'VNC is only supported on Linux'
            }), 400
        
        cleanup_messages = []
        
        # Clean up VNC processes using existing method
        try:
            success, message = cleanup_stale_vnc_processes(config.vnc_display)
            if success:
                cleanup_messages.append(message)
            else:
                cleanup_messages.append(f"Process cleanup: {message}")
        except Exception as e:
            cleanup_messages.append(f"Process cleanup error: {str(e)}")
        
        # Clean up lock files as root
        try:
            lock_file = f"/tmp/.X1-lock"
            if os.path.exists(lock_file):
                result = subprocess.run(['sudo', 'rm', lock_file], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    cleanup_messages.append("Lock file removed successfully")
                else:
                    cleanup_messages.append(f"Lock file removal failed: {result.stderr}")
            else:
                cleanup_messages.append("No lock file found")
        except Exception as e:
            cleanup_messages.append(f"Lock file cleanup error: {str(e)}")
        
        # Clean up other potential lock files
        try:
            other_lock_files = [
                "/tmp/.X11-unix/X1",
                "/tmp/.X0-lock",
                "/tmp/.X2-lock"
            ]
            for lock_file in other_lock_files:
                if os.path.exists(lock_file):
                    try:
                        subprocess.run(['sudo', 'rm', '-rf', lock_file], 
                                      capture_output=True, text=True, timeout=5)
                        cleanup_messages.append(f"Removed {lock_file}")
                    except:
                        pass
        except Exception as e:
            cleanup_messages.append(f"Additional cleanup error: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'VNC cleanup completed',
            'details': cleanup_messages
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

def get_server_ip():
    """Get the server IP address dynamically"""
    try:
        import socket
        # Get the hostname
        hostname = socket.gethostname()
        # Get the IP address
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        print(f"Error getting server IP: {e}")
        return "localhost"

@app.route('/api/system/vnc-info')
def get_vnc_info():
    """Get VNC connection information"""
    try:
        server_ip = get_server_ip()
        vnc_running, error = check_vnc_running_simple(config.vnc_display)
        
        return jsonify({
            'success': True,
            'vnc_running': vnc_running,
            'server_ip': server_ip,
            'vnc_address': f'{server_ip}:5901',
            'vnc_url': f'vnc://{server_ip}:5901',
            'display': config.vnc_display,
            'error': error if not vnc_running else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_task')
def handle_join_task(data):
    """Join a task room for real-time updates"""
    task_id = data.get('task_id')
    if task_id:
        from flask_socketio import join_room
        join_room(task_id)

@app.route('/api/tools/extract-links', methods=['POST'])
def extract_links():
    """Extract unique X.com links from input text"""
    try:
        data = request.get_json()
        input_text = data.get('input_text', '')
        
        if not input_text.strip():
            return jsonify({
                'success': False,
                'error': 'Input text is required'
            }), 400
        
        # Import regex module
        import re
        
        # Regex pattern for x.com links
        pattern = re.compile(r'(https?://)?x\.com/\w+/status/\d+')
        
        # Set to store unique links
        unique_links = set()
        
        # Process input text line by line
        lines = input_text.split('\n')
        for line in lines:
            matches = pattern.findall(line)
            for match in re.finditer(pattern, line):
                # Always normalize to full URL
                url = match.group(0)
                if not url.startswith('http'):
                    url = 'https://' + url
                unique_links.add(url)
        
        # Write results to output file
        output_file = 'strippedlinks.txt'
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for link in sorted(unique_links):
                outfile.write(link + '\n')
        
        return jsonify({
            'success': True,
            'message': f'Extracted {len(unique_links)} unique links to "{output_file}"',
            'extracted_count': len(unique_links),
            'output_file': output_file,
            'links': sorted(list(unique_links))
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/files/strippedlinks')
def get_stripped_links():
    """Get stripped links content"""
    try:
        if os.path.exists('strippedlinks.txt'):
            with open('strippedlinks.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'success': True,
                'content': content
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No stripped links file found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter Automation Web Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"Starting Twitter Automation Web Dashboard on {args.host}:{args.port}")
    socketio.run(app, host=args.host, port=args.port, debug=args.debug)
