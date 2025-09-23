"""
Logging configuration for Events app.
"""

import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging for events
def setup_event_logging():
    """Setup logging configuration for events."""
    
    # Create logger
    logger = logging.getLogger('events')
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler for detailed logs
    detailed_handler = logging.FileHandler(
        os.path.join(logs_dir, f'events_detailed_{datetime.now().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    detailed_handler.setLevel(logging.DEBUG)
    detailed_handler.setFormatter(detailed_formatter)
    
    # File handler for errors only
    error_handler = logging.FileHandler(
        os.path.join(logs_dir, f'events_errors_{datetime.now().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers
    logger.addHandler(detailed_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create specific loggers
def get_event_logger():
    """Get events logger."""
    return logging.getLogger('events')

def get_cart_logger():
    """Get cart logger."""
    return logging.getLogger('events.cart')

def get_seat_logger():
    """Get seat selection logger."""
    return logging.getLogger('events.seats')

def get_booking_logger():
    """Get booking logger."""
    return logging.getLogger('events.booking')

# Setup logging
setup_event_logging() 