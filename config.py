"""
Configuration module for the Twitter automation app
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional

class Config:
    """Configuration class for the Twitter automation app"""
    
    def __init__(self):
        self.config_dir = Path("app/config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "use_gui_chrome": False,
            "vnc_display": ":1",
            "chrome_profile_dir": "chrome-data" if os.path.exists("chrome-data") else ("~/.config/chrome_profiles" if os.name == 'posix' else "chrome-data"),
            "chromedriver_path": "/usr/local/bin/chromedriver" if os.name == 'posix' else None,
            "vnc_enabled": True,
            "vnc_resolution": "1920x1080",
            "vnc_depth": 24,
            "min_wait_time": 5,
            "max_wait_time": 15,
            "max_retries": 3,
            "log_level": "INFO"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = {**default_config, **json.load(f)}
            except Exception as e:
                print(f"Error loading config: {e}")
                self.settings = default_config
        else:
            self.settings = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str) -> Optional[str]:
        """Get a configuration value"""
        return self.settings.get(key)
    
    def set(self, key: str, value: any):
        """Set a configuration value"""
        self.settings[key] = value
        self.save_config()
    
    def update(self, settings: Dict):
        """Update multiple settings at once"""
        self.settings.update(settings)
        self.save_config()
    
    @property
    def use_gui_chrome(self) -> bool:
        """Whether to use GUI Chrome via VNC"""
        return self.settings.get("use_gui_chrome", False)
    
    @use_gui_chrome.setter
    def use_gui_chrome(self, value: bool):
        """Set whether to use GUI Chrome via VNC"""
        self.settings["use_gui_chrome"] = value
        self.save_config()
    
    @property
    def vnc_display(self) -> str:
        """Get the VNC display number"""
        return self.settings.get("vnc_display", ":1")
    
    @vnc_display.setter
    def vnc_display(self, value: str):
        """Set the VNC display number"""
        self.settings["vnc_display"] = value
        self.save_config()
    
    @property
    def chrome_profile_dir(self) -> str:
        """Get the Chrome profile directory"""
        return os.path.expanduser(self.settings.get(
            "chrome_profile_dir",
            "~/.config/chrome_profiles" if os.name == 'posix' else "chrome-data"
        ))
    
    @chrome_profile_dir.setter
    def chrome_profile_dir(self, value: str):
        """Set the Chrome profile directory"""
        self.settings["chrome_profile_dir"] = value
        self.save_config()
    
    @property
    def chromedriver_path(self) -> Optional[str]:
        """Get the ChromeDriver path"""
        return self.settings.get("chromedriver_path")
    
    @chromedriver_path.setter
    def chromedriver_path(self, value: str):
        """Set the ChromeDriver path"""
        self.settings["chromedriver_path"] = value
        self.save_config()
    
    @property
    def min_wait_time(self) -> int:
        """Get the minimum wait time"""
        return self.settings.get("min_wait_time", 5)
    
    @min_wait_time.setter
    def min_wait_time(self, value: int):
        """Set the minimum wait time"""
        self.settings["min_wait_time"] = value
        self.save_config()
    
    @property
    def max_wait_time(self) -> int:
        """Get the maximum wait time"""
        return self.settings.get("max_wait_time", 15)
    
    @max_wait_time.setter
    def max_wait_time(self, value: int):
        """Set the maximum wait time"""
        self.settings["max_wait_time"] = value
        self.save_config()
    
    @property
    def max_retries(self) -> int:
        """Get the maximum number of retries"""
        return self.settings.get("max_retries", 3)
    
    @max_retries.setter
    def max_retries(self, value: int):
        """Set the maximum number of retries"""
        self.settings["max_retries"] = value
        self.save_config()
    
    @property
    def log_level(self) -> str:
        """Get the log level"""
        return self.settings.get("log_level", "INFO")
    
    @log_level.setter
    def log_level(self, value: str):
        """Set the log level"""
        self.settings["log_level"] = value
        self.save_config()

# Global configuration instance
config = Config()
