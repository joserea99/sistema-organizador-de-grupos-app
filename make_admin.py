import os
import sys

# Configure environment path to load the app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Usuario

def make_admin(email):
    """Eleva los privilegios de un usuario basándose en su correo."""
    app = create_app()
    with app.app_context():
        # Buscar usuario por correo exacto
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario:
            print(f"❌ Error: No se encontró ningún usuario con el correo: {email}")
            print("Asegúrate de haberte registrado primero en la aplicación y verifica que el correo esté bien escrito.")
            return False
            
        if usuario.is_admin:
            print(f"✅ Éxito: El usuario {usuario.nombre_completo or usuario.username} ({email}) YA es administrador.")
            return True
            
        # Dar privilegios
        try:
            usuario.is_admin = True
            db.session.commit()
            print(f"🎉 ¡Felicidades! Se acaban de otorgar privilegios de Súper Administrador a:")
            print(f"   Nombre: {usuario.nombre_completo or usuario.username}")
            print(f"   Correo: {email}")
            print(f"\nYa puedes recargar la página principal y verás el nuevo botón 'Panel Admin' en el menú izquierdo.")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error de base de datos al intentar actualizar: {str(e)}")
            return False

if __name__ == '__main__':
    print("=" * 50)
    print("Herramienta de Elevación de Administrador")
    print("=" * 50)
    print("Por favor, introduce el correo electrónico de tu cuenta principal:")
    print("(Ejemplo: tunombre@gmail.com)\n")
    
    target_email = input("Correo electrónico: ")
    make_admin(target_email)
