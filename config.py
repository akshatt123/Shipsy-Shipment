import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Use /tmp for serverless environments
    DATABASE_PATH = os.environ.get('DATABASE_PATH', '/tmp/shipments.db')
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', '4'))
    
class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_PATH = 'shipments.db'  # Local file for development
    
class ProductionConfig(Config):
    DEBUG = False
    DATABASE_PATH = '/tmp/shipments.db'  # Serverless temp directory
