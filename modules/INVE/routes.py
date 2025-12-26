# modules/INVE/routes.py
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from .queries import get_detalle_at_inve, actualizar_procedimiento_inve, actualizar_estado_at_completa_inve, reabrir_at_inve_ejecucion, cerrar_at_inve_ejecucion, reabrir_at_inve_inicio, cerrar_at_inve_inicio, gestionar_fase_inve

inve_bp = Blueprint('inve', __name__)

@inve_bp.route('/detalle-at-inve/<int:acfi_id>')
def pagina_detalle_at_inve(acfi_id):
    # 1. Usamos la función maestra
    datos = get_detalle_at_inve(acfi_id)
    
    # 2. Validación de seguridad (La que fallaba antes)
    if not datos or not datos.get('info'):
        flash("No se encontró la Investigación solicitada.", "error")
        return redirect(url_for('pagina_principal'))
    
    # 3. Renderizamos
    return render_template(
        'INVE/detalle_at_inve.html',  # Ruta en templates/INVE/
        info=datos['info'],
        actividades=datos['actividades']
    )

@inve_bp.route('/api/actualizar-procedimiento-inve', methods=['POST'])
def api_actualizar_procedimiento_inve():
    print("\n=== INICIO: api_actualizar_procedimiento_inve ===")
    
    data = request.get_json()
    print(f"1. JSON recibido: {data}")
    
    acfi_id = data.get('acfi_id')
    proc_nombre = data.get('proc_nombre')
    nuevo_estado = data.get('nuevo_estado')
    
    print(f"2. acfi_id: {acfi_id} (tipo: {type(acfi_id)})")
    print(f"3. proc_nombre: {proc_nombre} (tipo: {type(proc_nombre)})")
    print(f"4. nuevo_estado: {nuevo_estado} (tipo: {type(nuevo_estado)})")

    if not acfi_id or not proc_nombre or not nuevo_estado:
        print("5. ERROR: Parámetros incompletos")
        return jsonify({"success": False, "message": "Parámetros incompletos. acfi_id, proc_nombre y nuevo_estado son requeridos."}), 400

    print("6. Llamando a actualizar_procedimiento_inve()...")
    resultado = actualizar_procedimiento_inve(acfi_id, proc_nombre, nuevo_estado)
    print(f"7. Resultado de la función: {resultado}")
    
    print("=== FIN: api_actualizar_procedimiento_inve ===\n")
    return jsonify(resultado)

# --- API PARA ACTUALIZAR AT COMPLETA INVE ---
@inve_bp.route('/api/actualizar-at-completa-inve', methods=['POST'])
def api_actualizar_at_completa_inve():
    data = request.json
    acfi_id = data.get('acfi_id')
    accion = data.get('accion')
    # ... (Obtener acfi_id, accion de data) ...
    if not all([...]): return jsonify({"success": False, "message": "Faltan datos."}), 400
    success = actualizar_estado_at_completa_inve(acfi_id, accion)
    if success: return jsonify({"success": True, "message": "AT INVE actualizada."})
    else: return jsonify({"success": False, "message": "Error BD al actualizar AT INVE."}), 500

@inve_bp.route('/api/reabrir-inve-ejecucion', methods=['POST'])
def api_reabrir_inve_ejecucion():
    data = request.get_json()
    acfi_id = data.get('acfi_id')

    if not acfi_id:
        return jsonify({"success": False, "message": "ACFI_ID es requerido."}), 400

    resultado = reabrir_at_inve_ejecucion(acfi_id)
    return jsonify(resultado)

@inve_bp.route('/api/cerrar-inve-ejecucion', methods=['POST'])
def api_cerrar_inve_ejecucion():
    data = request.get_json()
    acfi_id = data.get('acfi_id')

    if not acfi_id:
        return jsonify({"success": False, "message": "ACFI_ID es requerido."}), 400

    resultado = cerrar_at_inve_ejecucion(acfi_id)
    return jsonify(resultado)

@inve_bp.route('/api/reabrir-inve-inicio', methods=['POST'])
def api_reabrir_inve_inicio():
    data = request.get_json()
    acfi_id = data.get('acfi_id')

    if not acfi_id:
        return jsonify({"success": False, "message": "ACFI_ID es requerido."}), 400

    resultado = reabrir_at_inve_inicio(acfi_id)
    return jsonify(resultado)

@inve_bp.route('/api/cerrar-inve-inicio', methods=['POST'])
def api_cerrar_inve_inicio():
    data = request.get_json()
    acfi_id = data.get('acfi_id')

    if not acfi_id:
        return jsonify({"success": False, "message": "ACFI_ID es requerido."}), 400

    resultado = cerrar_at_inve_inicio(acfi_id)
    return jsonify(resultado)

@inve_bp.route('/api/gestionar-fase-inve', methods=['POST'])
def api_gestionar_fase_inve():
    data = request.json
    acfi_id = data.get('acfi_id')
    fase = data.get('fase')     # 'EJECUCION' o 'INFORME_FINAL'
    accion = data.get('accion') # 'CERRAR' o 'REABRIR'

    if not all([acfi_id, fase, accion]):
        return jsonify({"success": False, "message": "Datos incompletos."}), 400

    resultado = gestionar_fase_inve(acfi_id, fase, accion)
    return jsonify(resultado)