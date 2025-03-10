import os
import logging
from datetime import datetime

class Logger:
    """Custom logger for the application."""
    
    def __init__(self, log_level=logging.INFO):
        """Initialize logger with specified log level."""
        self.logger = logging.getLogger('urge')
        self.logger.setLevel(log_level)
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # File handler for general logs
        log_file = os.path.join(logs_dir, f'urge_{datetime.now().strftime("%Y%m%d")}.log')
        if not self.logger.handlers:
            # Add handlers here
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)
        
        # File handler for user inputs
        self.inputs_file = os.path.join(logs_dir, f'inputs_{datetime.now().strftime("%Y%m%d")}.log')
    
    def info(self, message):
        """Log info level message."""
        self.logger.info(message)
    
    def error(self, message):
        """Log error level message."""
        self.logger.error(message)
    
    def warning(self, message):
        """Log warning level message."""
        self.logger.warning(message)
    
    def log_input(self, text, label=None):
        """Log user input with timestamp and selected label."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label_info = f", Label: {label}" if label else ""
        
        # Log to both regular log and inputs log
        self.logger.info(f"User input: {text}{label_info}")
        
        # Log to dedicated inputs file
        with open(self.inputs_file, 'a') as f:
            f.write(f"{timestamp} - Input: {text}{label_info}\n")