import oracledb
import sys
import os
import io
import pandas as pd
from .report_queries import (
    QUERY_CASOS_PD_ENTIDAD, QUERY_PRODUCTOS_NO_VINCULADOS, QUERY_PD_FECHAS_RESOLUCIONES,
    QUERY_ACTOS_TOTALES_SIAD, QUERY_CONTRAPARTES_SIAD )

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import config

def generar_reporte_excel(report_id):
    """
    Genera un archivo Excel en memoria basado en un report_id.
    Devuelve un objeto BytesIO que contiene el archivo .xlsx.
    """
    
    # 1. Mapeamos el ID del botón a la query real
    queries_map = {
        'casos_pd_entidad': QUERY_CASOS_PD_ENTIDAD,
        'productos_no_vinculados': QUERY_PRODUCTOS_NO_VINCULADOS,
        'pd_fechas_resoluciones': QUERY_PD_FECHAS_RESOLUCIONES,
        'actos_totales_siad': QUERY_ACTOS_TOTALES_SIAD,
        'reporte_usuarios_externos_SIAD': QUERY_CONTRAPARTES_SIAD
    }
    
    sql_query = queries_map.get(report_id)
    
    if not sql_query:
        print(f"Error en Capa 3: No se encontró query para el report_id: {report_id}")
        return None

    try:
        # --- INICIO DE LA CORRECCIÓN ---
        
        # 2. Conectamos a Oracle (el método estándar que ya usamos)
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            
            # ¡La magia de Pandas!
            # 3. Ejecuta la query y carga los resultados DIRECTAMENTE en un DataFrame
            #    Ahora pasamos el objeto 'connection' en lugar de un string.
            print(f"Capa 3: Ejecutando query para reporte '{report_id}'...")
            df = pd.read_sql(sql_query, con=connection)
            print(f"Capa 3: Query exitosa, {len(df)} filas obtenidas.")
            
        # --- FIN DE LA CORRECCIÓN ---

        # 4. Creamos un "archivo" Excel en la memoria RAM
        output_stream = io.BytesIO()
        
        # 5. Escribimos el DataFrame en ese archivo de memoria
        with pd.ExcelWriter(output_stream, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
        
        # 6. Devolvemos el "archivo" en memoria
        print("Capa 3: Archivo Excel generado en memoria.")
        return output_stream

    except oracledb.DatabaseError as e:
        print(f"Error de Base de Datos en Capa 3 (generar_reporte): {e}")
        return None
    except Exception as e:
        print(f"Error inesperado en Capa 3 (generar_reporte): {e}")
        return None
