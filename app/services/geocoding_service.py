from app.models import db, Tablero, Lista, Tarjeta

def fix_uncoded_people_for_tablero(tablero_id, creador_id):
    """
    Check if a person has an address but misses geocoding. Returns list of dictionary data.
    """
    tablero = Tablero.query.filter_by(id=tablero_id, creador_id=creador_id).first()
    if not tablero:
        return None
        
    personas_to_code = []
    
    # Check what people we need to geocode
    for lista in tablero.listas:
        for tarjeta in lista.tarjetas:
            has_address = bool(tarjeta.direccion and tarjeta.direccion.strip())
            needs_coords = (tarjeta.latitud == 0 and tarjeta.longitud == 0) or tarjeta.latitud is None
            
            if has_address and needs_coords:
                personas_to_code.append({
                    'id': tarjeta.id,
                    'nombre': tarjeta.nombre_completo,
                    'direccion': tarjeta.direccion
                })
                
    return personas_to_code

def update_person_coords(tablero_id, creador_id, persona_id, lat, lng):
    tablero = Tablero.query.filter_by(id=tablero_id, creador_id=creador_id).first()
    if not tablero:
        return False
        
    for lista in tablero.listas:
        for tarjeta in lista.tarjetas:
            if tarjeta.id == persona_id:
                tarjeta.latitud = float(lat)
                tarjeta.longitud = float(lng)
                db.session.commit()
                return True
                
    return False
