from flask import Blueprint, flash, redirect, render_template, request, session, url_for, current_app
from app.models import UserStorage, storage, db, Usuario
# from app.auth.oauth_helpers import oauth, init_oauth, generate_oauth_state, get_oauth_redirect_uri
from functools import wraps

auth_bp = Blueprint("auth", __name__)
user_storage = UserStorage()

def crear_tablero_ejemplo(user_id):
    """Create a sample tablero for new users with FAKE data for demo purposes"""
    try:
        from datetime import date
        
        # Create sample tablero
        tablero = storage.crear_tablero(
            nombre="📖 Mi Primer Grupo",
            descripcion="Tablero de ejemplo para conocer la aplicación",
            icono="👥",
            creador_id=user_id
        )
        
        # Add sample lists
        lista_nuevos = tablero.agregar_lista("Nuevos Contactos", "#3b82f6")
        lista_activos = tablero.agregar_lista("Miembros Activos", "#10b981")
        lista_lideres = tablero.agregar_lista("Líderes", "#f59e0b")
        
        # Commit lists to database
        from app.models import db
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
        
        storage.save_to_disk()
        return tablero
    except Exception as e:
        print(f"Error creating sample tablero: {e}")
        return None

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        if not username_or_email or not password:
            flash("Por favor ingresa usuario y contraseña.", "error")
            return render_template("auth/login.html")

        # Intentar buscar por username o email
        user_storage.load_from_disk() # Recargar datos para asegurar que vemos usuarios nuevos
        user = user_storage.get_user_by_username(username_or_email)
        if not user:
            user = user_storage.get_user_by_email(username_or_email)
        
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
        nombre_completo = request.form.get("nombre_completo", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Validaciones básicas
        if not all([username, email, password]):
            flash("Todos los campos son obligatorios.", "error")
            return render_template("auth/register.html")
            
        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("auth/register.html")
            
        # Intentar crear usuario
        print(f"DEBUG: Intentando registrar usuario: {username}, {email}")
        user = user_storage.create_user(username, email, password, nombre_completo)
        
        if user:
            print(f"DEBUG: Usuario creado exitosamente: {user.id}")
            
            # ONBOARDING: Create sample tablero for new user
            print(f"DEBUG: Creating sample tablero for new user {user.id}")
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


@auth_bp.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = user_storage.get_user(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    # Datos del usuario para el template
    usuario = user.to_dict()
    
    # Stats simuladas por ahora (se conectarán con TableroStorage luego)
    stats = {
        "total_tableros": 0,
        "total_listas": 0,
        "total_personas": 0,
        "total_tarjetas": 0,
        "tableros_activos": 0,
        "tareas_pendientes": 0,
        "tareas_completadas": 0,
        "miembros_activos": 0,
        "proyectos_completados": 0,
    }

    return render_template("auth/profile.html", usuario=usuario, stats=stats)


@auth_bp.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        user = user_storage.get_user(session["user_id"])
        
        if not user or not user.check_password(current_password):
            flash("La contraseña actual es incorrecta.", "error")
        elif new_password != confirm_password:
            flash("Las nuevas contraseñas no coinciden.", "error")
        elif len(new_password) < 6:
            flash("La nueva contraseña debe tener al menos 6 caracteres.", "error")
        else:
            user.set_password(new_password)
            user_storage.save_to_disk()
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


# TODO: Apple OAuth routes (when credentials are available)
# @auth_bp.route("/apple/login")
# ...

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

@auth_bp.route('/debug/db-check')
def debug_db_check():
    """Temporary debug route to check DB stats"""
    if 'user_id' not in session:
        return "Not logged in"
    
    user_id = session['user_id']
    from app.models import Usuario, Tablero, Lista, Tarjeta, storage, db
    
    # 1. User Info
    user = Usuario.query.get(user_id)
    user_info = f"User: {user.username} ({user.email}) ID: {user.id}<br>"
    
    # 2. Get Stats Output
    stats = storage.get_stats(user_id)
    stats_info = f"Storage.get_stats: {stats}<br>"
    
    # 3. Manual counting
    tableros = Tablero.query.filter_by(creador_id=user_id).all()
    manual_info = f"Manual Tableros Query found: {len(tableros)}<br>"
    
    details = "<ul>"
    for t in tableros:
        listas = Lista.query.filter_by(tablero_id=t.id).all()
        details += f"<li>Tablero {t.id} ({t.nombre}) - Creador: {t.creador_id}"
        details += "<ul>"
        for l in listas:
            count = Tarjeta.query.filter_by(lista_id=l.id).count()
            details += f"<li>Lista {l.id} ({l.nombre}): {count} tarjetas</li>"
        details += "</ul></li>"
    details += "</ul>"
    
    # 4. Check for ORPHANED cards (cards in lists that belong to this user but query missed?)
    # or cards that simply exist in the DB
    total_cards_db = Tarjeta.query.count()
    orphan_info = f"Total cards in ENTIRE DB: {total_cards_db}<br>"
    
    return f"<h1>Debug DB Stats</h1>{user_info}<hr>{stats_info}<hr>{manual_info}{details}<hr>{orphan_info}"
