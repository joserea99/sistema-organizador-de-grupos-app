import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta-cambiar'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///ministerio.db'
    UPLOADS_FOLDER = os.environ.get('UPLOADS_FOLDER') or 'app/static/uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16777216)
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') or ''
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stripe Configuration
    # Stripe Configuration
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY') or 'pk_test_tu_clave_publica'
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or 'sk_test_tu_clave_secreta'
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET') or ''
    STRIPE_PRICE_ID = os.environ.get('STRIPE_PRICE_ID') or 'price_tu_id_de_precio'

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    
class TestingConfig(Config):
    """Configuración de testing"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
