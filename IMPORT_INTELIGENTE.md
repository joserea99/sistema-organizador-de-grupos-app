# Sistema de Importación Inteligente de Excel/CSV

## ¿Qué se mejoró?

Se creó un **sistema de mapeo inteligente de columnas** que hace la importación de Excel/CSV mucho más flexible y robusta.

## Problema Anterior

Antes, el sistema esperaba nombres de columnas exactos como:
- `Nombre`
- `Teléfono` (con tilde)
- `Dirección` (con tilde)
- `Num Hijos`

Si tu archivo tenía:
- `Nombre Completo` ❌
- `Telefono` (sin tilde) ❌
- `Direccion` (sin tilde) ❌
- `Número de Hijos` ❌

...la importación fallaba.

## Solución Nueva

Ahora el sistema **reconoce automáticamente** múltiples variaciones de nombres de columnas:

### Ejemplos de lo que acepta:

#### Nombre
- ✅ `Nombre`
- ✅ `Name`
- ✅ `Nombre Completo`
- ✅ `Nombre y Familiar`
- ✅ `Titulo`
- ✅ `Persona`
- ✅ `Full Name`

#### Dirección
- ✅ `Dirección` (con tilde)
- ✅ `Direccion` (sin tilde)
- ✅ `Address`
- ✅ `Ubicación`
- ✅ `Domicilio`
- ✅ `Calle`
- ✅ `Descripción`

#### Teléfono
- ✅ `Teléfono` (con tilde)
- ✅ `Telefono` (sin tilde)
- ✅ `Phone`
- ✅ `Tel`
- ✅ `Celular`
- ✅ `Móvil`

#### Número de Hijos
- ✅ `Num Hijos`
- ✅ `Número de Hijos`
- ✅ `Numero de Hijos`
- ✅ `Hijos`
- ✅ `Children`

#### Cónyuge
- ✅ `Nombre Cónyuge`
- ✅ `Nombre Conyuge` (sin tilde)
- ✅ `Cónyuge`
- ✅ `Esposo`
- ✅ `Esposa`
- ✅ `Pareja`
- ✅ `Spouse`

...y muchas más!

## Características del Sistema

### 1. **Normalización Automática**
El sistema normaliza nombres de columnas:
- Quita tildes: `Teléfono` → `telefono`
- Convierte a minúsculas: `NOMBRE` → `nombre`
- Quita espacios: `Nombre Completo` → `nombrecompleto`
- Quita caracteres especiales: `Teléfono-Celular` → `telefonocelular`

### 2. **Independiente del Orden**
No importa en qué orden estén las columnas en tu archivo. El sistema las identificará automáticamente.

### 3. **Tolerante a Errores**
- Acepta columnas con o sin tildes
- Acepta mayúsculas o minúsculas
- Acepta múltiples formas de escribir lo mismo

### 4. **Mapeo Diagnóstico**
Cuando importas un archivo, el sistema muestra en la consola qué columnas detectó:

```
📊 Mapeo de columnas detectado:
  ✓ nombre               <- 'Nombre Completo'
  ✓ direccion            <- 'Direccion'
  ✓ telefono             <- 'Telefono'
  ✓ edad                 <- 'Edad'
  ✓ estado_civil         <- 'Estado Civil'
  ✓ num_hijos            <- 'Hijos'
  ✓ nombre_conyuge       <- 'Esposa'
  ⚠️  Columnas no encontradas: email, notas
```

## Archivos Modificados

### [`app/utils/excel_handler.py`](file:///Users/joserea/tu_proyecto_LIMPIO/app/utils/excel_handler.py)

**Nuevas funciones agregadas:**

1. **`normalizar_nombre_columna(nombre)`**
   - Normaliza nombres de columnas para comparación
   - Quita tildes, espacios, convierte a minúsculas

2. **`mapear_columnas(headers)`**
   - Mapea headers del archivo a nombres estándar
   - Reconoce ~70+ variaciones de nombres de columnas
   - Retorna diccionario `{campo_estandar: nombre_real_en_archivo}`

3. **`obtener_valor_flexible(fila, mapeo, campo)`**
   - Extrae valor usando el mapeo flexible
   - Maneja casos donde la columna no existe

4. **Mejoras a `extract_person_data()`**
   - Ahora usa mapeo inteligente
   - Más simple y mantenible
   - Reducido de ~180 líneas a ~80 líneas

5. **Mejoras a `process_import_file()`**
   - Crea el mapeo una vez
   - Muestra diagnóstico de columnas detectadas
   - Alerta sobre columnas faltantes

## Cómo Usar

### 1. Exportar Datos
- Ve a un tablero
- Haz clic en "Exportar" → Excel
- Se descarga un archivo `.xlsx`

### 2. Modificar el Excel (Opcional)
Ahora puedes:
- ✅ Cambiar nombres de columnas (mientras sean similares)
- ✅ Agregar columnas nuevas
- ✅ Cambiar el orden de las columnas
- ✅ Usar con/sin tildes
- ✅ Usar mayúsculas/minúsculas

### 3. Importar de Vuelta
- Ve a una lista
- Haz clic en "Importar"
- Selecciona el archivo
- ✅ **Funcionará automáticamente**

## Ejemplos de Archivos que Ahora Funcionan

### Ejemplo 1: Excel en Inglés
```
Name | Address | Phone | Age | Marital Status | Children | Spouse
John | 123 Main St | 555-1234 | 30 | Married | 2 | Jane
```
✅ **Funciona**

### Ejemplo 2: Excel sin tildes
```
Nombre | Direccion | Telefono | Edad | Estado Civil | Hijos | Conyuge
Juan | Av. Central | 555-4321 | 35 | Casado | 1 | Maria
```
✅ **Funciona**

### Ejemplo 3: Excel con nombres alternativos
```
Persona | Ubicacion | Celular | Años | Estatus | Numero de Hijos | Esposa
Pedro | Calle 5 | 555-9999 | 40 | Casado | 3 | Ana
```
✅ **Funciona**

### Ejemplo 4: Excel con orden diferente
```
Telefono | Nombre | Hijos | Direccion | Edad
555-1111 | Luis | 0 | Boulevard Norte | 28
```
✅ **Funciona**

## Campos Soportados

El sistema puede reconocer estos campos (con múltiples variaciones cada uno):

1. **Nombre** (obligatorio)
2. **Dirección**
3. **Teléfono**
4. **Edad**
5. **Estado Civil**
6. **Número de Hijos**
7. **Edades de Hijos**
8. **Nombre del Cónyuge**
9. **Edad del Cónyuge**
10. **Teléfono del Cónyuge**
11. **Trabajo del Cónyuge**
12. **Fecha de Matrimonio**
13. **Ocupación**
14. **Email**
15. **Responsable**
16. **Notas**

## Resultado

✅ **Importación mucho más flexible**
✅ **Funciona con archivos de diferentes fuentes**
✅ **Tolera errores de escritura**
✅ **Diagnóstico claro de qué se encontró**
✅ **Menos frustraciones al importar**

¡Ahora puedes importar archivos Excel/CSV de prácticamente cualquier formato!
