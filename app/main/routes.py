from flask import Blueprint, redirect, render_template, session, url_for
from app.models import storage

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return redirect(url_for("tableros.lista"))


@main_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    stats = storage.get_stats()
    # Agregar campos que el template espera
    stats.update({
        'recordatorios_pendientes': 5,
        'tareas_vencidas': 2,
        'proyectos_activos': 3
    })
    return render_template("main/dashboard.html", stats=stats)


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


@main_bp.route('/favicon.ico')
def favicon():
    return "", 204
