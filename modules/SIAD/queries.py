# modules/SIAD/queries.py
import oracledb
import sys
import os

# Configuración de rutas para importar config.py
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

def buscar_usuarios_siad(id_usuario, nombre, ap_paterno, ap_materno):
    """
    Busca usuarios en SIAD con filtros dinámicos.
    """
    
    # 1. Definimos la consulta base.
    #    (He adaptado tu query para que coincida con las
    #    columnas que espera el HTML: ID_USUARIO, NOMBRE_COMPLETO, ENTIDAD, ESTADO)
    base_query = """
        SELECT 
            uses.USES_ID AS ID_USUARIO,
            uses.USES_NOMBRES || ' ' || uses.USES_APATERNO || ' ' || uses.USES_AMATERNO AS NOMBRE_COMPLETO,
            uses.USES_RUN || '-' || uses.USES_DV AS RUT, -- <-- CAMPO NUEVO
            uses.USES_EMAIL AS EMAIL,                 -- <-- CAMPO NUEVO
            ensv.ENSV_NOMBRE AS ENTIDAD,
            uses.USES_VIGENCIA AS ESTADO
        FROM sica_escritorio_arqt.sies_usuario_escritorio uses
        INNER JOIN OWN_GLOB.GLOB_ENTIDADES_SERVICIOS ensv
            ON uses.ensv_id = ensv.ensv_id
    """
    
    # 2. Listas para construir la consulta dinámica
    where_conditions = []
    bind_vars = {}

    # 3. Añadimos los filtros solo si existen
    
    if id_usuario:
        where_conditions.append("uses.USES_ID = :id_bv")
        bind_vars["id_bv"] = id_usuario
        
    if nombre:
        where_conditions.append("lower(uses.uses_nombres) LIKE lower(:nombre_bv)")
        # Añadimos los '%' para la búsqueda LIKE
        bind_vars["nombre_bv"] = f"%{nombre}%" 
        
    if ap_paterno:
        where_conditions.append("lower(uses.uses_apaterno) LIKE lower(:ap_paterno_bv)")
        bind_vars["ap_paterno_bv"] = f"%{ap_paterno}%"

    if ap_materno:
        where_conditions.append("lower(uses.uses_amaterno) LIKE lower(:ap_materno_bv)")
        bind_vars["ap_materno_bv"] = f"%{ap_materno}%"

    # 4. Ensamblamos la consulta final
    #    (Solo añadimos WHERE si hay al menos una condición)
    final_query = base_query
    if where_conditions:
        final_query += " WHERE " + " AND ".join(where_conditions)
    
    # Añadimos un orden
    final_query += " ORDER BY uses.USES_APATERNO, uses.USES_AMATERNO, uses.USES_NOMBRES"

    print("--- CONSULTA DINÁMICA DE USUARIOS SIAD ---")
    print(final_query)
    print("--- CON VALORES ---")
    print(bind_vars)
    print("---------------------------------")
    
    # 5. Ejecutamos
    resultados = []
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(final_query, bind_vars)
                
                # Obtenemos los nombres de las columnas (ID_USUARIO, NOMBRE_COMPLETO...)
                column_names = [desc[0] for desc in cursor.description]
                
                for row in cursor.fetchall():
                    resultados.append(dict(zip(column_names, row)))
        
        print(f"Capa 3: Búsqueda de usuarios encontró {len(resultados)} resultados.")
        return resultados

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (buscar_usuarios_siad): {e}")
        return None

def desactivar_usuario_siad(user_id):
    """
    Desactiva un usuario SIAD (escritorio y proceso) en una sola transacción.
    Ejecuta ambas queries que proporcionaste.
    """
    
    # Query 1: DEJAR NO VIGENTE USUARIO ESCRITORIO
    query_escritorio = """
        UPDATE sica_escritorio_arqt.sies_usuario_escritorio
        SET USES_VIGENCIA = 'NO_VIGENTE'
        WHERE USES_ID = :user_id_bv
    """
    
    # Query 2: DEJAR NO VIGENTE USUARIOS CONTRAPARTE
    query_proceso = """
        UPDATE sica_escritorio_arqt.sies_usuario_proceso
        SET USPR_VIGENCIA = 'NO_VIGENTE'
        WHERE USES_ID = :user_id_bv
    """
    
    try:
        # 'with' maneja la conexión y la transacción
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                
                # Ejecutamos la Query 1
                cursor.execute(query_escritorio, user_id_bv=user_id)
                
                # Ejecutamos la Query 2
                cursor.execute(query_proceso, user_id_bv=user_id)
                
                # Si ambas tuvieron éxito, guardamos los cambios
                connection.commit()
                
                print(f"Capa 3: Éxito. Usuario {user_id} desactivado (escritorio y proceso).")
                return True

    except oracledb.DatabaseError as e:
        # Si algo falla, el 'with' hace rollback automáticamente
        print(f"Error en Capa 3 (desactivar_usuario_siad): {e}")
        return False
    
def get_usuario_siad_by_id(user_id):
    """
    Obtiene todos los detalles de un solo usuario de SIAD por su ID.
    """
    
    # Esta query trae los campos individuales para el formulario de edición
    query = """
        SELECT 
            USES_ID,
            USES_NOMBRES,
            USES_APATERNO,
            USES_AMATERNO,
            USES_RUN,
            USES_DV,
            USES_EMAIL,
            USES_VIGENCIA
        FROM sica_escritorio_arqt.sies_usuario_escritorio
        WHERE USES_ID = :user_id_bv
    """
    
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, user_id_bv=user_id)
                
                # Obtenemos los nombres de las columnas
                column_names = [desc[0] for desc in cursor.description]
                row = cursor.fetchone() # Solo esperamos una fila
                
                if row:
                    print(f"Capa 3: Datos encontrados para el usuario {user_id}.")
                    # Devolvemos un solo diccionario con los datos
                    return dict(zip(column_names, row))
        
        print(f"Capa 3: No se encontró usuario con ID {user_id}.")
        return None

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_usuario_siad_by_id): {e}")
        return None

def get_actos_siad(proc_numero_siad, caso_numero):
    """
    Obtiene la lista de Actos Administrativos (TIAC) para un Proceso y Caso SIAD.
    Ejecuta la Query 1 que proporcionaste.
    """
    
    # Esta es tu Query 1, usando bind variables seguras
    query = """
        SELECT tiac.tiac_id, tiac.TIAC_NOMBRE
        FROM siad_glob.siad_tipo_actuacion tiac
        WHERE tiac.caso_id IN (
            SELECT caso.caso_ID
            FROM siad_glob.siad_proceso proc
            INNER JOIN siad_glob.siad_caso caso
                ON caso.proc_id = proc.proc_id
            WHERE proc.PROC_NUMERO_SIAD = :proc_num_bv
              AND caso.CASO_NUMERO = :caso_num_bv
        )
        ORDER BY tiac.TIAC_NOMBRE 
    """ # Añadí un ORDER BY para consistencia
    
    resultados = []
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                # Pasamos los números del proceso y caso
                cursor.execute(query, {
                    "proc_num_bv": proc_numero_siad,
                    "caso_num_bv": caso_numero
                })
                
                # Convertimos cada fila en un diccionario
                column_names = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    resultados.append(dict(zip(column_names, row)))
        
        print(f"Capa 3: Búsqueda de actos para {proc_numero_siad}.{caso_numero} encontró {len(resultados)} resultados.")
        return resultados

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_actos_siad): {e}")
        return None # Devolvemos None si hay error
    except Exception as e:
        # Capturamos otros errores (ej. si los números no son válidos)
        print(f"Error general en Capa 3 (get_actos_siad): {e}")
        return None
    
def get_registros_siad(tiac_id):
    """
    Obtiene la lista de Actuaciones (registros) para un TIAC_ID específico.
    Ejecuta la Query 2.
    """
    
    # Tu Query 2, usando una variable bind segura
    query = """
        SELECT 
            ACTU_ID, 
            TO_CHAR(ACTU_FECHA, 'DD-MM-YYYY') AS ACTU_FECHA, -- Formatear fecha para mostrar
            ACTU_ESTADO, 
            ACTU_TIPO_DOCUMENTO, 
            ACTU_OBSERVACION, 
            ACTU_NUMERO_PROX,
            ACTU_VIGENCIA -- Añadí VIGENCIA por si es útil
        FROM siad_glob.siad_actuacion actu
        WHERE actu.tiac_id = :tiac_id_bv
        ORDER BY ACTU_FECHA DESC, ACTU_ID DESC -- Orden de ejemplo
    """
    
    resultados = []
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tiac_id_bv=tiac_id)
                
                # Convertir cada fila a un diccionario
                column_names = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    resultados.append(dict(zip(column_names, row)))
        
        print(f"Capa 3: Búsqueda de registros para TIAC_ID {tiac_id} encontró {len(resultados)} resultados.")
        return resultados

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_registros_siad): {e}")
        return None # Devolver None en caso de error

def actualizar_estado_actuaciones_siad(lista_actu_ids, nuevo_estado):
    """
    Actualiza el ACTU_ESTADO para una lista de ACTU_ID en siad_actuacion.
    Usa una transacción para asegurar que todos se actualicen o ninguno.
    """
    
    # 1. Validar el nuevo estado permitido
    estados_validos = ['BORRADOR_CGR', 'ENVIADA_CGR', 'NO_VIGENTE']
    if nuevo_estado not in estados_validos:
        print(f"Error en Capa 3: Estado no válido para actualización SIAD: {nuevo_estado}")
        return False
        
    # 2. Validar que la lista de IDs no esté vacía y sean números
    if not lista_actu_ids or not all(isinstance(id_val, int) for id_val in lista_actu_ids):
        print(f"Error en Capa 3: Lista de IDs inválida o vacía: {lista_actu_ids}")
        return False

    # 3. Construir la consulta UPDATE con IN y múltiples placeholders
    #    Creamos tantos ':id_bvX' como IDs haya en la lista
    query = f"""
        UPDATE siad_glob.siad_actuacion
        SET ACTU_ESTADO = :estado_bv
        WHERE actu_id IN ({', '.join([f':id_bv{i}' for i in range(len(lista_actu_ids))])})
    """
    
    # 4. Crear el diccionario de bind variables (estado + todos los IDs)
    bind_vars = {'estado_bv': nuevo_estado}
    for i, actu_id in enumerate(lista_actu_ids):
        bind_vars[f'id_bv{i}'] = actu_id

    print("--- UPDATE ACTUACIONES SIAD ---")
    print(query)
    print(f"--- CON VALORES (Estado: {nuevo_estado}, IDs: {lista_actu_ids}) ---")
        
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                # Ejecutar la consulta
                cursor.execute(query, bind_vars)
                # Confirmar la transacción
                connection.commit()
                print(f"Capa 3: Éxito. {cursor.rowcount} actuaciones SIAD actualizadas a {nuevo_estado}.")
                # cursor.rowcount nos dice cuántas filas fueron afectadas
                return True

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (actualizar_estado_actuaciones_siad): {e}")
        return False

def get_actos_termino_siad(proc_numero_siad, caso_numero):
    """
    Obtiene la lista de Actos Administrativos de Término (AAFI)
    para un Proceso y Caso SIAD, incluyendo fecha formateada y número próximo.
    """
    
    query = """
        SELECT 
            saaf.aafi_id, 
            TO_CHAR(saaf.AAFI_FECHA , 'DD-MM-YYYY') AS AAFI_FECHA,
            saaf.aafi_tipo, 
            saaf.aafi_nombre_descripcion, 
            saaf.aafi_numero_prox, 
            saaf.aafi_estado, 
            saaf.aafi_vigencia
        FROM siad_glob.siad_acto_administrativo_fin saaf
        WHERE saaf.caso_id IN (
            SELECT caso.caso_ID
            FROM siad_glob.siad_proceso proc
            INNER JOIN siad_glob.siad_caso caso
                ON caso.proc_id = proc.proc_id
            WHERE proc.PROC_NUMERO_SIAD = :proc_num_bv
              AND caso.CASO_NUMERO = :caso_num_bv
        )
        ORDER BY saaf.aafi_nombre_descripcion
    """
    
    resultados = []
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {
                    "proc_num_bv": proc_numero_siad,
                    "caso_num_bv": caso_numero
                })
                
                column_names = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    resultados.append(dict(zip(column_names, row)))
        
        print(f"Capa 3: Búsqueda de actos de término para {proc_numero_siad}.{caso_numero} encontró {len(resultados)} resultados.")
        return resultados

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_actos_termino_siad): {e}")
        return None
    except Exception as e:
        print(f"Error general en Capa 3 (get_actos_termino_siad): {e}")
        return None

def actualizar_estado_actos_termino(lista_aafi_ids, accion):
    """
    Actualiza el estado (AAFI_ESTADO o AAFI_VIGENCIA) para una lista
    de AAFI_ID en siad_acto_administrativo_fin.
    Usa una transacción.
    """
    
    # 1. Determinar la columna y el valor a actualizar
    columna_a_actualizar = ""
    nuevo_valor = ""
    
    if accion == 'borrador':
        columna_a_actualizar = "AAFI_ESTADO"
        nuevo_valor = 'BORRADOR_CGR'
    elif accion == 'enviado':
        columna_a_actualizar = "AAFI_ESTADO"
        nuevo_valor = 'ENVIADA_CGR'
    elif accion == 'no_vigente':
        columna_a_actualizar = "AAFI_VIGENCIA" # ¡Ojo! Es AAFI_VIGENCIA para "no vigente"
        nuevo_valor = 'NO_VIGENTE'
    else:
        print(f"Error en Capa 3: Acción no válida para Acto de Término: {accion}")
        return False
        
    # 2. Validar IDs
    if not lista_aafi_ids or not all(isinstance(id_val, int) for id_val in lista_aafi_ids):
        print(f"Error en Capa 3: Lista de AAFI_IDs inválida o vacía: {lista_aafi_ids}")
        return False

    # 3. Construir la consulta UPDATE dinámicamente
    query = f"""
        UPDATE siad_glob.siad_acto_administrativo_fin
        SET {columna_a_actualizar} = :valor_bv 
        WHERE AAFI_ID IN ({', '.join([f':id_bv{i}' for i in range(len(lista_aafi_ids))])})
    """
    
    # 4. Crear bind variables
    bind_vars = {'valor_bv': nuevo_valor}
    for i, aafi_id in enumerate(lista_aafi_ids):
        bind_vars[f'id_bv{i}'] = aafi_id

    print("--- UPDATE ACTOS TÉRMINO SIAD ---")
    print(query)
    print(f"--- CON VALORES ({columna_a_actualizar}={nuevo_valor}, IDs: {lista_aafi_ids}) ---")
        
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, bind_vars)
                connection.commit()
                print(f"Capa 3: Éxito. {cursor.rowcount} actos de término SIAD actualizados.")
                return True

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (actualizar_estado_actos_termino): {e}")
        return False

def guardar_cambios_usuario(user_id, nombres, ap_paterno, ap_materno, email, rut, dv, vigencia):
    """
    Actualiza los datos de un usuario en la tabla sies_usuario_escritorio
    basado en la query de edición.
    """
    
    # Esta es tu query, adaptada a bind variables seguras
    # Nota: He omitido 'SET USES_ID = ...' ya que el ID no debe cambiarse,
    # solo se usa en el WHERE.
    query = """
        UPDATE sica_escritorio_arqt.sies_usuario_escritorio
        SET 
            USES_NOMBRES = :nombres_bv,
            USES_APATERNO = :ap_paterno_bv,
            USES_AMATERNO = :ap_materno_bv,
            USES_RUN = :rut_bv,
            USES_DV = :dv_bv,
            USES_EMAIL = :email_bv,
            USES_VIGENCIA = :vigencia_bv
        WHERE 
            USES_ID = :user_id_bv
    """
    
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                
                # Ejecutamos la consulta con todos los valores del formulario
                cursor.execute(query, {
                    "nombres_bv": nombres,
                    "ap_paterno_bv": ap_paterno,
                    "ap_materno_bv": ap_materno,
                    "rut_bv": rut,
                    "dv_bv": dv,
                    "email_bv": email,
                    "vigencia_bv": vigencia,
                    "user_id_bv": user_id
                })
                
                # Guardamos los cambios en la BD
                connection.commit()
                
                print(f"Capa 3: Usuario {user_id} actualizado exitosamente.")
                return True

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (guardar_cambios_usuario): {e}")
        return False
