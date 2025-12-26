# modules/PRDI/routes.py
import os
import csv
from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify, current_app
# Importamos las nuevas funciones
from .queries import (
    get_prdi_cabecera, 
    get_prdi_actividades, 
    get_pdis_id_por_resolucion, 
    get_prdi_cabecera_por_id,
    eliminar_actividad_prdi,
    devolver_actividad_carpeta,
    reabrir_actividad_prdi,
    get_datos_para_respaldo,
    renumerar_folios_prdi,
    MAPA_ETAPAS
)

prdi_bp = Blueprint('prdi', __name__)

@prdi_bp.route('/buscador-prdi', methods=['GET', 'POST'])
def pagina_buscador_prdi():
    resultado_cabecera = None
    # Agregamos 'tipo_busqueda' a los filtros para mantener el radio button seleccionado
    filtros = {'numero': '', 'anio': '', 'tipo_busqueda': 'prdi'} 

    if request.method == 'POST':
        numero = request.form.get('numero')
        anio = request.form.get('anio')
        tipo_busqueda = request.form.get('tipo_busqueda') # 'prdi' o 'resolucion'
        
        filtros['numero'] = numero
        filtros['anio'] = anio
        filtros['tipo_busqueda'] = tipo_busqueda

        if numero and anio:
            
            # --- CASO 1: Búsqueda Normal (PRDI) ---
            if tipo_busqueda == 'prdi':
                resultado_cabecera = get_prdi_cabecera(numero, anio)
                if not resultado_cabecera:
                    flash("No se encontró el Procedimiento (PRDI) con los datos ingresados.", "error")

            # --- CASO 2: Búsqueda por Resolución ---
            elif tipo_busqueda == 'resolucion':
                # 1. Buscamos el ID
                pdis_id = get_pdis_id_por_resolucion(numero, anio)
                
                if pdis_id:
                    # 2. Si tenemos ID, buscamos la cabecera
                    resultado_cabecera = get_prdi_cabecera_por_id(pdis_id)
                else:
                    flash("No se encontró ninguna Resolución de Inicio con esos datos.", "error")
            
        else:
            flash("Debe ingresar Número y Año.", "error")

    return render_template(
        'PRDI/buscador_prdi.html',
        pdis=resultado_cabecera,
        filtros=filtros
    )

# ... (El resto de las APIs se mantiene igual) ...
@prdi_bp.route('/api/prdi-actividades', methods=['POST'])
def api_prdi_actividades():
    # ... tu código existente ...
    data = request.json
    pdis_id = data.get('pdis_id')
    etapa_seleccionada = data.get('etapa')
    
    if not pdis_id or not etapa_seleccionada:
        return jsonify({"success": False, "message": "Datos incompletos"}), 400

    codigo_bd = MAPA_ETAPAS.get(etapa_seleccionada)
    if not codigo_bd:
        return jsonify({"success": False, "message": "Etapa no válida"}), 400

    actividades = get_prdi_actividades(pdis_id, codigo_bd)
    return jsonify({"success": True, "actividades": actividades})

# --- API REAL PARA ELIMINAR ACTIVIDAD ---
@prdi_bp.route('/api/prdi-eliminar', methods=['POST'])
def api_prdi_eliminar():
    data = request.json
    acti_id = data.get('acti_id')
    
    if not acti_id:
        return jsonify({"success": False, "message": "Falta el ID de actividad"}), 400

    # Llamamos a la capa de datos
    exito = eliminar_actividad_prdi(acti_id)
    
    if exito:
        return jsonify({
            "success": True, 
            "message": "Actividad eliminada correctamente. (Estado actualizado y folios limpiados)"
        })
    else:
        return jsonify({
            "success": False, 
            "message": "Error al eliminar la actividad en la base de datos."
        }), 500

@prdi_bp.route('/api/prdi-devolver', methods=['POST'])
def api_prdi_devolver():
    data = request.json
    acti_id = data.get('acti_id')
    
    if not acti_id:
        return jsonify({"success": False, "message": "Falta el ID de actividad"}), 400

    exito = devolver_actividad_carpeta(acti_id)
    
    if exito:
        return jsonify({
            "success": True, 
            "message": "Actividad devuelta a la carpeta de trabajo correctamente."
        })
    else:
        return jsonify({
            "success": False, 
            "message": "Error al actualizar la actividad."
        }), 500
    
@prdi_bp.route('/api/prdi-reabrir', methods=['POST'])
def api_prdi_reabrir():
    data = request.json
    acti_id = data.get('acti_id')
    
    if not acti_id:
        return jsonify({"success": False, "message": "Falta el ID de actividad"}), 400

    exito = reabrir_actividad_prdi(acti_id)
    
    if exito:
        return jsonify({
            "success": True, 
            "message": "Actividad reabierta correctamente (Estado REVISION y flujo reiniciado)."
        })
    else:
        return jsonify({
            "success": False, 
            "message": "Error al reabrir la actividad en la base de datos."
        }), 500

def generar_respaldo_csv(pdis_id):
    """
    Crea un archivo CSV de respaldo en C:\Respaldo Mesa
    Retorna (True, Ruta) si tuvo éxito, o (False, Error).
    """
    try:
        # 1. Definir rutas y nombres
        carpeta_base = r"C:\Respaldo Mesa"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"Respaldo_Folios_PDIS_{pdis_id}_{timestamp}.csv"
        ruta_completa = os.path.join(carpeta_base, nombre_archivo)

        # 2. Crear carpeta si no existe
        if not os.path.exists(carpeta_base):
            os.makedirs(carpeta_base)
            print(f"Carpeta creada: {carpeta_base}")

        # 3. Obtener los datos de la BD
        datos = get_datos_para_respaldo(pdis_id)
        if not datos:
            return False, "No se encontraron datos para respaldar (o error de BD)."

        # 4. Escribir el archivo CSV
        # newline='' es importante en Windows para evitar líneas en blanco extra
        with open(ruta_completa, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';') # Usamos ; para que Excel lo abra fácil
            
            # Cabecera
            writer.writerow(['ACTI_ID', 'FOLIO_DESDE', 'FOLIO_HASTA', 'ESTADO', 'ETAPA'])
            
            # Datos
            # La query devuelve: (ACTI_ID, DESDE, HASTA, ESTADO, UBICACION)
            writer.writerows(datos)

        return True, ruta_completa

    except Exception as e:
        error_msg = f"Error generando respaldo en disco: {str(e)}"
        print(error_msg)
        return False, error_msg

@prdi_bp.route('/api/prdi-renumerar', methods=['POST'])
def api_prdi_renumerar():
    data = request.json
    pdis_id = data.get('pdis_id')
    
    if not pdis_id:
        return jsonify({"success": False, "message": "Falta el ID del PRDI"}), 400

    # --- PASO CRÍTICO: RESPALDO ---
    exito_respaldo, mensaje_respaldo = generar_respaldo_csv(pdis_id)
    
    if not exito_respaldo:
        # Si falla el respaldo, NO hacemos la renumeración. Seguridad ante todo.
        return jsonify({
            "success": False, 
            "message": f"ABORTADO: No se pudo crear el respaldo. {mensaje_respaldo}"
        }), 500

    # --- SI EL RESPALDO SALIÓ BIEN, PROCEDEMOS ---
    resultado = renumerar_folios_prdi(pdis_id)
    
    if resultado['success']:
        # Agregamos al mensaje de éxito la ubicación del respaldo
        resultado['message'] += f" (Respaldo guardado en: {mensaje_respaldo})"
        return jsonify(resultado)
    else:
        return jsonify(resultado), 500