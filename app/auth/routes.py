from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.models import UserStorage

auth_bp = Blueprint("auth", __name__)
user_storage = UserStorage()

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
            return redirect(url_for("main.index"))
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
