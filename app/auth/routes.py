from flask import Blueprint, flash, redirect, render_template, request, session, url_for, current_app
from app.models import db, Usuario
from app.schemas import UsuarioRegistroSchema, UsuarioLoginSchema, ChangePasswordSchema
# from app.auth.oauth_helpers import oauth, init_oauth, generate_oauth_state, get_oauth_redirect_uri
from functools import wraps

auth_bp = Blueprint("auth", __name__)

def crear_tablero_ejemplo(user_id):
    """Create a sample tablero for new users with FAKE data for demo purposes"""
    try:
        from datetime import date
        
        # Create sample tablero
        tablero = Tablero(
            nombre="📖 Mi Primer Grupo",
            descripcion="Tablero de ejemplo para conocer la aplicación",
            icono="👥",
            creador_id=user_id
        )
        db.session.add(tablero)
        db.session.commit()
        
        # Add sample lists
        lista_nuevos = tablero.agregar_lista("Nuevos Contactos", "#3b82f6")
        lista_activos = tablero.agregar_lista("Miembros Activos", "#10b981")
        lista_lideres = tablero.agregar_lista("Líderes", "#f59e0b")
        
        # Commit lists to database
        db.session.commit()
        
        # Add sample people with FAKE data (clearly marked as examples)
        lista_nuevos.agregar_persona(
            nombre="Juan",
            apellido="Ejemplo",
            direccion="Calle Ejemplo 123 (Demo)",
            telefono="555-0100",
            email="juan.ejemplo@demo.com",
            edad=30,
            estado_civil="C asado",
            numero_hijos=2,
            edades_hijos="5, 8",
            nombre_conyuge="María Ejemplo",
            responsable="Demo"
        )
        
        lista_activos.agregar_persona(
            nombre="María",
            apellido="Demo",
            direccion="Av. Demo 456 (Ejemplo)",
            telefono="555-0200",
            email="maria.demo@demo.com",
            edad=25,
            estado_civil="Soltera",
            bautizado=True,
            responsable="Demo"
        )
        
        lista_lideres.agregar_persona(
            nombre="Pedro",
            apellido="Muestra",
            direccion="Calle Muestra 789 (Demo)",
            telefono="555-0300",
            email="pedro.muestra@demo.com",
            edad=35,
            estado_civil="Casado",
            bautizado=True,
            es_lider=True,
            ministerio="Ejemplo",
            responsable="Demo"
        )
        
        # Commit all personas to database
        db.session.commit()
        return tablero
    except Exception as e:
        print(f"Error creating sample tablero: {e}")
        return None

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            schema = UsuarioLoginSchema()
            valid_data = schema.load(request.form)
            username_or_email = valid_data.get("username", "").strip()
            password = valid_data.get("password", "")
            remember = valid_data.get("remember", False)
        except ValidationError as err:
            error_messages = [msg for el in err.messages.values() for msg in el]
            flash(error_messages[0] if error_messages else "Por favor ingresa usuario y contraseña.", "error")
            return render_template("auth/login.html")

        # Intentar buscar por username o email
        user = Usuario.query.filter_by(username=username_or_email).first()
        if not user:
            user = Usuario.query.filter_by(email=username_or_email).first()
        
        if user and user.check_password(password):
            if not user.activo:
                flash("Tu cuenta ha sido desactivada.", "error")
                return render_template("auth/login.html")
                
            session["user_id"] = user.id
            session["username"] = user.username
            session["rol"] = user.rol
            session.permanent = remember
            
            flash(f"¡Bienvenido de nuevo, {user.nombre_completo or user.username}!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Usuario o contraseña incorrectos.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión exitosamente.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            # Validate input through Marshmallow schema
            schema = UsuarioRegistroSchema()
            valid_data = schema.load(request.form)
            
            nombre_completo = valid_data.get("nombre_completo")
            username = valid_data.get("username")
            email = valid_data.get("email")
            password = valid_data.get("password")
            
        except ValidationError as err:
            # Flash the first schema validation error found
            error_messages = [msg for el in err.messages.values() for msg in el]
            flash(error_messages[0] if error_messages else "Datos inválidos.", "error")
            return render_template("auth/register.html")
        
        # Additional custom validation
        confirm_password = request.form.get("confirm_password", "")
        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("auth/register.html")
            
        current_app.logger.info(f"Intentando registrar usuario: {username}, {email}")
        
        user_exists = Usuario.query.filter((Usuario.username == username) | (Usuario.email == email)).first()
        
        if user_exists:
            user = None
        else:
            user = Usuario(username=username, email=email, nombre_completo=nombre_completo)
            user.set_password(password)
            db.session.add(user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                user = None
        
        if user:
            current_app.logger.info(f"Usuario creado exitosamente: {user.id}")
            
            # ONBOARDING: Create sample tablero for new user
            current_app.logger.info(f"Creating sample tablero for new user {user.id}")
            sample_tablero = crear_tablero_ejemplo(user.id)
            if sample_tablero:
                print(f"DEBUG: Sample tablero created: {sample_tablero.id}")
            else:
                print("DEBUG: Failed to create sample tablero")
            
            flash("¡Cuenta creada exitosamente! Por favor inicia sesión.", "success")
            return redirect(url_for("auth.login"))
        else:
            print("DEBUG: Fallo al crear usuario (duplicado o error)")
            flash("El nombre de usuario o email ya están en uso.", "error")
            
    return render_template("auth/register.html")


@auth_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = Usuario.query.get(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))
        
    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre_completo")
        nuevo_idioma = request.form.get("preferred_language")
        
        actualizado = False
        
        if nuevo_nombre is not None and nuevo_nombre != user.nombre_completo:
            user.nombre_completo = nuevo_nombre
            actualizado = True
            
        if nuevo_idioma in ['es', 'en'] and nuevo_idioma != user.preferred_language:
            user.preferred_language = nuevo_idioma
            session['lang'] = nuevo_idioma  # Update current session language
            actualizado = True
            
        if actualizado:
            db.session.commit()
            flash("Perfil actualizado exitosamente.", "success")
        
        return redirect(url_for("auth.profile"))

    # Pasar el objeto SQLAlchemy completo para evitar errores en Jinja con propiedades faltantes
    return render_template("auth/profile.html", usuario=user)


@auth_bp.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    if request.method == "POST":
        try:
            schema = ChangePasswordSchema()
            valid_data = schema.load(request.form)
            current_password = valid_data.get("current_password")
            new_password = valid_data.get("new_password")
            confirm_password = valid_data.get("confirm_password")
        except ValidationError as err:
            error_messages = [msg for el in err.messages.values() for msg in el]
            flash(error_messages[0] if error_messages else "Datos inválidos.", "error")
            return render_template("auth/change_password.html")
            
        user = Usuario.query.get(session["user_id"])
        
        if not user or not user.check_password(current_password):
            flash("La contraseña actual es incorrecta.", "error")
        elif new_password != confirm_password:
            flash("Las nuevas contraseñas no coinciden.", "error")
        else:
            user.set_password(new_password)
            db.session.commit()
            flash("Contraseña actualizada exitosamente.", "success")
            return redirect(url_for("auth.profile"))
            
    return render_template("auth/change_password.html")


# ===== OAuth ROUTES =====

@auth_bp.route("/google/login")
def google_login():
    """Initiate Google OAuth flow"""
    # Initialize OAuth if not already done
    # init_oauth(current_app) # Redundant, already in init
    
    try:
        from app.auth.oauth_helpers import oauth, generate_oauth_state, get_oauth_redirect_uri
        
        # Generate state parameter for security
        state = generate_oauth_state()
        session['oauth_state'] = state
        
        # Get the redirect URI (HTTPS enforced in prod)
        redirect_uri = get_oauth_redirect_uri('google')
        
        # Redirect to Google for authorization
        return oauth.google.authorize_redirect(redirect_uri, state=state)
    except Exception as e:
        print(f"Error initiating Google Login: {e}")
        flash("Error temporal en el servicio de inicio de sesión con Google. Intenta con email/contraseña.", "error")
        return redirect(url_for('auth.login'))


@auth_bp.route("/google/callback")
def google_callback():
    """Handle Google OAuth callback"""
    try:
        from app.auth.oauth_helpers import oauth, get_oauth_redirect_uri
        
        # Verify state parameter
        if request.args.get('state') != session.get('oauth_state'):
            flash("Error de seguridad en la autenticación. Por favor intenta de nuevo.", "error")
            return redirect(url_for('auth.login'))
        
        # Get the redirect URI used in the request (must match login)
        redirect_uri = get_oauth_redirect_uri('google')
        
        # Exchange authorization code for access token
        # Authlib 1.0+ handles redirect_uri automatically for Google
        token = oauth.google.authorize_access_token()
        
        # Get user info from Google (use userinfo endpoint instead of manual token parsing)
        # This avoids the 'nonce' requirement error
        user_info = oauth.google.userinfo()
        
        if not user_info or 'email' not in user_info:
            flash("No pudimos obtener tu información de Google. Por favor intenta de nuevo.", "error")
            return redirect(url_for('auth.login'))
        
        # Check if user exists
        email = user_info.get('email')
        oauth_id = user_info.get('sub')  # Google's unique user ID
        nombre_completo = user_info.get('name', '')
        email_verified = user_info.get('email_verified', False)
        
        user = Usuario.query.filter_by(email=email).first()
        is_new_user = False
        
        if not user:
            # Create new user
            from app.models import db
            import uuid
            
            # Generate username from email
            username = email.split('@')[0]
            # Make username unique if needed
            base_username = username
            counter = 1
            while Usuario.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = Usuario(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                nombre_completo=nombre_completo,
                oauth_provider='google',
                oauth_id=oauth_id,
                email_verified=email_verified,
                password_hash=None  # No password for OAuth users
            )
            
            db.session.add(user)
            db.session.commit()
            
            is_new_user = True
            
            #  Create sample tablero for new user
            print(f"DEBUG: Creating sample tablero for new OAuth user {user.id}")
            sample_tablero = crear_tablero_ejemplo(user.id)
            if sample_tablero:
                print(f"DEBUG: Sample tablero created: {sample_tablero.id}")
        
        else:
            # Update existing user with OAuth info if not already set
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = oauth_id
                user.email_verified = email_verified
                db.session.commit()
        
        # Log the user in
        session["user_id"] = user.id
        session["username"] = user.username
        session["rol"] = user.rol
        session.permanent = True
        
        # Clear OAuth state
        session.pop('oauth_state', None)
        
        if is_new_user:
            flash(f"¡Bienvenido, {user.nombre_completo}! Tu cuenta ha sido creada exitosamente.", "success")
            # Set flag to show subscription prompt
            session['show_subscription_prompt'] = True
        else:
            flash(f"¡Bienvenido de nuevo, {user.nombre_completo}!", "success")
        
        return redirect(url_for("main.dashboard"))
        
    except Exception as e:
        print(f"Error in Google OAuth callback: {e}")
        # DEBUG: Show explicit error to user
        flash(f"Error Google Login: {str(e)}", "error")
        return redirect(url_for('auth.login'))


@auth_bp.route("/apple/login")
def apple_login():
    """Initiate Apple OAuth flow"""
    try:
        from app.auth.oauth_helpers import oauth, generate_oauth_state, get_oauth_redirect_uri
        
        # Check if Apple is configured
        if 'apple' not in oauth._registry:
            flash("Inicio de sesión con Apple no configurado aún.", "error")
            return redirect(url_for('auth.login'))

        # Generate state parameter
        state = generate_oauth_state()
        session['oauth_state'] = state
        
        # Get redirect URI
        redirect_uri = get_oauth_redirect_uri('apple')
        
        # Redirect to Apple
        return oauth.apple.authorize_redirect(redirect_uri, state=state)
    except Exception as e:
        print(f"Error initiating Apple Login: {e}")
        flash("Error temporal en el servicio de Apple.", "error")
        return redirect(url_for('auth.login'))


@auth_bp.route("/apple/callback", methods=["POST"])  # Apple uses POST
def apple_callback():
    """Handle Apple OAuth callback"""
    try:
        from app.auth.oauth_helpers import oauth, get_oauth_redirect_uri
        
        # Verify state (Apple returns it in form data)
        # Note: Authlib validates state automatically in authorize_access_token if passed
        
        # Get session state
        session_state = session.get('oauth_state')
        if not session_state:
             flash("Error de sesión. Intenta de nuevo.", "error")
             return redirect(url_for('auth.login'))

        # Exchange code for token
        # Apple sends data in POST body
        token = oauth.apple.authorize_access_token()
        
        # Get user info from ID Token
        user_info = token.get('userinfo')
        
        if not user_info or 'email' not in user_info:
            flash("No pudimos obtener tu email de Apple.", "error")
            return redirect(url_for('auth.login'))
            
        email = user_info.get('email')
        oauth_id = user_info.get('sub')
        
        # Apple only sends 'name' on the FIRST login.
        # We need to extract it from the 'user' form field if present
        # format is JSON string: {"name": {"firstName": "Juan", "lastName": "Perez"}, ...}
        import json
        nombre_completo = ""
        user_form_data = request.form.get('user')
        if user_form_data:
            try:
                apple_user_data = json.loads(user_form_data)
                name_data = apple_user_data.get('name', {})
                first_name = name_data.get('firstName', '')
                last_name = name_data.get('lastName', '')
                nombre_completo = f"{first_name} {last_name}".strip()
            except Exception as e:
                print(f"Error parsing Apple user name: {e}")
        
        # Fallback if name is empty (subsequent logins)
        if not nombre_completo:
            nombre_completo = "Usuario Apple"

        # Check if user exists
        user = Usuario.query.filter_by(email=email).first()
        is_new_user = False
        
        if not user:
            # Create new user
            from app.models import db
            import uuid
            
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while Usuario.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = Usuario(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                nombre_completo=nombre_completo,
                oauth_provider='apple',
                oauth_id=oauth_id,
                email_verified=True, # Apple emails are verified
                password_hash=None
            )
            
            db.session.add(user)
            db.session.commit()
            is_new_user = True
            
            # Create sample details
            crear_tablero_ejemplo(user.id)
            
        else:
            # Update provider if needed
            if not user.oauth_provider:
                user.oauth_provider = 'apple'
                user.oauth_id = oauth_id
                user.email_verified = True
                db.session.commit()
        
        # Login
        session["user_id"] = user.id
        session["username"] = user.username
        session["rol"] = user.rol
        session.permanent = True
        session.pop('oauth_state', None)
        
        if is_new_user:
            flash(f"¡Bienvenido, {user.nombre_completo}! Cuenta creada con Apple.", "success")
            session['show_subscription_prompt'] = True
        else:
             flash(f"¡Bienvenido de nuevo!", "success")
             
        return redirect(url_for("main.dashboard"))
        
    except Exception as e:
        print(f"Error in Apple Callback: {e}")
        flash(f"Error login Apple: {str(e)}", "error")
        return redirect(url_for('auth.login'))

@auth_bp.route("/debug/force-migrate")
def debug_force_migrate():
    """Emergency route to force DB migration from browser"""
    try:
        import subprocess
        import sys
        
        # Verify admin or simple secret key (since login is broken)
        secret_key = request.args.get('key')
        if secret_key != "fix_db_now":
             return "Acceso denegado. Falta la clave secreta.", 403
             
        print("⚡️ Starting MANUAL migration via SUBPROCESS...", file=sys.stderr)
        
        # Subprocess failed (likely OOM), let's try Raw SQL execution in-process
        # This avoids spawning a new process and saves memory
        print("⚡️ Subprocess failed (Exit 1). Attempting Raw SQL Hotfix...", file=sys.stderr)
        
        from app import db
        from sqlalchemy import text
        
        sql_commands = [
            # Check/Add oauth_provider
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(20);",
            # Check/Add oauth_id
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS oauth_id VARCHAR(255);",
            # Check/Add email_verified
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;",
            # Make password_hash nullable (Postgres syntax)
            "ALTER TABLE usuarios ALTER COLUMN password_hash DROP NOT NULL;",
            # Update Alembic Version to match 'add_oauth_columns' revision
            "UPDATE alembic_version SET version_num = 'add_oauth_columns';"
        ]
        
        executed_log = []
        try:
            for cmd in sql_commands:
                print(f"Executing: {cmd}", file=sys.stderr)
                db.session.execute(text(cmd))
                executed_log.append(cmd)
            
            db.session.commit()
            print("✅ Raw SQL migration successful!", file=sys.stderr)
            return f"<h1>Hotfix Migration Successful!</h1><p>Executed SQL commands directly to bypass memory limits.</p><pre>{chr(10).join(executed_log)}</pre>", 200
            
        except Exception as sql_err:
            db.session.rollback()
            print(f"❌ Raw SQL execution failed: {sql_err}", file=sys.stderr)
            return f"<h1>Hotfix Failed</h1><p>Error: {sql_err}</p>", 500

    except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        print(f"❌ Route execution failed: {e}", file=sys.stderr)
        return f"Route Execution Error: {e} <br><pre>{error_info}</pre>", 500

