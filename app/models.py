from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import extract, func

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)  # Nullable for OAuth users
    nombre_completo = db.Column(db.String(120))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    rol = db.Column(db.String(20), default='user')
    suscripcion_activa = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(120))
    preferred_language = db.Column(db.String(5), default='es')
    
    # OAuth fields
    oauth_provider = db.Column(db.String(20))  # 'google', 'apple', or None for email
    oauth_id = db.Column(db.String(255))  # Unique ID from OAuth provider
    email_verified = db.Column(db.Boolean, default=False)  # True for OAuth, False for email

    
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

    @property
    def total_personas(self):
        return sum(len(l.tarjetas) for l in self.listas)

    @property
    def color(self):
        # Generar un color consistente basado en el nombre
        colors = ["#4f46e5", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
        if not self.nombre: return colors[0]
        return colors[sum(ord(c) for c in self.nombre) % len(colors)]

    def to_dict(self):
        total_tarjetas = sum(len(l.tarjetas) for l in self.listas)
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'tipo': self.tipo,
            'listas': [l.to_dict() for l in self.listas],
            'total_listas': len(self.listas),
            'total_tarjetas': total_tarjetas,
            'undo_stack': getattr(self, 'undo_stack', []),
            'historial': getattr(self, 'historial', [])
        }

    def agregar_lista(self, nombre, color="#e2e8f0"):
        lista = Lista(nombre=nombre, color=color, tablero_id=self.id)
        db.session.add(lista)
        return lista

    def get_lista(self, lista_id):
        return Lista.query.filter_by(id=lista_id, tablero_id=self.id).first()

    def eliminar_lista(self, lista_id):
        lista = self.get_lista(lista_id)
        if lista:
            db.session.delete(lista)
            return True
        return False
            
    def registrar_accion(self, usuario, accion, detalle):
        if not hasattr(self, 'historial'):
            self.historial = []
        
        evento = {
            'usuario': usuario,
            'accion': accion,
            'detalles': detalle,
            'fecha': datetime.now().isoformat()
        }
        self.historial.insert(0, evento)
        # Limitar historial a 50 eventos
        self.historial = self.historial[:50]
        
    def registrar_undo(self, tipo, datos):
        if not hasattr(self, 'undo_stack'):
            self.undo_stack = []
            
        self.undo_stack.append({
            'type': tipo,
            'data': datos
        })

    def get_todas_las_personas(self):
        personas = []
        for lista in self.listas:
            for tarjeta in lista.tarjetas:
                personas.append(tarjeta.to_dict())
        return personas

    @property
    def orden_listas(self):
        # Return list IDs sorted by 'orden'
        # Since 'orden' is not fully implemented in DB update logic yet, we rely on default order
        # But for reordering to work, we need a list we can manipulate in memory if we want transient reordering
        # Or we should query sorted.
        # For now, let's return a list of IDs that matches self.listas order
        if not hasattr(self, '_orden_listas'):
            self._orden_listas = [l.id for l in self.listas]
        return self._orden_listas
    
    @orden_listas.setter
    def orden_listas(self, value):
        self._orden_listas = value
        # Here we should update the 'orden' field in DB for each list
        # But for now, let's just keep it in memory or update DB immediately
        for index, lista_id in enumerate(value):
            lista = self.get_lista(lista_id)
            if lista:
                lista.orden = index


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

    def agregar_persona(self, **kwargs):
        # Filter kwargs to only match Tarjeta columns to avoid errors
        valid_columns = [c.key for c in Tarjeta.__table__.columns]
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_columns}
        
        tarjeta = Tarjeta(lista_id=self.id, **filtered_kwargs)
        db.session.add(tarjeta)
        return tarjeta

    def get_tarjeta(self, tarjeta_id):
        return Tarjeta.query.filter_by(id=tarjeta_id, lista_id=self.id).first()

    def eliminar_tarjeta(self, tarjeta_id):
        tarjeta = self.get_tarjeta(tarjeta_id)
        if tarjeta:
            db.session.delete(tarjeta)

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
    
    # Datos del Cónyuge (Ampliado)
    edad_conyuge = db.Column(db.Integer)
    telefono_conyuge = db.Column(db.String(50))
    email_conyuge = db.Column(db.String(120)) # New field
    trabajo_conyuge = db.Column(db.String(100))
    fecha_matrimonio = db.Column(db.Date)
    notas = db.Column(db.Text) # Notas generales
    
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

    @property
    def tiene_hijos(self):
        return self.numero_hijos is not None and self.numero_hijos > 0

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
            'lista_id': self.lista_id,
            # Campos adicionales para exportación y edición
            'numero_hijos': self.numero_hijos,
            'edades_hijos': self.edades_hijos,
            'nombre_conyuge': self.nombre_conyuge,
            'edad_conyuge': self.edad_conyuge if hasattr(self, 'edad_conyuge') else None, # Handle potential missing attr
            'telefono_conyuge': self.telefono_conyuge if hasattr(self, 'telefono_conyuge') else None,
            'email_conyuge': self.email_conyuge if hasattr(self, 'email_conyuge') else None,
            'trabajo_conyuge': self.trabajo_conyuge if hasattr(self, 'trabajo_conyuge') else None,
            'fecha_matrimonio': str(self.fecha_matrimonio) if hasattr(self, 'fecha_matrimonio') and self.fecha_matrimonio else None,
            'bautizado': self.bautizado,
            'es_lider': self.es_lider,
            'ministerio': self.ministerio,
            'notas': self.notas if hasattr(self, 'notas') else '',
            'tiene_hijos': self.tiene_hijos
        }

# Classes Removed