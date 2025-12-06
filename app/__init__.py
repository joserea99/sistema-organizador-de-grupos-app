import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass

from flask import Flask, request, session
from flask_babel import Babel
from app.models import db

def get_locale():
    """Determine the best language to use for the request"""
    try:
        # 1. Check if user is authenticated and has a language preference
        if 'user_id' in session:
            from app.models import Usuario
            user = Usuario.query.filter_by(id=session['user_id']).first()
            if user and hasattr(user, 'preferred_language') and user.preferred_language:
                return user.preferred_language
        
        # 2. Check session for temporary language selection
        if 'language' in session:
            return session['language']
        
        # 3. Fall back to browser's accept_languages
        return request.accept_languages.best_match(['es', 'en']) or 'es'
    except Exception as e:
        # Fallback to Spanish if any error occurs
        print(f"Error in get_locale: {e}")
        return 'es'



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

    # Babel/i18n Config
    app.config['BABEL_DEFAULT_LOCALE'] = 'es'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['es', 'en']
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

    # Inicializar extensiones
    db.init_app(app)
    
    # Initialize Babel
    babel = Babel(app, locale_selector=get_locale)

    
    # Crear tablas si no existen
    # Crear tablas si no existen
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            # No re-raise to allow app to start and show health check
            
        # Inicializar storage de compatibilidad
        from app.models import storage, TableroStorage
    
    @app.route('/health')
    def health_check():
        return "OK", 200
    
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
