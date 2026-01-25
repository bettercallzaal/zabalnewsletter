"""
Debug Logger - Controllable visibility for ZABAL system
Provides editor-level clarity without console noise
"""

import json
import os
import datetime

class DebugLogger:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                "..", 
                "config", 
                "debug.json"
            )
        
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            # Default to silent if no config
            self.config = {
                "enabled": False,
                "level": "off"
            }
    
    def is_enabled(self, check_key=None):
        """Check if logging is enabled globally or for specific feature"""
        if not self.config.get("enabled"):
            return False
        
        if self.config.get("level") == "off":
            return False
        
        if check_key:
            return self.config.get(check_key, False)
        
        return True
    
    def should_log(self, level="verbose"):
        """Check if current level allows this log"""
        if not self.is_enabled():
            return False
        
        current_level = self.config.get("level", "off")
        
        level_hierarchy = {
            "off": 0,
            "basic": 1,
            "verbose": 2,
            "trace": 3
        }
        
        return level_hierarchy.get(current_level, 0) >= level_hierarchy.get(level, 2)
    
    def log(self, label, message, level="verbose", force=False):
        """
        Log a message with optional truncation and formatting
        
        Args:
            label: Category/section label
            message: Content to log
            level: "basic", "verbose", or "trace"
            force: Override level check (for critical info)
        """
        if not force and not self.should_log(level):
            return
        
        # Build timestamp
        timestamp = ""
        if self.config.get("timestamps"):
            timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
        
        # Truncate if needed
        if self.config.get("truncate_long_text") and isinstance(message, str):
            max_chars = self.config.get("max_chars", 800)
            if len(message) > max_chars:
                message = message[:max_chars] + " …[truncated]"
        
        # Color support (basic ANSI)
        if self.config.get("color_output"):
            label = f"\033[1;36m{label}\033[0m"  # Cyan bold
        
        print(f"{timestamp}{label}: {message}")
    
    def log_section(self, title, level="verbose"):
        """Log a section divider"""
        if not self.should_log(level):
            return
        print(f"\n{'=' * 60}")
        print(f"{title}")
        print(f"{'=' * 60}")
    
    def log_dict(self, label, data, level="verbose"):
        """Log a dictionary with pretty formatting"""
        if not self.should_log(level):
            return
        
        self.log(label, "", level)
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    self.log(f"  {key}", f"{type(value).__name__} with {len(value)} items", level)
                else:
                    self.log(f"  {key}", str(value)[:100], level)
        else:
            self.log(label, str(data), level)
    
    def log_diff(self, label, old_data, new_data, level="verbose"):
        """Log differences between two data structures"""
        if not self.should_log(level):
            return
        
        self.log_section(f"DIFF: {label}", level)
        
        # Simple diff for now (can add deepdiff later)
        if isinstance(old_data, dict) and isinstance(new_data, dict):
            # Added keys
            added = set(new_data.keys()) - set(old_data.keys())
            if added:
                self.log("+ ADDED KEYS", list(added), level)
            
            # Removed keys
            removed = set(old_data.keys()) - set(new_data.keys())
            if removed:
                self.log("- REMOVED KEYS", list(removed), level)
            
            # Changed values
            for key in set(old_data.keys()) & set(new_data.keys()):
                if old_data[key] != new_data[key]:
                    self.log(f"~ CHANGED: {key}", 
                           f"old={len(str(old_data[key]))} chars, new={len(str(new_data[key]))} chars", 
                           level)
        else:
            self.log("OLD", str(old_data)[:200], level)
            self.log("NEW", str(new_data)[:200], level)


# Global instance for easy import
logger = DebugLogger()
