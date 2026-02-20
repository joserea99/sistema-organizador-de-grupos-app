from app.models import db, Tablero, Lista, Tarjeta
from app.services.stats_service import get_stats, get_upcoming_birthdays
from app.services.geocoding_service import fix_uncoded_people_for_tablero, update_person_coords
from app.services.excel_service import generar_plantilla_excel_bytes
import datetime

def test_excel_service_compiles():
    output, ftype = generar_plantilla_excel_bytes()
    assert ftype in ('excel', 'csv')
    assert output is not None

def test_stats_service(app, new_user):
    with app.app_context():
        # Insert test data
        t = Tablero(nombre="Test", creador_id=new_user.id)
        db.session.add(t)
        db.session.commit()
        
        l = Lista(nombre="En Progreso", tablero_id=t.id)
        db.session.add(l)
        db.session.commit()
        
        tarjeta = Tarjeta(nombre="Persona", lista_id=l.id)
        db.session.add(tarjeta)
        db.session.commit()
        
        # Test stats
        stats = get_stats(new_user.id)
        assert stats["total_tableros"] == 1
        assert stats["total_listas"] == 1
        assert stats["total_personas"] == 1

def test_upcoming_birthdays(app, new_user):
    with app.app_context():
        t = Tablero(nombre="Test", creador_id=new_user.id)
        db.session.add(t)
        db.session.commit()
        
        l = Lista(nombre="En Progreso", tablero_id=t.id)
        db.session.add(l)
        db.session.commit()
        
        now = datetime.datetime.now()
        tarjeta = Tarjeta(
            nombre="Cumpleañero", 
            lista_id=l.id,
            fecha_nacimiento=now.date()
        )
        db.session.add(tarjeta)
        db.session.commit()

        birthdays = get_upcoming_birthdays()
        # Ensure our test birthday appears in the output
        found = False
        for b in birthdays:
            if b.nombre == "Cumpleañero":
                found = True
                break
        assert found

def test_geocoding_service(app, new_user):
    with app.app_context():
        t = Tablero(nombre="Test", creador_id=new_user.id)
        db.session.add(t)
        db.session.commit()
        
        l = Lista(nombre="En Progreso", tablero_id=t.id)
        db.session.add(l)
        db.session.commit()
        
        persona = Tarjeta(
            nombre="Local", 
            direccion="Fake Address",
            lista_id=l.id
        )
        db.session.add(persona)
        db.session.commit()

        # Should be identified as needing geocoding
        uncoded = fix_uncoded_people_for_tablero(t.id, new_user.id)
        assert len(uncoded) == 1
        assert uncoded[0]['nombre'] == "Local"
        
        # Should correctly update coords
        res = update_person_coords(t.id, new_user.id, persona.id, 10.0, 20.0)
        assert res is True
        
        db.session.refresh(persona)
        assert persona.latitud == 10.0
        assert persona.longitud == 20.0
