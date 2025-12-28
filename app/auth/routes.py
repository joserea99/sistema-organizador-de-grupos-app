from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.models import UserStorage, storage

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
            estado_civil="Casado",
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
