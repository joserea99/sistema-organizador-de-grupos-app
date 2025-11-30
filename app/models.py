from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre_completo = db.Column(db.String(120))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    rol = db.Column(db.String(20), default='user')
    suscripcion_activa = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(120))
    
    # Relaciones
    tableros = db.relationship('Tablero', backref='creador', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nombre_completo': self.nombre_completo,
            'rol': self.rol,
            'suscripcion_activa': self.suscripcion_activa
        }

class Tablero(db.Model):
    __tablename__ = 'tableros'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500))
    icono = db.Column(db.String(10), default="👥")
    tipo = db.Column(db.String(50), default="ministerio")
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    creador_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relaciones
    listas = db.relationship('Lista', backref='tablero', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'tipo': self.tipo,
            'listas': [l.to_dict() for l in self.listas]
        }

class Lista(db.Model):
    __tablename__ = 'listas'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), default="#e2e8f0")
    descripcion = db.Column(db.String(200))
    orden = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    tablero_id = db.Column(db.String(36), db.ForeignKey('tableros.id'), nullable=False)
    
    # Relaciones
    tarjetas = db.relationship('Tarjeta', backref='lista', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'color': self.color,
            'descripcion': self.descripcion,
            'tarjetas': [t.to_dict() for t in self.tarjetas]
        }

class Tarjeta(db.Model):
    __tablename__ = 'tarjetas'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(120))
    
    # Datos demográficos
    edad = db.Column(db.Integer)
    fecha_nacimiento = db.Column(db.Date)
    estado_civil = db.Column(db.String(50))
    ocupacion = db.Column(db.String(100))
    
    # Datos familiares
    nombre_conyuge = db.Column(db.String(100))
    numero_hijos = db.Column(db.Integer, default=0)
    edades_hijos = db.Column(db.String(100)) # Guardado como string "5,8,12"
    
    # Datos eclesiásticos
    bautizado = db.Column(db.Boolean, default=False)
    es_lider = db.Column(db.Boolean, default=False)
    ministerio = db.Column(db.String(100))
    
    # Metadatos
    orden = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lista_id = db.Column(db.String(36), db.ForeignKey('listas.id'), nullable=False)
    
    # Geolocalización
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido or ''}".strip()

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'nombre_completo': self.nombre_completo,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'edad': self.edad,
            'estado_civil': self.estado_civil,
            'ocupacion': self.ocupacion,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'lista_id': self.lista_id
        }

# Clases de compatibilidad para no romper el código existente
class UserStorage:
    def get_user(self, user_id):
        return Usuario.query.get(user_id)
    
    def get_user_by_username(self, username):
        return Usuario.query.filter_by(username=username).first()
        
    def get_user_by_email(self, email):
        return Usuario.query.filter_by(email=email).first()
        
    def create_user(self, username, email, password, nombre_completo=""):
        if self.get_user_by_username(username) or self.get_user_by_email(email):
            return None
        
        user = Usuario(username=username, email=email, nombre_completo=nombre_completo)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
            return user
        except:
            db.session.rollback()
            return None

    def save_to_disk(self):
        db.session.commit()

# Instancia global para compatibilidad
storage = None # Se inicializará en create_app