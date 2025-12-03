# Guía de Configuración de Stripe

Para que los pagos funcionen correctamente, necesitas configurar tu cuenta de Stripe para que coincida con las variables que has puesto en Railway.

## 1. Crear el Producto (Suscripción)

1.  Ve a tu [Dashboard de Stripe](https://dashboard.stripe.com/).
2.  Ve a la sección **Productos** (Products).
3.  Haz clic en **+ Añadir producto**.
4.  Nombre: `Suscripción Premium` (o el nombre que quieras).
5.  Precio: `9.99` (o el monto que desees).
6.  Intervalo: **Mensual** (Recurring).
7.  Haz clic en **Guardar producto**.
8.  En la página del producto creado, busca la sección "Precios" y copia el **API ID** del precio.
    *   Debe empezar por `price_...` (ejemplo: `price_1Pxyz...`).
    *   **Acción:** Este valor debe ir en la variable `STRIPE_PRICE_ID` en Railway.

## 2. Configurar el Webhook (Para activar las cuentas automáticamente)

El "Webhook" es la forma en que Stripe le avisa a tu aplicación que un pago se ha completado con éxito.

1.  Ve a **Desarrolladores** (Developers) -> **Webhooks**.
2.  Haz clic en **+ Añadir endpoint**.
3.  **URL del endpoint:** `https://web-production-cbf14.up.railway.app/billing/webhook`
4.  **Eventos a escuchar:** Haz clic en "+ Seleccionar eventos" y busca:
    *   `checkout.session.completed` (Pago exitoso).
    *   `customer.subscription.deleted` (Suscripción cancelada).
5.  Haz clic en **Añadir endpoint**.
6.  En la pantalla siguiente, busca donde dice "Secreto de firma" (Signing secret) y haz clic en **Revelar**.
    *   Debe empezar por `whsec_...`.
    *   **Acción:** Este valor debe ir en la variable `STRIPE_WEBHOOK_SECRET` en Railway.

## 3. Claves API (API Keys)

Asegúrate de que las claves que tienes en Railway coinciden con las de tu cuenta:

1.  Ve a **Desarrolladores** -> **Claves de API**.
2.  **Clave publicable** (`pk_...`) -> Va en `STRIPE_PUBLIC_KEY`.
3.  **Clave secreta** (`sk_...`) -> Va en `STRIPE_SECRET_KEY`.

---

### ¿Cómo actualizar las variables en Railway?

1.  Ve a tu proyecto en [Railway](https://railway.app/).
2.  Haz clic en tu servicio (la aplicación).
3.  Ve a la pestaña **Variables**.
4.  Edita las variables con los valores correctos que acabas de obtener de Stripe.
5.  Railway redeplegará la aplicación automáticamente.
