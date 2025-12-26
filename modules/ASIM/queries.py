# modules/ASIM/queries.py
import oracledb
import sys
import os

# Ajusta ruta para config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
try:
    import config
except ImportError:
    import config

def get_db_connection():
    return oracledb.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        dsn=config.DB_DSN
    )

def get_detalle_at_asim(acfi_id):
    print(f"Capa 3 (ASIM): Buscando datos para {acfi_id}")
    
    info = get_info_cabecera_asim(acfi_id)
    # Si no hay cabecera, no tiene sentido buscar actividades
    if not info:
        print("Capa 3 ERROR: No se encontró cabecera ASIM.")
        return None

    actividades = get_actividades_asim(acfi_id)
    
    return {
        'info': info,
        'actividades': actividades
    }

def get_info_cabecera_asim(acfi_id):
    query = """
        WITH QueryNumerada AS (
            SELECT
                ASTR.ACFI_ID, UCE.unce_nombre AS UCE, 
                PRGE.PRGE_NUMERO AS N_PROGRAMA,
                ENSV.ENSV_NOMBRE AS SERVICIO, 
                ASTR.ASTR_MATERIA AS MATERIA, 
                ASTR.ASTR_ESTADO AS ESTADO, 
                INAC.INAU_NUMERO AS N_INFORME,
                ASTR.ASTR_TIPO_ORIGEN, 
                PRGE.PRGE_NOMBRE_ACFI AS TIPO_PROGRAMA,
                CASE 
                    WHEN INAC.INAU_ESTADO = 'VBP' THEN 'Si'
                    ELSE 'No'
                END AS PUBLICADO,
                'No' AS REEVALUACION,
                ASTR.UNCE_ID AS UCE_ID,
                ROW_NUMBER() OVER (
                    PARTITION BY ASTR.ACFI_ID 
                    ORDER BY ASTR.ASTR_ID DESC
                ) AS RN
            FROM
                OWN_ASTR.ASTR_ASIGNACION_TRABAJO ASTR
            LEFT JOIN own_glob.glob_unidades_control_ext UCE ON ASTR.unce_id = UCE.unce_id
            LEFT JOIN own_glob.glob_entidades_servicios ENSV ON ASTR.ENSV_ID = ENSV.ensv_id
            LEFT JOIN own_astr.astr_programa_general PRGE ON ASTR.prge_id = PRGE.prge_id
            LEFT JOIN own_bifa.bifa_informe_actividad INAC ON ASTR.ACFI_ID = INAC.ACFI_ID
            
            WHERE ASTR.ACFI_ID = :acfi_id_bv
        )
        SELECT * FROM QueryNumerada WHERE RN = 1
    """
    
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, acfi_id_bv=acfi_id)
                
                # --- MAGIA AUTOMÁTICA ---
                # Esto convierte las columnas del SQL directamente a un diccionario.
                # Así "ASTR_TIPO_ORIGEN" del SQL se convierte en la clave del dict.
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    cursor.rowfactory = lambda *args: dict(zip(columns, args))
                    
                    fila = cursor.fetchone()
                    
                    if not fila:
                        print(f"Capa 3: No se encontró información para ACFI_ID {acfi_id}.")
                        return None
                        
                    # Retornamos SOLO el diccionario de la fila, sin envolverlo en nada más.
                    return fila
                    
        return None

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_detalle_at_info): {e}")
        return None

def get_actividades_asim(acfi_id):
    """
    Obtiene un MAPA de los procedimientos que SÍ existen para una
    AUDITORIA_SIMPLIFICADA.
    Devuelve: {'1.1': {'id': 31, 'estado': 'CERRADO'}, ...}
    """
    
    if not acfi_id:
        print("Capa 3: No se proporcionó ACFI_ID para Simplificada.")
        return {}

    # Consulta similar a Cumplimiento, pero con el 'tipo' correcto
    # ASUNCIÓN: El 'tipo' en ejec_procedimiento es 'AUDITORIA_SIMPLIFICADA'
    #            Ajusta si es necesario.
    query = """
        SELECT 
            aupr.PROC_ID, 
            SUBSTR(
                proc.texto_ayuda, 
                INSTR(proc.texto_ayuda, ' ') + 1
            )AS ITEM_NUMERO,
            aupr.AUPR_ESTADO
        FROM own_ejec.ejec_audit_proc aupr
        INNER JOIN own_ejec.ejec_procedimiento proc
            ON proc.proc_id = aupr.proc_id
        WHERE aupr.LIAU_ID = :acfi_id_bv -- Usando ACFI_ID como LIAU_ID
          AND proc.tipo = 'AUDITORIA_SIMPLIFICADA' -- Filtro por tipo Simplificada
    """
    
    status_map = {}
    
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, acfi_id_bv=acfi_id)
                
                for fila in cursor.fetchall():
                    proc_id = fila[0]
                    item_numero = fila[1] # ej: "1.1"
                    estado = fila[2]      # ej: "CERRADO"
                    
                    if item_numero:
                        status_map[item_numero] = {
                            "id": proc_id,
                            "estado": estado
                        }
        
        print(f"Capa 3: Mapa de estados (Simplificada) creado con {len(status_map)} items.")
        return status_map

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_actividades_simplificada): {e}")
        return {}
