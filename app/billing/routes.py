import stripe
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, jsonify
from app.models import UserStorage

billing_bp = Blueprint('billing', __name__)
user_storage = UserStorage()

@billing_bp.before_request
def check_auth():
    if request.endpoint == 'billing.webhook':
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

@billing_bp.route('/webhook', methods=['POST'])
def webhook():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    payload = request.get_data()  # Get raw bytes without decoding
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
    
    current_app.logger.info(f"Webhook received. Signature header present: {sig_header is not None}")
    current_app.logger.info(f"Endpoint secret configured: {endpoint_secret is not None}")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        current_app.logger.info(f"Webhook event constructed successfully: {event['type']}")
    except ValueError as e:
        current_app.logger.error(f"Webhook ValueError: {e}")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"Webhook SignatureVerificationError: {e}")
        return 'Invalid signature', 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        handle_checkout_session(session_data)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)

    return jsonify(success=True)

def handle_checkout_session(session_data):
    user_id = session_data.get('client_reference_id')
    customer_id = session_data.get('customer')
    
    if user_id:
        user = user_storage.get_user(user_id)
        if user:
            user.suscripcion_activa = True
            user.stripe_customer_id = customer_id
            user_storage.save_to_disk()
            print(f"Suscripción activada para usuario {user.username}")

def handle_subscription_deleted(subscription):
    customer_id = subscription.get('customer')
    # Buscar usuario por stripe_customer_id
    user = user_storage.get_user_by_stripe_id(customer_id)
    if user:
        user.suscripcion_activa = False
        user_storage.save_to_disk()
        print(f"Suscripción desactivada para usuario {user.username}")
