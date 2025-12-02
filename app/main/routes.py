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
    
    from app.models import Tarjeta
    
    # Obtener todas las tarjetas
    todas_tarjetas = Tarjeta.query.all()
    
    # Diccionario para agrupar miembros únicos
    miembros = {}
    
    for t in todas_tarjetas:
        # Normalizar clave para agrupación (Email > Nombre Completo)
        email = t.email.strip().lower() if t.email else None
        nombre_completo = f"{t.nombre} {t.apellido or ''}".strip().lower()
        
        # Usar email como clave primaria, o nombre si no hay email
        clave = email if email else nombre_completo
        
        if not clave:
            continue
            
        if clave not in miembros:
            miembros[clave] = {
                'id': t.id, # ID de referencia (usamos el de la primera tarjeta encontrada)
                'datos': t, # Objeto tarjeta para acceder a propiedades
                'grupos': [],
                'ids_tarjetas': [] # Para saber qué tarjetas son de esta persona
            }
        
        # Agregar ID de tarjeta a la lista de IDs de esta persona
        miembros[clave]['ids_tarjetas'].append(t.id)
        
        # Agregar información de membresía (Tablero/Lista)
        if t.lista and t.lista.tablero:
            miembros[clave]['grupos'].append({
                'tablero': t.lista.tablero.nombre,
                'lista': t.lista.nombre,
                'tablero_id': t.lista.tablero.id,
                'lista_id': t.lista.id,
                'color': t.lista.tablero.color
            })
            
        # Lógica básica de fusión de datos:
        # Si la tarjeta actual tiene información que le falta a la principal, la actualizamos
        main_data = miembros[clave]['datos']
        if not main_data.telefono and t.telefono:
            main_data.telefono = t.telefono
        if not main_data.direccion and t.direccion:
            main_data.direccion = t.direccion
        if not main_data.fecha_nacimiento and t.fecha_nacimiento:
            main_data.fecha_nacimiento = t.fecha_nacimiento

    # Convertir a lista y ordenar alfabéticamente
    lista_miembros = list(miembros.values())
    lista_miembros.sort(key=lambda x: x['datos'].nombre_completo)
    
    return render_template("main/personas.html", personas=lista_miembros)

@main_bp.route('/favicon.ico')
def favicon():
    return "", 204

@main_bp.route('/debug-config')
def debug_config():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    import os
    keys = [
        'STRIPE_PUBLIC_KEY',
        'STRIPE_SECRET_KEY',
        'STRIPE_PRICE_ID',
        'STRIPE_WEBHOOK_SECRET'
    ]
    
    html = "<h1>Estado de Configuración (Debug)</h1><ul>"
    for key in keys:
        val = os.environ.get(key)
        status = "✅ Configurado" if val and val.strip() else "❌ FALTANTE"
        # Show first 4 chars for verification if configured
        preview = f"({val[:4]}...)" if val and len(val) > 4 else ""
        html += f"<li><strong>{key}:</strong> {status} {preview}</li>"
    html += "</ul><a href='/dashboard'>Volver</a>"
    
    return html
