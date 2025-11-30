# Plan: Organizador de Grupos - Nueva Versión Modular

## 🎯 Objetivo
Crear una versión completamente nueva y limpia con **sistema de temas intercambiables** que mantenga toda la funcionalidad actual pero con mejor arquitectura.

## 🏗️ Estructura Propuesta

```
app/
├── static/
│   ├── css/
│   │   ├── base.css           # Estilos estructurales (no cambian)
│   │   ├── themes/
│   │   │   ├── moderno.css    # Tema dark con glassmorphism
│   │   │   ├── clasico.css    # Tema light profesional
│   │   │   └── minimalista.css # Tema clean & simple
│   │   └── components/
│   │       ├── cards.css
│   │       ├── modals.css
│   │       ├── forms.css
│   │       └── maps.css
│   ├── js/
│   │   ├── app.js             # Inicialización principal
│   │   ├── themes.js          # Sistema de cambio de temas
│   │   ├── kanban.js          # Drag & drop
│   │   ├── maps.js            # Google Maps
│   │   ├── filters.js         # Búsqueda y filtros
│   │   └── modals.js          # Gestión de modales
│   └── img/
│       └── themes/            # Recursos por tema
├── templates/
│   ├── base.html              # Template base
│   ├── components/            # Componentes reutilizables
│   │   ├── header.html
│   │   ├── card.html
│   │   └── modal.html
│   └── tableros/
│       ├── lista_v2.html      # Nueva versión dashboard
│       └── ver_v2.html        # Nueva versión kanban
```

## 📋 Fases de Implementación

### Fase 1: Sistema de Temas (Base)
**Prioridad: ALTA**

Crear la infraestructura de temas:
- Variables CSS para colores, espaciados, sombras
- Sistema de cambio de tema con persistencia (localStorage)
- 3 temas iniciales (Moderno, Clásico, Minimalista)

### Fase 2: Templates Base
**Prioridad: ALTA**

Crear templates limpios y modulares:
- Layout base con selector de temas
- Dashboard de tableros
- Vista Kanban básica

### Fase 3: Funcionalidad Core
**Prioridad: ALTA**

Migrar funcionalidades esenciales:
- CRUD de personas
- Drag & Drop
- Expansión de tarjetas
- Búsqueda y filtros

### Fase 4: Features Avanzados
**Prioridad: MEDIA**

- Google Maps
- Agrupación geográfica
- Importación Excel/CSV

### Fase 5: Polish
**Prioridad: BAJA**

- Animaciones
- Responsive
- Documentación

## 🎨 Temas Planificados

### 1. Tema "Moderno" (Dark)
- Background: Gradiente oscuro
- Glassmorphism en tarjetas
- Colores vibrantes (púrpura, azul, coral)
- Sombras pronunciadas

### 2. Tema "Clásico" (Light)
- Background: Blanco/gris claro
- Bordes sutiles
- Colores profesionales (azul, verde)
- Diseño limpio y tradicional

### 3. Tema "Minimalista"
- Background: Blanco puro
- Sin sombras (o muy sutiles)
- Colores monocromáticos
- Espacios amplios

## ✅ Beneficios

1. **Modularidad**: CSS y JS separados por función
2. **Mantenibilidad**: Cambios de tema sin tocar funcionalidad
3. **Escalabilidad**: Fácil agregar nuevos temas
4. **Personalización**: Usuario elige su preferencia
5. **Limpieza**: Código organizado y documentado

## 🚀 Siguientes Pasos

1. Crear estructura de carpetas
2. Implementar sistema de temas base
3. Crear primer tema funcional
4. Migrar funcionalidad crítica
5. Testing exhaustivo
