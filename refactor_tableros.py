import re

filename = 'app/tableros/routes.py'
with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace imports
content = content.replace('from app.models import storage, UserStorage', 'from app.models import db, Tablero, Lista, Tarjeta, Usuario\nfrom app.services.stats_service import get_stats')
content = content.replace('user_storage = UserStorage()', '')

# Remove user_storage usages (already dealt with mostly but just in case)
content = re.sub(r'user_storage\.get_user\((.*?)\)', r'Usuario.query.get(\1)', content)

# Replace storage get_tablero
content = re.sub(r'storage\.get_tablero\((.*?)\)', r"Tablero.query.filter_by(id=\1, creador_id=session.get('user_id')).first()", content)

# Replace storage get_tableros_usuario
content = re.sub(r'storage\.get_tableros_usuario\((.*?)\)', r'Tablero.query.filter_by(creador_id=\1).order_by(Tablero.fecha_creacion.desc()).all()', content)

# Replace storage.save_to_disk()
content = content.replace('storage.save_to_disk()', 'db.session.commit()')

# Replace storage.get_stats
content = content.replace('storage.get_stats', 'get_stats')

# Replace crear_tablero
content = re.sub(
    r'storage\.crear_tablero\(\s*nombre=(.*?),\s*descripcion=(.*?),\s*icono=(.*?),\s*creador_id=(.*?)\s*\)',
    r'Tablero(nombre=\1, descripcion=\2, icono=\3, creador_id=\4)\n    db.session.add(tablero)\n    db.session.commit()',
    content,
    flags=re.DOTALL
)

# Fix the assignment issue for crear_tablero (it was `tablero = storage.crear_tablero(...)`)
content = re.sub(
    r'tablero = Tablero\(nombre=(.*?),\s*descripcion=(.*?),\s*icono=(.*?),\s*creador_id=(.*?)\)\s*db\.session\.add\(tablero\)\s*db\.session\.commit\(\)',
    r'tablero = Tablero(nombre=\1, descripcion=\2, icono=\3, creador_id=\4)\n    db.session.add(tablero)\n    db.session.commit()',
    content
)

# And similarly for elimination
content = re.sub(
    r'storage\.eliminar_tablero\((.*?)\)',
    r"Tablero.query.filter_by(id=\1, creador_id=session.get('user_id')).delete()\n    db.session.commit()",
    content
)


with open(filename, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
