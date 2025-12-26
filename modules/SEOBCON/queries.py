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

def get_seobcon_observaciones(lista_ids_str):
    """
    Obtiene observaciones de SEOBCON basado en un string de IDs separados por coma.
    """
    if not lista_ids_str:
        return []
    
    # 1. Limpiar y convertir el string de IDs a una lista de enteros
    try:
        # Quitar espacios, filtrar vacíos, convertir a int
        ids_limpios = [int(id_str.strip()) for id_str in lista_ids_str.split(',') if id_str.strip()]
        if not ids_limpios:
            return []
    except ValueError:
        print("Error en Capa 3 (get_seobcon_observaciones): IDs contienen valores no numéricos.")
        return None # Indica un error

    # 2. Construir placeholders y bind variables
    placeholders = ', '.join([f':id_bv{i}' for i in range(len(ids_limpios))])
    bind_vars = {f'id_bv{i}': id_val for i, id_val in enumerate(ids_limpios)}
    
    # 3. Query
    query = f"""
        SELECT OBSE_ID, OBSE_OBSERVACION, OBSE_ESTADO
        FROM seobcon_glob.seoc_observacion
        WHERE OBSE_ID IN ({placeholders})
        ORDER BY OBSE_ID
    """
    
    resultados = []
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, bind_vars)
                column_names = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    resultados.append(dict(zip(column_names, row)))
        
        print(f"Capa 3: Búsqueda SEOBCON encontró {len(resultados)} resultados.")
        return resultados

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_seobcon_observaciones): {e}")
        return None

def actualizar_estado_seobcon(lista_ids, nuevo_estado):
    """
    Actualiza el OBSE_ESTADO para una lista de OBSE_ID.
    """
    
    # 1. Validar estado (¡IMPORTANTE! Ajusta 'EN_REVISION_CGR' y 'PENDIENTE' a tus estados reales)
    estados_validos = ['EN_REVISION_CGR', 'PENDIENTE'] 
    if nuevo_estado not in estados_validos:
        print(f"Error en Capa 3: Estado no válido para SEOBCON: {nuevo_estado}")
        return False
        
    # 2. Validar IDs (ya deberían ser enteros desde app.py)
    if not lista_ids: return False

    # 3. Construir placeholders y bind variables
    placeholders = ', '.join([f':id_bv{i}' for i in range(len(lista_ids))])
    bind_vars = {'estado_bv': nuevo_estado}
    for i, actu_id in enumerate(lista_ids):
        bind_vars[f'id_bv{i}'] = actu_id

    # 4. Query UPDATE
    query = f"""
        UPDATE seobcon_glob.seoc_observacion
        SET OBSE_ESTADO = :estado_bv
        WHERE OBSE_ID IN ({placeholders})
    """
    print(f"Error en Capa 3 (actualizar_estquery): {query}")
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, bind_vars)
                connection.commit()
                print(f"Capa 3: Éxito. {cursor.rowcount} observaciones SEOBCON actualizadas a {nuevo_estado}.")
                return True

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (actualizar_estado_seobcon): {e}")
        print(f"Error en Capa 3 (actualizar_estquery): {query}")
        return False
