from flask import Blueprint, render_template, redirect, url_for, flash, session
from functools import wraps
from app.models import db, Usuario, Tablero, Lista

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Por favor inicia sesión para continuar.", "warning")
            return redirect(url_for('auth.login'))
            
        user = Usuario.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash("Acceso denegado. Se requieren permisos de administrador.", "error")
            return redirect(url_for('main.dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/hacerme_admin')
def hacerme_admin():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user = Usuario.query.get(session['user_id'])
    if user:
        user.is_admin = True
        db.session.commit()
        flash("¡Magia completada! Ahora eres Súper Administrador.", "success")
        
    return redirect(url_for('main.dashboard'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Obtener métricas globales
    total_usuarios = Usuario.query.count()
    usuarios_premium = Usuario.query.filter_by(suscripcion_activa=True).count()
    
    total_tableros = Tablero.query.count()
    
    # Calcular total de tarjetas de forma segura
    total_tarjetas = 0
    # Es más eficiente hacer un join, pero para sqlite/postgres compatibilidad simple:
    todas_listas = Lista.query.all()
    for lista in todas_listas:
        total_tarjetas += len(lista.tarjetas)
        
    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).all()
    
    stats = {
        'total_usuarios': total_usuarios,
        'usuarios_premium': usuarios_premium,
        'total_tableros': total_tableros,
        'total_tarjetas': total_tarjetas
    }
    
    return render_template('admin/dashboard.html', usuarios=usuarios, stats=stats)
