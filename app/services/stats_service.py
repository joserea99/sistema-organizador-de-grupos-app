from datetime import datetime
from sqlalchemy import extract
from app.models import db, Tablero, Lista, Tarjeta
from app.cache import cache

@cache.memoize(timeout=600)
def get_stats(user_id=None):
    """Get statistics, optionally filtered by user"""
    now = datetime.now()
    
    if user_id:
        # Get user's tableros
        tableros_usuario = Tablero.query.filter_by(creador_id=user_id).all()
        tablero_ids = [t.id for t in tableros_usuario]
        
        # Get listas for user's tableros
        listas_usuario = Lista.query.filter(Lista.tablero_id.in_(tablero_ids)).all() if tablero_ids else []
        lista_ids = [l.id for l in listas_usuario]
        
        # Get personas in user's listas
        if lista_ids:
            total_personas = Tarjeta.query.filter(Tarjeta.lista_id.in_(lista_ids)).count()
            nuevos_mes = Tarjeta.query.filter(
                Tarjeta.lista_id.in_(lista_ids),
                extract('year', Tarjeta.fecha_creacion) == now.year,
                extract('month', Tarjeta.fecha_creacion) == now.month
            ).count()
        else:
            total_personas = 0
            nuevos_mes = 0
        
        return {
            "total_tableros": len(tableros_usuario),
            "total_listas": len(listas_usuario),
            "total_personas": total_personas,
            "nuevos_mes": nuevos_mes,
            "recordatorios_pendientes": 0
        }
    
    # Global stats (for admin or fallback)
    nuevos_mes = Tarjeta.query.filter(
        extract('year', Tarjeta.fecha_creacion) == now.year,
        extract('month', Tarjeta.fecha_creacion) == now.month
    ).count()
    
    return {
        "total_tableros": Tablero.query.count(),
        "total_listas": Lista.query.count(),
        "total_personas": Tarjeta.query.count(),
        "nuevos_mes": nuevos_mes,
        "recordatorios_pendientes": 0
    }

@cache.memoize(timeout=600)
def get_upcoming_birthdays(limit=5):
    # Simple implementation: get birthdays in current month
    now = datetime.now()
    return Tarjeta.query.filter(
        Tarjeta.fecha_nacimiento != None,
        extract('month', Tarjeta.fecha_nacimiento) == now.month,
        extract('day', Tarjeta.fecha_nacimiento) >= now.day
    ).order_by(extract('day', Tarjeta.fecha_nacimiento)).limit(limit).all()
