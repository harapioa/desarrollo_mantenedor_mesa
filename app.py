# app.py

import os
import re
import datetime
import oracledb
# Import config con manejo de error
try:
    import config
except ImportError:
    print("Error: No se encontró el archivo config.py.")
    print("Asegúrate de crearlo con tus credenciales de base de datos.")
    exit()

from flask import Flask, render_template, request, redirect, jsonify, flash, url_for, send_file
from database_queries import (
    get_todas_las_uces, get_servicios_por_uce_id, buscar_auditorias,
    get_detalle_at_info, get_actividades_cumplimiento, actualizar_estado_procedimiento,
    actualizar_estado_at_completa, buscar_usuarios_siad, desactivar_usuario_siad,
    get_usuario_siad_by_id, guardar_cambios_usuario, get_actividades_simplificada,
    get_actos_siad, get_registros_siad, actualizar_estado_actuaciones_siad,
    get_actos_termino_siad, actualizar_estado_actos_termino, get_actividades_ara,
    actualizar_estado_procedimiento_ara, actualizar_estado_at_completa_ara,
    get_actividades_inve, actualizar_estado_procedimiento_inve, actualizar_estado_at_completa_inve,
    generar_reporte_excel
)

# --- 2. Apuntar a la carpeta del Instant Client ---
# Obtenemos la ruta absoluta a la carpeta del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))
# Construimos la ruta a nuestra carpeta 'instantclient_23_8'
client_lib_dir = os.path.join(basedir, 'oracle_client', 'instantclient_23_8')

# Le decimos a la librería oracledb dónde buscar sus archivos
try:
    oracledb.init_oracle_client(lib_dir=client_lib_dir)
except Exception as e:
    print(f"Error al inicializar Oracle Instant Client en: {client_lib_dir}")
    print(f"Asegúrate de haber descomprimido el Instant Client en esa carpeta.")
    print(f"Error detallado: {e}")
    exit()

# --- 3. Crear la aplicación Flask ---
app = Flask(__name__)
app.secret_key = "mi-clave-secreta-para-flash" # Puedes poner cualquier texto

# --- 4. Función para probar la conexión ---
def probar_conexion_oracle():
    print("Intentando conectar a Oracle...")
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            print("Conexión a Oracle OK.")
    except oracledb.DatabaseError as e:
        print("Error al conectar a la base de datos Oracle.")
        print(f"Detalle del error: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- 5. Rutas de la aplicación ---
@app.route('/mantenedor_mesa/index.html')
def pagina_principal():
    return render_template('mesa_de_servicio.html')

# --- Redirigir desde la raíz a la nueva página principal ---
@app.route('/')
def redirect_to_main():
    # 'pagina_principal' sigue siendo el nombre de la FUNCIÓN
    return redirect(url_for('pagina_principal'))

@app.route('/buscador-ats/<string:tipo_origen>', methods=['GET', 'POST'])
def pagina_buscador_ats(tipo_origen):

    lista_de_resultados = None
    filtros_aplicados = {} 

    if request.method == 'POST':
            # 1. Obtener datos (añadir num_referencia)
            periodo = request.form.get('periodo')
            nro_at = request.form.get('numero_at')
            uce_id = request.form.get('uce')
            servicio_id = request.form.get('servicio')
            nro_programa = request.form.get('n_programa')
            num_referencia = request.form.get('num_referencia') # <-- NUEVO CAMPO

            # (Limpieza de valores 'Seleccione..')
            if uce_id == "Seleccione..": uce_id = ""
            if servicio_id == "Seleccione..": servicio_id = ""

            # Añadir num_referencia a filtros_aplicados
            filtros_aplicados = {
                'periodo': periodo, 'nro_at': nro_at, 'uce_id': uce_id,
                'servicio_id': servicio_id, 'n_programa': nro_programa,
                'num_referencia': num_referencia # <-- NUEVO CAMPO
            }

            # 2. Validación (Ahora incluye num_referencia)
            if not periodo:
                flash("El campo 'Período de Planificación' es obligatorio.", 'error')
                lista_de_resultados = None
            # Chequeamos si TODOS los otros campos opcionales están vacíos
            elif not nro_at and not uce_id and not servicio_id and not nro_programa and not num_referencia: # <-- NUEVO CAMPO
                flash("Además del Período, debe ingresar al menos otro criterio de búsqueda.", 'error')
                lista_de_resultados = None
            else:
                # 3. Llamar a la Capa 3 (pasar num_referencia)
                print(f"Capa 2: Iniciando búsqueda para '{tipo_origen}' con filtros: {filtros_aplicados}")
                lista_de_resultados = buscar_auditorias(
                    periodo=periodo, nro_at=nro_at, uce_id=uce_id,
                    servicio_id=servicio_id, nro_programa=nro_programa,
                    tipo_origen=tipo_origen,
                    num_referencia=num_referencia # <-- NUEVO PARÁMETRO
                )
    # Contamos los resultados
    num_resultados_encontrados = len(lista_de_resultados) if lista_de_resultados is not None else 0

    # 4. Renderizar la plantilla

    # ¡MODIFICADO!
    # Usamos el nuevo archivo 'buscador_generico.html'
    # y le pasamos el 'tipo_origen' para que el HTML sepa qué mostrar
    return render_template(
    'buscador_generico.html', 
    resultados=lista_de_resultados,
    filtros=filtros_aplicados,
    tipo_origen=tipo_origen,
    num_resultados=num_resultados_encontrados # <-- ¡Variable nueva!
)

# ================================================================
# INICIO: CAPA 2 (NUEVOS API ENDPOINTS)
# ================================================================

# ENDPOINT 1: Devuelve la lista de UCEs (Padre)
@app.route('/api/uces')
def api_get_uces():
    print("Capa 2: Petición recibida en /api/uces")
    
    # Llama a la Capa 3
    uces = get_todas_las_uces()
    
    if uces is not None:
        return jsonify(uces)
    else:
        return jsonify({"error": "No se pudieron cargar las UCEs"}), 500

# ENDPOINT 2: Devuelve los Servicios (Hijo) para una UCE específica
# <int:uce_id> captura el número de la URL y lo pasa a la función
@app.route('/api/servicios/<int:uce_id>')
def api_get_servicios(uce_id):
    print(f"Capa 2: Petición recibida en /api/servicios/{uce_id}")
    
    # Llama a la Capa 3 pasándole el ID
    servicios = get_servicios_por_uce_id(uce_id)
    
    if servicios is not None:
        return jsonify(servicios)
    else:
        return jsonify({"error": "No se pudieron cargar los servicios"}), 500

# ================================================================
# FIN: CAPA 2
# ================================================================

# --- RUTA DE DETALLE INTELIGENTE ---
@app.route('/detalle/<string:tipo_origen>/<int:acfi_id>')
def pagina_detalle_at(tipo_origen, acfi_id):
    print(f"Capa 2: Solicitud de detalle para TIPO: {tipo_origen}, ID: {acfi_id}")

    # 1. Obtener la información de cabecera (genérica)
    info_cabecera = get_detalle_at_info(acfi_id)

    if not info_cabecera:
        flash(f"Error: No se encontró la AT con ID {acfi_id}.", 'error')
        return redirect(url_for('pagina_principal'))

    # 2. Lógica para decidir qué plantilla y qué actividades cargar

    lista_actividades = {}
    template_a_renderizar = ""

    if tipo_origen == 'AUDITORIA_CUMPLIMIENTO':
        # ¡Aquí está tu lógica!
        lista_actividades = get_actividades_cumplimiento(acfi_id)
        template_a_renderizar = 'detalle_at_cumplimiento.html'

    elif tipo_origen == 'AUDITORIA_SIMPLIFICADA':
        lista_actividades = get_actividades_simplificada(acfi_id)
        template_a_renderizar = 'detalle_at_simplificada.html'

    elif tipo_origen == 'ATENCION_REFERENCIA':
        lista_actividades = get_actividades_ara(acfi_id)
        template_a_renderizar = 'detalle_at_ara.html'

    elif tipo_origen == 'INVESTIGACION':
        lista_actividades = get_actividades_inve(acfi_id)
        template_a_renderizar = 'detalle_at_inve.html'

    elif tipo_origen == 'AUDITORIA_FINANCIERA':
        # (En el futuro, aquí llamarías a otra función)
        # lista_actividades = get_actividades_financiera(acfi_id)
        # template_a_renderizar = 'detalle_at_financiera.html' 
        flash(f"Página de detalle para '{tipo_origen}' aún no implementada.", 'error')
        return redirect(request.referrer or url_for('pagina_principal'))

    else:
        flash(f"Error: No hay una página de detalle definida para el tipo '{tipo_origen}'.", 'error')
        return redirect(request.referrer or url_for('pagina_principal'))

    # 3. Renderizar la plantilla correcta con los datos
    return render_template(
        template_a_renderizar,
        info=info_cabecera,
        actividades=lista_actividades
    )

# --- API ENDPOINT PARA ACTUALIZAR ESTADO DE PROCEDIMIENTO ---
@app.route('/api/actualizar-procedimiento', methods=['POST'])
def api_actualizar_procedimiento():

    # 1. Obtenemos los datos que envió el JavaScript
    data = request.json
    acfi_id = data.get('acfi_id')       # Este es nuestro LIAU_ID
    proc_id = data.get('proc_id')
    nuevo_estado = data.get('nuevo_estado') # 'ABIERTO' o 'CERRADO'

    if not acfi_id or not proc_id or not nuevo_estado:
        return jsonify({"success": False, "message": "Faltan datos."}), 400

    # 2. Llamamos a la Capa 3 para hacer el trabajo
    success = actualizar_estado_procedimiento(
        liau_id=acfi_id,
        proc_id=proc_id,
        nuevo_estado=nuevo_estado
    )

    # 3. Respondemos al JavaScript
    if success:
        return jsonify({"success": True, "message": "Procedimiento actualizado."})
    else:
        return jsonify({"success": False, "message": "Error en la base de datos al actualizar."}), 500

# --- API ENDPOINT PARA ACTUALIZAR LA AT COMPLETA ---
@app.route('/api/actualizar-at-completa', methods=['POST'])
def api_actualizar_at_completa():

    data = request.json
    acfi_id = data.get('acfi_id')
    accion = data.get('accion') # 'reabrir' o 'cerrar'

    if not acfi_id or not accion:
        return jsonify({"success": False, "message": "Faltan datos."}), 400

    # Llamamos a la Capa 3
    success = actualizar_estado_at_completa(
        acfi_id=acfi_id,
        accion=accion
    )

    if success:
        return jsonify({"success": True, "message": "AT actualizada."})
    else:
        return jsonify({"success": False, "message": "Error en la base de datos."}), 500
    
@app.route('/reportes')
def pagina_reportes():
    print("Capa 2: Navegando a la página de Reportes.")
    # Simplemente muestra el HTML que acabamos de crear
    return render_template('reportes.html')

# --- RUTA PARA GESTIÓN DE USUARIOS SIAD ---
# (Usamos GET y POST, como en el buscador)
@app.route('/gestion-usuarios-siad', methods=['GET', 'POST'])
def pagina_gestion_usuarios_siad():

    lista_de_resultados = None
    filtros_aplicados = {}

    if request.method == 'POST':
            # 1. Si el usuario presiona "Buscar"
            id_usuario = request.form.get('id_usuario')
            nombre = request.form.get('nombre')
            ap_paterno = request.form.get('ap_paterno')
            ap_materno = request.form.get('ap_materno')
            
            filtros_aplicados = {
                'id_usuario': id_usuario,
                'nombre': nombre,
                'ap_paterno': ap_paterno,
                'ap_materno': ap_materno
            }

            # 2. Validación: si todos los campos están vacíos, no buscar
            if not id_usuario and not nombre and not ap_paterno and not ap_materno:
                flash("Debe ingresar al menos un criterio de búsqueda.", 'error')
                lista_de_resultados = None # No mostrará la tabla
            else:
                # 3. Llamar a la Capa 3 con los filtros
                print(f"Capa 2: Buscando usuarios con filtros: {filtros_aplicados}")
                lista_de_resultados = buscar_usuarios_siad(
                    id_usuario=id_usuario,
                    nombre=nombre,
                    ap_paterno=ap_paterno,
                    ap_materno=ap_materno
                )
        # --------------------------------------------------------

    return render_template(
        'gestion_usuarios_siad.html',
        resultados=lista_de_resultados,
        filtros=filtros_aplicados
    )

# --- API ENDPOINT PARA DESCARGAR REPORTES EN EXCEL ---
@app.route('/api/download-report/<string:report_id>')
def api_download_report(report_id):

    print(f"Capa 2: Petición de reporte recibida para: {report_id}")

    # 1. Llamamos a la Capa 3 para generar el Excel en memoria
    excel_data_stream = generar_reporte_excel(report_id)

    # 2. Si la Capa 3 falló (ej. error de SQL)
    if excel_data_stream is None:
        print("Capa 2: Falló la generación del reporte en Capa 3.")
        # Devolvemos un error que el JavaScript entenderá
        return jsonify({"success": False, "message": "Error al generar reporte."}), 500

    # 3. Preparamos el nombre del archivo

    # Mapa de nombres base (los que nos diste)
    filename_map = {
        'casos_pd_entidad': 'Casos PD Entidad v1.0',
        'productos_no_vinculados': 'Productos no vinculados v1.0',
        'pd_fechas_resoluciones': 'Reporte PDs y fechas resoluciones Nacional Materias',
        'actos_totales_siad': 'Reporte actos totales casos siad v1.4'
    }

    base_name = filename_map.get(report_id, 'Reporte')
        
        # --- ¡LÍNEA NUEVA! ---
        # Limpiamos el nombre base de espacios al inicio o al final
    base_name_limpio = base_name.strip()
        
        # Obtenemos la fecha de hoy (20-10-2025)
    today_str = datetime.datetime.now().strftime("%d-%m-%Y")
        
        # Creamos el nombre final del archivo (usando el nombre limpio)
    final_filename = f"{base_name_limpio} {today_str}.xlsx"

    # 4. Enviamos el archivo al navegador
    print(f"Capa 2: Enviando archivo: {final_filename}")

    
    nombre_limpio_final = re.sub(r'[^\w\s\-\.]', '', final_filename).strip()
    print(f"Capa 2: Enviando archivo con nombre: '{nombre_limpio_final}'")
    print(f"Capa 2: Nombre final (repr): {repr(final_filename)}")

    # Regresamos el "puntero" del archivo en memoria al inicio
    excel_data_stream.seek(0)

    return send_file(
        excel_data_stream,
        # Usamos el nombre 100% limpio
        download_name=nombre_limpio_final,
        # Esto le dice al navegador que es un archivo .xlsx
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        # Esto asegura que se "descargue" y no se "muestre"
        as_attachment=True
    )

# --- RUTA PARA MOSTRAR LA PÁGINA DE EDICIÓN DE USUARIO ---
@app.route('/gestion-usuarios-siad/editar/<int:user_id>')
def pagina_editar_usuario_siad(user_id):
    
    # 1. Llamamos a la Capa 3 para buscar los datos del usuario
    usuario_data = get_usuario_siad_by_id(user_id)
    
    if usuario_data:
        # 2. Si lo encontramos, mostramos la plantilla con los datos
        return render_template(
            'editar_usuario_siad.html', 
            usuario=usuario_data
        )
    else:
        # 3. Si no, volvemos al buscador con un error
        flash(f"Error: No se encontró un usuario con ID {user_id}.", 'error')
        return redirect(url_for('pagina_gestion_usuarios_siad'))

# --- RUTA FICTICIA PARA GUARDAR CAMBIOS DE USUARIO (EVITA ERROR) ---
@app.route('/guardar_cambios_usuario_siad', methods=['POST'])
def guardar_cambios_usuario_siad():
    # Lee datos del formulario
    user_id = request.form.get('user_id')
    nombres = request.form.get('nombres')
    ap_paterno = request.form.get('ap_paterno')
    ap_materno = request.form.get('ap_materno')
    email = request.form.get('email')
    rut = request.form.get('rut')
    dv = request.form.get('dv')
    vigencia = request.form.get('vigencia')  # <-- agregado para evitar TypeError

    # Llamada a la función de la capa de datos (ahora con vigencia)
    resultado = guardar_cambios_usuario(user_id, nombres, ap_paterno, ap_materno, email, rut, dv, vigencia)

    if isinstance(resultado, dict):
        if resultado.get('success'):
            flash(resultado.get('message', 'Guardado correctamente.'), 'success')
        else:
            flash(resultado.get('message', 'Error al guardar.'), 'error')
    else:
        if resultado:
            flash('Usuario actualizado correctamente.', 'success')
        else:
            flash('Error al actualizar usuario.', 'error')

    return redirect(url_for('pagina_gestion_usuarios_siad'))

# --- API ENDPOINT PARA DESACTIVAR USUARIO SIAD ---
@app.route('/api/desactivar-usuario-siad', methods=['POST'])
def api_desactivar_usuario_siad():

    # Obtenemos el ID que envió el JavaScript
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"success": False, "message": "Falta el ID de usuario."}), 400

    # Llamamos a la Capa 3 para que haga el trabajo
    success = desactivar_usuario_siad(user_id=user_id)

    # Respondemos al JavaScript
    if success:
        return jsonify({"success": True, "message": "Usuario desactivado."})
    else:
        return jsonify({"success": False, "message": "Error en la base de datos."}), 500

# --- RUTA PARA MODIFICAR ACTUACIÓN SIAD (Página Inicial) ---
@app.route('/modificar-actuacion-siad', methods=['GET', 'POST'])
def pagina_modificar_actuacion_siad():

    # Estas variables las usaremos para pasar datos a la plantilla
    proceso_caso_buscado = None
    lista_de_actos = None
    lista_actos_termino = None

    if request.method == 'POST':
            proceso_caso = request.form.get('proceso_caso')
            proceso_caso_buscado = proceso_caso
            lista_de_actos = None
            lista_actos_termino = None # Nueva lista

            # 1. Validar el formato "numero.numero"
            if proceso_caso and '.' in proceso_caso:
                partes = proceso_caso.split('.')
                if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit():
                    proc_numero = int(partes[0])
                    caso_numero = int(partes[1])
                    
                    # 2. Llamar a AMBAS funciones de Capa 3
                    print(f"Capa 2: Buscando actos para Proceso={proc_numero}, Caso={caso_numero}")
                    lista_de_actos = get_actos_siad(proc_numero, caso_numero)
                    lista_actos_termino = get_actos_termino_siad(proc_numero, caso_numero) # <-- LLAMADA NUEVA
                    
                    # Manejar errores de consulta (si alguna falló, lista será None)
                    if lista_de_actos is None or lista_actos_termino is None:
                        flash("Error al consultar la base de datos para uno o ambos tipos de actos.", 'error')
                        # Devolvemos listas vacías para que el HTML muestre "No encontrado"
                        lista_de_actos = lista_de_actos or [] 
                        lista_actos_termino = lista_actos_termino or []
                    # Mensaje si no se encontró nada en ninguna lista
                    elif not lista_de_actos and not lista_actos_termino:
                         flash("No se encontraron actos administrativos ni actos de término para el Proceso.Caso ingresado.", 'info')

                else:
                    flash("Formato de 'Proceso.Caso' inválido. Use números, ej: 10000.1", 'error')
            else:
                flash("Formato de 'Proceso.Caso' inválido o campo vacío.", 'error')
                
    # Pasamos AMBAS listas a la plantilla
    return render_template(
        'modificar_actuacion_siad.html',
        proceso_caso_buscado=proceso_caso_buscado,
        actos=lista_de_actos,
        actos_termino=lista_actos_termino # <-- Ahora siempre tendrá un valor (None en GET)
    )
    

# --- ENDPOINT API PARA OBTENER REGISTROS DADO UN ACTO ---
@app.route('/api/get-registros-siad/<int:tiac_id>')
def api_get_registros_siad(tiac_id):

    print(f"Capa 2: Petición API recibida para registros de TIAC_ID: {tiac_id}")

    # Llama a Capa 3
    registros = get_registros_siad(tiac_id)

    if registros is not None:
        # Si tuvo éxito, devuelve los datos como JSON
        return jsonify(registros)
    else:
        # Si hubo un error en BD, devuelve un estado de error
        return jsonify({"error": "Error al obtener registros de la base de datos."}), 500

# --- API ENDPOINT PARA ACTUALIZAR ESTADO(S) DE ACTUACIÓN(ES) SIAD ---
@app.route('/api/actualizar-actuaciones-siad', methods=['POST'])
def api_actualizar_actuaciones_siad():

    data = request.json
    lista_ids = data.get('lista_ids') # Esperamos una lista de IDs
    accion = data.get('accion')       # 'borrador', 'enviado', 'no_vigente'

    if not lista_ids or not accion or not isinstance(lista_ids, list):
        return jsonify({"success": False, "message": "Faltan datos o formato incorrecto (se espera lista de IDs)."}), 400

    # Mapear la acción del JS al estado de la BD
    estado_bd = None
    if accion == 'borrador':
        estado_bd = 'BORRADOR_CGR'
    elif accion == 'enviado':
        estado_bd = 'ENVIADA_CGR'
    elif accion == 'no_vigente':
        estado_bd = 'NO_VIGENTE'
    else:
         return jsonify({"success": False, "message": "Acción no válida."}), 400

    # Convertir IDs a enteros por seguridad
    try:
        lista_ids_int = [int(id_val) for id_val in lista_ids]
    except ValueError:
         return jsonify({"success": False, "message": "Lista de IDs contiene valores no numéricos."}), 400

    # Llamar a la Capa 3
    success = actualizar_estado_actuaciones_siad(
        lista_actu_ids=lista_ids_int,
        nuevo_estado=estado_bd
    )

    if success:
        return jsonify({"success": True, "message": f"{len(lista_ids_int)} actuación(es) actualizada(s)."})
    else:
        return jsonify({"success": False, "message": "Error en la base de datos al actualizar."}), 500

# --- API ENDPOINT PARA ACTUALIZAR ESTADO(S) DE ACTO(S) DE TÉRMINO SIAD ---
@app.route('/api/actualizar-actos-termino-siad', methods=['POST'])
def api_actualizar_actos_termino_siad():

    data = request.json
    lista_ids = data.get('lista_ids') # Esperamos una lista de AAFI_IDs
    accion = data.get('accion')       # 'borrador', 'enviado', 'no_vigente'

    if not lista_ids or not accion or not isinstance(lista_ids, list):
        return jsonify({"success": False, "message": "Faltan datos o formato incorrecto (se espera lista de IDs)."}), 400

    # Validar la acción permitida (ya se valida en Capa 3, pero es bueno tenerlo aquí también)
    acciones_validas = ['borrador', 'enviado', 'no_vigente']
    if accion not in acciones_validas:
         return jsonify({"success": False, "message": "Acción no válida."}), 400

    # Convertir IDs a enteros por seguridad
    try:
        lista_ids_int = [int(id_val) for id_val in lista_ids]
    except ValueError:
         return jsonify({"success": False, "message": "Lista de IDs contiene valores no numéricos."}), 400

    # Llamar a la Capa 3
    success = actualizar_estado_actos_termino(
        lista_aafi_ids=lista_ids_int,
        accion=accion # Pasamos la acción directamente ('borrador', 'enviado', 'no_vigente')
    )

    if success:
        return jsonify({"success": True, "message": f"{len(lista_ids_int)} acto(s) de término actualizado(s)."})
    else:
        return jsonify({"success": False, "message": "Error en la base de datos al actualizar."}), 500

# --- API PARA ACTUALIZAR PROCEDIMIENTO ARA ---
@app.route('/api/actualizar-procedimiento-ara', methods=['POST'])
def api_actualizar_procedimiento_ara():
    data = request.json
    acfi_id = data.get('acfi_id')
    proc_id = data.get('proc_id')
    nuevo_estado = data.get('nuevo_estado')
    if not all([acfi_id, proc_id, nuevo_estado]): return jsonify({"success": False, "message": "Faltan datos."}), 400
    success = actualizar_estado_procedimiento_ara(acfi_id, proc_id, nuevo_estado)
    if success: return jsonify({"success": True, "message": "Procedimiento ARA actualizado."})
    else: return jsonify({"success": False, "message": "Error BD al actualizar procedimiento ARA."}), 500

# --- API PARA ACTUALIZAR AT COMPLETA ARA ---
@app.route('/api/actualizar-at-completa-ara', methods=['POST'])
def api_actualizar_at_completa_ara():
    data = request.json
    acfi_id = data.get('acfi_id')
    accion = data.get('accion')
    if not all([acfi_id, accion]): return jsonify({"success": False, "message": "Faltan datos."}), 400
    success = actualizar_estado_at_completa_ara(acfi_id, accion)
    if success: return jsonify({"success": True, "message": "AT ARA actualizada."})
    else: return jsonify({"success": False, "message": "Error BD al actualizar AT ARA."}), 500

@app.route('/api/actualizar-procedimiento-inve', methods=['POST'])
def api_actualizar_procedimiento_inve():
    data = request.json
    acfi_id = data.get('acfi_id')
    proc_id = data.get('proc_id')
    nuevo_estado = data.get('nuevo_estado')
    # ... (Obtener acfi_id, proc_id, nuevo_estado de data) ...
    if not acfi_id or not proc_id or not nuevo_estado:
        # Si falta alguno de los datos necesarios
        print(f"Error Capa 2 (INVE Proc Update): Faltan datos - acfi_id={acfi_id}, proc_id={proc_id}, estado={nuevo_estado}") # Log para ver qué falta
        return jsonify({"success": False, "message": "Faltan datos requeridos (ID AT, ID Proc, Nuevo Estado)."}), 400
    # --- Fin Validación ---

    # Si la validación pasa, llamar a la Capa 3
    print(f"Capa 2 (INVE Proc Update): Llamando a Capa 3 con acfi_id={acfi_id}, proc_id={proc_id}, estado={nuevo_estado}") # Log para confirmar llamada
    success = actualizar_estado_procedimiento_inve(acfi_id, proc_id, nuevo_estado)
    if success: return jsonify({"success": True, "message": "Procedimiento INVE actualizado."})
    else: return jsonify({"success": False, "message": "Error BD al actualizar procedimiento INVE."}), 500

# --- API PARA ACTUALIZAR AT COMPLETA INVE ---
@app.route('/api/actualizar-at-completa-inve', methods=['POST'])
def api_actualizar_at_completa_inve():
    data = request.json
    acfi_id = data.get('acfi_id')
    accion = data.get('accion')
    # ... (Obtener acfi_id, accion de data) ...
    if not all([...]): return jsonify({"success": False, "message": "Faltan datos."}), 400
    success = actualizar_estado_at_completa_inve(acfi_id, accion)
    if success: return jsonify({"success": True, "message": "AT INVE actualizada."})
    else: return jsonify({"success": False, "message": "Error BD al actualizar AT INVE."}), 500

# ================================================================
# --- 6. Iniciar la aplicación ---
# ================================================================
if __name__ == '__main__':
    # Antes de arrancar el servidor web, probamos la conexión
    probar_conexion_oracle()
    
    print("\nIniciando servidor web Flask...")
    app.run(debug=True)

