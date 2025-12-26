# modules/PRDI/queries.py
import oracledb
from ..COMMON.db import get_db_connection

# ... (Mantén tu MAPA_ETAPAS y get_prdi_actividades igual) ...
MAPA_ETAPAS = {
    'INDAGATORIA': 'CP_PP_INDAGATORIA',
    'ACUSATORIA': 'CP_PP_ACUSATORIA',
    'RESOLUTIVA': 'CP_PP_RESOLUTIVA',
    'CUADERNO_SEPARADO': 'CS_CUADERNO_SEPARADO_1'
}

# --- NUEVO: Buscar ID por Resolución ---
def get_pdis_id_por_resolucion(numero_res, anio_res):
    """
    Busca el PDIS_ID asociado a una Resolución de Inicio.
    """
    sql = """
        SELECT acti.pdis_id
        FROM own_eeprdi.eeprdi_resolucion reso
        LEFT JOIN own_eeprdi.eeprdi_actividad acti ON acti.reso_id = reso.reso_id
        WHERE reso.RESO_NUMERO = :numero
          AND TO_CHAR(reso.RESO_FECHA, 'YYYY') = :anio
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, numero=numero_res, anio=anio_res)
                row = cursor.fetchone()
                if row:
                    return row[0] # Retorna solo el ID (ej: 101280)
        return None
    except Exception as e:
        print(f"Error en get_pdis_id_por_resolucion: {e}")
        return None

# --- NUEVO: Buscar Cabecera por ID (Para usar después de encontrar la resolución) ---
def get_prdi_cabecera_por_id(pdis_id):
    sql = """
        SELECT 
            pdis.PDIS_ID, 
            pdis.PDIS_TIPO,
            pdis.PDIS_ESTADO,
            TO_CHAR(pdis.PDIS_FECHA, 'DD/MM/YYYY') as PDIS_FECHA,
            pdis.PDIS_VIGENCIA
        FROM own_eeprdi.eeprdi_proc_disciplinario pdis 
        WHERE pdis.PDIS_ID = :id
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, id=pdis_id)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    cursor.rowfactory = lambda *args: dict(zip(columns, args))
                    return cursor.fetchone()
        return None
    except Exception as e:
        print(f"Error en get_prdi_cabecera_por_id: {e}")
        return None

# --- EXISTENTE (Se mantiene para la búsqueda normal) ---
def get_prdi_cabecera(numero, anio):
    sql = """
        SELECT 
            pdis.PDIS_ID, 
            pdis.PDIS_TIPO,
            pdis.PDIS_ESTADO,
            TO_CHAR(pdis.PDIS_FECHA, 'DD/MM/YYYY') as PDIS_FECHA,
            pdis.PDIS_VIGENCIA
        FROM own_eeprdi.eeprdi_proc_disciplinario pdis 
        WHERE pdis.PDIS_NUMERO = :numero 
          AND TO_CHAR(pdis.PDIS_FECHA, 'YYYY') = :anio
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, numero=numero, anio=anio)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    cursor.rowfactory = lambda *args: dict(zip(columns, args))
                    return cursor.fetchone()
        return None
    except Exception as e:
        print(f"Error en get_prdi_cabecera: {e}")
        return None

# ... (Mantén get_prdi_actividades igual) ...
def get_prdi_actividades(pdis_id, etapa_codigo):
    # (Tu código anterior con el ajuste de fecha que hicimos)
    sql = """
        SELECT 
            acti.ACTI_ID, 
            foli.FOLI_DESDE,
            foli.FOLI_HASTA, 
            foli.FOLI_PREFIJO, 
            foli.FOLI_TEXTO, 
            TO_CHAR(acti.ACTI_FECHA_REGISTRO, 'DD/MM/YYYY HH24:MI:SS') as ACTI_FECHA,
            acti.ACTI_ESTADO
        FROM own_eeprdi.eeprdi_actividad acti
        LEFT JOIN own_eeprdi.eeprdi_folio foli ON foli.acti_id = acti.acti_id 
        WHERE acti.pdis_id = :pdis_id
          AND acti.ACTI_UBICACION = :etapa
          AND acti.ACTI_ESTADO not in ( 'NO_VIGENTE' )
        ORDER BY foli.FOLI_DESDE
    """
    # ... resto del try/catch ...
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, pdis_id=pdis_id, etapa=etapa_codigo)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    cursor.rowfactory = lambda *args: dict(zip(columns, args))
                    return cursor.fetchall()
        return []
    except Exception as e:
        print(f"Error en get_prdi_actividades: {e}")
        return []

# --- Función para eliminar actividad (Lógica) ---
def eliminar_actividad_prdi(acti_id):
    """
    1. Marca la actividad como 'NO_VIGENTE'.
    2. Limpia los folios (NULL) asociados a esa actividad.
    """
    sql_estado = """
        UPDATE own_eeprdi.eeprdi_actividad
        SET ACTI_ESTADO = 'NO_VIGENTE'
        WHERE ACTI_ID = :id
    """
    
    sql_folio = """
        UPDATE own_eeprdi.eeprdi_folio
        SET FOLI_DESDE = null, FOLI_HASTA = null
        WHERE ACTI_ID = :id
    """
    
    try:
        # Usamos 'con' para manejar la transacción manualmente
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Ejecutar cambio de estado
            cursor.execute(sql_estado, id=acti_id)
            
            # 2. Ejecutar limpieza de folios
            cursor.execute(sql_folio, id=acti_id)
            
            # 3. Confirmar cambios (Commit)
            conn.commit()
            return True
            
        except Exception as e:
            # Si algo falla en medio, deshacemos todo
            conn.rollback()
            print(f"Error en transacción eliminar_actividad_prdi: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Error de conexión en eliminar_actividad_prdi: {e}")
        return False
    
def devolver_actividad_carpeta(acti_id):
    """
    Establece ACTI_VISIBLE_EXPEDIENTE = 0 para la actividad dada.
    """
    sql = """
        UPDATE own_eeprdi.eeprdi_actividad
        SET ACTI_VISIBLE_EXPEDIENTE = 0
        WHERE ACTI_ID = :id
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, id=acti_id)
                conn.commit()
                return True
    except Exception as e:
        print(f"Error en devolver_actividad_carpeta: {e}")
        return False

def reabrir_actividad_prdi(acti_id):
    """
    1. Cambia estado de la actividad a 'REVISION'.
    2. Devuelve el flujo de revisión de 'FIRMAR' a 'BORRADOR'.
    """
    sql_actividad = """
        UPDATE own_eeprdi.eeprdi_actividad
        SET ACTI_ESTADO = 'REVISION'
        WHERE ACTI_ID = :id
    """
    
    sql_flujo = """
        UPDATE own_eeprdi.eeprdi_revision_actividad
        SET REAC_ACCION = 'BORRADOR'
        WHERE ACTI_ID = :id 
          AND REAC_ACCION = 'FIRMAR'
    """
    
    try:
        # Usamos transacción manual
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Actualizar estado principal
            cursor.execute(sql_actividad, id=acti_id)
            
            # 2. Actualizar flujo (Solo si estaba en FIRMAR)
            cursor.execute(sql_flujo, id=acti_id)
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error en transacción reabrir_actividad_prdi: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Error de conexión en reabrir_actividad_prdi: {e}")
        return False

def get_datos_para_respaldo(pdis_id):
    """
    Obtiene TODOS los registros de actividad/folio para un PRDI específico,
    incluyendo su etapa, para guardarlos en el archivo de respaldo.
    """
    sql = """
        SELECT 
            acti.ACTI_ID, 
            foli.FOLI_DESDE, 
            foli.FOLI_HASTA, 
            acti.ACTI_ESTADO,
            acti.ACTI_UBICACION -- Guardamos también la etapa (INDAGATORIA, etc.)
        FROM own_eeprdi.eeprdi_actividad acti
        LEFT JOIN own_eeprdi.eeprdi_folio foli ON foli.acti_id = acti.acti_id
        WHERE acti.pdis_id = :id
        ORDER BY foli.FOLI_DESDE ASC NULLS LAST
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, id=pdis_id)
                # Retornamos lista de tuplas directamente para escribir rápido en CSV
                return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo datos para respaldo: {e}")
        return []

def renumerar_folios_prdi(pdis_id):
    """
    Recalcula los folios para que sean consecutivos, eliminando huecos.
    Se basa en el orden actual de FOLI_DESDE.
    """
    # 1. Obtenemos TODAS las actividades con folio del PRDI, ordenadas
    sql_select = """
        SELECT acti.ACTI_ID, foli.FOLI_DESDE, foli.FOLI_HASTA
        FROM own_eeprdi.eeprdi_actividad acti
        JOIN own_eeprdi.eeprdi_folio foli ON foli.acti_id = acti.acti_id
        WHERE acti.pdis_id = :id
          AND acti.ACTI_ESTADO != 'NO_VIGENTE' -- Ignoramos las eliminadas
          AND foli.FOLI_DESDE IS NOT NULL
        ORDER BY foli.FOLI_DESDE ASC
    """
    
    sql_update = """
        UPDATE own_eeprdi.eeprdi_folio
        SET FOLI_DESDE = :nuevo_desde, FOLI_HASTA = :nuevo_hasta
        WHERE ACTI_ID = :acti_id
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # A. Obtener lista actual
        cursor.execute(sql_select, id=pdis_id)
        # Fetchall devuelve lista de tuplas [(acti_id, desde, hasta), ...]
        filas = cursor.fetchall() 
        
        if not filas:
            return {"success": False, "message": "No hay folios para renumerar."}

        # B. Calcular y Actualizar
        # Asumimos que el primer folio debe mantenerse o arrancar desde el primero encontrado
        # Si quieres que siempre arranque en 1, cambia esto a: contador_folio = 1
        contador_folio = filas[0][1] 
        
        updates_realizados = 0

        for row in filas:
            acti_id = row[0]
            antiguo_desde = row[1]
            antiguo_hasta = row[2]
            
            # Calculamos cuantas páginas tiene este documento
            # Ejemplo: 1841 a 1842 = 2 páginas
            paginas = (antiguo_hasta - antiguo_desde) + 1
            
            # Calculamos nuevos rangos
            nuevo_desde = contador_folio
            nuevo_hasta = contador_folio + paginas - 1
            
            # Solo actualizamos si cambiaron los valores (optimización)
            if nuevo_desde != antiguo_desde or nuevo_hasta != antiguo_hasta:
                cursor.execute(sql_update, 
                               nuevo_desde=nuevo_desde, 
                               nuevo_hasta=nuevo_hasta, 
                               acti_id=acti_id)
                updates_realizados += 1
            
            # Avanzamos el contador para el siguiente documento
            contador_folio = nuevo_hasta + 1
            
        conn.commit()
        return {"success": True, "message": f"Se reordenaron {updates_realizados} registros correctamente."}
        
    except Exception as e:
        conn.rollback()
        print(f"Error en renumerar_folios_prdi: {e}")
        return {"success": False, "message": str(e)}
    finally:
        cursor.close()
        conn.close()