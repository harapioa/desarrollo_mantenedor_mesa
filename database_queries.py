# database_queries.py

import oracledb
import config

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
    
def buscar_auditorias(periodo, nro_at, uce_id, servicio_id, nro_programa, tipo_origen, num_referencia, num_acfi=None):
    """
    Ejecuta la búsqueda principal con filtros dinámicos.
    """

    inner_select_query = """
        SELECT
            ASTR.ACFI_ID AS ACFI_ID,
            UCE.unce_nombre AS UCE,
            PRGE.PRGE_NUMERO AS N_PROGRAMA,
            ENSV.ENSV_NOMBRE AS SERVICIO,
            ASTR.ASTR_ESTADO AS ESTADO,
            ASTR.ASTR_TIPO_ORIGEN AS TIPO_ORIGEN,
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
        LEFT JOIN own_astr.astr_presentacion_at pres ON pres.astr_id = ASTR.astr_id
        LEFT JOIN own_plpr.plpr_presentaciones_deim prdi ON prdi.PRDI_ID = pres.PRDI_ID
    """

    where_conditions = []
    bind_vars = {}

    where_conditions.append("ASTR.ASTR_TIPO_ORIGEN = :tipo_origen_bv")
    bind_vars["tipo_origen_bv"] = tipo_origen
    where_conditions.append("ASTR.ASTR_ESTADO NOT IN ('ELIMINADA', 'BORRADOR')")

    if num_acfi:
        where_conditions.append("ASTR.ACFI_ID = :num_acfi_bv")
        bind_vars["num_acfi_bv"] = num_acfi
    else:
        where_conditions.append("PRGE.prge_periodo = :periodo_bv")
        bind_vars["periodo_bv"] = periodo
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

    if num_referencia:
        where_conditions.append("UPPER(prdi.PRDI_NUMERO) LIKE UPPER(:num_ref_bv)")
        bind_vars["num_ref_bv"] = f"%{num_referencia}%"

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
        FROM QueryNumerada
        WHERE RN = 1
        ORDER BY ACFI_ID DESC
    """

    print("--- CONSULTA DINÁMICA EJECUTADA ---")
    print(final_query)
    print("--- CON VALORES ---")
    print(bind_vars)
    print("---------------------------------")

    resultados = []
    try:
        with oracledb.connect(
            user=config.DB_USER, 
            password=config.DB_PASSWORD, 
            dsn=config.DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(final_query, bind_vars)
                column_names = [desc[0] for desc in cursor.description]
                
                for row in cursor.fetchall():
                    resultado_dict = dict(zip(column_names, row))
                    resultados.append(resultado_dict)
                    
        print(f"Capa 3: Búsqueda encontró {len(resultados)} resultados.")
        return resultados
    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (buscar_auditorias): {e}")
        return None

def get_detalle_at_info(acfi_id):
    """
    Obtiene la información de cabecera para un ACFI_ID específico.
    Si es INVESTIGACION, también obtiene INVE_ESTADO.
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
                
                column_names = [desc[0] for desc in cursor.description]
                row = cursor.fetchone()
                
                if row:
                    info = dict(zip(column_names, row))
                    
                    # Si es INVESTIGACION, obtener INVE_ESTADO adicional
                    if info.get('ASTR_TIPO_ORIGEN') == 'INVESTIGACION':
                        query_inve = """
                            SELECT INVE.INVE_ESTADO
                            FROM OWN_INVE3.INVE3_INVEST_ESPECIAL INVE
                            WHERE INVE.INVE_ID = :acfi_id
                            FETCH FIRST 1 ROWS ONLY
                        """
                        cursor.execute(query_inve, {"acfi_id": acfi_id})
                        inve_row = cursor.fetchone()
                        
                        if inve_row:
                            info['INVE_ESTADO'] = inve_row[0]
                        else:
                            info['INVE_ESTADO'] = None
                    
                    print(f"Capa 3: Información de detalle para {acfi_id} encontrada.")
                    return info
        
        print(f"Capa 3: No se encontró información para {acfi_id}.")
        return None

    except oracledb.DatabaseError as e:
        print(f"Error en Capa 3 (get_detalle_at_info): {e}")
        return None
 