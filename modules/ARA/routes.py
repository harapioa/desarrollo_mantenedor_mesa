# modules/SEOBCON/routes.py
from flask import Blueprint, render_template, request, jsonify, url_for, flash, redirect
# Importamos las funciones de queries.py
from .queries import cambiar_servicio_at, actualizar_estado_procedimiento_ara, actualizar_estado_at_completa_ara, get_detalle_at_ara

ara_bp = Blueprint('ara_bp', __name__)

@ara_bp.route('/detalle-at-ara/<int:acfi_id>')

def pagina_detalle_at_ara(acfi_id):
    # 1. Buscamos la data en la BD usando la función de queries.py
    print(f"1. pagina_detalle_at_ara: {acfi_id}")
    datos = get_detalle_at_ara(acfi_id)
    
    # 2. Si no hay datos, mostramos error y volvemos al inicio
    if not datos or not datos.get('info'):
        flash("No se encontró la Atención Referencia solicitada.", "error")
        print(f"1. No se encontró la Atención Referencia solicitada. Volviendo al inicio.")
        return redirect(url_for('pagina_principal')) 
    
    # 3. Renderizamos el HTML pasando los datos
    return render_template(
        'ARA/detalle_at_ara.html',
        info=datos['info'],
        actividades=datos['actividades']
    )

# --- API PARA ACTUALIZAR PROCEDIMIENTO ARA ---
@ara_bp.route('/api/actualizar-procedimiento-ara', methods=['POST'])
def api_actualizar_procedimiento_ara():
    print("\n=== INICIO: api_actualizar_procedimiento_ara ===")
    
    data = request.get_json()
    print(f"1. JSON recibido: {data}")
    
    acfi_id = data.get('acfi_id')
    proc_nombre = data.get('proc_nombre')  # '1.1', '1.2', etc.
    nuevo_estado = data.get('nuevo_estado')  # 'ABIERTO' o 'CERRADO'
    
    print(f"2. acfi_id: {acfi_id}")
    print(f"3. proc_nombre: {proc_nombre}")
    print(f"4. nuevo_estado: {nuevo_estado}")

    if not acfi_id or not proc_nombre or not nuevo_estado:
        print("5. ERROR: Parámetros incompletos")
        return jsonify({
            "success": False, 
            "message": "Parámetros incompletos. Se requieren: acfi_id, proc_nombre y nuevo_estado."
        }), 400

    print("5. Parámetros validados")
    
    # Convertir proc_nombre ('1.1') a proc_id (número)
    # ASUNCIÓN: '1.1' -> 1, '1.2' -> 2, '1.3' -> 3, etc.
    try:
        proc_numero = int(proc_nombre.split('.')[1])
        print(f"6. proc_nombre '{proc_nombre}' convertido a proc_id: {proc_numero}")
    except (ValueError, IndexError):
        print(f"7. ERROR: No se pudo convertir proc_nombre: {proc_nombre}")
        return jsonify({
            "success": False, 
            "message": f"Formato de procedimiento inválido: {proc_nombre}"
        }), 400
    
    print("7. Llamando a actualizar_estado_procedimiento_ara()...")
    resultado = actualizar_estado_procedimiento_ara(acfi_id, proc_numero, nuevo_estado)
    print(f"8. Resultado de la función: {resultado}")
    
    print("=== FIN: api_actualizar_procedimiento_ara ===\n")
    return jsonify(resultado if isinstance(resultado, dict) else {"success": resultado})

# --- API PARA ACTUALIZAR AT COMPLETA ARA ---
@ara_bp.route('/api/actualizar-at-completa-ara', methods=['POST'])
def api_actualizar_at_completa_ara():
    print("\n=== INICIO: api_actualizar_at_completa_ara ===")
    
    data = request.get_json()
    print(f"1. JSON recibido: {data}")
    
    acfi_id = data.get('acfi_id')
    accion = data.get('accion')
    
    print(f"2. acfi_id: {acfi_id}")
    print(f"3. accion: {accion}")

    if not acfi_id or not accion:
        print("4. ERROR: Parámetros incompletos")
        return jsonify({
            "success": False, 
            "message": "Parámetros incompletos. Se requieren acfi_id y accion."
        }), 400

    if accion not in ['reabrir', 'cerrar']:
        print(f"5. ERROR: Acción no válida: {accion}")
        return jsonify({
            "success": False, 
            "message": f"Acción no válida. Debe ser 'reabrir' o 'cerrar'."
        }), 400

    print("4. Parámetros validados correctamente")
    print("5. Llamando a actualizar_estado_at_completa_ara()...")
    
    resultado = actualizar_estado_at_completa_ara(acfi_id, accion)
    
    print(f"6. Resultado de la función: {resultado}")
    print("=== FIN: api_actualizar_at_completa_ara ===\n")
    
    if resultado:
        return jsonify({"success": True, "message": f"AT ARA actualizada a {accion}."})
    else:
        return jsonify({"success": False, "message": "Error al actualizar AT ARA."})

# --- API ENDPOINT PARA CAMBIAR SERVICIO EN AT ---
@ara_bp.route('/api/cambiar-servicio-at', methods=['POST'])
def api_cambiar_servicio_at():
    print("\n=== INICIO: api_cambiar_servicio_at ===")
    
    data = request.get_json()
    print(f"1. JSON recibido: {data}")
    
    acfi_id = data.get('acfi_id')
    nuevo_servicio_id = data.get('nuevo_servicio_id')
    nuevo_servicio_nombre = data.get('nuevo_servicio_nombre')
    uce_nombre = data.get('uce_nombre')
    tipo_producto = data.get('tipo_producto')
    
    print(f"2. acfi_id: {acfi_id}")
    print(f"3. nuevo_servicio_id: {nuevo_servicio_id}")
    print(f"4. nuevo_servicio_nombre: {nuevo_servicio_nombre}")
    print(f"5. uce_nombre: {uce_nombre}")
    print(f"6. tipo_producto: {tipo_producto}")

    if not acfi_id or not nuevo_servicio_id or not nuevo_servicio_nombre or not tipo_producto:
        print("7. ERROR: Parámetros incompletos")
        return jsonify({"success": False, "message": "Parámetros incompletos. Se requieren: acfi_id, nuevo_servicio_id, nuevo_servicio_nombre y tipo_producto."}), 400

    print("8. Llamando a cambiar_servicio_at()...")
    resultado = cambiar_servicio_at(acfi_id, nuevo_servicio_id, nuevo_servicio_nombre, uce_nombre, tipo_producto)
    print(f"9. Resultado de la función: {resultado}")
    
    print("=== FIN: api_cambiar_servicio_at ===\n")
    return jsonify(resultado)
