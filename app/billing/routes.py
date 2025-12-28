import stripe
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, jsonify
from app.models import UserStorage

billing_bp = Blueprint('billing', __name__)
user_storage = UserStorage()

@billing_bp.before_request
def check_auth():
    if request.endpoint == 'billing.webhook':
        return
    if request.endpoint == 'billing.webhook_test':  # Also allow webhook_test without auth
        return
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

@billing_bp.route('/subscribe')
def subscribe():
    user = user_storage.get_user(session['user_id'])
    
    if not user:
        # Si el usuario no existe en el storage (posible inconsistencia), forzar logout
        session.clear()
        return redirect(url_for('auth.login'))
        
    if user.suscripcion_activa:
        return render_template('billing/success.html', message="Ya tienes una suscripción activa.")
        
    return render_template('billing/subscribe.html', 
                         key=current_app.config['STRIPE_PUBLIC_KEY'])

@billing_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    user = user_storage.get_user(session['user_id'])
    
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=user.id,
            customer_email=user.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': current_app.config['STRIPE_PRICE_ID'],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('billing.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('billing.cancel', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"Error al conectar con Stripe: {str(e)}", "error")
        return redirect(url_for('billing.subscribe'))

@billing_bp.route('/success')
def success():
    return render_template('billing/success.html')

@billing_bp.route('/cancel')
def cancel():
    return render_template('billing/cancel.html')

@billing_bp.route('/create-portal-session', methods=['POST'])
def create_portal_session():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    user = user_storage.get_user(session['user_id'])
    
    if not user or not user.stripe_customer_id:
        flash("No se encontró información de suscripción.", "error")
        return redirect(url_for('auth.profile'))

    try:
        # Authenticate your user.
        checkout_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=url_for('auth.profile', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"Error al conectar con Stripe Portal: {str(e)}", "error")
        return redirect(url_for('auth.profile'))

@billing_bp.route('/webhook', methods=['POST'])
def webhook():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
    
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        current_app.logger.info(f"✅ Webhook verified: {event['type']}")
        print(f"✅ Webhook received and verified: {event['type']}")
    except ValueError as e:
        # Invalid payload
        current_app.logger.error("❌ Error parsing payload: " + str(e))
        print(f"❌ Error parsing payload: {e}")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        current_app.logger.error("❌ Error verifying webhook signature: " + str(e))
        print(f"❌ Error verifying webhook signature: {e}")
        return 'Invalid signature', 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        print(f"📦 Processing checkout.session.completed for session: {session_data.get('id')}")
        handle_checkout_session(session_data)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        print(f"🗑️ Processing customer.subscription.deleted for customer: {subscription.get('customer')}")
        handle_subscription_deleted(subscription)
    else:
        print(f"ℹ️ Unhandled event type: {event['type']}")

    return jsonify(success=True)

@billing_bp.route('/webhook-test')
def webhook_test():
    """Diagnostic endpoint to test webhook configuration"""
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET', '')
    stripe_secret = current_app.config.get('STRIPE_SECRET_KEY', '')
    
    status = {
        'webhook_secret_configured': bool(webhook_secret and webhook_secret != ''),
        'webhook_secret_length': len(webhook_secret) if webhook_secret else 0,
        'stripe_secret_configured': bool(stripe_secret and stripe_secret != ''),
        'webhook_url': url_for('billing.webhook', _external=True),
        'environment': 'TEST' if 'test' in stripe_secret else 'LIVE' if stripe_secret else 'NOT_CONFIGURED'
    }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Webhook Diagnostics</title>
        <style>
            body {{ font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .ok {{ background: #d4edda; border: 1px solid #c3e6cb; }}
            .error {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
            code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>🔍 Stripe Webhook Diagnostics</h1>
        
        <div class="status {'ok' if status['webhook_secret_configured'] else 'error'}">
            <strong>Webhook Secret:</strong> {'✅ Configured' if status['webhook_secret_configured'] else '❌ NOT CONFIGURED'}
            <br>Length: {status['webhook_secret_length']} characters
        </div>
        
        <div class="status {'ok' if status['stripe_secret_configured'] else 'error'}">
            <strong>Stripe Secret Key:</strong> {'✅ Configured' if status['stripe_secret_configured'] else '❌ NOT CONFIGURED'}
            <br>Environment: <code>{status['environment']}</code>
        </div>
        
        <div class="status ok">
            <strong>Webhook URL:</strong><br>
            <code>{status['webhook_url']}</code>
        </div>
        
        <h2>📋 Setup Checklist</h2>
        <ol>
            <li>Go to Stripe Dashboard → Developers → Webhooks</li>
            <li>Click "Add endpoint"</li>
            <li>Enter webhook URL: <code>{status['webhook_url']}</code></li>
            <li>Select events to listen for:
                <ul>
                    <li><code>checkout.session.completed</code></li>
                    <li><code>customer.subscription.deleted</code></li>
                </ul>
            </li>
            <li>Click "Add endpoint"</li>
            <li>Copy the "Signing secret" (starts with <code>whsec_...</code>)</li>
            <li>Add it to Railway environment variables as <code>STRIPE_WEBHOOK_SECRET</code></li>
            <li>Restart the Railway service</li>
        </ol>
        
        <h2>🧪 Test Your Webhook</h2>
        <p>After configuration, use Stripe CLI or dashboard to send test events:</p>
        <pre>stripe trigger checkout.session.completed</pre>
        
        <p><a href="/dashboard">← Back to Dashboard</a></p>
    </body>
    </html>
    """
    
    return html

def handle_checkout_session(session_data):
    user_id = session_data.get('client_reference_id')
    customer_id = session_data.get('customer')
    
    print(f"🔍 Looking for user with ID: {user_id}")
    print(f"📝 Customer ID from Stripe: {customer_id}")
    
    if user_id:
        user = user_storage.get_user(user_id)
        if user:
            print(f"✅ User found: {user.username}")
            print(f"📊 Current subscription status: {user.suscripcion_activa}")
            
            user.suscripcion_activa = True
            user.stripe_customer_id = customer_id
            user_storage.save_to_disk()
            
            print(f"✅ Subscription activated for user {user.username}")
            print(f"💾 User saved with stripe_customer_id: {customer_id}")
        else:
            print(f"❌ User NOT found with ID: {user_id}")
    else:
        print(f"❌ No client_reference_id in session data")

def handle_subscription_deleted(subscription):
    customer_id = subscription.get('customer')
    print(f"🔍 Looking for user with stripe_customer_id: {customer_id}")
    
    # Buscar usuario por stripe_customer_id
    user = user_storage.get_user_by_stripe_id(customer_id)
    if user:
        print(f"✅ User found: {user.username}")
        user.suscripcion_activa = False
        user_storage.save_to_disk()
        print(f"✅ Subscription deactivated for user {user.username}")
    else:
        print(f"❌ User NOT found with stripe_customer_id: {customer_id}")
