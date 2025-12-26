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

from flask import Flask, render_template, request, redirect, jsonify, flash, url_for
from database_queries import (
    get_todas_las_uces, get_servicios_por_uce_id, buscar_auditorias,
    get_detalle_at_info
)
from modules.REPORTES.routes import reportes_bp
from modules.ACUM.routes import acum_bp 
from modules.API.routes import api_bp
from modules.SIAD.routes import siad_bp
from modules.SEOBCON.routes import seobcon_bp
from modules.ARA.routes import ara_bp
from modules.INVE.routes import inve_bp
from modules.ASIM.routes import asim_bp
from modules.PRDI.routes import prdi_bp

# actualizar_estado_procedimiento_inve,
# --- 2. Apuntar a la carpeta del Instant Client ---
# Obtenemos la ruta absoluta a la carpeta del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))
# Construimos la ruta a nuestra carpeta 'instantclient_23_8'
client_lib_dir = os.path.join(basedir, 'oracle_client', 'instantclient_23_8')

# --- 3. Crear la aplicación Flask ---
app = Flask(__name__)
app.secret_key = "mi-clave-secreta-para-flash" # Puedes poner cualquier texto
app.register_blueprint(reportes_bp)
app.register_blueprint(acum_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(siad_bp)
app.register_blueprint(seobcon_bp)
app.register_blueprint(ara_bp)
app.register_blueprint(inve_bp)
app.register_blueprint(asim_bp)
app.register_blueprint(prdi_bp)

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

# --- RUTA DEL BUSCADOR DE ATS (GENÉRICO) ---
@app.route('/buscador-ats/<string:tipo_origen>', methods=['GET', 'POST'])
def pagina_buscador_ats(tipo_origen):

    lista_de_resultados = None
    filtros_aplicados = {} 

    if request.method == 'POST':
        # 1. Obtener datos
        periodo = request.form.get('periodo')
        nro_at = request.form.get('numero_at')
        uce_id = request.form.get('uce')
        servicio_id = request.form.get('servicio')
        nro_programa = request.form.get('n_programa')
        num_referencia = request.form.get('num_referencia')
        num_acfi = request.form.get('acfi_id')

        # 2. Validación mejorada
        # Caso especial: Si busca SOLO por acfi_id, no requiere periodo
        if num_acfi and num_acfi.strip():
            # Búsqueda directa por ACFI_ID (no necesita periodo ni otros campos)
            print(f"Capa 2: Búsqueda directa por ACFI_ID: {num_acfi}")
            lista_de_resultados = buscar_auditorias(
                periodo=None, 
                nro_at=None, 
                uce_id=None,
                servicio_id=None, 
                nro_programa=None,
                tipo_origen=tipo_origen,
                num_referencia=None, 
                num_acfi=num_acfi
            )
        else:
            # Búsqueda normal: requiere periodo + al menos otro criterio
            if not periodo or not periodo.strip():
                flash("El campo 'Período de Planificación' es obligatorio (a menos que busque directamente por ACFI_ID).", 'error')
                lista_de_resultados = None

            elif not nro_at and not uce_id and not servicio_id and not nro_programa and not num_referencia:
                flash("Además del Período, debe ingresar al menos otro criterio de búsqueda.", 'error')
                lista_de_resultados = None

            else:
                # 3. Llamar a la Capa 3
                print(f"Capa 2: Iniciando búsqueda para '{tipo_origen}' con filtros: periodo={periodo}, nro_at={nro_at}, uce_id={uce_id}, servicio_id={servicio_id}, nro_programa={nro_programa}, num_referencia={num_referencia}")

                lista_de_resultados = buscar_auditorias(
                    periodo=periodo, 
                    nro_at=nro_at, 
                    uce_id=uce_id,
                    servicio_id=servicio_id, 
                    nro_programa=nro_programa,
                    tipo_origen=tipo_origen,
                    num_referencia=num_referencia, 
                    num_acfi=None
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
        return redirect(url_for('acum_bp.pagina_detalle_at_acum', acfi_id=acfi_id))

    elif tipo_origen == 'AUDITORIA_SIMPLIFICADA':
        return redirect(url_for('asim_bp.pagina_detalle_at_asim', acfi_id=acfi_id))    

    elif tipo_origen == 'ATENCION_REFERENCIA':
        print(f"Capa 2: Redirigiendo a página de detalle ARA para ACFI_ID: {acfi_id}")
        return redirect(url_for('ara_bp.pagina_detalle_at_ara', acfi_id=acfi_id))

    elif tipo_origen == 'INVESTIGACION':
        return redirect(url_for('inve.pagina_detalle_at_inve', acfi_id=acfi_id))

    elif tipo_origen == 'AUDITORIA_FINANCIERA':
        # (En el futuro, aquí llamarías a otra función)
        # lista_actividades = get_actividades_financiera(acfi_id)
        # template_a_renderizar = 'detalle_at_financiera.html' 
        flash(f"Página de detalle para '{tipo_origen}' aún no implementada.", 'error')
        return redirect(request.referrer or url_for('pagina_principal'))

    else:
        flash(f"Error: No hay una página de detalle definida para el tipo '{tipo_origen}'.", 'error')
        return redirect(request.referrer or url_for('pagina_principal'))


# --- API ENDPOINT PARA REABRIR EJECUCIÓN ---
@app.route('/api/reabrir-ejecucion', methods=['POST'])
def api_reabrir_ejecucion():
    data = request.get_json()
    acfi_id = data.get('acfi_id')

    if not acfi_id:
        return jsonify({"success": False, "message": "ACFI_ID es requerido."}), 400

    resultado = reabrir_at_ejecucion(acfi_id)
    return jsonify(resultado)

# ================================================================
# --- 6. Iniciar la aplicación ---
# ================================================================
if __name__ == '__main__':
    # Antes de arrancar el servidor web, probamos la conexión
    probar_conexion_oracle()
    
    print("\nIniciando servidor web Flask...")
    app.run(debug=True)

