from app.schemas import UsuarioRegistroSchema, TableroSchema, ListaSchema, TarjetaBaseSchema
from marshmallow import ValidationError
import pytest

def test_usuario_registro_schema_valido():
    schema = UsuarioRegistroSchema()
    data = {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "securepassword",
        "nombre_completo": "John Doe",
        "confirm_password": "securepassword"
    }
    result = schema.load(data)
    assert result["username"] == "johndoe"
    assert result["email"] == "john@example.com"

def test_usuario_registro_schema_invalido():
    schema = UsuarioRegistroSchema()
    data = {
        "username": "jo", # Too short
        "email": "invalid-email", # Bad email format
        "password": "123", # Too short
        "nombre_completo": "J" # Too short
    }
    with pytest.raises(ValidationError) as excinfo:
        schema.load(data)
    
    assert "username" in excinfo.value.messages
    assert "email" in excinfo.value.messages
    assert "password" in excinfo.value.messages
    assert "nombre_completo" in excinfo.value.messages

def test_tablero_schema_valido():
    schema = TableroSchema()
    data = {"nombre": "Mi Tablero", "descripcion": "Un tablero genial", "icono": "🌟"}
    result = schema.load(data)
    assert result["nombre"] == "Mi Tablero"

def test_tablero_schema_invalido_sin_nombre():
    schema = TableroSchema()
    data = {"descripcion": "Falta nombre"}
    with pytest.raises(ValidationError) as excinfo:
        schema.load(data)
    assert "nombre" in excinfo.value.messages

def test_tarjeta_schema_valida():
    schema = TarjetaBaseSchema()
    data = {
        "nombre": "Pedro",
        "lista_id": "1",
        "email": "pedro@example.com",
        "fecha_nacimiento": "1990-05-15"
    }
    result = schema.load(data)
    assert result["nombre"] == "Pedro"
    assert result["lista_id"] == "1"
    assert result["fecha_nacimiento"].year == 1990

def test_tarjeta_schema_ignora_fecha_vacia():
    schema = TarjetaBaseSchema()
    data = {
        "nombre": "Pedro",
        "lista_id": "1",
        "fecha_nacimiento": "" # Should be converted to None gracefully by our validator
    }
    result = schema.load(data)
    assert result["fecha_nacimiento"] is None
