# database_queries.py

import oracledb
import config
import pandas as pd  # <-- Para crear el Excel
from io import BytesIO

try:
    from report_queries import (
        QUERY_CASOS_PD_ENTIDAD,
        QUERY_PRODUCTOS_NO_VINCULADOS,
        QUERY_PD_FECHAS_RESOLUCIONES,
        QUERY_ACTOS_TOTALES_SIAD
    )
except ImportError:
    print("ERROR: No se pudo encontrar el archivo 'report_queries.py'")
    # (Esto es solo una salvaguarda)
    QUERY_CASOS_PD_ENTIDAD = "SELECT 1 FROM DUAL"
    QUERY_PRODUCTOS_NO_VINCULADOS = "SELECT 1 FROM DUAL"
    QUERY_PD_FECHAS_RESOLUCIONES = "SELECT 1 FROM DUAL"
    QUERY_ACTOS_TOTALES_SIAD = "SELECT 1 FROM DUAL"

def get_todas_las_uces():
    """
    Ejecuta la Query 1 para obtener la lista de UCEs (Padre).
    Retorna una lista de diccionarios: [{'id': 1, 'nombre': 'UCE_A'}, ...]
    """
    
    # Query 1 (Padre)
    sql_query = """
        SELECT unce_id, unce_nombre
        FROM own_glob.glob_unidades_control_ext
        WHERE unce_id NOT IN (19, 20, 21, 22, 56)
        ORDER BY unce_nombre
    """
    
    resultados = []
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                
                # Convertimos cada fila en un diccionario
                for fila in cursor.fetchall():
                    resultados.append({
                        "unce_id": fila[0],
                        "unce_nombre": fila[1]
                    })
        
        print("Capa 3: Lista de UCEs obtenida de Oracle.")
        return resultados

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_todas_las_uces): {e}")
        return None

def get_servicios_por_uce_id(id_de_la_uce):
    """
    Ejecuta la Query 2 para obtener los Servicios (Hijo)
    basado en el ID de la UCE seleccionada.
    """
    
    # Query 2 (Hijo)
    # Usamos ':uce_id' como "bind variable". Es más seguro.
    sql_query = """
        SELECT ENSV.ensv_id, ENSV.ENSV_NOMBRE
        FROM own_glob.glob_uce_servicios UCSE
        INNER JOIN own_glob.glob_entidades_servicios ENSV
            ON UCSE.ensv_id = ENSV.ensv_id
        WHERE ENSV.ensv_estado = 'ACTIVO'
        AND UCSE.unce_id = :id_de_la_uce 
        ORDER BY ENSV.ENSV_NOMBRE
    """
    
    resultados = []
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                # Pasamos el ID como parámetro a la consulta
                cursor.execute(sql_query, id_de_la_uce=id_de_la_uce)
                
                for fila in cursor.fetchall():
                    resultados.append({
                        "ensv_id": fila[0],
                        "ensv_nombre": fila[1]
                    })
        
        print(f"Capa 3: Servicios para UCE ID {id_de_la_uce} obtenidos.")
        return resultados

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_servicios_por_uce_id): {e}")
        return None
    
def buscar_auditorias(periodo, nro_at, uce_id, servicio_id, nro_programa, tipo_origen, num_referencia=None): # <-- Nuevo parámetro
    """
    Ejecuta la búsqueda principal con filtros dinámicos, adaptada para ARA.
    Usa ROW_NUMBER() para deduplicar.
    """

    # 1. BASE DE LA CONSULTA (Modificada)
    #    - Añadidos JOINs para pres y prdi
    #    - Eliminada MATERIA
    inner_select_query = """
        SELECT
            ASTR.ACFI_ID AS ACFI_ID,
            UCE.unce_nombre AS UCE,
            PRGE.PRGE_NUMERO AS N_PROGRAMA,
            ENSV.ENSV_NOMBRE AS SERVICIO,
            ASTR.ASTR_ESTADO AS ESTADO,
            ASTR.ASTR_TIPO_ORIGEN AS TIPO_ORIGEN,

            -- Añadir PRDI_NUMERO temporalmente para el filtro LIKE
            prdi.PRDI_NUMERO AS NUMERO_REFERENCIA_TEMP,

            ROW_NUMBER() OVER (
                PARTITION BY ASTR.ACFI_ID
                ORDER BY ASTR.ASTR_ID DESC
            ) AS RN

        FROM
            OWN_ASTR.ASTR_ASIGNACION_TRABAJO ASTR
        LEFT JOIN own_glob.glob_unidades_control_ext UCE ON ASTR.unce_id = UCE.unce_id
        LEFT JOIN own_glob.glob_entidades_servicios ENSV ON ASTR.ENSV_ID = ENSV.ensv_id
        LEFT JOIN own_astr.astr_programa_general PRGE ON ASTR.prge_id = PRGE.prge_id
        -- NUEVOS JOINS para Número de Referencia (ARA)
        LEFT JOIN own_astr.astr_presentacion_at pres ON pres.astr_id = ASTR.astr_id
        LEFT JOIN own_plpr.plpr_presentaciones_deim prdi ON prdi.PRDI_ID = pres.PRDI_ID
    """

    # 2. CONSTRUCCIÓN DINÁMICA DE CONDICIONES (Añadido filtro num_referencia)
    where_conditions = []
    bind_vars = {}

    # Filtros obligatorios/estáticos
    where_conditions.append("ASTR.ASTR_TIPO_ORIGEN = :tipo_origen_bv")
    bind_vars["tipo_origen_bv"] = tipo_origen
    where_conditions.append("PRGE.prge_periodo = :periodo_bv")
    bind_vars["periodo_bv"] = periodo
    where_conditions.append("ASTR.ASTR_ESTADO NOT IN ('ELIMINADA', 'BORRADOR')") # Mantenemos exclusiones

    # Filtros opcionales
    if nro_at:
        where_conditions.append("ASTR.ASTR_CORRELATIVO = :nro_at_bv")
        bind_vars["nro_at_bv"] = nro_at
    if uce_id:
        where_conditions.append("ASTR.unce_id = :uce_id_bv")
        bind_vars["uce_id_bv"] = uce_id
    if servicio_id:
        where_conditions.append("ASTR.ENSV_ID = :servicio_id_bv")
        bind_vars["servicio_id_bv"] = servicio_id
    if nro_programa:
        where_conditions.append("PRGE.PRGE_NUMERO = :nro_prog_bv")
        bind_vars["nro_prog_bv"] = nro_programa
        # where_conditions.append("PRGE.prge_periodo = :periodo_bv") # Ya está incluido periodo

    # NUEVO FILTRO OPCIONAL: Número de Referencia (para ARA)
    if num_referencia:
        # Usamos UPPER para búsqueda insensible a mayúsculas/minúsculas
        where_conditions.append("UPPER(prdi.PRDI_NUMERO) LIKE UPPER(:num_ref_bv)")
        bind_vars["num_ref_bv"] = f"%{num_referencia}%"


    # 3. ENSAMBLAJE FINAL DE LA CONSULTA (Modificado SELECT externo)
    #    - Eliminada MATERIA
    final_query = f"""
        WITH QueryNumerada AS (
            {inner_select_query}
            WHERE {" AND ".join(where_conditions)}
        )
        SELECT
            ACFI_ID,
            UCE,
            N_PROGRAMA,
            SERVICIO,
            ESTADO,
            TIPO_ORIGEN
            -- Ya no seleccionamos NUMERO_REFERENCIA_TEMP aquí
        FROM QueryNumerada
        WHERE RN = 1
        ORDER BY ACFI_ID DESC -- O el orden que prefieras
    """

    print("--- CONSULTA DINÁMICA (con ARA) EJECUTADA ---")
    print(final_query)
    print("--- CON VALORES ---")
    print(bind_vars)
    print("---------------------------------")

    # 4. EJECUCIÓN (Sin cambios)
    resultados = []
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection: # Tu conexión
            with connection.cursor() as cursor:
                cursor.execute(final_query, bind_vars)
                column_names = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    resultados.append(dict(zip(column_names, row)))
        print(f"Capa 3: Búsqueda (con ARA) encontró {len(resultados)} resultados.")
        return resultados
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (buscar_auditorias con ARA): {e}")
        return None

def get_detalle_at_info(acfi_id):
    """
    Obtiene la información de cabecera para un ACFI_ID específico,
    usando la misma lógica de ROW_NUMBER() para asegurar el último registro.
    """
    
    # !!! ATENCIÓN: AJUSTA ESTOS NOMBRES DE COLUMNAS !!!
    # He asumido nombres como ASTR_N_INFORME, PRGE_TIPO, ASTR_PUBLICADO, etc.
    # Debes reemplazarlos con los nombres reales de tus tablas.
    
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
                'No' AS REEVALUACION, -- (Valores de ejemplo, ajústalos)
                
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
                
                column_names = [desc[0] for desc in cursor.description]
                row = cursor.fetchone()
                
                if row:
                    print(f"Capa 3: Información de detalle para {acfi_id} encontrada.")
                    return dict(zip(column_names, row))
        
        print(f"Capa 3: No se encontró información para {acfi_id}.")
        return None

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_detalle_at_info): {e}")
        return None

def get_actividades_cumplimiento(acfi_id):
    """
    Obtiene un MAPA de los procedimientos que SÍ existen para esta AT.
    El resultado es un diccionario, ej:
    { 
        '1.1': {'id': 37, 'estado': 'CERRADO'},
        '1.2': {'id': 39, 'estado': 'ABIERTO'}
    }
    """
    
    if not acfi_id:
        print("Capa 3: No se proporcionó ACFI_ID, no se pueden buscar actividades.")
        return {}

    # Tu consulta
    query = """
        SELECT 
            aupr.PROC_ID, 
            REGEXP_SUBSTR(
                proc.texto_ayuda, 
                '<b>PROCEDIMIENTO ([0-9\.]+) - ', 1, 1, NULL, 1
            ) AS ITEM_NUMERO,
            aupr.AUPR_ESTADO
        FROM own_ejec.ejec_audit_proc aupr
        INNER JOIN own_ejec.ejec_procedimiento proc
            ON proc.proc_id = aupr.proc_id
        WHERE aupr.LIAU_ID = :acfi_id_bv -- Usamos el ACFI_ID como LIAU_ID
    """
    
    # Creamos el mapa que vamos a devolver
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
        
        print(f"Capa 3: Mapa de estados creado con {len(status_map)} items.")
        return status_map

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_actividades_cumplimiento): {e}")
        return {}
    
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

def actualizar_estado_at_completa(acfi_id, accion):
    """
    Ejecuta las DOS queries (ASTR y LIAU) para reabrir o cerrar
    la AT completa dentro de una sola transacción.
    """
    
    # 1. Definimos los nuevos estados basados en la acción
    if accion == 'reabrir':
        nuevo_estado_astr = 'EN_PROCESO' # Según tu query
        nuevo_estado_liau = 'EN_CIERRE'  # Según tu query
    elif accion == 'cerrar':
        nuevo_estado_astr = 'CERRADA'
        nuevo_estado_liau = 'CERRADA'
    else:
        print(f"Error en Capa 3: Acción no válida: {accion}")
        return False

    # 2. Definimos las dos queries
    query_astr = """
        UPDATE own_astr.astr_asignacion_trabajo
        SET astr_estado = :estado_astr
        WHERE astr_tipo = 'INFORME_FINAL' AND acfi_id = :acfi_id_bv
    """
    query_liau = """
        UPDATE own_ejec.ejec_linea_auditoria
        SET LIAU_ESTADO = :estado_liau
        WHERE LIAU_ID = :acfi_id_bv
    """
    
    try:
        # Iniciamos la conexión. La transacción empieza automáticamente.
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
                
                # 4. Ejecutamos la Query 2
                cursor.execute(query_liau, {
                    "estado_liau": nuevo_estado_liau,
                    "acfi_id_bv": acfi_id
                })
                
                # 5. Si ambas tuvieron éxito, confirmamos la transacción
                connection.commit() 
                
                print(f"Capa 3: Éxito. AT Completa {acfi_id} actualizada a {accion}.")
                return True

    except oracledb.DatabaseError as e:
        # 6. Si algo falló, el 'with' se encarga del rollback
        print(f"Error en Capa 3 (actualizar_estado_at_completa): {e}")
        return False
    
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
        'actos_totales_siad': QUERY_ACTOS_TOTALES_SIAD
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
        output_stream = BytesIO()
        
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

def get_actividades_simplificada(acfi_id):
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
    placeholders = ', '.join([f':id_bv{i}' for i in range(len(lista_actu_ids))])
    query = f"""
        UPDATE siad_glob.siad_actuacion
        SET ACTU_ESTADO = :estado_bv
        WHERE actu_id IN ({placeholders})
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
    para un Proceso y Caso SIAD.
    """
    
    # Esta es tu nueva query, usando bind variables
    query = """
        SELECT saaf.aafi_id, saaf.aafi_tipo, saaf.aafi_nombre_descripcion, 
               saaf.aafi_numero_prox, saaf.aafi_estado, saaf.aafi_vigencia
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
    placeholders = ', '.join([f':id_bv{i}' for i in range(len(lista_aafi_ids))])
    # Usamos f-string para insertar el nombre de la columna (seguro porque lo validamos antes)
    query = f"""
        UPDATE siad_glob.siad_acto_administrativo_fin
        SET {columna_a_actualizar} = :valor_bv 
        WHERE AAFI_ID IN ({placeholders})
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
    
def get_actividades_ara(acfi_id):
    """
    Obtiene un MAPA de los procedimientos ARA existentes para este ACFI_ID (ARA_ID).
    Asume PROC_ID 1 a 7.
    """
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
        print(f"Capa 3: Mapa de estados (ARA) creado con {len(status_map)} items.")
        return status_map
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_actividades_ara): {e}")
        return {}

def actualizar_estado_procedimiento_ara(acfi_id, proc_id, nuevo_estado):
    """Actualiza el estado de UN procedimiento ARA."""
    if nuevo_estado not in ('ABIERTO', 'CERRADO'): return False
    query = """
        UPDATE own_ara3.ara3_audit_proc
        SET APAR_ESTADO = :estado_bv
        WHERE ARA_ID = :acfi_id_bv AND PROC_ID = :proc_id_bv
    """
    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {"estado_bv": nuevo_estado, "acfi_id_bv": acfi_id, "proc_id_bv": proc_id})
                connection.commit()
                print(f"Capa 3: Procedimiento ARA {proc_id} para AT {acfi_id} actualizado a {nuevo_estado}.")
                return True
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (actualizar_estado_procedimiento_ara): {e}")
        return False

def actualizar_estado_at_completa_ara(acfi_id, accion):
    """Actualiza la AT completa (ASTR y ARA) en una transacción."""
    if accion == 'reabrir':
        nuevo_estado_astr = 'EN_PROCESO'
        nuevo_estado_ara = 'EN_EJECUCION' # ¡OJO! Estado diferente
    elif accion == 'cerrar':
        nuevo_estado_astr = 'CERRADA'
        nuevo_estado_ara = 'CERRADA'
    else: return False

    query_astr = "UPDATE own_astr.astr_asignacion_trabajo SET astr_estado = :estado_astr WHERE acfi_id = :acfi_id_bv"
    query_ara = "UPDATE own_ara3.ara3_atencion_referencia SET ARA_ESTADO = :estado_ara WHERE ARA_ID = :acfi_id_bv"

    try:
        with oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_astr, {"estado_astr": nuevo_estado_astr, "acfi_id_bv": acfi_id})
                cursor.execute(query_ara, {"estado_ara": nuevo_estado_ara, "acfi_id_bv": acfi_id})
                connection.commit()
                print(f"Capa 3: Éxito. AT Completa ARA {acfi_id} actualizada a {accion}.")
                return True
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (actualizar_estado_at_completa_ara): {e}")
        return False
    
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