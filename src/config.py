import json
import os

class Config:
    """Configuration handler for the application."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from config.json file."""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))), 'config.json')
            
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            # Default configuration if file not found
            self._config = {
                "app": {"name": "Urge", "window_width": 600, "window_height": 40},
                "ui": {"background_color": "#333", "text_color": "#fff", 
                      "font_size_normal": "14px", "font_size_large": "16px"},
                "labels": {"1": "Label 1", "2": "Label 2", "3": "Label 3", 
                          "4": "Label 4", "5": "Label 5"},
                "paths": {"logs": "./logs", "assets": "./assets"}
            }
    
    def get(self, section, key=None):
        """Get configuration value."""
        if key is None:
            return self._config.get(section, {})
        return self._config.get(section, {}).get(key)