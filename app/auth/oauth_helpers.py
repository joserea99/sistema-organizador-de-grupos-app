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
    
    # TODO: Register Apple OAuth when credentials are available
    # oauth.register(
    #     name='apple',
    #     client_id=app.config['APPLE_CLIENT_ID'],
    #     ...
    # )
    
    return oauth


def generate_oauth_state():
    """Generate a secure random state parameter for OAuth"""
    return secrets.token_urlsafe(32)


def get_oauth_redirect_uri(provider):
    """Get the OAuth redirect URI for a provider"""
    return url_for(f'auth.{provider}_callback', _external=True)
