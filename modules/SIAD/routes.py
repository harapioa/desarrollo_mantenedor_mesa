# modules/SIAD/routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .queries import buscar_usuarios_siad, desactivar_usuario_siad, get_usuario_siad_by_id, get_actos_siad, get_registros_siad, actualizar_estado_actuaciones_siad, get_actos_termino_siad, actualizar_estado_actos_termino, guardar_cambios_usuario

siad_bp = Blueprint('siad_bp', __name__)

# --- RUTA PARA GESTIÓN DE USUARIOS SIAD ---
# (Usamos GET y POST, como en el buscador)
@siad_bp.route('/gestion-usuarios-siad', methods=['GET', 'POST'])
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
                print(f"Capa 2: Buscando usuarios with filtros: {filtros_aplicados}")
                lista_de_resultados = buscar_usuarios_siad(
                    id_usuario=id_usuario,
                    nombre=nombre,
                    ap_paterno=ap_paterno,
                    ap_materno=ap_materno
                )
        # --------------------------------------------------------

    return render_template(
        'SIAD/gestion_usuarios_siad.html',
        resultados=lista_de_resultados,
        filtros=filtros_aplicados
    )


# --- RUTA PARA MOSTRAR LA PÁGINA DE EDICIÓN DE USUARIO ---
@siad_bp.route('/gestion-usuarios-siad/editar/<int:user_id>')
def pagina_editar_usuario_siad(user_id):
    
    # 1. Llamamos a la Capa 3 para buscar los datos del usuario
    usuario_data = get_usuario_siad_by_id(user_id)
    
    if usuario_data:
        # 2. Si lo encontramos, mostramos la plantilla con los datos
        return render_template(
            'SIAD/editar_usuario_siad.html', 
            usuario=usuario_data
        )
    else:
        # 3. Si no, volvemos al buscador con un error
        flash(f"Error: No se encontró un usuario con ID {user_id}.", 'error')
        return redirect(url_for('siad_bp.pagina_gestion_usuarios_siad'))

# --- RUTA FICTICIA PARA GUARDAR CAMBIOS DE USUARIO (EVITA ERROR) ---
@siad_bp.route('/guardar_cambios_usuario_siad', methods=['POST'])
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

    return redirect(url_for('siad_bp.pagina_gestion_usuarios_siad'))

# --- API ENDPOINT PARA DESACTIVAR USUARIO SIAD ---
@siad_bp.route('/api/desactivar-usuario-siad', methods=['POST'])
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
@siad_bp.route('/modificar-actuacion-siad', methods=['GET', 'POST'])
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
        'SIAD/modificar_actuacion_siad.html',
        proceso_caso_buscado=proceso_caso_buscado,
        actos=lista_de_actos,
        actos_termino=lista_actos_termino # <-- Ahora siempre tendrá un valor (None en GET)
    )
    

# --- ENDPOINT API PARA OBTENER REGISTROS DADO UN ACTO ---
@siad_bp.route('/api/get-registros-siad/<int:tiac_id>')
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
@siad_bp.route('/api/actualizar-actuaciones-siad', methods=['POST'])
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
@siad_bp.route('/api/actualizar-actos-termino-siad', methods=['POST'])
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
