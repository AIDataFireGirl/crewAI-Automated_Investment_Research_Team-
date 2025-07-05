"""
Security Configuration Module
Handles rate limiting, input validation, and API key management for the investment research system.
"""

import os
import time
import hashlib
import logging
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime, timedelta
import re

class SecurityManager:
    """Manages security aspects of the investment research system."""
    
    def __init__(self):
        self.rate_limit_requests = {}  # Track API requests per minute
        self.max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))
        self.max_tokens_per_request = int(os.getenv('MAX_TOKENS_PER_REQUEST', 4000))
        self.enable_rate_limiting = os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup secure logging configuration."""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'investment_research.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def validate_api_key(self, api_key: str, key_type: str) -> bool:
        """
        Validate API key format and security.
        
        Args:
            api_key: The API key to validate
            key_type: Type of API key (openai, news, etc.)
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not api_key or api_key == f"your_{key_type}_api_key_here":
            self.logger.error(f"Invalid {key_type} API key provided")
            return False
        
        # Basic validation patterns for different API key types
        validation_patterns = {
            'openai': r'^sk-[a-zA-Z0-9]{48}$',
            'news': r'^[a-zA-Z0-9]{32}$',
            'alpha_vantage': r'^[a-zA-Z0-9]{16}$'
        }
        
        pattern = validation_patterns.get(key_type, r'^[a-zA-Z0-9]{16,}$')
        if not re.match(pattern, api_key):
            self.logger.error(f"Invalid {key_type} API key format")
            return False
        
        return True
    
    def rate_limit_check(self, user_id: str = "default") -> bool:
        """
        Check if user has exceeded rate limits.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            bool: True if within limits, False if exceeded
        """
        if not self.enable_rate_limiting:
            return True
        
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old entries
        self.rate_limit_requests = {
            k: v for k, v in self.rate_limit_requests.items() 
            if v > minute_ago
        }
        
        # Check current requests
        user_requests = [t for t in self.rate_limit_requests.values() if t > minute_ago]
        
        if len(user_requests) >= self.max_requests_per_minute:
            self.logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Add current request
        self.rate_limit_requests[f"{user_id}_{current_time}"] = current_time
        return True
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            str: Sanitized text
        """
        # Remove potentially dangerous characters
        dangerous_chars = ['<script>', '</script>', 'javascript:', 'onload=', 'onerror=']
        sanitized = text
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Limit length
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000]
        
        return sanitized
    
    def validate_ticker_symbol(self, ticker: str) -> bool:
        """
        Validate stock ticker symbol format.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            bool: True if valid format
        """
        if not ticker:
            return False
        
        # Basic ticker validation (1-5 characters, alphanumeric)
        pattern = r'^[A-Z]{1,5}$'
        return bool(re.match(pattern, ticker.upper()))
    
    def hash_sensitive_data(self, data: str) -> str:
        """
        Hash sensitive data for logging purposes.
        
        Args:
            data: Sensitive data to hash
            
        Returns:
            str: Hashed data
        """
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log security events for monitoring.
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        self.logger.info(f"Security Event - {event_type}: {details}")

# Global security manager instance
security_manager = SecurityManager()

def rate_limit_decorator(func):
    """Decorator to apply rate limiting to functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not security_manager.rate_limit_check():
            raise Exception("Rate limit exceeded. Please try again later.")
        return func(*args, **kwargs)
    return wrapper

def input_validation_decorator(func):
    """Decorator to validate and sanitize input parameters."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Sanitize string arguments
        sanitized_args = []
        for arg in args:
            if isinstance(arg, str):
                sanitized_args.append(security_manager.sanitize_input(arg))
            else:
                sanitized_args.append(arg)
        
        # Sanitize keyword arguments
        sanitized_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                sanitized_kwargs[key] = security_manager.sanitize_input(value)
            else:
                sanitized_kwargs[key] = value
        
        return func(*sanitized_args, **sanitized_kwargs)
    return wrapper 