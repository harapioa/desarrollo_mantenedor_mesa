# modules/SEOBCON/queries.py
import oracledb
import sys
import os

# --- CONFIGURACIÓN DE RUTAS ---
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

    
def get_actividades_ara(acfi_id):
    """
    Obtiene un MAPA de los procedimientos ARA existentes para este ACFI_ID (ARA_ID).
    Asume PROC_ID 1 a 7.
    """
    print(f"\n=== INICIO: get_actividades_ara ===")
    print(f"1. Parámetro recibido: acfi_id={acfi_id}")  
    if not acfi_id: return {}

    # Query para buscar estados en la tabla ARA
    # ASUNCIÓN: La tabla tiene columnas ARA_ID, PROC_ID, APAR_ESTADO
    query = """
        SELECT PROC_ID, APAR_ESTADO
        FROM own_ara3.ara3_audit_proc
        WHERE ARA_ID = :acfi_id_bv
          AND PROC_ID BETWEEN 1 AND 7 -- Asumiendo IDs 1 a 7
    """
    status_map = {}
    
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, acfi_id_bv=acfi_id)
                for fila in cursor.fetchall():
                    proc_id_num = fila[0]
                    estado = fila[1]
                    # Construimos la llave como '1.X' (ej: '1.1', '1.2',...)
                    # basado en los IDs 1 a 7
                    item_numero = f"1.{proc_id_num}"
                    status_map[item_numero] = {
                        "id": proc_id_num, # Guardamos el PROC_ID real
                        "estado": estado
                    }
        print("2. Query preparada {query}") 
        print(f"Capa 3: Mapa de estados (ARA) creado con {len(status_map)} items.")
        return status_map
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_actividades_ara): {e}")
        return {}

def actualizar_estado_procedimiento_ara(acfi_id, proc_id, nuevo_estado):
    """Actualiza el estado de UN procedimiento ARA."""
    
    print(f"\n=== INICIO: actualizar_estado_procedimiento_ara ===")
    print(f"1. Parámetros: acfi_id={acfi_id}, proc_id={proc_id}, nuevo_estado={nuevo_estado}")
    
    if nuevo_estado not in ('ABIERTO', 'CERRADO'):
        print(f"2. ERROR: Estado no válido: {nuevo_estado}")
        return {"success": False, "message": f"Estado no válido: {nuevo_estado}"}
    
    query = """
        UPDATE own_ara3.ara3_audit_proc
        SET APAR_ESTADO = :estado_bv
        WHERE ARA_ID = :acfi_id_bv AND PROC_ID = :proc_id_bv
    """
    
    print(f"2. Query preparada")
    
    try:
        print("3. Iniciando conexión a Oracle...")
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            print("4. Conexión establecida")
            
            with connection.cursor() as cursor:
                print("5. Cursor creado")
                
                print(f"6. Ejecutando query con parámetros:")
                print(f"   - estado: {nuevo_estado}")
                print(f"   - acfi_id: {acfi_id}")
                print(f"   - proc_id: {proc_id}")
                
                cursor.execute(query, {
                    "estado_bv": nuevo_estado, 
                    "acfi_id_bv": acfi_id, 
                    "proc_id_bv": proc_id
                })
                
                print(f"7. Query ejecutada. Filas afectadas: {cursor.rowcount}")
                
                connection.commit()
                print("8. Commit realizado")
        
        print(f"9. Capa 3: Procedimiento ARA {proc_id} para AT {acfi_id} actualizado a {nuevo_estado}.")
        resultado = {"success": True, "message": f"Procedimiento 1.{proc_id} actualizado a {nuevo_estado}."}
        print(f"10. Resultado: {resultado}")
        print("=== FIN: actualizar_estado_procedimiento_ara (EXITOSO) ===\n")
        return resultado
        
    except oracledb.DatabaseError as e:
        print(f"ERROR en conexión/ejecución: {e}")
        print("=== FIN: actualizar_estado_procedimiento_ara (ERROR) ===\n")
        return {"success": False, "message": f"Error al actualizar procedimiento: {e}"}
    
    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        print("=== FIN: actualizar_estado_procedimiento_ara (ERROR GENERAL) ===\n")
        return {"success": False, "message": f"Error inesperado: {e}"}

def actualizar_estado_at_completa_ara(acfi_id, accion):
    """
    Actualiza el estado de una AT ARA completa (ASTR y ARA).
    Actualiza ambas tablas en una transacción.
    accion: 'reabrir' o 'cerrar'
    """
    
    print(f"\n=== INICIO: actualizar_estado_at_completa_ara ===")
    print(f"1. Parámetros: acfi_id={acfi_id}, accion={accion}")
    
    if accion == 'reabrir':
        nuevo_estado_astr = 'EN_PROCESO'
        nuevo_estado_ara = 'EN_EJECUCION'
        print(f"2. Acción: REABRIR -> ASTR={nuevo_estado_astr}, ARA={nuevo_estado_ara}")
    elif accion == 'cerrar':
        nuevo_estado_astr = 'CERRADA'
        nuevo_estado_ara = 'CERRADA'
        print(f"2. Acción: CERRAR -> ASTR={nuevo_estado_astr}, ARA={nuevo_estado_ara}")
    else:
        print(f"3. ERROR: Acción no válida: {accion}")
        return False

    query_astr = """
        UPDATE own_astr.astr_asignacion_trabajo 
        SET astr_estado = :estado_astr 
        WHERE astr_tipo = 'EJECUCION' AND acfi_id = :acfi_id_bv
    """
    
    query_ara = """
        UPDATE own_ara3.ara3_atencion_referencia 
        SET ara_estado = :estado_ara 
        WHERE ara_id = :acfi_id_bv
    """

    print(f"3. Query ASTR preparada")
    print(f"4. Query ARA preparada")

    try:
        print("5. Iniciando conexión a Oracle...")
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            print("6. Conexión establecida")
            
            with connection.cursor() as cursor:
                print("7. Cursor creado")
                
                print("8. Ejecutando UPDATE ASTR...")
                cursor.execute(query_astr, {
                    "estado_astr": nuevo_estado_astr, 
                    "acfi_id_bv": acfi_id
                })
                print(f"9. Filas ASTR afectadas: {cursor.rowcount}")
                
                print("10. Ejecutando UPDATE ARA...")
                cursor.execute(query_ara, {
                    "estado_ara": nuevo_estado_ara, 
                    "acfi_id_bv": acfi_id
                })
                print(f"11. Filas ARA afectadas: {cursor.rowcount}")
                
                print("12. Realizando commit...")
                connection.commit()
                print("13. Commit realizado")
                
        print(f"14. Capa 3: Éxito. AT Completa ARA {acfi_id} actualizada a {accion}.")
        print("=== FIN: actualizar_estado_at_completa_ara (EXITOSO) ===\n")
        return True
        
    except oracledb.DatabaseError as e:
        print(f"ERROR en conexión/ejecución: {e}")
        print(f"Tipo de error: {type(e)}")
        print("=== FIN: actualizar_estado_at_completa_ara (ERROR) ===\n")
        return False
    
    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        print(f"Tipo de error: {type(e)}")
        print("=== FIN: actualizar_estado_at_completa_ara (ERROR GENERAL) ===\n")
        return False
    
def get_info_cabecera_ara(acfi_id):
    """
    Obtiene la información de cabecera para un ACFI_ID específico.
    """
    
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
                row = cursor.fetchone()
                if not row:
                    print(f"Capa 3: No se encontró información para ACFI_ID: {acfi_id}")
                    return None
                
                column_names = [desc[0] for desc in cursor.description]
                resultado = dict(zip(column_names, row))
                
                print(f"Capa 3: Información de cabecera obtenida para ACFI_ID: {acfi_id}")
                return resultado
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_detalle_at_info): {e}")
        return None
    
# --- 3. FUNCIÓN MAESTRA (LA QUE LLAMA ROUTES) ---
def get_detalle_at_ara(acfi_id):
    print(f"Capa 3: Buscando datos completos para ARA ID: {acfi_id}")
    
    info = get_info_cabecera_ara(acfi_id)
    actividades = get_actividades_ara(acfi_id)
    
    if not info:
        print("Capa 3 ERROR: No se encontró cabecera (info).")
        return None
        
    return {
        'info': info,
        'actividades': actividades
    }

def cambiar_servicio_at(acfi_id, nuevo_servicio_id, nuevo_servicio_nombre, uce_nombre, tipo_producto):
    """
    Cambia el servicio de una AT (solo para ARA e INVESTIGACION).
    Actualiza ASTR y ACFI con el nuevo servicio y nombre.
    """
    
    print("\n=== INICIO: cambiar_servicio_at ===")
    print(f"1. Parámetros recibidos:")
    print(f"   - acfi_id: {acfi_id}")
    print(f"   - nuevo_servicio_id: {nuevo_servicio_id}")
    print(f"   - nuevo_servicio_nombre: {nuevo_servicio_nombre}")
    print(f"   - uce_nombre: {uce_nombre}")
    print(f"   - tipo_producto: {tipo_producto}")
    
    # Validación de tipo de producto
    tipos_permitidos = ['ATENCION_REFERENCIA', 'INVESTIGACION']
    if tipo_producto not in tipos_permitidos:
        print(f"2. ERROR: Tipo de producto no permitido: {tipo_producto}")
        return {"success": False, "message": f"Cambio de servicio no permitido para tipo: {tipo_producto}"}
    
    # Validar parámetros
    if not acfi_id or not nuevo_servicio_id or not nuevo_servicio_nombre:
        print("2. ERROR: Parámetros incompletos")
        return {"success": False, "message": "Parámetros incompletos."}
    
    print("2. Parámetros validados correctamente")
    
    # Construir el nuevo nombre de ACFI
    nuevo_nombre_acfi = f"{tipo_producto} {nuevo_servicio_nombre} {uce_nombre}"
    print(f"3. Nuevo nombre ACFI generado: {nuevo_nombre_acfi}")
    
    # Query 1: Actualizar ASTR
    query_astr = """
        UPDATE own_astr.astr_asignacion_trabajo
        SET ENSV_ID = :nuevo_servicio_id
        WHERE ACFI_ID = :acfi_id
    """
    
    # Query 2: Actualizar ACFI
    query_acfi = """
        UPDATE own_glob.acfi_actividad_fiscalizacion
        SET ENSV_ID = :nuevo_servicio_id,
            ACFI_NOMBRE = :nuevo_nombre_acfi
        WHERE ACFI_ID = :acfi_id
    """
    
    try:
        print("4. Iniciando conexión a Oracle...")
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            print("5. Conexión establecida")
            
            with connection.cursor() as cursor:
                print("6. Cursor creado")
                
                # Ejecutar Query 1
                print("7. Ejecutando UPDATE en ASTR...")
                cursor.execute(query_astr, {
                    "nuevo_servicio_id": nuevo_servicio_id,
                    "acfi_id": acfi_id
                })
                print(f"8. ASTR actualizada. Filas afectadas: {cursor.rowcount}")
                
                # Ejecutar Query 2
                print("9. Ejecutando UPDATE en ACFI...")
                cursor.execute(query_acfi, {
                    "nuevo_servicio_id": nuevo_servicio_id,
                    "nuevo_nombre_acfi": nuevo_nombre_acfi,
                    "acfi_id": acfi_id
                })
                print(f"10. ACFI actualizada. Filas afectadas: {cursor.rowcount}")
                
            print("11. Realizando commit...")
            connection.commit()
            print("12. Commit realizado")
        
        print(f"13. Capa 3: Servicio de AT {acfi_id} cambido a {nuevo_servicio_nombre}.")
        resultado = {"success": True, "message": f"Servicio actualizado a {nuevo_servicio_nombre}."}
        print(f"14. Resultado final: {resultado}")
        print("=== FIN: cambiar_servicio_at (EXITOSO) ===\n")
        return resultado
    
    except oracledb.DatabaseError as e:
        print(f"ERROR en conexión/ejecución: {e}")
        print(f"Tipo de error: {type(e)}")
        print("=== FIN: cambiar_servicio_at (ERROR DB) ===\n")
        return {"success": False, "message": f"Error al cambiar servicio: {e}"}
    
    except Exception as e:
        print(f"ERROR GENERAL NO ESPERADO: {e}")
        print(f"Tipo de error: {type(e)}")
        print("=== FIN: cambiar_servicio_at (ERROR GENERAL) ===\n")
        return {"success": False, "message": f"Error inesperado: {e}"}
