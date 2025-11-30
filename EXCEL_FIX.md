# Corrección de Importación/Exportación de Excel

## Problema Identificado

Cuando exportabas datos en Excel desde la aplicación y luego intentabas importarlos de nuevo, el proceso fallaba. Esto se debía a dos problemas:

### 1. Nombres de Columnas Inconsistentes
El exportador de Excel usaba nombres de columnas diferentes a los que el importador esperaba:

| Exportador (antes) | Importador espera |
|-------------------|-------------------|
| `Número de Hijos` | `Num Hijos` |
| `Edades de Hijos` | `Edades Hijos` |
| `Nombre Completo` | `Nombre` |

### 2. Campos Faltantes del Cónyuge
El modelo `Tarjeta` no tenía los siguientes campos del cónyuge:
- `edad_conyuge`
- `trabajo_conyuge`
- `fecha_matrimonio`

## Soluciones Aplicadas

### 1. Sincronización de Nombres de Columnas
**Archivo:** [`app/tableros/routes.py`](file:///Users/joserea/tu_proyecto_LIMPIO/app/tableros/routes.py)

Se modificó la función de exportación para usar los mismos nombres de columnas que el importador:

```python
# ANTES
'Nombre Completo': getattr(tarjeta, 'nombre_completo', ...),
'Número de Hijos': getattr(tarjeta, 'numero_hijos', ''),
'Edades de Hijos': getattr(tarjeta, 'edades_hijos', ''),

# DESPUÉS
'Nombre': getattr(tarjeta, 'nombre_completo', ...),
'Num Hijos': getattr(tarjeta, 'numero_hijos', ''),
'Edades Hijos': getattr(tarjeta, 'edades_hijos', ''),
```

### 2. Campos del Cónyuge Agregados
**Archivo:** [`app/models.py`](file:///Users/joserea/tu_proyecto_LIMPIO/app/models.py)

Se agregaron los campos faltantes al modelo `Tarjeta`:

```python
class Tarjeta:
    def __init__(self, ...):
        # Información del cónyuge
        self.nombre_conyuge = ""
        self.edad_conyuge = None        # ← NUEVO
        self.telefono_conyuge = ""
        self.trabajo_conyuge = ""       # ← NUEVO
        self.fecha_matrimonio = ""      # ← NUEVO
```

### 3. Actualización de Métodos de Serialización
Se actualizaron los siguientes métodos en `app/models.py`:
- `to_dict()` - Para incluir nuevos campos en la salida JSON
- `_serialize_tarjeta()` - Para guardar campos en JSON
- `_deserialize_tarjeta()` - Para cargar campos desde JSON

## Cómo Usar

### Exportar Datos
1. Accede a un tablero
2. Haz clic en el botón de exportar
3. Selecciona formato Excel
4. Se descarga un archivo `.xlsx` con todos los datos

### Importar Datos
1. Accede a una lista
2. Haz clic en el botón "Importar"
3. Selecciona el archivo Excel exportado
4. Los datos se importarán correctamente ✅

## Columnas en el Excel Exportado

El archivo Excel exportado ahora contiene las siguientes columnas (compatibles con la importación):

1. **Lista** - Nombre de la lista donde está la persona
2. **Nombre** - Nombre completo de la persona
3. **Dirección** - Dirección física
4. **Teléfono** - Número de teléfono
5. **Edad** - Edad de la persona
6. **Estado Civil** - Soltero, Casado, etc.
7. **Num Hijos** - Número de hijos
8. **Edades Hijos** - Edades separadas por comas (ej: "5, 8, 12")
9. **Nombre Cónyuge** - Nombre del cónyuge
10. **Edad Cónyuge** - Edad del cónyuge
11. **Teléfono Cónyuge** - Teléfono del cónyuge
12. **Trabajo Cónyuge** - Ocupación del cónyuge
13. **Fecha Matrimonio** - Fecha de matrimonio
14. **Ocupación** - Ocupación de la persona
15. **Email** - Correo electrónico
16. **Responsable** - Quien registró a la persona
17. **Notas** - Notas adicionales

## Resultado

✅ **Ahora puedes exportar datos de personas en Excel e importarlos de vuelta sin errores**

El ciclo completo de exportación → importación funciona correctamente.
