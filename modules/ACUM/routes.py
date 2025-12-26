# Archivo: modules/ACUM/routes.py
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from .queries import get_detalle_at_acum, gestionar_fase_acum, actualizar_procedimiento_acum

# Definimos el Blueprint
acum_bp = Blueprint('acum_bp', __name__)

# Asumo que esta ruta recibe parámetros, por ejemplo el ID de la auditoría
@acum_bp.route('/detalle-acum/<int:acfi_id>') 
def pagina_detalle_at_acum(acfi_id):
    datos = get_detalle_at_acum(acfi_id)
    if not datos or not datos.get('info'):
        flash("No se encontró la Auditoría Cumplimiento solicitada.", "error")
        return redirect(url_for('pagina_principal'))
    
    return render_template('ACUM/detalle_at_cumplimiento.html', 
        info=datos['info'],
        actividades=datos['actividades']
    )

# Ruta para gestionar fases (ejemplo)
@acum_bp.route('/api/gestionar-fase-acum', methods=['POST'])
def api_gestionar_fase_acum():
    data = request.json
    acfi_id = data.get('acfi_id')
    fase = data.get('fase')
    accion = data.get('accion')

    if not all([acfi_id, fase, accion]):
        return jsonify({"success": False, "message": "Datos incompletos."}), 400

    resultado = gestionar_fase_acum(acfi_id, fase, accion)
    return jsonify(resultado)

# Ruta para actualizar el estado de un procedimiento (candado)
@acum_bp.route('/api/actualizar-procedimiento-acum', methods=['POST'])
def api_actualizar_procedimiento_acum():
    data = request.json
    acfi_id = data.get('acfi_id')
    proc_id = data.get('proc_id')       # Usaremos el ID numérico
    nuevo_estado = data.get('nuevo_estado')

    print(f"Datos recibidos: acfi_id={acfi_id}, proc_id={proc_id}, nuevo_estado={nuevo_estado}")

    if not all([acfi_id, proc_id, nuevo_estado]):
        return jsonify({"success": False, "message": "Datos incompletos."}), 400

    resultado = actualizar_procedimiento_acum(acfi_id, proc_id, nuevo_estado)
    return jsonify(resultado)