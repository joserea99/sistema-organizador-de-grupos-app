"""OAuth authentication helper functions for Google and Apple Sign-In"""

from authlib.integrations.flask_client import OAuth
from flask import url_for, current_app
import secrets

# Initialize OAuth
oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with Flask app"""
    oauth.init_app(app)
    
    # Register Google OAuth
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
        }
    )
    
    # Register Apple OAuth
    if app.config.get('APPLE_CLIENT_ID') and app.config.get('APPLE_PRIVATE_KEY'):
        oauth.register(
            name='apple',
            client_id=app.config.get('APPLE_CLIENT_ID'),
            client_secret=app.config.get('APPLE_PRIVATE_KEY'),
            server_metadata_url='https://appleid.apple.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'name email',
                'response_mode': 'form_post',
            }
        )
    
    return oauth


def generate_oauth_state():
    """Generate a secure random state parameter for OAuth"""
    return secrets.token_urlsafe(32)


def get_oauth_redirect_uri(provider):
    """Get the OAuth redirect URI for a provider, forcing HTTPS in production"""
    uri = url_for(f'auth.{provider}_callback', _external=True)
    
    # Force HTTPS in production (if not in debug mode)
    # This fixes redirect_uri_mismatch on Railway/Heroku behind proxies
    if not current_app.debug and uri.startswith('http://'):
        uri = uri.replace('http://', 'https://', 1)
        
    return uri
