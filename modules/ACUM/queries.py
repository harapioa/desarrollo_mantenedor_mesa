# modules/ASIM/queries.py
import oracledb

from ..COMMON.db import get_db_connection

# --- FUNCIÓN MAESTRA (Coordinador) ---
def get_detalle_at_acum(acfi_id):
    # 1. Obtenemos SOLO la info de cabecera
    info = get_info_cabecera_acum(acfi_id)
    
    # Si no hay info, retornamos None para que el router redirija
    if not info:
        return None
        
    # 2. Obtenemos las actividades por separado
    actividades = get_actividades_acum(acfi_id)
    
    # 3. Retornamos la estructura limpia
    return {
        "info": info,
        "actividades": actividades
    }

# --- FUNCIÓN 1: CABECERA ---
def get_info_cabecera_acum(acfi_id):
    # 1. Query General (Base)
    sql_general = """
        WITH QueryNumerada AS (
            SELECT
                ASTR.ACFI_ID, 
                UCE.unce_nombre AS UCE, 
                PRGE.PRGE_NUMERO AS N_PROGRAMA,
                ENSV.ENSV_NOMBRE AS SERVICIO, 
                ASTR.ASTR_MATERIA AS MATERIA, 
                ASTR.ASTR_ESTADO AS ESTADO, 
                INAC.INAU_NUMERO AS N_INFORME,
                'AUDITORIA_CUMPLIMIENTO' as ASTR_TIPO_ORIGEN, 
                PRGE.PRGE_NOMBRE_ACFI AS TIPO_PROGRAMA,
                CASE WHEN INAC.INAU_ESTADO = 'VBP' THEN 'Si' ELSE 'No' END AS PUBLICADO,
                'No' AS REEVALUACION,
                ASTR.UNCE_ID AS UCE_ID,
                ROW_NUMBER() OVER (PARTITION BY ASTR.ACFI_ID ORDER BY ASTR.ASTR_ID DESC) AS RN
            FROM OWN_ASTR.ASTR_ASIGNACION_TRABAJO ASTR
            LEFT JOIN own_glob.glob_unidades_control_ext UCE ON ASTR.unce_id = UCE.unce_id
            LEFT JOIN own_glob.glob_entidades_servicios ENSV ON ASTR.ENSV_ID = ENSV.ensv_id
            LEFT JOIN own_astr.astr_programa_general PRGE ON ASTR.prge_id = PRGE.prge_id
            LEFT JOIN own_bifa.bifa_informe_actividad INAC ON ASTR.ACFI_ID = INAC.ACFI_ID
            WHERE ASTR.ACFI_ID = :id
        )
        SELECT * FROM QueryNumerada WHERE RN = 1
    """

    # 2. Query Fases (Ejecución vs Informe Final)
    sql_fases = """
        SELECT ASTR_TIPO, ASTR_ESTADO 
        FROM own_astr.astr_asignacion_trabajo 
        WHERE ACFI_ID = :id 
          AND ASTR_TIPO IN ('EJECUCION', 'INFORME_FINAL')
    """
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # A. Ejecutar General
                cursor.execute(sql_general, id=acfi_id)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    cursor.rowfactory = lambda *args: dict(zip(columns, args))
                    info = cursor.fetchone()
                else:
                    return None
                
                if not info: return None

                # B. Ejecutar Fases
                cursor.execute(sql_fases, id=acfi_id)
                cursor.rowfactory = None # Reset para leer tuplas
                
                # Valores por defecto
                info['ESTADO_EJECUCION'] = 'NO_INICIADA'
                info['ESTADO_FINAL'] = 'NO_INICIADA'

                for row in cursor:
                    tipo = row[0]
                    estado = row[1]
                    if tipo == 'EJECUCION':
                        info['ESTADO_EJECUCION'] = estado
                    elif tipo == 'INFORME_FINAL':
                        info['ESTADO_FINAL'] = estado
                
                return info

    except oracledb.DatabaseError as e:
        print(f"Error en get_info_cabecera_acum: {e}")
        return None

# --- FUNCIÓN 2: ACTIVIDADES ---
def get_actividades_acum(acfi_id):
    if not acfi_id: return {}

    query = """
        SELECT 
            aupr.PROC_ID, 
            REGEXP_SUBSTR(proc.texto_ayuda, '<b>PROCEDIMIENTO ([0-9\.]+) - ', 1, 1, NULL, 1) AS ITEM_NUMERO,
            aupr.AUPR_ESTADO
        FROM own_ejec.ejec_audit_proc aupr
        INNER JOIN own_ejec.ejec_procedimiento proc ON proc.proc_id = aupr.proc_id
        WHERE aupr.LIAU_ID = :acfi_id_bv
    """
    
    status_map = {}
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, acfi_id_bv=acfi_id)
                for fila in cursor.fetchall():
                    # fila[0]=ID, fila[1]=Numero(1.1), fila[2]=Estado
                    if fila[1]:
                        status_map[fila[1]] = {"id": fila[0], "estado": fila[2]}
        return status_map
    except Exception as e:
        print(f"Error en get_actividades_acum: {e}")
        return {}
    
def gestionar_fase_acum(acfi_id, fase, accion):
    """
    fase: 'EJECUCION' o 'INFORME_FINAL'
    accion: 'CERRAR' o 'REABRIR'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Validar estados actuales
        cursor.execute("""
            SELECT ASTR_TIPO, ASTR_ESTADO 
            FROM own_astr.astr_asignacion_trabajo 
            WHERE ACFI_ID = :id AND ASTR_TIPO IN ('EJECUCION', 'INFORME_FINAL')
        """, id=acfi_id)
        
        estados = {row[0]: row[1] for row in cursor.fetchall()}
        est_ejec = estados.get('EJECUCION', 'NO_EXISTE')
        est_final = estados.get('INFORME_FINAL', 'NO_EXISTE')

        nuevo_estado = ''

        # --- REGLAS DE NEGOCIO ---
        if fase == 'EJECUCION':
            if accion == 'REABRIR':
                if est_final == 'CERRADA':
                    return {"success": False, "message": "No se puede reabrir Ejecución si la Fase Final está cerrada."}
                nuevo_estado = 'EN_PROCESO'
            elif accion == 'CERRAR':
                nuevo_estado = 'CERRADA'

        elif fase == 'INFORME_FINAL':
            if accion == 'REABRIR':
                nuevo_estado = 'EN_PROCESO'
            elif accion == 'CERRAR':
                if est_ejec != 'CERRADA':
                    return {"success": False, "message": "No se puede cerrar Informe Final si Ejecución sigue abierta."}
                nuevo_estado = 'CERRADA'

        # Ejecutar Update
        sql_update = """
            UPDATE own_astr.astr_asignacion_trabajo
            SET ASTR_ESTADO = :estado
            WHERE ACFI_ID = :id AND ASTR_TIPO = :tipo
        """
        cursor.execute(sql_update, estado=nuevo_estado, id=acfi_id, tipo=fase)
        conn.commit()
        
        return {"success": True, "message": f"Fase {fase} {accion} correctamente."}

    except Exception as e:
        conn.rollback()
        print(f"Error gestionar_fase_acum: {e}")
        return {"success": False, "message": str(e)}
    finally:
        cursor.close()
        conn.close()

def actualizar_procedimiento_acum(acfi_id, proc_id, nuevo_estado):
    """
    Actualiza el estado (ABIERTO/CERRADO) de un procedimiento específico (candado).
    """
    sql = """
        UPDATE own_ejec.ejec_audit_proc
        SET AUPR_ESTADO = :estado
        WHERE LIAU_ID = :acfi_id 
          AND PROC_ID = :proc_id
    """
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, estado=nuevo_estado, acfi_id=acfi_id, proc_id=proc_id)
                conn.commit()
                return {"success": True, "message": "Procedimiento actualizado."}
    except Exception as e:
        print(f"Error actualizar_procedimiento_acum: {e}")
        return {"success": False, "message": str(e)}