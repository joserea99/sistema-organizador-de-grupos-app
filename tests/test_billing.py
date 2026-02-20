import pytest
from unittest.mock import patch, MagicMock
from app.models import db, Usuario

def login(client, username, password):
    return client.post('/auth/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_subscribe_page_requires_login(client):
    response = client.get('/billing/subscribe', follow_redirects=True)
    # The login page has the word "iniciar" for Iniciar Sesión usually
    assert b'Bienvenido' in response.data or b'Iniciar' in response.data 

def test_subscribe_page_loads(client, new_user):
    login(client, 'testuser', 'TestPass123!')
    response = client.get('/billing/subscribe')
    assert response.status_code == 200
    assert b'Premium' in response.data

@patch('app.billing.routes.stripe.checkout.Session.create')
def test_create_checkout_session(mock_checkout_create, client, new_user):
    # Mock Stripe response
    mock_checkout_create.return_value = MagicMock(url='https://checkout.stripe.com/test-session')
    
    login(client, 'testuser', 'TestPass123!')
    response = client.post('/billing/create-checkout-session')
    
    # Should redirect to Stripe URL
    assert response.status_code == 303 # 303 See Other
    assert response.headers['Location'] == 'https://checkout.stripe.com/test-session'

@patch('app.billing.routes.stripe.Webhook.construct_event')
def test_webhook_success(mock_construct_event, client, app, new_user):
    # Mock webhook event
    mock_event = {
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'client_reference_id': new_user.id, 
                'customer': 'cus_test_12345'
            }
        }
    }
        
    mock_construct_event.return_value = mock_event
    
    # Send webhook request
    response = client.post('/billing/webhook', 
                              data='fake_payload',
                              headers={'Stripe-Signature': 'fake_signature'})
    
    assert response.status_code == 200
    
    # Verify user was updated
    with app.app_context():
        # Re-query
        user = Usuario.query.get(new_user.id)
        assert user.suscripcion_activa is True
        assert user.stripe_customer_id == 'cus_test_12345'
