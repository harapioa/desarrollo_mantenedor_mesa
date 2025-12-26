# modules/API/routes.py
from flask import Blueprint, request, jsonify
# IMPORTANTE: Importa aquí tu función de base de datos (la Capa 3)
# Asegúrate de saber dónde está 'actualizar_estado_at_completa'. 
# Si está en un archivo común de queries, impórtalo.
from . import queries

# Definimos el Blueprint con el nombre 'api_bp'
api_bp = Blueprint('api_bp', __name__)

# NOTA: En el paso 3 definiremos que todo este blueprint empieza con '/api'
# Por lo tanto, aquí la ruta es solo '/actualizar-at-completa'
@api_bp.route('/actualizar-at-completa', methods=['POST'])
def api_actualizar_at_completa():
    data = request.json
    acfi_id = data.get('acfi_id')
    accion = data.get('accion') 
    tipo_origen = data.get('tipo_origen')

    if not acfi_id or not accion:
        return jsonify({"success": False, "message": "Faltan datos."}), 400

    # Llamamos a la lógica compartida (Capa 3)
    success = queries.actualizar_estado_at_completa(
        acfi_id=acfi_id,
        accion=accion,
        tipo_origen=tipo_origen
    )

    if success:
        return jsonify({"success": True, "message": "AT actualizada."})
    else:
        return jsonify({"success": False, "message": "Error en la base de datos."}), 500
    
# --- API ENDPOINT PARA ACTUALIZAR ESTADO DE PROCEDIMIENTO ---
@api_bp.route('/actualizar-procedimiento', methods=['POST'])
def api_actualizar_procedimiento():

    # 1. Obtenemos los datos que envió el JavaScript
    data = request.json
    acfi_id = data.get('acfi_id')       # Este es nuestro LIAU_ID
    proc_id = data.get('proc_id')
    nuevo_estado = data.get('nuevo_estado') # 'ABIERTO' o 'CERRADO'

    if not acfi_id or not proc_id or not nuevo_estado:
        return jsonify({"success": False, "message": "Faltan datos."}), 400

    # 2. Llamamos a la Capa 3 para hacer el trabajo
    success = queries.actualizar_estado_procedimiento(
        liau_id=acfi_id,
        proc_id=proc_id,
        nuevo_estado=nuevo_estado
    )

    # 3. Respondemos al JavaScript
    if success:
        return jsonify({"success": True, "message": "Procedimiento actualizado."})
    else:
        return jsonify({"success": False, "message": "Error en la base de datos al actualizar."}), 500
