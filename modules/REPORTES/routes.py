# Archivo: modules/REPORTES/routes.py
from flask import Blueprint, render_template, jsonify, send_file
import datetime
import re

from .queries import generar_reporte_excel

# Creamos el Blueprint. 
# El nombre 'reportes_bp' es como lo identificará Flask internamente.
reportes_bp = Blueprint('reportes_bp', __name__)

# Definimos la ruta. 
# Si en el futuro configuras un url_prefix='/reportes', aquí solo pondrías '/'
@reportes_bp.route('/reportes')
def pagina_reportes():
    print("Capa 2: Navegando a la página de Reportes.")
    # ruta: 'REPORTES/reportes.html'
    return render_template('REPORTES/reportes.html')

# --- API ENDPOINT PARA DESCARGAR REPORTES EN EXCEL ---
@reportes_bp.route('/api/download-report/<string:report_id>')
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
        'actos_totales_siad': 'Reporte actos totales casos siad v1.4',
        'reporte_usuarios_externos_SIAD': 'Reporte usuarios externos SIAD v1.0'
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
