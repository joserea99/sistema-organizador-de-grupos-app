# Guía: Habilitar Google Maps API

## 🗺️ Problema Actual

La aplicación tiene la API Key `AIzaSyAM44jyxplaDzn1m7bJ79RtQGCmzYNuOCg` configurada, pero muestra errores:
- `NoApiKeys`
- `InvalidKey`

Esto significa que las APIs necesarias no están habilitadas en Google Cloud Console.

---

## ✅ Solución: Habilitar APIs en Google Cloud Console

### Paso 1: Acceder a Google Cloud Console

1. Ve a: https://console.cloud.google.com/
2. Inicia sesión con tu cuenta de Google
3. Selecciona el proyecto asociado a esta API key

### Paso 2: Habilitar las APIs Necesarias

Necesitas habilitar dos APIs:

#### 1. Maps JavaScript API
1. En el menú lateral, ve a **APIs & Services** → **Library**
2. Busca "Maps JavaScript API"
3. Haz clic en **ENABLE** (Habilitar)

#### 2. Geocoding API
1. En la biblioteca, busca "Geocoding API"
2. Haz clic en **ENABLE** (Habilitar)

### Paso 3: Verificar Restricciones de la API Key

1. Ve a **APIs & Services** → **Credentials**
2. Encuentra la key `AIzaSyAM44jyxplaDzn1m7bJ79RtQGCmzYNuOCg`
3. Haz clic para editar
4. En **API restrictions**, asegúrate de que incluya:
   - Maps JavaScript API
   - Geocoding API
5. En **Application restrictions**, si tienes restricciones HTTP, asegúrate de incluir:
   - `http://localhost:5000/*`
   - `http://127.0.0.1:5000/*`

### Paso 4: Guardar y Esperar

1. Guarda los cambios
2. **Espera 5-10 minutos** para que los cambios se propaguen
3. Recarga tu aplicación con Cmd+Shift+R (Mac) o Ctrl+Shift+F5 (Windows)

---

## 🆘 Alternativa: Generar Nueva API Key

Si no tienes acceso al proyecto o la key está restringida:

1. En Google Cloud Console, ve a **APIs & Services** → **Credentials**
2. Haz clic en **+ CREATE CREDENTIALS** → **API Key**
3. Copia la nueva key
4. Actualiza el archivo `/Users/joserea/tu_proyecto_LIMPIO/app/__init__.py`:
   ```python
   app.config["GOOGLE_MAPS_API_KEY"] = "TU_NUEVA_API_KEY_AQUI"
   ```
5. Habilita las APIs (Paso 2 arriba) para esta nueva key

---

## 📝 Notas Importantes

- **Facturación**: Google Maps requiere tener facturación habilitada, pero tiene un crédito gratuito mensual generoso
- **Seguridad**: En producción, restringe la key por dominio/IP
- **Límites**: Revisa los límites de uso en la consola para evitar cargos inesperados

---

## ✅ Verificación

Una vez habilitadas las APIs, el mapa debería:
1. Mostrar el mapa base de Google Maps (gris con calles)
2. Renderizar marcadores para cada dirección de persona
3. Permitir zoom e interacción

Si después de 10 minutos sigue sin funcionar, verifica la consola del navegador (F12) para ver los errores exactos.
