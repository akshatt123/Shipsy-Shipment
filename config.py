import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Database configuration
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'shipments.db')
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', '4'))
    
    # SQLite specific settings
    SQLITE_TIMEOUT = 20
    SQLITE_CHECK_SAME_THREAD = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_PATH = 'shipments.db'  # Local file for development
    
class ProductionConfig(Config):
    DEBUG = False
    DATABASE_PATH = '/tmp/shipments.db'  # Serverless temp directory
    
class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ':memory:'  # In-memory database for testing
