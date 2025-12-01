from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify, send_file, current_app
from io import BytesIO
from datetime import datetime
import pandas as pd
import json
from app.models import storage, UserStorage

tableros_bp = Blueprint("tableros", __name__)
user_storage = UserStorage()

@tableros_bp.before_request
def check_subscription():
    # Permitir peticiones OPTIONS y archivos estáticos
    if request.method == 'OPTIONS' or request.endpoint == 'static':
        return
        
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user = user_storage.get_user(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
        
    # Verificar suscripción (con periodo de gracia de 14 días)
    # if not user.suscripcion_activa:
    #     dias_desde_registro = (datetime.now() - user.fecha_registro).days
    #     if dias_desde_registro > 14:
    #         flash("Tu periodo de prueba ha terminado. Por favor suscríbete para continuar.", "warning")
    #         return redirect(url_for('billing.subscribe'))
    pass

# Datos de plantillas (mantenemos las plantillas)
PLANTILLAS_EJEMPLO = {
    "direccion_adultos": {
        "liderazgo-1": {
            "nombre": "Reunión de Líderes",
            "descripcion": "Template para reuniones de liderazgo ministerial",
            "icono": "👥",
            "listas": ["Agenda", "Decisiones", "Seguimiento"],
        },
        "planificacion-1": {
            "nombre": "Planificación Anual",
            "descripcion": "Template para planificación estratégica",
            "icono": "📋",
            "listas": ["Objetivos", "Recursos", "Cronograma"],
        },
    },
    "familia": {
        "actividades-fam-1": {
            "nombre": "Actividades Familiares",
            "descripcion": "Template para eventos y actividades familiares",
            "icono": "👨‍👩‍👧‍👦",
            "listas": ["Planificación", "Participantes", "Recursos"],
        },
        "crecimiento-fam-1": {
            "nombre": "Crecimiento Familiar",
            "descripcion": "Template para seguimiento del crecimiento familiar",
            "icono": "🌱",
            "listas": ["Metas", "Progreso", "Reflexiones"],
        },
    },
    "estudiantes": {
        "juventud-1": {
            "nombre": "Grupo Juvenil",
            "descripcion": "Template para actividades y proyectos juveniles",
            "icono": "🎓",
            "listas": ["Actividades", "Participantes", "Recursos"],
        },
        "estudios-1": {
            "nombre": "Estudios Bíblicos",
            "descripcion": "Template para organizar estudios bíblicos",
            "icono": "📖",
            "listas": ["Temas", "Materiales", "Participantes"],
        },
    },
    "crecimiento": {
        "personal-1": {
            "nombre": "Crecimiento Personal",
            "descripcion": "Template para desarrollo personal y espiritual",
            "icono": "🚀",
            "listas": ["Metas", "Hábitos", "Reflexiones"],
        },
        "espiritual-1": {
            "nombre": "Metas Espirituales",
            "descripcion": "Template para el crecimiento espiritual",
            "icono": "🙏",
            "listas": ["Objetivos", "Prácticas", "Progreso"],
        },
    },
    "servicio": {
        "comunitario-1": {
            "nombre": "Proyectos de Servicio",
            "descripcion": "Template para proyectos de servicio comunitario",
            "icono": "🤝",
            "listas": ["Planificación", "Voluntarios", "Impacto"],
        },
        "ministerios-1": {
            "nombre": "Ministerios",
            "descripcion": "Template para gestionar diferentes ministerios",
            "icono": "⛪",
            "listas": ["Actividades", "Miembros", "Recursos"],
        },
    },
}


@tableros_bp.route("/")
def lista():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Obtener tableros reales del storage
    tableros = [t.to_dict() for t in storage.get_all_tableros()]
    stats = storage.get_stats()
    
    return render_template("tableros/lista.html", tableros=tableros, stats=stats)


# Colores para las listas
KANBAN_COLORS = [
    "#ef4444", "#dc2626", "#b91c1c", # Rojos
    "#f97316", "#ea580c", "#c2410c", # Naranjas
    "#f59e0b", "#d97706", "#b45309", # Ambar
    "#84cc16", "#65a30d", "#4d7c0f", # Lima
    "#10b981", "#059669", "#047857", # Esmeralda
    "#06b6d4", "#0891b2", "#0e7490", # Cyan
    "#3b82f6", "#2563eb", "#1d4ed8", # Azul
    "#6366f1", "#4f46e5", "#4338ca", # Indigo
    "#8b5cf6", "#7c3aed", "#6d28d9", # Violeta
    "#ec4899", "#db2777", "#be185d", # Rosa
    "#f43f5e", "#e11d48", "#be123c", # Rose
    "#64748b", "#475569", "#334155"  # Slate
]

@tableros_bp.route("/<tablero_id>")
def ver(tablero_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    tablero = storage.get_tablero(tablero_id)
    if not tablero:
        flash("Tablero no encontrado", "error")
        return redirect(url_for("tableros.lista"))

    tablero_dict = tablero.to_dict()
    listas = tablero_dict['listas']
    usuario = {"username": session.get("username")}
    
    return render_template("tableros/ver.html", 
                         tablero=tablero_dict, 
                         listas=listas, 
                         usuario=usuario,
                         colores=KANBAN_COLORS)


@tableros_bp.route("/api/tablero/<tablero_id>/data")
def get_tablero_data(tablero_id):
    """Obtener datos completos del tablero en JSON"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    tablero = storage.get_tablero(tablero_id)
    if not tablero:
        return jsonify({'error': 'Tablero no encontrado'}), 404
        
    return jsonify(tablero.to_dict())


@tableros_bp.route("/crear")
def crear():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("tableros/crear.html", plantillas=PLANTILLAS_EJEMPLO)


@tableros_bp.route("/procesar", methods=["POST"])
def procesar():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Obtener datos del formulario
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    icono = request.form.get("icono", "📋").strip()
    
    if not nombre:
        flash("El nombre del tablero es obligatorio", "error")
        return redirect(url_for("tableros.crear"))

    # Crear tablero real
    tablero = storage.crear_tablero(
        nombre=nombre,
        descripcion=descripcion,
        icono=icono,
        creador_id=session.get("user_id")
    )
    
    # Agregar listas iniciales si se especificaron
    listas_nombres = request.form.getlist("nombres_listas[]")
    print(f"DEBUG: Listas recibidas del formulario: {listas_nombres}")
    
    if listas_nombres:
        for lista_nombre in listas_nombres:
            if lista_nombre.strip():
                tablero.agregar_lista(lista_nombre.strip())
        
        # Guardar cambios en la base de datos (commit de las listas)
        storage.save_to_disk()
    
    flash(f"¡Tablero '{nombre}' creado exitosamente!", "success")
    return redirect(url_for("tableros.ver", tablero_id=tablero.id))


@tableros_bp.route("/plantillas")
def plantillas():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("tableros/plantillas.html", plantillas=PLANTILLAS_EJEMPLO)


@tableros_bp.route("/crear_desde_plantilla/<plantilla_id>")
def crear_desde_plantilla(plantilla_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Buscar la plantilla
    plantilla_encontrada = None
    for categoria_key, categoria in PLANTILLAS_EJEMPLO.items():
        if plantilla_id in categoria:
            plantilla_encontrada = categoria[plantilla_id]
            break

    if not plantilla_encontrada:
        flash("Plantilla no encontrada", "error")
        return redirect(url_for("tableros.plantillas"))

    # Crear tablero desde plantilla
    tablero = storage.crear_tablero(
        nombre=plantilla_encontrada["nombre"],
        descripcion=plantilla_encontrada["descripcion"],
        icono=plantilla_encontrada["icono"],
        creador_id=session.get("user_id")
    )
    
    # Agregar listas de la plantilla
    for lista_nombre in plantilla_encontrada["listas"]:
        tablero.agregar_lista(lista_nombre)
    
    flash(f"¡Tablero creado desde plantilla: {plantilla_encontrada['nombre']}!", "success")
    return redirect(url_for("tableros.ver", tablero_id=tablero.id))


# ===== RUTAS FUNCIONALES (REEMPLAZANDO PLACEHOLDERS) =====

@tableros_bp.route("/agregar_tarjeta", methods=["POST"])
def agregar_tarjeta():
    """Agregar nueva tarjeta a una lista (AJAX)"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # El lista_id viene como query parameter
        lista_id = request.args.get('lista_id')
        
        # Los otros datos pueden venir como JSON o form data
        data = request.get_json()
        if not data:
            # Si no hay JSON, intentar form data
            data = request.form.to_dict()
        
        if not lista_id and data:
            lista_id = data.get('lista_id')

        if not lista_id:
            return jsonify({'error': 'Lista ID es requerido'}), 400
        
        # Buscar la lista en todos los tableros
        lista_encontrada = None
        tablero_encontrado = None
        
        # Optimización: Si viene el tablero_id, buscar directamente
        tablero_id = data.get('tablero_id')
        if tablero_id:
            tablero = storage.get_tablero(tablero_id)
            if tablero:
                lista = tablero.get_lista(lista_id)
                if lista:
                    lista_encontrada = lista
                    tablero_encontrado = tablero
        
        # Si no se encontró (o no venía tablero_id), buscar en todos
        if not lista_encontrada:
            for tablero in storage.get_all_tableros():
                lista = tablero.get_lista(lista_id)
                if lista:
                    lista_encontrada = lista
                    tablero_encontrado = tablero
                    break
        
        if not lista_encontrada:
            # Intentar buscar lista_id en el body si no vino en args
            if not lista_id and data.get('lista_id'):
                lista_id = data.get('lista_id')
                for tablero in storage.get_all_tableros():
                    lista = tablero.get_lista(lista_id)
                    if lista:
                        lista_encontrada = lista
                        tablero_encontrado = tablero
                        break
            
            if not lista_encontrada:
                return jsonify({'error': 'Lista no encontrada'}), 404
        
        # Extraer datos de la persona
        nombre = data.get('nombre', '').strip()
        apellido = data.get('apellido', '').strip()
        direccion = data.get('direccion', '').strip()
        telefono = data.get('telefono', '').strip()
        
        # Si viene titulo en lugar de nombre/apellido (compatibilidad)
        titulo = data.get('titulo', '').strip()
        if titulo and not nombre:
            partes_titulo = titulo.split(' ', 1)
            nombre = partes_titulo[0] if partes_titulo else 'Persona'
            apellido = partes_titulo[1] if len(partes_titulo) > 1 else ''
        
        if not nombre:
            nombre = 'Nueva persona'
        
        # Crear nueva persona usando el método agregar_persona
        nueva_persona = lista_encontrada.agregar_persona(
            nombre=nombre,
            apellido=apellido,
            direccion=direccion,
            telefono=telefono,
            edad=int(data.get('edad')) if data.get('edad') else None,
            estado_civil=data.get('estado_civil', ''),
            numero_hijos=int(data.get('numero_hijos', 0)),
            edades_hijos=data.get('edades_hijos', ''),
            ocupacion=data.get('ocupacion', ''),
            nombre_conyuge=data.get('nombre_conyuge', ''),
            telefono_conyuge=data.get('telefono_conyuge', ''),
            edad_conyuge=int(data.get('edad_conyuge')) if data.get('edad_conyuge') else None,
            trabajo_conyuge=data.get('trabajo_conyuge', ''),
            fecha_matrimonio=data.get('fecha_matrimonio', ''),
            email=data.get('email', ''),
            notas=data.get('notas', ''),
            codigo_postal=data.get('codigo_postal', ''),
            responsable=data.get('responsable', session.get('username', '')),
            # Campos eclesiásticos
            bautizado=data.get('bautizado') == 'on' or data.get('bautizado') == True,
            asiste_grupo=data.get('asiste_grupo') == 'on' or data.get('asiste_grupo') == True,
            ministerio=data.get('ministerio', ''),
            es_lider=data.get('es_lider') == 'on' or data.get('es_lider') == True
        )
        
        # Registrar en historial
        if tablero_encontrado: # Ensure tablero was found
            tablero_encontrado.registrar_accion(
                session.get('username', 'Usuario'),
                'Crear Tarjeta',
                f'Se creó a "{nueva_persona.nombre_completo}" en la lista "{lista_encontrada.nombre}"'
            )
            
            # Registrar Undo
            tablero_encontrado.registrar_undo(
                'crear_tarjeta',
                {
                    'tarjeta_id': nueva_persona.id,
                    'lista_id': lista_encontrada.id
                }
            )
        
        storage.save_to_disk()
        
        return jsonify({
            'success': True,
            'tarjeta': nueva_persona.to_dict(),
            'message': f'Persona "{nueva_persona.nombre_completo}" creada exitosamente'
        }), 201
        
    except Exception as e:
        print(f"Error en agregar_tarjeta: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/mover_tarjeta", methods=["POST"])
def mover_tarjeta():
    """Mover tarjeta entre listas (Drag & Drop)"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        tarjeta_id = data.get('tarjeta_id')
        lista_destino_id = data.get('lista_destino_id')
        
        if not all([tarjeta_id, lista_destino_id]):
            return jsonify({'error': 'Datos incompletos'}), 400
            
        # Buscar tarjeta y lista destino usando SQLAlchemy
        from app.models import Tarjeta, Lista, db
        
        tarjeta = Tarjeta.query.get(tarjeta_id)
        lista_destino = Lista.query.get(lista_destino_id)
        
        if not tarjeta or not lista_destino:
            return jsonify({'error': 'Tarjeta o lista no encontrada'}), 404
            
        # Actualizar lista_id
        tarjeta.lista_id = lista_destino.id
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarjeta movida exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/agregar_lista", methods=["POST"])
def agregar_lista():
    """Agregar nueva lista a un tablero (AJAX)"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        if not data:
            # Si no hay JSON, intentar form data
            data = request.form.to_dict()
        
        titulo = data.get('titulo', '').strip()
        color = data.get('color', '#3b82f6').strip()
        tablero_id = data.get('tablero_id', '').strip()
        
        if not titulo:
            return jsonify({'error': 'El título de la lista es requerido'}), 400
        
        if not tablero_id:
            return jsonify({'error': 'El ID del tablero es requerido'}), 400
        
        # Buscar el tablero
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            return jsonify({'error': 'Tablero no encontrado'}), 404
        
        # Agregar nueva lista usando el método existente
        nueva_lista = tablero.agregar_lista(titulo, color)
        
        # Registrar en historial
        tablero.registrar_accion(
            session.get('username', 'Usuario'),
            'Crear Lista',
            f'Se creó la lista "{titulo}"'
        )
        
        # Registrar Undo
        tablero.registrar_undo(
            'crear_lista',
            {
                'lista_id': nueva_lista.id
            }
        )
        
        # Guardar cambios en disco
        storage.save_to_disk()
        
        return jsonify({
            'success': True,
            'lista': nueva_lista.to_dict(),
            'message': f'Lista "{titulo}" creada exitosamente'
        }), 201
        
    except Exception as e:
        print(f"Error en agregar_lista: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/importar_excel/<lista_id>", methods=["GET", "POST"])
# @login_required
def importar_excel(lista_id):
    """Importar tarjetas desde archivo Excel/CSV"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    try:
        # Buscar la lista en todos los tableros
        lista_encontrada = None
        tablero_encontrado = None
        
        for tablero in storage.get_all_tableros():
            lista = tablero.get_lista(lista_id)
            if lista:
                lista_encontrada = lista
                tablero_encontrado = tablero
                break
        
        if not lista_encontrada:
            flash('Lista no encontrada', 'error')
            return redirect(url_for('tableros.lista'))
        
        if request.method == 'GET':
            # Preparar datos para el template
            lista_data = lista_encontrada.to_dict()
            lista_data['tablero_id'] = tablero_encontrado.id
            lista_data['tablero_nombre'] = tablero_encontrado.nombre
            
            return render_template('tableros/importar.html', lista=lista_data)
        
        elif request.method == 'POST':
            # Procesar archivo subido
            if 'archivo' not in request.files:
                flash('No se seleccionó ningún archivo', 'error')
                return redirect(request.url)
            
            archivo = request.files['archivo']
            if archivo.filename == '':
                flash('No se seleccionó ningún archivo', 'error')
                return redirect(request.url)
            
            # Validar tamaño del archivo
            archivo.seek(0, 2)
            file_size = archivo.tell()
            archivo.seek(0)

            if file_size > 10 * 1024 * 1024:  # 10MB
                flash('❌ El archivo es demasiado grande. Máximo 10MB permitido.', 'error')
                return redirect(request.url)
            
            # Usar el excel_handler para procesar el archivo
            from app.utils.excel_handler import process_import_file
            
            personas_data, errores, file_type, columnas_faltantes = process_import_file(archivo, archivo.filename)
            
            if columnas_faltantes:
                flash(f'⚠️ Advertencia: No se encontraron las siguientes columnas: {", ".join(columnas_faltantes)}. Verifica los encabezados de tu archivo.', 'warning')
            
            # Importar personas a la lista
            tarjetas_importadas = 0
            for persona_data in personas_data:
                try:
                    lista_encontrada.agregar_persona(
                        responsable=session.get('username', 'Usuario'),
                        **persona_data
                    )
                    tarjetas_importadas += 1
                except Exception as e:
                    errores.append(f'Error creando persona: {str(e)}')
            
            # Guardar cambios a disco
            storage.save_to_disk()
            
            # Mostrar resultados
            if tarjetas_importadas > 0:
                flash(f'✅ Se importaron {tarjetas_importadas} personas exitosamente', 'success')
            
            if errores:
                flash(f'⚠️ Se encontraron {len(errores)} errores: {"; ".join(errores[:3])}{"..." if len(errores) > 3 else ""}', 'warning')
            
            if tarjetas_importadas == 0:
                flash('❌ No se importó ninguna persona. Verifica el formato del archivo.', 'error')
                return redirect(request.url)
            
            return redirect(url_for('tableros.ver', tablero_id=tablero_encontrado.id))
                    
    except Exception as e:
        flash(f'Error en la importación: {str(e)}', 'error')
        return redirect(url_for('tableros.lista'))


@tableros_bp.route("/descargar_plantilla")
def descargar_plantilla_excel():
    """Descargar template de Excel REAL para importación con campos del cónyuge"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    try:
        # Intentar generar Excel real
        try:
            import pandas as pd
            
            # Crear datos de ejemplo (igual estructura que tu CSV actual)
            data = {
                'Nombre': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Pedro Sánchez'],
                'Dirección': ['Calle 123 Col. Centro', 'Av. Principal 456', 'Blvd. Sur 789', 'Col. Norte 321', 'Calle Centro 654'],
                'Teléfono': ['555-0123', '555-0124', '555-0125', '555-0126', '555-0127'],
                'Edad': [35, 28, 42, 31, 29],
                'Estado Civil': ['Casado', 'Soltera', 'Casado', 'Casada', 'Soltero'],
                'Num Hijos': [2, 0, 3, 1, 0],
                'Edades Hijos': ['5, 8', '', '10, 12, 15', '7', ''],
                'Nombre Cónyuge': ['María Pérez', '', 'Ana López', 'Roberto Martínez', ''],
                'Edad Cónyuge': [32, '', 38, 33, ''],
                'Teléfono Cónyuge': ['555-0130', '', '555-0131', '555-0132', ''],
                'Trabajo Cónyuge': ['Maestra', '', 'Doctora', 'Ingeniero', ''],
                'Fecha Matrimonio': ['2018-06-15', '', '2005-03-20', '2015-09-10', '']
            }
            
            # Crear DataFrame
            df = pd.DataFrame(data)
            
            # Crear archivo Excel en memoria
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Plantilla', index=False)
                
                # Ajustar ancho de columnas
                workbook = writer.book
                worksheet = writer.sheets['Plantilla']
                
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name='plantilla_personas_con_conyuge.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except ImportError:
            # Fallback a CSV si pandas no está disponible
            flash('⚠️ Generando CSV (pandas no disponible)', 'warning')
            
            # Tu contenido CSV original exacto
            contenido_csv = """Nombre,Dirección,Teléfono,Edad,Estado Civil,Num Hijos,Edades Hijos,Nombre Cónyuge,Edad Cónyuge,Teléfono Cónyuge,Trabajo Cónyuge,Fecha Matrimonio
Juan Pérez,Calle 123 Col. Centro,555-0123,35,Casado,2,"5,8",María Pérez,32,555-0130,Maestra,2018-06-15
María García,Av. Principal 456,555-0124,28,Soltera,0,,,,,
Carlos López,Blvd. Sur 789,555-0125,42,Casado,3,"10,12,15",Ana López,38,555-0131,Doctora,2005-03-20
Ana Martínez,Col. Norte 321,555-0126,31,Casada,1,"7",Roberto Martínez,33,555-0132,Ingeniero,2015-09-10
Pedro Sánchez,Calle Centro 654,555-0127,29,Soltero,0,,,,,"""
            
            output = BytesIO()
            output.write(contenido_csv.encode('utf-8'))
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name='plantilla_personas_con_conyuge.csv',
                mimetype='text/csv'
            )
        
    except Exception as e:
        flash(f'Error generando plantilla: {str(e)}', 'error')
        return redirect(url_for('tableros.lista'))


# ===== RUTAS ADICIONALES =====

@tableros_bp.route("/eliminar_lista/<lista_id>", methods=["DELETE"])
def eliminar_lista(lista_id):
    """Eliminar una lista del tablero"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Buscar la lista en todos los tableros
        for tablero in storage.get_all_tableros():
            lista = tablero.get_lista(lista_id)
            if lista:
                # Verificar que la lista no tenga tarjetas
                if len(lista.tarjetas) > 0:
                    return jsonify({
                        'error': 'No se puede eliminar una lista que contiene tarjetas'
                    }), 400
                
                # Eliminar lista usando el método existente
                nombre_lista = lista.nombre
                
                # Guardar datos para Undo
                posicion = -1
                try:
                    posicion = tablero.orden_listas.index(lista_id)
                except ValueError:
                    pass
                
                lista_data = lista.to_dict()
                
                tablero.eliminar_lista(lista_id)
                
                # Registrar en historial
                tablero.registrar_accion(
                    session.get('username', 'Usuario'),
                    'Eliminar Lista',
                    f'Se eliminó la lista "{nombre_lista}"'
                )
                
                # Registrar Undo
                tablero.registrar_undo(
                    'eliminar_lista',
                    {
                        'lista_data': lista_data,
                        'posicion': posicion
                    }
                )
                
                storage.save_to_disk()
                
                return jsonify({
                    'success': True,
                    'message': 'Lista eliminada exitosamente'
                }), 200
        
        return jsonify({'error': 'Lista no encontrada'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/eliminar_tarjeta/<tarjeta_id>", methods=["DELETE"])
def eliminar_tarjeta(tarjeta_id):
    """Eliminar una tarjeta de una lista"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Buscar la tarjeta en todos los tableros y listas
        for tablero in storage.get_all_tableros():
            for lista in tablero.listas:
                tarjeta = lista.get_tarjeta(tarjeta_id)
                if tarjeta:
                    # Guardar datos para Undo
                    posicion = -1
                    try:
                        posicion = lista.tarjetas.index(tarjeta)
                    except ValueError:
                        pass
                    
                    tarjeta_data = tarjeta.to_dict()
                    
                    # Eliminar tarjeta usando el método existente
                    nombre_tarjeta = tarjeta.nombre_completo
                    lista.eliminar_tarjeta(tarjeta_id)
                    
                    # Registrar Undo
                    tablero.registrar_undo(
                        'eliminar_tarjeta',
                        {
                            'tarjeta_data': tarjeta_data,
                            'lista_id': lista.id,
                            'posicion': posicion
                        }
                    )
                    
                    # Registrar en historial
                    tablero.registrar_accion(
                        session.get('username', 'Usuario'),
                        'Eliminar Tarjeta',
                        f'Se eliminó a "{nombre_tarjeta}" de la lista "{lista.nombre}"'
                    )
                    storage.save_to_disk()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Tarjeta eliminada exitosamente'
                    }), 200
        
        return jsonify({'error': 'Tarjeta no encontrada'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route('/<tablero_id>/lista/editar', methods=['POST'])
# Assuming login_required is defined elsewhere, if not, replace with session check
# @login_required 
def editar_lista_api(tablero_id):
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    tablero = storage.get_tablero(tablero_id)
    if not tablero:
        return jsonify({'success': False, 'error': 'Tablero no encontrado'}), 404
        
    data = request.json
    lista_id = data.get('lista_id')
    nombre = data.get('nombre')
    color = data.get('color')
    
    if not lista_id or not nombre:
        return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400
        
    # Find the list within the tablero
    lista_encontrada = tablero.get_lista(lista_id)
    if lista_encontrada:
        lista_encontrada.nombre = nombre
        lista_encontrada.color = color
        storage.save_to_disk()
        return jsonify({'success': True, 'message': 'Lista actualizada exitosamente'})
    
    return jsonify({'success': False, 'error': 'Lista no encontrada'}), 404

@tableros_bp.route('/<tablero_id>/lista/eliminar', methods=['POST'])
# Assuming login_required is defined elsewhere, if not, replace with session check
# @login_required
def eliminar_lista_api(tablero_id):
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    tablero = storage.get_tablero(tablero_id)
    if not tablero:
        return jsonify({'success': False, 'error': 'Tablero no encontrado'}), 404
        
    data = request.json
    lista_id = data.get('lista_id')
    
    if not lista_id:
        return jsonify({'success': False, 'error': 'Falta ID de lista'}), 400
        
    # Eliminar la lista directamente (el frontend pedirá confirmación)
    if tablero.eliminar_lista(lista_id):
        storage.save_to_disk()
        return jsonify({'success': True, 'message': 'Lista eliminada exitosamente'})
    
    return jsonify({'success': False, 'error': 'Lista no encontrada'}), 404

@tableros_bp.route("/eliminar/<tablero_id>", methods=["POST"])
def eliminar(tablero_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    tablero = storage.get_tablero(tablero_id)
    if not tablero:
        flash("Tablero no encontrado", "error")
        return redirect(url_for("tableros.lista"))
    
    # Eliminar tablero
    storage.eliminar_tablero(tablero_id)
    flash(f"Tablero '{tablero.nombre}' eliminado exitosamente", "success")
    return redirect(url_for("tableros.lista"))


@tableros_bp.route("/editar/<tablero_id>", methods=["GET", "POST"])
def editar(tablero_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    tablero = storage.get_tablero(tablero_id)
    if not tablero:
        flash("Tablero no encontrado", "error")
        return redirect(url_for("tableros.lista"))
    
    if request.method == 'POST':
        # Procesar edición del tablero
        nuevo_nombre = request.form.get('nombre', '').strip()
        nueva_descripcion = request.form.get('descripcion', '').strip()
        nuevo_icono = request.form.get('icono', tablero.icono)
        
        if nuevo_nombre:
            tablero.nombre = nuevo_nombre
            tablero.descripcion = nueva_descripcion
            tablero.icono = nuevo_icono
            flash('Tablero actualizado exitosamente', 'success')
        
        return redirect(url_for('tableros.ver', tablero_id=tablero.id))
    
    return render_template("tableros/editar.html", tablero=tablero.to_dict())


@tableros_bp.route("/editar_lista/<lista_id>", methods=["GET", "POST"])
def editar_lista(lista_id):
    """Editar una lista del tablero"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    # Buscar la lista en todos los tableros
    lista_encontrada = None
    tablero_encontrado = None
    
    for tablero in storage.get_all_tableros():
        lista = tablero.get_lista(lista_id)
        if lista:
            lista_encontrada = lista
            tablero_encontrado = tablero
            break
    
    if not lista_encontrada:
        flash('Lista no encontrada', 'error')
        return redirect(url_for('tableros.lista'))
    
    if request.method == 'GET':
        # Mostrar formulario de edición
        return render_template('tableros/editar_lista.html', 
                             lista=lista_encontrada.to_dict(),
                             tablero=tablero_encontrado.to_dict())
    
    elif request.method == 'POST':
        # Procesar edición
        nuevo_nombre = request.form.get('nombre', '').strip()
        nuevo_color = request.form.get('color', lista_encontrada.color)
        
        if not nuevo_nombre:
            flash('El nombre de la lista es requerido', 'error')
            return redirect(request.url)
        
        # Actualizar lista
        lista_encontrada.nombre = nuevo_nombre
        lista_encontrada.color = nuevo_color
        
        flash(f'Lista "{nuevo_nombre}" actualizada exitosamente', 'success')
        return redirect(url_for('tableros.ver', tablero_id=tablero_encontrado.id))


@tableros_bp.route("/editar_tarjeta/<lista_id>/<tarjeta_id>", methods=["GET", "POST"])
def editar_tarjeta(lista_id, tarjeta_id):
    """Editar una tarjeta"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    # Buscar la tarjeta en todos los tableros
    tarjeta_encontrada = None
    lista_encontrada = None
    tablero_encontrado = None
    
    for tablero in storage.get_all_tableros():
        for lista in tablero.listas:
            tarjeta = lista.get_tarjeta(tarjeta_id)
            if tarjeta:
                tarjeta_encontrada = tarjeta
                lista_encontrada = lista
                tablero_encontrado = tablero
                break
        if tarjeta_encontrada:
            break
    
    if not tarjeta_encontrada:
        flash('Tarjeta no encontrada', 'error')
        return redirect(url_for('tableros.lista'))
    
    if request.method == 'GET':
        # Mostrar formulario de edición
        return render_template('tableros/editar_tarjeta.html', 
                             tarjeta=tarjeta_encontrada.to_dict(),
                             lista=lista_encontrada.to_dict(),
                             tablero=tablero_encontrado.to_dict())
    
    elif request.method == 'POST':
        # Procesar edición completa con todos los campos
        try:
            # Información Personal
            tarjeta_encontrada.nombre = request.form.get('nombre', '').strip()
            tarjeta_encontrada.apellido = request.form.get('apellido', '').strip()
            tarjeta_encontrada.edad = int(request.form.get('edad')) if request.form.get('edad') else None
            tarjeta_encontrada.estado_civil = request.form.get('estado_civil', '')
            tarjeta_encontrada.ocupacion = request.form.get('ocupacion', '')
            
            # Contacto y Ubicación
            tarjeta_encontrada.telefono = request.form.get('telefono', '').strip()
            tarjeta_encontrada.email = request.form.get('email', '').strip()
            tarjeta_encontrada.direccion = request.form.get('direccion', '').strip()
            
            # Información Familiar
            tarjeta_encontrada.numero_hijos = int(request.form.get('numero_hijos', 0))
            tarjeta_encontrada.edades_hijos = request.form.get('edades_hijos', '')
            tarjeta_encontrada.nombre_conyuge = request.form.get('nombre_conyuge', '')
            tarjeta_encontrada.telefono_conyuge = request.form.get('telefono_conyuge', '')
            
            # Información Adicional
            tarjeta_encontrada.responsable = request.form.get('responsable', '')
            tarjeta_encontrada.estado = request.form.get('estado', 'activa')
            tarjeta_encontrada.notas = request.form.get('notas', '').strip()
            
            # Campos Eclesiásticos
            tarjeta_encontrada.bautizado = 'bautizado' in request.form
            tarjeta_encontrada.asiste_grupo = 'asiste_grupo' in request.form
            tarjeta_encontrada.es_lider = 'es_lider' in request.form
            tarjeta_encontrada.ministerio = request.form.get('ministerio', '')
            
            # Actualizar campos calculados
            tarjeta_encontrada.titulo = tarjeta_encontrada.nombre_completo
            tarjeta_encontrada.descripcion = tarjeta_encontrada.direccion
            tarjeta_encontrada.fecha_actualizacion = datetime.now()
            
            storage.save_to_disk()
            
            flash(f'Tarjeta "{tarjeta_encontrada.nombre_completo}" actualizada exitosamente', 'success')
            return redirect(url_for('tableros.ver', tablero_id=tablero_encontrado.id))
            
        except Exception as e:
            flash(f'Error actualizando tarjeta: {str(e)}', 'error')
            return redirect(request.url)

# ===== RUTAS DE CLUSTERING GEOGRÁFICO =====

@tableros_bp.route("/api/geocoding/get_uncoded", methods=["POST"])
def get_uncoded_people():
    """Obtener personas que necesitan geocodificación"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    try:
        data = request.json
        tablero_id = data.get('tablero_id')
        
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            return jsonify({'error': 'Tablero no encontrado'}), 404
            
        personas_to_code = []
        personas = tablero.get_todas_las_personas()
        
        print(f"DEBUG: Checking {len(personas)} people for geocoding in tablero {tablero.nombre}")
        
        for p_dict in personas:
            # Buscar la tarjeta real
            tarjeta = None
            for lista in tablero.listas:
                t = lista.get_tarjeta(p_dict['id'])
                if t:
                    tarjeta = t
                    break
            
            if tarjeta:
                # Debug info for each person with address
                if tarjeta.direccion:
                    print(f"DEBUG: Person {tarjeta.nombre_completo} has address: '{tarjeta.direccion}'. Lat: {tarjeta.latitud}, Lng: {tarjeta.longitud}")
                
                # Check if needs geocoding (address exists, and coords are missing or 0)
                has_address = bool(tarjeta.direccion and tarjeta.direccion.strip())
                needs_coords = (tarjeta.latitud == 0 and tarjeta.longitud == 0) or tarjeta.latitud is None
                
                if has_address and needs_coords:
                    print(f"DEBUG: Adding {tarjeta.nombre_completo} to geocode list")
                    personas_to_code.append({
                        'id': tarjeta.id,
                        'nombre': tarjeta.nombre_completo,
                        'direccion': tarjeta.direccion
                    })
        
        return jsonify({
            'success': True, 
            'personas': personas_to_code,
            'count': len(personas_to_code)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tableros_bp.route("/api/personas/update_coords", methods=["POST"])
def update_person_coords():
    """Actualizar coordenadas de una persona específica"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    try:
        data = request.json
        tablero_id = data.get('tablero_id')
        persona_id = data.get('persona_id')
        lat = data.get('lat')
        lng = data.get('lng')
        
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            return jsonify({'error': 'Tablero no encontrado'}), 404
            
        # Buscar persona
        tarjeta_encontrada = None
        for lista in tablero.listas:
            t = lista.get_tarjeta(persona_id)
            if t:
                tarjeta_encontrada = t
                break
        
        if tarjeta_encontrada:
            tarjeta_encontrada.latitud = float(lat)
            tarjeta_encontrada.longitud = float(lng)
            storage.save_to_disk()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Persona no encontrada'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tableros_bp.route("/api/clustering/preview", methods=["POST"])
def preview_clustering():
    """Generar vista previa de clusters"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    try:
        data = request.json
        tablero_id = data.get('tablero_id')
        max_distance = float(data.get('max_distance', 2.0)) # Millas
        min_size = int(data.get('min_size', 5))
        max_size = int(data.get('max_size', 12))
        
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            return jsonify({'error': 'Tablero no encontrado'}), 404
            
        # Obtener personas con coordenadas
        personas = [p for p in tablero.get_todas_las_personas() if p.get('latitud') and p.get('longitud')]
        
        if not personas:
            return jsonify({'success': False, 'message': 'No hay personas con coordenadas para agrupar'})
            
        from app.utils.clustering import ClusteringManager
        # No necesitamos API key para el algoritmo, solo para geocoding
        cluster_manager = ClusteringManager("") 
        
        clusters = cluster_manager.create_clusters(personas, max_distance, min_size, max_size)
        
        return jsonify({
            'success': True,
            'clusters': clusters,
            'total_clustered': sum(c['count'] for c in clusters)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tableros_bp.route("/api/clustering/apply", methods=["POST"])
def apply_clustering():
    """Crear listas basadas en los clusters"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    try:
        data = request.json
        tablero_id = data.get('tablero_id')
        clusters = data.get('clusters', [])
        
        print(f"DEBUG: apply_clustering called for tablero {tablero_id} with {len(clusters)} clusters")
        print(f"DEBUG: Clusters data: {json.dumps(clusters, indent=2)}")
        
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            print(f"DEBUG: Tablero {tablero_id} not found")
            return jsonify({'error': 'Tablero no encontrado'}), 404
            
        if not clusters:
             print("DEBUG: No clusters provided")
             return jsonify({'success': False, 'message': 'No hay grupos para crear.'})
            
        created_lists = 0
        moved_people = 0
        
        # Paleta de colores distintivos para los grupos
        colores_grupos = [
            "#EF4444", # Rojo
            "#F59E0B", # Ambar
            "#10B981", # Esmeralda
            "#3B82F6", # Azul
            "#6366F1", # Indigo
            "#8B5CF6", # Violeta
            "#EC4899", # Rosa
            "#F97316", # Naranja
            "#84CC16", # Lima
            "#06B6D4", # Cyan
            "#14B8A6", # Teal
            "#64748B", # Slate
            "#A855F7", # Purple
            "#D946EF", # Fuchsia
            "#F43F5E", # Rose
            "#EAB308", # Yellow
            "#22C55E", # Green
            "#0EA5E9", # Sky
            "#4F46E5", # Indigo
            "#C026D3"  # Fuchsia Dark
        ]
        
        for i, cluster in enumerate(clusters):
            if cluster.get('is_outlier'):
                continue
                
            # Crear nueva lista con color rotativo
            nombre_lista = f"Grupo Geográfico {i+1}"
            color_asignado = colores_grupos[i % len(colores_grupos)]
            nueva_lista = tablero.agregar_lista(nombre_lista, color=color_asignado)
            created_lists += 1
            
            # Mover personas a la nueva lista
            for member in cluster['members']:
                # Buscar persona en su lista actual
                tarjeta_mover = None
                lista_origen = None
                
                for lista in tablero.listas:
                    t = lista.get_tarjeta(member['id'])
                    if t:
                        tarjeta_mover = t
                        lista_origen = lista
                        break
                
                if tarjeta_mover and lista_origen:
                    # Mover actualizando la foreign key
                    tarjeta_mover.lista_id = nueva_lista.id
                    moved_people += 1
            
            # Guardar cambios por cada cluster
            storage.save_to_disk()
        
        storage.save_to_disk()
        
        return jsonify({
            'success': True,
            'message': f'Se crearon {created_lists} listas con {moved_people} personas.',
            'created_lists': created_lists
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

            



@tableros_bp.route("/descargar/<formato>")
def descargar_datos(formato):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    flash(f"Descarga {formato} (funcionalidad próximamente)", "info")
    return redirect(url_for("tableros.lista"))


@tableros_bp.route("/exportar_datos/<tablero_id>/<formato>")
def exportar_datos(tablero_id, formato):
    """Exportar datos del tablero en diferentes formatos"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    try:
        # Buscar el tablero
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            flash('Tablero no encontrado', 'error')
            return redirect(url_for('tableros.lista'))
        
        # Recopilar todos los datos
        datos_exportacion = []
        for lista in tablero.listas.values():
            for tarjeta in lista.tarjetas:
                # Convertir tarjeta a diccionario con información completa
                # IMPORTANTE: Los nombres de columnas deben coincidir con excel_handler.py
                persona_data = {
                    'Lista': lista.nombre,
                    'Nombre': getattr(tarjeta, 'nombre_completo', tarjeta.titulo or ''),
                    'Dirección': getattr(tarjeta, 'direccion', tarjeta.descripcion or ''),
                    'Teléfono': getattr(tarjeta, 'telefono', ''),
                    'Edad': getattr(tarjeta, 'edad', ''),
                    'Estado Civil': getattr(tarjeta, 'estado_civil', ''),
                    'Num Hijos': getattr(tarjeta, 'numero_hijos', ''),
                    'Edades Hijos': getattr(tarjeta, 'edades_hijos', ''),
                    'Nombre Cónyuge': getattr(tarjeta, 'nombre_conyuge', ''),
                    'Edad Cónyuge': getattr(tarjeta, 'edad_conyuge', ''),
                    'Teléfono Cónyuge': getattr(tarjeta, 'telefono_conyuge', ''),
                    'Trabajo Cónyuge': getattr(tarjeta, 'trabajo_conyuge', ''),
                    'Fecha Matrimonio': getattr(tarjeta, 'fecha_matrimonio', ''),
                    'Ocupación': getattr(tarjeta, 'ocupacion', ''),
                    'Email': getattr(tarjeta, 'email', ''),
                    'Responsable': getattr(tarjeta, 'responsable', ''),
                    'Notas': getattr(tarjeta, 'notas', ''),
                }
                datos_exportacion.append(persona_data)
        
        if not datos_exportacion:
            flash('No hay datos para exportar en este tablero', 'warning')
            return redirect(url_for('tableros.ver', tablero_id=tablero_id))
        
        # Generar archivo según formato
        if formato == 'csv':
            return _generar_csv(datos_exportacion, tablero.nombre)
        elif formato == 'excel':
            return _generar_excel(datos_exportacion, tablero.nombre)
        elif formato == 'json':
            return _generar_json(datos_exportacion, tablero.nombre)
        else:
            flash('Formato no soportado', 'error')
            return redirect(url_for('tableros.ver', tablero_id=tablero_id))
            
    except Exception as e:
        flash(f'Error al exportar datos: {str(e)}', 'error')
        return redirect(url_for('tableros.ver', tablero_id=tablero_id))


def _generar_csv(datos, nombre_tablero):
    """Generar archivo CSV"""
    import csv
    from io import StringIO
    
    output = StringIO()
    if datos:
        fieldnames = datos[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(datos)
    
    # Convertir a bytes
    csv_bytes = BytesIO()
    csv_bytes.write(output.getvalue().encode('utf-8'))
    csv_bytes.seek(0)
    
    filename = f"{nombre_tablero}_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        csv_bytes,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv'
    )


def _generar_excel(datos, nombre_tablero):
    """Generar archivo Excel"""
    try:
        import pandas as pd
        
        # Crear DataFrame
        df = pd.DataFrame(datos)
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Datos', index=False)
            
            # Ajustar ancho de columnas
            worksheet = writer.sheets['Datos']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        filename = f"{nombre_tablero}_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except ImportError:
        # Si pandas no está disponible, generar CSV con extensión xlsx
        return _generar_csv(datos, nombre_tablero)


def _generar_json(datos, nombre_tablero):
    """Generar archivo JSON"""
    import json
    
    output_data = {
        'tablero': nombre_tablero,
        'fecha_exportacion': datetime.now().isoformat(),
        'total_personas': len(datos),
        'datos': datos
    }
    
    json_bytes = BytesIO()
    json_bytes.write(json.dumps(output_data, indent=2, ensure_ascii=False).encode('utf-8'))
    json_bytes.seek(0)
    
    filename = f"{nombre_tablero}_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return send_file(
        json_bytes,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )


@tableros_bp.route("/mover_lista", methods=["POST"])
def mover_lista():
    """Reordenar listas en el tablero (Drag & Drop)"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        lista_id = data.get('lista_id')
        nueva_posicion = data.get('nueva_posicion', 0)
        
        if not lista_id:
            return jsonify({'error': 'Lista ID requerido'}), 400
        
        # Buscar la lista y el tablero
        lista_encontrada = None
        tablero_encontrado = None
        
        for tablero in storage.get_all_tableros():
            lista = tablero.get_lista(lista_id)
            if lista:
                lista_encontrada = lista
                tablero_encontrado = tablero
                break
        
        if not lista_encontrada or not tablero_encontrado:
            return jsonify({'error': 'Lista no encontrada'}), 404
        
        # Reordenar lista en el tablero
        if lista_id in tablero_encontrado.orden_listas:
            tablero_encontrado.orden_listas.remove(lista_id)
            # Asegurar que el índice sea válido
            if nueva_posicion < 0:
                nueva_posicion = 0
            elif nueva_posicion > len(tablero_encontrado.orden_listas):
                nueva_posicion = len(tablero_encontrado.orden_listas)
                
            tablero_encontrado.orden_listas.insert(nueva_posicion, lista_id)
            storage.save_to_disk()
            
            return jsonify({
                'success': True,
                'message': 'Lista reordenada exitosamente'
            }), 200
        else:
             return jsonify({'error': 'ID de lista no encontrado en el orden del tablero'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/api/deshacer", methods=["POST"])
def deshacer_accion():
    """Deshacer la última acción"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    try:
        data = request.json
        tablero_id = data.get('tablero_id')
        
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            return jsonify({'error': 'Tablero no encontrado'}), 404
            
        if not tablero.undo_stack:
            return jsonify({'error': 'No hay acciones para deshacer'}), 400
            
        # Obtener última acción
        undo_action = tablero.undo_stack.pop()
        action_type = undo_action['type']
        undo_data = undo_action['data']
        
        print(f"Deshaciendo acción: {action_type}")
        
        if action_type == 'mover_tarjeta':
            tarjeta_id = undo_data['tarjeta_id']
            lista_origen_id = undo_data['lista_origen_id']
            lista_destino_id = undo_data['lista_destino_id']
            nueva_posicion = undo_data['nueva_posicion']
            
            # Buscar tarjeta y listas
            tarjeta = None
            lista_origen = tablero.get_lista(lista_origen_id)
            lista_destino = tablero.get_lista(lista_destino_id)
            
            # Buscar tarjeta en cualquier lista (debería estar en lista_origen actual, que es la destino original)
            for l in tablero.listas:
                t = l.get_tarjeta(tarjeta_id)
                if t:
                    tarjeta = t
                    # Remover de donde esté
                    l.tarjetas.remove(t)
                    break
            
            if tarjeta and lista_destino:
                lista_destino.tarjetas.insert(nueva_posicion, tarjeta)
                
        elif action_type == 'eliminar_tarjeta':
            tarjeta_data = undo_data['tarjeta_data']
            lista_id = undo_data['lista_id']
            posicion = undo_data['posicion']
            
            lista = tablero.get_lista(lista_id)
            if lista:
                # Recrear tarjeta
                tarjeta = storage._deserialize_tarjeta(tarjeta_data)
                if posicion >= 0 and posicion <= len(lista.tarjetas):
                    lista.tarjetas.insert(posicion, tarjeta)
                else:
                    lista.tarjetas.append(tarjeta)
                    
        elif action_type == 'crear_tarjeta':
            tarjeta_id = undo_data['tarjeta_id']
            lista_id = undo_data['lista_id']
            
            lista = tablero.get_lista(lista_id)
            if lista:
                lista.eliminar_tarjeta(tarjeta_id)
                
        elif action_type == 'eliminar_lista':
            lista_data = undo_data['lista_data']
            posicion = undo_data['posicion']
            
            # Recrear lista
            lista = storage._deserialize_lista(lista_data)
            tablero.listas[lista.id] = lista
            
            if posicion >= 0 and posicion <= len(tablero.orden_listas):
                tablero.orden_listas.insert(posicion, lista.id)
            else:
                tablero.orden_listas.append(lista.id)
                
        elif action_type == 'crear_lista':
            lista_id = undo_data['lista_id']
            tablero.eliminar_lista(lista_id)
            
        elif action_type == 'bulk_move':
            moves = undo_data['moves']
            # Revertir cada movimiento
            for move in moves:
                tarjeta_id = move['tarjeta_id']
                lista_origen_id = move['lista_origen_id']
                # lista_destino_id = move['lista_destino_id'] # No needed for undo
                
                # Mover tarjeta de vuelta a origen
                tarjeta = None
                # Buscar tarjeta
                for l in tablero.listas:
                    t = l.get_tarjeta(tarjeta_id)
                    if t:
                        tarjeta = t
                        l.tarjetas.remove(t)
                        break
                
                if tarjeta:
                    lista_origen = tablero.get_lista(lista_origen_id)
                    if lista_origen:
                        index = move.get('index', -1)
                        if index >= 0 and index <= len(lista_origen.tarjetas):
                            lista_origen.tarjetas.insert(index, tarjeta)
                        else:
                            lista_origen.tarjetas.append(tarjeta)

        elif action_type == 'bulk_delete':
            deleted_cards = undo_data['deleted_cards']
            # Restaurar cada tarjeta
            for item in deleted_cards:
                tarjeta_data = item['tarjeta_data']
                lista_id = item['lista_id']
                
                lista = tablero.get_lista(lista_id)
                if lista:
                    tarjeta = storage._deserialize_tarjeta(tarjeta_data)
                    index = item.get('index', -1)
                    if index >= 0 and index <= len(lista.tarjetas):
                        lista.tarjetas.insert(index, tarjeta)
                    else:
                        lista.tarjetas.append(tarjeta)

        # Registrar en historial que se deshizo
        tablero.registrar_accion(
            session.get('username', 'Usuario'),
            'Deshacer',
            f'Se deshizo la acción: {action_type}'
        )
        
        storage.save_to_disk()
        
        return jsonify({'success': True, 'message': 'Acción deshecha exitosamente'})
        
    except Exception as e:
        print(f"Error en deshacer: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@tableros_bp.route("/api/bulk/move", methods=["POST"])
def bulk_move():
    """Mover múltiples tarjetas"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    try:
        data = request.json
        tablero_id = data.get('tablero_id')
        tarjeta_ids = data.get('tarjeta_ids', [])
        lista_destino_id = data.get('lista_destino_id')
        
        if not tarjeta_ids or not lista_destino_id:
            return jsonify({'error': 'Datos incompletos'}), 400
            
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            return jsonify({'error': 'Tablero no encontrado'}), 404
            
        lista_destino = tablero.get_lista(lista_destino_id)
        if not lista_destino:
            return jsonify({'error': 'Lista destino no encontrada'}), 404
            
        moves_recorded = []
        count = 0
        
        for tarjeta_id in tarjeta_ids:
            # Buscar tarjeta y su lista actual
            tarjeta = None
            lista_origen = None
            
            for l in tablero.listas:
                t = l.get_tarjeta(tarjeta_id)
                if t:
                    tarjeta = t
                    lista_origen = l
                    break
            
            if tarjeta and lista_origen:
                # Si ya está en la lista destino, saltar
                if lista_origen.id == lista_destino.id:
                    continue
                    
                # Guardar índice original
                try:
                    index = lista_origen.tarjetas.index(tarjeta)
                except ValueError:
                    index = -1

                # Mover actualizando foreign key
                tarjeta.lista_id = lista_destino.id
                
                moves_recorded.append({
                    'tarjeta_id': tarjeta.id,
                    'lista_origen_id': lista_origen.id,
                    'lista_destino_id': lista_destino.id,
                    'index': index
                })
                count += 1
        
        if count > 0:
            # Registrar historial
            tablero.registrar_accion(
                session.get('username', 'Usuario'),
                'Mover Tarjetas',
                f'Se movieron {count} tarjetas a "{lista_destino.nombre}"'
            )
            
            # Registrar Undo
            tablero.registrar_undo(
                'bulk_move',
                {
                    'moves': moves_recorded
                }
            )
            
            storage.save_to_disk()
            
        return jsonify({'success': True, 'count': count})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tableros_bp.route("/api/bulk/delete", methods=["POST"])
def bulk_delete():
    """Eliminar múltiples tarjetas"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
        
    try:
        data = request.json
        tablero_id = data.get('tablero_id')
        tarjeta_ids = data.get('tarjeta_ids', [])
        
        if not tarjeta_ids:
            return jsonify({'error': 'Datos incompletos'}), 400
            
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            return jsonify({'error': 'Tablero no encontrado'}), 404
            
        deleted_cards = []
        count = 0
        
        for tarjeta_id in tarjeta_ids:
            # Buscar tarjeta
            for l in tablero.listas:
                t = l.get_tarjeta(tarjeta_id)
                if t:
                    # Guardar datos para undo
                    try:
                        index = l.tarjetas.index(t)
                    except ValueError:
                        index = -1
                        
                    deleted_cards.append({
                        'tarjeta_data': t.to_dict(),
                        'lista_id': l.id,
                        'index': index
                    })
                    # Eliminar
                    l.tarjetas.remove(t)
                    count += 1
                    break
        
        if count > 0:
            # Registrar historial
            tablero.registrar_accion(
                session.get('username', 'Usuario'),
                'Eliminar Tarjetas',
                f'Se eliminaron {count} tarjetas'
            )
            
            # Registrar Undo
            tablero.registrar_undo(
                'bulk_delete',
                {
                    'deleted_cards': deleted_cards
                }
            )
            
            storage.save_to_disk()
            
        return jsonify({'success': True, 'count': count})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    return jsonify(tablero.to_dict())