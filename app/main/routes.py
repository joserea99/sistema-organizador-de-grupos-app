from flask import Blueprint, redirect, render_template, session, url_for
from app.models import storage

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
def dashboard():
    try:
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        stats = storage.get_stats()
        tableros_activos = storage.get_recent_tableros()
        
        # Obtener cumpleaños próximos y formatearlos como recordatorios
        cumpleanos = storage.get_upcoming_birthdays()
        recordatorios_urgentes = []
        
        from datetime import datetime
        now = datetime.now()
        
        for p in cumpleanos:
            # Calcular urgencia
            urgencia = "pronto"
            if p.fecha_nacimiento:
                if p.fecha_nacimiento.day == now.day and p.fecha_nacimiento.month == now.month:
                    urgencia = "hoy"
                
                # Obtener nombres de tablero y lista de manera segura
                tablero_nombre = "General"
                lista_nombre = "Sin lista"
                if p.lista:
                    lista_nombre = p.lista.nombre
                    if p.lista.tablero:
                        tablero_nombre = p.lista.tablero.nombre

                recordatorios_urgentes.append({
                    'nombre': f"Cumpleaños de {p.nombre} {p.apellido or ''}",
                    'tablero_nombre': tablero_nombre,
                    'lista_nombre': lista_nombre,
                    'urgencia': urgencia
                })
                
        stats['recordatorios_pendientes'] = len(recordatorios_urgentes)
        
        return render_template("main/dashboard.html", 
                            stats=stats, 
                            tableros_activos=tableros_activos,
                            recordatorios_urgentes=recordatorios_urgentes)
    except Exception as e:
        import traceback
        return f"Error en dashboard: {str(e)} <br> <pre>{traceback.format_exc()}</pre>"


@main_bp.route("/recordatorios")
def recordatorios():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    # Datos que el template espera
    contadores = {
        'todos': 12,
        'vencidos': 3,
        'hoy': 5,
        'proximos': 4
    }
    recordatorios = []  # Lista vacía por ahora
    
    return render_template("main/recordatorios.html", contadores=contadores, recordatorios=recordatorios)
@main_bp.route("/personas")
def personas():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    # Obtener todas las personas
    from app.models import Tarjeta
    personas = Tarjeta.query.order_by(Tarjeta.nombre, Tarjeta.apellido).all()
    
    return render_template("main/personas.html", personas=personas)

@main_bp.route('/favicon.ico')
def favicon():
    return "", 204
