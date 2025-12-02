import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass

from flask import Flask
from app.models import db

def create_app():
    # Cargar variables de entorno
    load_dotenv()

    app = Flask(__name__)

    # Configuración desde variables de entorno
    # Configuración desde variables de entorno
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave-por-defecto-cambiar")
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.config["GOOGLE_MAPS_API_KEY"] = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyAM44jyxplaDzn1m7bJ79RtQGCmzYNuOCg")
    
    # Stripe Config
    app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY', 'pk_test_tu_clave_publica')
    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY', 'sk_test_tu_clave_secreta')
    app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    app.config['STRIPE_PRICE_ID'] = os.getenv('STRIPE_PRICE_ID', 'price_tu_id_de_precio')

    # Database Config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
        
        # Inicializar storage de compatibilidad
        from app.models import storage, TableroStorage
    
    # Registrar blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.tableros.routes import tableros_bp
    from app.billing.routes import billing_bp
    from app.api.routes import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(tableros_bp, url_prefix="/tableros")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(billing_bp, url_prefix="/billing")

    return app
