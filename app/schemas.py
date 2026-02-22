from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load, EXCLUDE, INCLUDE

class UsuarioRegistroSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        
    username = fields.String(required=True, validate=validate.Length(min=3, max=80, error="El nombre de usuario debe tener entre 3 y 80 caracteres."))
    email = fields.Email(required=True, error_messages={"invalid": "Dirección de correo electrónico inválida.", "required": "El correo es requerido."})
    password = fields.String(required=True, validate=validate.Length(min=6, error="La contraseña debe tener al menos 6 caracteres."))
    nombre_completo = fields.String(required=True, validate=validate.Length(min=2, max=100, error="El nombre completo es requerido."))

class UsuarioLoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    username = fields.String(required=True, error_messages={"required": "El usuario o correo es requerido."})
    password = fields.String(required=True, error_messages={"required": "La contraseña es requerida."})
    remember = fields.Boolean(load_default=False)

class ChangePasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    current_password = fields.String(required=True, error_messages={"required": "La contraseña actual es requerida."})
    new_password = fields.String(required=True, validate=validate.Length(min=6, error="La nueva contraseña debe tener al menos 6 caracteres."))
    confirm_password = fields.String(required=True, error_messages={"required": "Debes confirmar la contraseña."})

class TableroSchema(Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=100, error="El nombre del tablero es requerido."))
    descripcion = fields.String(validate=validate.Length(max=500), load_default="")
    icono = fields.String(validate=validate.Length(max=50), load_default="folder")
    
class TableroCreacionSchema(TableroSchema):
    # Cuando creamos un tablero, podríamos recibir un array de nombres de listas
    listas = fields.List(fields.String(validate=validate.Length(min=1, max=100)), load_default=[])

class ListaSchema(Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=100, error="El nombre de la lista es requerido."))
    tablero_id = fields.String(required=True)

class TarjetaBaseSchema(Schema):
    class Meta:
        unknown = INCLUDE
        
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=100, error="El nombre de la persona es requerido."))
    lista_id = fields.String(required=True)
    
    telefono = fields.String(validate=validate.Length(max=20), allow_none=True, load_default=None)
    direccion = fields.String(validate=validate.Length(max=200), allow_none=True, load_default=None)
    lider_grupo = fields.String(validate=validate.Length(max=100), allow_none=True, load_default=None)
    etapa = fields.String(validate=validate.Length(max=50), allow_none=True, load_default=None)
    estado_asistencia = fields.String(validate=validate.Length(max=50), allow_none=True, load_default=None)
    rol = fields.String(validate=validate.Length(max=50), allow_none=True, load_default=None)
    sexo = fields.String(validate=validate.OneOf(["M", "F", "Otro", ""]), allow_none=True, load_default=None)
    es_matrimonio = fields.Boolean(load_default=False)
    nombre_esposo = fields.String(validate=validate.Length(max=100), allow_none=True, load_default=None)
    notas = fields.String(allow_none=True, load_default="")
    
    # Dates that come as empty strings from HTML forms must be handled
    fecha_nacimiento = fields.Date(allow_none=True, load_default=None)
    fecha_bautismo = fields.Date(allow_none=True, load_default=None)
    fecha_encuentro = fields.Date(allow_none=True, load_default=None)
    
    @pre_load
    def clean_empty_dates(self, in_data, **kwargs):
        # HTML forms send empty strings for empty date fields
        for field in ["fecha_nacimiento", "fecha_bautismo", "fecha_encuentro", "fecha_matrimonio"]:
            if field in in_data and in_data[field] == "":
                in_data[field] = None
        return in_data

