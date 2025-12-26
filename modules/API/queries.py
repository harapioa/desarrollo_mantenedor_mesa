# Archivo: modules/API/queries.py
import oracledb
import sys
import os

# Truco para importar config desde la carpeta raíz si da problemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import config 

def actualizar_estado_at_completa(acfi_id, accion, tipo_origen):
    """
    Ejecuta las DOS queries (ASTR y LIAU) para reabrir o cerrar
    la AT completa dentro de una sola transacción.
    """
    
    # 1. Definimos los nuevos estados basados en la acción
    if accion == 'reabrir':
        nuevo_estado_astr = 'EN_PROCESO' 
        nuevo_estado_liau = 'EN_CIERRE'  
    elif accion == 'cerrar':
        nuevo_estado_astr = 'CERRADA'
        nuevo_estado_liau = 'CERRADA'
    else:
        print(f"Error en Capa 3: Acción no válida: {accion}")
        return False

    # 2. Definimos las dos queries
    if tipo_origen == 'AUDITORIA_CUMPLIMIENTO':
        query_astr = """
            UPDATE own_astr.astr_asignacion_trabajo
            SET astr_estado = :estado_astr
            WHERE astr_tipo = 'INFORME_FINAL' AND acfi_id = :acfi_id_bv
        """
    elif tipo_origen == 'AUDITORIA_SIMPLIFICADA':
        query_astr = """
            UPDATE own_astr.astr_asignacion_trabajo
            SET astr_estado = :estado_astr
            WHERE acfi_id = :acfi_id_bv
        """
    else:
        print(f"Error en Capa 3: Tipo de origen no válido: {tipo_origen}")
        return False
    
    query_liau = """
        UPDATE own_ejec.ejec_linea_auditoria
        SET LIAU_ESTADO = :estado_liau
        WHERE LIAU_ID = :acfi_id_bv
    """
    
    try:
        # Iniciamos la conexión.
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                
                # 3. Ejecutamos la Query 1
                cursor.execute(query_astr, {
                    "estado_astr": nuevo_estado_astr,
                    "acfi_id_bv": acfi_id
                })
                print(f"Capa 3: Query AT Completa {query_astr} variables {nuevo_estado_astr}.")
                
                # 4. Ejecutamos la Query 2
                cursor.execute(query_liau, {
                    "estado_liau": nuevo_estado_liau,
                    "acfi_id_bv": acfi_id
                })
                print(f"Capa 3: Query AT Completa {query_liau} variables {nuevo_estado_liau}.")
                
                # 5. Confirmamos transacción
                connection.commit() 
                
                print(f"Capa 3: Éxito. AT Completa {acfi_id} actualizada a {accion}.")
                return True

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (actualizar_estado_at_completa): {e}")
        return False

def actualizar_estado_procedimiento(liau_id, proc_id, nuevo_estado):
    """
    Ejecuta el UPDATE para cambiar el estado de un procedimiento
    y confirma la transacción (commit).
    """
    
    # 1. Validación de Seguridad:
    # Nos aseguramos de que solo se puedan pasar 'ABIERTO' o 'CERRADO'
    # Esto previene cualquier tipo de inyección SQL en el valor del estado.
    if nuevo_estado not in ('ABIERTO', 'CERRADO'):
        print(f"Error en Capa 3: Intento de actualizar con estado no válido: {nuevo_estado}")
        return False

    # 2. La consulta UPDATE simple y segura:
    # Usamos los IDs que ya tenemos.
    query = """
        UPDATE own_ejec.ejec_audit_proc
        SET AUPR_ESTADO = :estado_bv
        WHERE LIAU_ID = :liau_id_bv
          AND PROC_ID = :proc_id_bv
    """
    
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                # 3. Ejecutamos la consulta
                cursor.execute(query, {
                    "estado_bv": nuevo_estado,
                    "liau_id_bv": liau_id,
                    "proc_id_bv": proc_id
                })
                
                # 4. ¡El paso más importante! Guardamos los cambios.
                connection.commit() 
                
                print(f"Capa 3: Éxito. LIAU_ID {liau_id}, PROC_ID {proc_id} actualizado a {nuevo_estado}.")
                return True

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (actualizar_estado_procedimiento): {e}")
        return False