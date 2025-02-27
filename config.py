"""Application Configuration"""
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BaseConfig:
    """Base configuration settings"""
    CALENDAR_ID: str = os.getenv('CALENDAR_ID', 't15olu87ufqa11j6oc2f19kvao@group.calendar.google.com')
    PHOTO_INTERVAL: int = int(os.getenv('PHOTO_INTERVAL', '6000'))
    CALENDAR_INTERVAL: int = int(os.getenv('CALENDAR_INTERVAL', '30000'))
    PHOTO_DIRECTORY: str = os.getenv('PHOTO_DIRECTORY', 'static/album')

@dataclass
class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG: bool = True
    LOG_LEVEL: str = 'DEBUG'
    TESTING: bool = True
    PHOTO_OPTIMIZATION: bool = False  # Don't optimize photos in development

@dataclass
class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG: bool = False
    LOG_LEVEL: str = 'INFO'
    TESTING: bool = False
    PHOTO_OPTIMIZATION: bool = True  # Optimize photos in production

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()
