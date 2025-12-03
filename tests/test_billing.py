import unittest
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models import Usuario

class BillingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Create a test user
            user = Usuario(username='testuser', email='test@example.com', nombre_completo='Test User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username, password):
        return self.client.post('/auth/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_subscribe_page_requires_login(self):
        response = self.client.get('/billing/subscribe', follow_redirects=True)
        self.assertIn(b'Bienvenido de nuevo', response.data) # Should redirect to login

    def test_subscribe_page_loads(self):
        self.login('testuser', 'password123')
        response = self.client.get('/billing/subscribe')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Plan Premium', response.data)

    @patch('app.billing.routes.stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_checkout_create):
        # Mock Stripe response
        mock_checkout_create.return_value = MagicMock(url='https://checkout.stripe.com/test-session')
        
        self.login('testuser', 'password123')
        response = self.client.post('/billing/create-checkout-session')
        
        # Should redirect to Stripe URL
        self.assertEqual(response.status_code, 303) # 303 See Other
        self.assertEqual(response.headers['Location'], 'https://checkout.stripe.com/test-session')

    @patch('app.billing.routes.stripe.Webhook.construct_event')
    def test_webhook_success(self, mock_construct_event):
        # Mock webhook event
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'client_reference_id': '1', # ID might be UUID, need to check how it's generated in setup
                    'customer': 'cus_test123'
                }
            }
        }
        
        # Get the actual user ID
        with self.app.app_context():
            user = Usuario.query.filter_by(username='testuser').first()
            mock_event['data']['object']['client_reference_id'] = user.id
            
        mock_construct_event.return_value = mock_event
        
        # Send webhook request
        response = self.client.post('/billing/webhook', 
                                  data='fake_payload',
                                  headers={'Stripe-Signature': 'fake_signature'})
        
        self.assertEqual(response.status_code, 200)
        
        # Verify user was updated
        with self.app.app_context():
            user = Usuario.query.filter_by(username='testuser').first()
            self.assertTrue(user.suscripcion_activa)
            self.assertEqual(user.stripe_customer_id, 'cus_test123')

if __name__ == '__main__':
    unittest.main()
