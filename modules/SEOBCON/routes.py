# modules/SEOBCON/routes.py
from flask import Blueprint, render_template, request, flash, jsonify, url_for
from .queries import get_seobcon_observaciones, actualizar_estado_seobcon

# Definimos el Blueprint
seobcon_bp = Blueprint('seobcon_bp', __name__)

# --- RUTA PARA MODIFICAR OBSERVACIÓN SEOBCON ---
@seobcon_bp.route('/modificar-seobcon', methods=['GET', 'POST'])


# --- RUTA PARA MODIFICAR OBSERVACIÓN SEOBCON ---
@seobcon_bp.route('/modificar-seobcon', methods=['GET', 'POST'])
def pagina_modificar_seobcon():
    
    lista_observaciones = None
    ids_buscados_str = ""

    if request.method == 'POST':
        ids_buscados_str = request.form.get('obse_ids', '')
        
        if not ids_buscados_str:
            flash("Debe ingresar al menos un ID de observación.", 'error')
        else:
            lista_observaciones = get_seobcon_observaciones(ids_buscados_str)
            if lista_observaciones is None:
                flash("Error al consultar la base de datos. Verifique que los IDs sean numéricos.", 'error')
            elif not lista_observaciones:
                flash("No se encontraron observaciones para los IDs ingresados.", 'info')

    return render_template(
        'SEOBCON/modificar_seobcon.html',
        observaciones=lista_observaciones,
        ids_buscados=ids_buscados_str # Para rellenar el textarea
    )

# --- API ENDPOINT PARA ACTUALIZAR ESTADO SEOBCON ---
@seobcon_bp.route('/api/actualizar-seobcon', methods=['POST'])
def api_actualizar_seobcon():
    
    data = request.json
    lista_ids_str = data.get('lista_ids') # Esperamos una lista de strings/ints
    nuevo_estado = data.get('nuevo_estado')  # ej: 'REVISADA'

    if not lista_ids_str or not nuevo_estado or not isinstance(lista_ids_str, list):
        return jsonify({"success": False, "message": "Faltan datos (lista_ids, nuevo_estado)."}), 400
    
    # Convertir IDs a enteros
    try:
        lista_ids_int = [int(id_val) for id_val in lista_ids_str]
    except ValueError:
         return jsonify({"success": False, "message": "Lista de IDs contiene valores no numéricos."}), 400

    # Llamar a la Capa 3
    success = actualizar_estado_seobcon(
        lista_ids=lista_ids_int,
        nuevo_estado=nuevo_estado
    )
    
    if success:
        return jsonify({"success": True, "message": f"{len(lista_ids_int)} observación(es) actualizada(s)."})
    else:
        return jsonify({"success": False, "message": "Error en la base de datos al actualizar."}), 500
