# modules/INVE/queries.py
import oracledb
import sys
import os
from ..COMMON.db import get_db_connection

# Ajusta ruta para config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
try:
    import config
except ImportError:
    import config

def get_detalle_at_inve(acfi_id):
    print(f"Capa 3 (INVE): Buscando datos para {acfi_id}")
    
    info = get_info_cabecera_inve(acfi_id)
    actividades = get_actividades_inve(acfi_id)
    
    if not info:
        print("Capa 3 ERROR: No se encontró cabecera INVE.")
        return None
        
    return {
        'info': info,
        'actividades': actividades
    }

def get_info_cabecera_inve(acfi_id):
    """
    Obtiene info general y, CRUCIALMENTE, los estados separados de EJECUCION e INFORME_FINAL.
    """
    # 1. Obtenemos datos generales (Tu query original simplificada o mantenida)
    # ... (Usa tu query actual de cabecera aquí para traer UCE, SERVICIO, ETC) ...
    # Voy a resumir la parte de los estados específicos que es lo nuevo:
    
    sql_general = """
        WITH QueryNumerada AS (
            SELECT
                ASTR.ACFI_ID, 
                UCE.unce_nombre AS UCE, 
                PRGE.PRGE_NUMERO AS N_PROGRAMA,
                ENSV.ENSV_NOMBRE AS SERVICIO, 
                ASTR.ASTR_TIPO_ORIGEN,
                PRGE.PRGE_NOMBRE_ACFI AS TIPO_PROGRAMA,
                ASTR.UNCE_ID AS UCE_ID,
                -- ESTADO GLOBAL (Del INVE padre)
                (SELECT INVE_ESTADO FROM own_inve3.inve3_invest_especial WHERE INVE_ID = ASTR.ACFI_ID) as INVE_ESTADO,
                ROW_NUMBER() OVER (PARTITION BY ASTR.ACFI_ID ORDER BY ASTR.ASTR_ID DESC) AS RN
            FROM OWN_ASTR.ASTR_ASIGNACION_TRABAJO ASTR
            LEFT JOIN own_glob.glob_unidades_control_ext UCE ON ASTR.unce_id = UCE.unce_id
            LEFT JOIN own_glob.glob_entidades_servicios ENSV ON ASTR.ENSV_ID = ENSV.ensv_id
            LEFT JOIN own_astr.astr_programa_general PRGE ON ASTR.prge_id = PRGE.prge_id
            WHERE ASTR.ACFI_ID = :id
        )
        SELECT * FROM QueryNumerada WHERE RN = 1
    """

    # 2. Query para obtener los estados de las fases ASTR hijas
    sql_fases = """
        SELECT ASTR_TIPO, ASTR_ESTADO 
        FROM own_astr.astr_asignacion_trabajo 
        WHERE ACFI_ID = :id 
          AND ASTR_TIPO IN ('EJECUCION', 'INFORME_FINAL')
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # A. Datos Generales
                cursor.execute(sql_general, id=acfi_id)
                columns = [col[0] for col in cursor.description]
                cursor.rowfactory = lambda *args: dict(zip(columns, args))
                info = cursor.fetchone()

                if not info: return None

                # B. Estados de Fases (Esto es lo nuevo y vital)
                cursor.execute(sql_fases, id=acfi_id)
                # Reseteamos rowfactory para leer tuplas simples
                cursor.rowfactory = None 
                
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
    except Exception as e:
        print(f"Error en get_info_cabecera_inve: {e}")
        return None

# --- FUNCIONES PARA INVESTIGACIÓN ESPECIAL (INVE) ---

def get_actividades_inve(acfi_id):
    """
    Obtiene un MAPA de los procedimientos INVE existentes para este ACFI_ID (INVE_ID).
    Intenta mapear PROC_ID a PROC_GRUPO ('1.1', '2.3', etc.) basado en imagen.
    """
    if not acfi_id: return {}

    # Query para buscar estados en la tabla INVE
    # ASUNCIÓN: Tabla own_inve3.inve3_audit_proc con INVE_ID, PROC_ID, IAPR_ESTADO
    # ASUNCIÓN: Tabla own_ejec.ejec_procedimiento tiene PROC_ID y texto_ayuda para obtener 'X.Y'
    query = """
        SELECT
            iapr.PROC_ID,
            iapr.IAPR_ESTADO,
            REGEXP_SUBSTR(
                proc.PROC_TEXTO_AYUDA,
                '<b>PROCEDIMIENTO (\d+\.\d+)', 1, 1, NULL, 1
            ) AS PROC_GRUPO_NUM
        FROM own_inve3.inve3_audit_proc iapr
        INNER JOIN own_inve3.inve3_procedimiento proc ON proc.proc_id = iapr.PROC_ID
        WHERE iapr.INVE_ID = :acfi_id_bv
    """
    status_map = {}
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, acfi_id_bv=acfi_id)
                for fila in cursor.fetchall():
                    proc_id_num = fila[0]
                    estado = fila[1]
                    item_numero = fila[2] # '1.1', '1.8', '2.1', etc.

                    if item_numero: # Solo añadir si pudimos extraer el número
                        status_map[item_numero] = {
                            "id": proc_id_num,
                            "estado": estado
                        }
                    else:
                         print(f"Advertencia INVE: No se pudo extraer PROC_GRUPO_NUM para PROC_ID {proc_id_num}")

        print(f"Capa 3: Mapa de estados (INVE) creado con {len(status_map)} items.")
        return status_map
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_actividades_inve): {e}")
        return {}
    except Exception as e:
         print(f"Error general en Capa 3 (get_actividades_inve): {e}")
         return {}


def actualizar_estado_procedimiento_inve(acfi_id, proc_id, nuevo_estado):
    """Actualiza el estado de UN procedimiento INVE."""
    print(acfi_id, proc_id, nuevo_estado)
    if nuevo_estado not in ('ABIERTO', 'CERRADO'): return False
    query = """
        UPDATE own_inve3.inve3_audit_proc
        SET IAPR_ESTADO = :estado_bv
        WHERE INVE_ID = :acfi_id_bv AND PROC_ID = :proc_id_bv
    """
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {"estado_bv": nuevo_estado, "acfi_id_bv": acfi_id, "proc_id_bv": proc_id})
                connection.commit()
                print(f"Capa 3: Procedimiento INVE {proc_id} para AT {acfi_id} actualizado a {nuevo_estado}.")
                return True
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (actualizar_estado_procedimiento_inve): {e}")
        return False

def actualizar_estado_at_completa_inve(acfi_id, accion):
    """Actualiza la AT completa (ASTR y INVE) en una transacción."""
    if accion == 'reabrir':
        nuevo_estado_astr = 'EN_PROCESO'
        nuevo_estado_inve = 'EN_CIERRE' # ¡OJO! Estado diferente
    elif accion == 'cerrar':
        nuevo_estado_astr = 'CERRADA'
        nuevo_estado_inve = 'CERRADA'
    else: return False

    query_astr = "UPDATE own_astr.astr_asignacion_trabajo SET astr_estado = :estado_astr WHERE astr_tipo = 'INFORME_FINAL' AND acfi_id = :acfi_id_bv" # Añadido filtro astr_tipo
    query_inve = "UPDATE own_inve3.inve3_invest_especial SET INVE_ESTADO = :estado_inve WHERE INVE_ID = :acfi_id_bv"

    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_astr, {"estado_astr": nuevo_estado_astr, "acfi_id_bv": acfi_id})
                cursor.execute(query_inve, {"estado_inve": nuevo_estado_inve, "acfi_id_bv": acfi_id})
                connection.commit()
                print(f"Capa 3: Éxito. AT Completa INVE {acfi_id} actualizada a {accion}.")
                return True
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (actualizar_estado_at_completa_inve): {e}")
        return False

def reabrir_at_inve_ejecucion(acfi_id):
    """
    Reabre la AT de EJECUCION INVE (tipo = 'EJECUCION').
    """
    query = """
        UPDATE own_astr.astr_asignacion_trabajo astr
        SET astr.astr_estado = 'EN_PROCESO'
        WHERE astr.astr_tipo = 'EJECUCION' 
          AND astr.acfi_id = :acfi_id
    """
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {"acfi_id": acfi_id})
            connection.commit()
        print(f"Capa 3: AT INVE EJECUCION {acfi_id} reabierta correctamente.")
        return {"success": True, "message": "AT INVE de Ejecución reabierta correctamente."}
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (reabrir_at_inve_ejecucion): {e}")
        return {"success": False, "message": f"Error al reabrir AT INVE de Ejecución: {e}"}

def cerrar_at_inve_ejecucion(acfi_id):
    """
    Cierra la AT de EJECUCION INVE (tipo = 'EJECUCION').
    """
    query = """
        UPDATE own_astr.astr_asignacion_trabajo astr
        SET astr.astr_estado = 'CERRADA'
        WHERE astr.astr_tipo = 'EJECUCION' 
          AND astr.acfi_id = :acfi_id
    """
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {"acfi_id": acfi_id})
            connection.commit()
        print(f"Capa 3: AT INVE EJECUCION {acfi_id} cerrada correctamente.")
        return {"success": True, "message": "AT INVE de Ejecución cerrada correctamente."}
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (cerrar_at_inve_ejecucion): {e}")
        return {"success": False, "message": f"Error al cerrar AT INVE de Ejecución: {e}"}

def reabrir_at_inve_inicio(acfi_id):
    """
    Reabre la AT INVE de INICIO (ASTR_TIPO = 'INICIO').
    Actualiza ASTR_ESTADO a 'EN_PROCESO'.
    """
    query = """
        UPDATE own_astr.astr_asignacion_trabajo astr
        SET astr.astr_estado = 'EN_PROCESO'
        WHERE astr.astr_tipo = 'EJECUCION' 
          AND astr.acfi_id = :acfi_id
    """
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {"acfi_id": acfi_id})
            connection.commit()
        print(f"Capa 3: AT INVE INICIO {acfi_id} reabierta correctamente.")
        return {"success": True, "message": "AT INVE de Inicio reabierta correctamente."}
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (reabrir_at_inve_inicio): {e}")
        return {"success": False, "message": f"Error al reabrir AT INVE de Inicio: {e}"}

def cerrar_at_inve_inicio(acfi_id):
    """
    Cierra la AT INVE de INICIO (ASTR_TIPO = 'INICIO').
    Actualiza ASTR_ESTADO a 'CERRADA'.
    """
    query = """
        UPDATE own_astr.astr_asignacion_trabajo astr
        SET astr.astr_estado = 'CERRADA'
        WHERE astr.astr_tipo = 'EJECUCION' 
          AND astr.acfi_id = :acfi_id
    """
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {"acfi_id": acfi_id})
            connection.commit()
        print(f"Capa 3: AT INVE INICIO {acfi_id} cerrada correctamente.")
        return {"success": True, "message": "AT INVE de Inicio cerrada correctamente."}
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (cerrar_at_inve_inicio): {e}")
        return {"success": False, "message": f"Error al cerrar AT INVE de Inicio: {e}"}

def actualizar_procedimiento_inve(acfi_id, proc_nombre, nuevo_estado):
    """
    Actualiza el estado de un procedimiento en INVE.
    proc_nombre: '1.1', '1.2', '1.3', etc.
    nuevo_estado: 'ABIERTO' o 'CERRADO'
    """
    
    print("\n=== INICIO: actualizar_procedimiento_inve ===")
    print(f"1. Parámetros recibidos:")
    print(f"   - acfi_id: {acfi_id}")
    print(f"   - proc_nombre: {proc_nombre}")
    print(f"   - nuevo_estado: {nuevo_estado}")
    
    # Validación básica
    if not acfi_id or not proc_nombre or not nuevo_estado:
        print("2. ERROR: Parámetros vacíos detectados")
        return {"success": False, "message": "Parámetros incompletos."}
    
    print("2. Parámetros validados correctamente")
    
    # Mapear el nombre del procedimiento (1.1, 1.2, etc.) al texto de búsqueda
    proc_patron = f"%PROCEDIMIENTO {proc_nombre}%"
    print(f"3. Patrón de búsqueda generado: {proc_patron}")
    
    query = """
        UPDATE own_inve3.inve3_audit_proc aupr
        SET aupr.IAPR_ESTADO = :nuevo_estado
        WHERE aupr.INVE_ID = :acfi_id
          AND aupr.PROC_ID = (select proc.proc_id
        from own_inve3.inve3_procedimiento proc
        where proc.PROC_TEXTO_AYUDA like '%PROCEDIMIENTO ' || :proc_nombre || '%'
          )
    """
    
    print(f"4. Query preparada: {query}")
    
    try:
        print("5. Iniciando conexión a Oracle...")
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            print("6. Conexión establecida")
            
            with connection.cursor() as cursor:
                print("7. Cursor creado")
                
                print(f"8. Ejecutando query con parámetros:")
                print(f"   - nuevo_estado: {nuevo_estado}")
                print(f"   - acfi_id: {acfi_id}")
                print(f"   - proc_patron: {proc_nombre}")
                
                cursor.execute(query, {
                    "nuevo_estado": nuevo_estado,
                    "acfi_id": acfi_id,
                    "proc_nombre": proc_nombre
                })
                
                print(f"9. Query ejecutada. Filas afectadas: {cursor.rowcount}")
                
            print("10. Realizando commit...")
            connection.commit()
            print("11. Commit realizado")
        
        print(f"12. Capa 3: Procedimiento {proc_nombre} de INVE {acfi_id} actualizado a {nuevo_estado}.")
        resultado = {"success": True, "message": f"Procedimiento {proc_nombre} actualizado a {nuevo_estado}."}
        print(f"13. Resultado final: {resultado}")
        print("=== FIN: actualizar_procedimiento_inve (EXITOSO) ===\n")
        return resultado
    
    except oracledb.DatabaseError as e:
        print(f"ERROR en paso de conexión/ejecución: {e}")
        print(f"Tipo de error: {type(e)}")
        print("=== FIN: actualizar_procedimiento_inve (ERROR) ===\n")
        return {"success": False, "message": f"Error al actualizar procedimiento: {e}"}
    
    except Exception as e:
        print(f"ERROR GENERAL NO ESPERADO: {e}")
        print(f"Tipo de error: {type(e)}")
        print("=== FIN: actualizar_procedimiento_inve (ERROR GENERAL) ===\n")
        return {"success": False, "message": f"Error inesperado: {e}"}

def gestionar_fase_inve(acfi_id, fase, accion):
    """
    Maneja la lógica de negocio para cerrar/reabrir fases.
    fase: 'EJECUCION' o 'INFORME_FINAL'
    accion: 'CERRAR' o 'REABRIR'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Verificar estados actuales antes de actuar (Reglas de Negocio)
        cursor.execute("""
            SELECT ASTR_TIPO, ASTR_ESTADO 
            FROM own_astr.astr_asignacion_trabajo 
            WHERE ACFI_ID = :id AND ASTR_TIPO IN ('EJECUCION', 'INFORME_FINAL')
        """, id=acfi_id)
        
        estados = {row[0]: row[1] for row in cursor.fetchall()}
        est_ejec = estados.get('EJECUCION', 'NO_EXISTE')
        est_final = estados.get('INFORME_FINAL', 'NO_EXISTE')

        # --- LÓGICA DE EJECUCIÓN (A1) ---
        if fase == 'EJECUCION':
            if accion == 'REABRIR':
                # REGLA: No se puede reabrir Ejecución si Final está CERRADA
                if est_final == 'CERRADA':
                    return {"success": False, "message": "No se puede reabrir Ejecución porque la fase Final está cerrada."}
                nuevo_estado = 'EN_PROCESO'

            elif accion == 'CERRAR':
                nuevo_estado = 'CERRADA'

        # --- LÓGICA DE INFORME FINAL (A2) ---
        elif fase == 'INFORME_FINAL':
            if accion == 'REABRIR':
                nuevo_estado = 'EN_PROCESO'
                # Al reabrir final, también actualizamos el estado global INVE a EN_PROCESO (opcional, según tu regla)
                
            elif accion == 'CERRAR':
                # REGLA: Para cerrar final, ejecución debe estar cerrada (usualmente)
                if est_ejec != 'CERRADA':
                    return {"success": False, "message": "No se puede cerrar Informe Final si Ejecución sigue abierta."}
                nuevo_estado = 'CERRADA'

        # 2. Ejecutar actualización
        sql_update = """
            UPDATE own_astr.astr_asignacion_trabajo
            SET ASTR_ESTADO = :estado
            WHERE ACFI_ID = :id AND ASTR_TIPO = :tipo
        """
        cursor.execute(sql_update, estado=nuevo_estado, id=acfi_id, tipo=fase)

        # 3. Si cerramos INFORME_FINAL, cerramos la INVE padre
        if fase == 'INFORME_FINAL' and accion == 'CERRAR':
            cursor.execute("UPDATE own_inve3.inve3_invest_especial SET INVE_ESTADO = 'CERRADA' WHERE INVE_ID = :id", id=acfi_id)
        
        # 4. Si reabrimos INFORME_FINAL, la INVE padre vuelve a EN_CIERRE o EN_PROCESO
        if fase == 'INFORME_FINAL' and accion == 'REABRIR':
            cursor.execute("UPDATE own_inve3.inve3_invest_especial SET INVE_ESTADO = 'EN_PROCESO' WHERE INVE_ID = :id", id=acfi_id)

        conn.commit()
        return {"success": True, "message": f"Fase {fase} {accion} correctamente."}

    except Exception as e:
        conn.rollback()
        print(f"Error gestionar_fase_inve: {e}")
        return {"success": False, "message": str(e)}
    finally:
        cursor.close()
        conn.close()