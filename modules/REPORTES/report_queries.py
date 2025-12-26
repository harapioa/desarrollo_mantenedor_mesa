# Archivo: modules/REPORTES/report_queries.py
# Este archivo solo almacena las grandes cadenas de texto SQL para los reportes.

# Reporte 1: Casos PD Entidad
QUERY_CASOS_PD_ENTIDAD = """
    SELECT DISTINCT
    caso.caso_id,
    proc.proc_id                                                    proc_id,
    proc.proc_numero_siad,
    caso.caso_numero,
    proc.proc_numero_siad
    || '.'
    || caso.caso_numero                                             nro_siad,
    /*proc.proc_numero_rpd
    || '.'
    || caso.caso_numero                                             caso_rpd,*/
    --proc.proc_numero_rpd                                            proc_rpd,
    to_char(caso.caso_fecha, 'YYYY')                                periodo_siad,
    caso.caso_categoria                                             categoria,
    caso.caso_tipo_prdi                                             tipo_prdi,
    caso.caso_estado_tramitacion                                    estado_tramitacion,
    caso.caso_tipo_orden                                            tipo_orden,
    caso.caso_estado_seguimiento                                    estado_seguimiento,
    ensv.ensv_nombre                                                entidad,
    ensv.ensv_id                                                    entidad_id,
    caso.caso_area                                                  area,
    caso.caso_fecha                                                 fecha,
    analista.usua_id                                                analista_id,
    analista.usua_nombre                                            analista_nombres,
    analista.usua_apellido_paterno                                  analista_paterno,
    analista.usua_apellido_materno                                  analista_materno,
    pdis.pdis_numero                                                pd_numero,
    pdis.pdis_fecha                                                 pd_fecha,
    unidad_ejecutora.unce_id                                        unidad_ejecutora_id,
    unidad_ejecutora.unce_nombre_ejecutor_pd                        unidad_ejecutora_nombre,
    entidad_ejecutora.ensv_id                                       entidad_ejecutora_id,
    entidad_ejecutora.ensv_nombre                                   entidad_ejecutora_nombre,
    pdad.pdis_id,
    prpd.lista_productos                                            productos_origen_pd,
    prpd.pd_origen_tipos,
    prpd.pd_origen_numeros,
    prpd.pd_origen_fechas,
    prpd.pd_origen_periodos,
    prpd.pd_origen_unidades,
    prod_orig.lista_productos_caso                                  productos_origen_caso,
    prod_orig.prod_tipos,
    prod_orig.prod_numeros,
    prod_orig.prod_fechas,
    prod_orig.prod_periodos,
    prod_orig.prod_unidades,
    sees.seesdescripcion                                            sector_estrategico,
    resolucion_inicio.resolucion_numero                             reso_ini_numero,
    resolucion_inicio.resolucion_fecha                              reso_ini_fecha,
    resolucion_inicio.resolucion_naturaleza                         reso_ini_naturaleza,
    resolucion_contralor.resolucion_numero                          reso_contralor_numero,
    resolucion_contralor.resolucion_fecha                           reso_contralor_fecha,
    resolucion_contralor.resolucion_naturaleza                      reso_contralor_naturaleza,
    resolucion_recurso.resolucion_numero                            reso_recurso_numero,
    resolucion_recurso.resolucion_fecha                             reso_recurso_fecha,
    resolucion_recurso.resolucion_naturaleza                        reso_recurso_naturaleza,
    oficio_remision.oficio_remision_numero,
    oficio_remision.oficio_remision_fecha,
    oficio_remision.oficio_remision_entidad,
    oficio_remision.oficio_remision_cargo,
    acto_admin_termino.acto_admin_termino_tipo,
    acto_admin_termino.acto_admin_termino_numero,
    acto_admin_termino.acto_admin_termino_fecha,
    acto_admin_termino.acto_admin_termino_conclusion,
    acto_admin_termino.acto_admin_termino_descripcion,
    lista_origenes_oficio.orof_origen,
    lista_origenes_oficio.orof_fuente,
    lista_origenes_oficio.orof_fecha,
    main.nombre                                                     materia,
    upper(trim(caso.caso_fi_nombres))
    || ' '
    || upper(trim(caso.caso_fi_apaterno))
    || ' '
    || upper(trim(caso.caso_fi_amaterno))                           fiscal_investigador,
    nvl(resp_adm_alcalde_prop.resp_adm_alcalde_prop, 0)             resp_adm_alcalde_propuesta,
    nvl(absolucion_propuesta.numero_medidas, 0)                     num_absolucion_propuesta,
    nvl(censura_propuesta.numero_medidas, 0)                        num_censura_propuesta,
    nvl(multa_propuesta.numero_medidas, 0)                          num_multa_propuesta,
    nvl(suspension_propuesta.numero_medidas, 0)                     num_suspension_propuesta,
    nvl(destitucion_propuesta.numero_medidas, 0)                    num_destitucion_propuesta,
    nvl(otra_propuesta.numero_medidas, 0)                           num_otra_propuesta,
    nvl(num_inculpados_propuesta.numero_inculpados, 0)              num_inculpados_propuesta,
    nvl(absolucion_aplicada.numero_medidas, 0)                      num_absolucion_aplicada,
    nvl(censura_aplicada.numero_medidas, 0)                         num_censura_aplicada,
    nvl(multa_aplicada.numero_medidas, 0)                           num_multa_aplicada,
    nvl(suspension_aplicada.numero_medidas, 0)                      num_suspension_aplicada,
    nvl(destitucion_aplicada.numero_medidas, 0)                     num_destitucion_aplicada,
    nvl(otra_aplicada.numero_medidas, 0)                            num_otra_aplicada,
    nvl(caso.caso_resp_adm_alcalde, 0)                              resp_adm_alcalde_aplicada,
    nvl(num_inculpados_aplicada.numero_inculpados, 0)               num_inculpados_aplicada,
    acto_inicio_caso.acto_inicio_caso_numero,
    acto_inicio_caso.acto_inicio_caso_fecha,
    acto_ter_ex_caso.acto_ter_ex_caso_numero,
    acto_ter_ex_caso.acto_ter_ex_caso_fecha,
    acto_ter_af_caso.acto_ter_af_caso_numero,
    acto_ter_af_caso.acto_ter_af_caso_fecha,
    acto_ter_af_caso.acto_ter_af_caso_conclusion,
    acto_ter_af_caso.acto_ter_af_caso_descripcion,
    acto_adm_reap_caso.acto_adm_reap_caso_numero,
    acto_adm_reap_caso.acto_adm_reap_caso_fecha,
    acto_adm_reap_caso.acto_adm_reap_caso_tipo,
    CASE
        WHEN materias.materias_generales = '.' THEN
            NULL
        ELSE
            regexp_substr(materias.materias_generales, '[^|]+', 1, 1)
    END                                                             AS materia_general_1,
    CASE
        WHEN materias.materias_especificas = '.' THEN
            NULL
        ELSE
            decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 1)
                   || '.'
                   || regexp_substr(materias.materias_especificas, '[^|]+', 1, 1),
                   '.',
                   NULL,
                   regexp_substr(materias.indices_mage, '[^|]+', 1, 1)
                   || '.'
                   || regexp_substr(materias.materias_especificas, '[^|]+', 1, 1))
    END                                                             AS materia_específica_1,
    regexp_substr(materias.materias_generales, '[^|]+', 1, 2)       materia_general_2,
    decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 2)
           || '.'
           || regexp_substr(materias.materias_especificas, '[^|]+', 1, 2),
           '.',
           NULL,
           regexp_substr(materias.indices_mage, '[^|]+', 1, 2)
           || '.'
           || regexp_substr(materias.materias_especificas, '[^|]+', 1, 2)) materia_específica_2,
    regexp_substr(materias.materias_generales, '[^|]+', 1, 3)       materia_general_3,
    decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 3)
           || '.'
           || regexp_substr(materias.materias_especificas, '[^|]+', 1, 3),
           '.',
           NULL,
           regexp_substr(materias.indices_mage, '[^|]+', 1, 3)
           || '.'
           || regexp_substr(materias.materias_especificas, '[^|]+', 1, 3)) materia_específica_3,
    regexp_substr(materias.materias_generales, '[^|]+', 1, 4)       materia_general_4,
    decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 4)
           || '.'
           || regexp_substr(materias.materias_especificas, '[^|]+', 1, 4),
           '.',
           NULL,
           regexp_substr(materias.indices_mage, '[^|]+', 1, 4)
           || '.'
           || regexp_substr(materias.materias_especificas, '[^|]+', 1, 4)) materia_específica_4,
    regexp_substr(materias.materias_generales, '[^|]+', 1, 5)       materia_general_5,
    decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 5)
           || '.'
           || regexp_substr(materias.materias_especificas, '[^|]+', 1, 5),
           '.',
           NULL,
           regexp_substr(materias.indices_mage, '[^|]+', 1, 5)
           || '.'
           || regexp_substr(materias.materias_especificas, '[^|]+', 1, 5)) materia_específica_5,
    prof.prof_numero,
    prof.prof_fecha,
    prof.prof_periodo
FROM
         siad_glob.siad_caso caso
    INNER JOIN siad_glob.siad_proceso                  proc ON caso.proc_id = proc.proc_id
                                              AND proc.proc_vigencia = 'VIGENTE'
    INNER JOIN own_glob.acfi_actividad_fiscalizacion   acfi ON proc.proc_id = acfi.acfi_id
                                                             AND acfi.acfi_estado = 'VIGENTE'
    INNER JOIN own_glob.glob_entidades_servicios       ensv ON caso.ensv_id = ensv.ensv_id
    LEFT JOIN siad_glob.siad_proceso_producto         prpr ON proc.proc_id = prpr.proc_id
    LEFT JOIN own_arqt.arqt_usuarios                  analista ON analista.usua_id = caso.usua_id
    LEFT JOIN siad_glob.acfi_vinculadas_v1_1          acvi_pdis ON acvi_pdis.proc_id = proc.proc_id
    LEFT JOIN own_eeprdi.eeprdi_proc_disciplinario    pdis ON acvi_pdis.acfi_id = pdis.pdis_id
    LEFT JOIN own_glob.glob_unidades_control_ext      unidad_ejecutora ON unidad_ejecutora.unce_id = pdis.unce_id
    LEFT JOIN own_glob.glob_entidades_servicios       entidad_ejecutora ON caso.caso_entidad_instruye_id = entidad_ejecutora.ensv_id
    LEFT JOIN siad_glob.acfi_vinculadas_v1_1          acvi_acfi ON acvi_acfi.proc_id = proc.proc_id
    LEFT JOIN sica_wl_1.eeprdi_prdi_ad_v1             pdad ON acvi_acfi.acfi_id = pdad.pdis_id
    LEFT JOIN sica_wl_1.eeprdi_prod_origen_pdis_v1_1  prpd ON pdis.pdis_id = prpd.pdis_id
    INNER JOIN parametro.tblsectorestrategico          sees ON sees.seescodigo = ensv.ensv_sector_estrategico
    LEFT JOIN (
        SELECT
            acvi.proc_id,
            LISTAGG(acvi.tipo_producto
                    || ';'
                    || acvi.producto_numero
                    || '/'
                    || acvi.producto_periodo
                    || '; '
                    || acvi.unidad_origen
                    || '; ',
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                acvi.proc_id
            ) lista_productos_caso,
            LISTAGG(acvi.tipo_producto || CHR(10)) WITHIN GROUP(
            ORDER BY
                acvi.proc_id
            ) prod_tipos,
            LISTAGG(acvi.producto_numero || CHR(10)) WITHIN GROUP(
            ORDER BY
                acvi.proc_id
            ) prod_numeros,
            LISTAGG(acvi.producto_fecha || CHR(10)) WITHIN GROUP(
            ORDER BY
                acvi.proc_id
            ) prod_fechas,
            LISTAGG(acvi.producto_periodo || CHR(10)) WITHIN GROUP(
            ORDER BY
                acvi.proc_id
            ) prod_periodos,
            LISTAGG(acvi.unidad_origen || CHR(10)) WITHIN GROUP(
            ORDER BY
                acvi.proc_id
            ) prod_unidades
        FROM
            siad_glob.acfi_vinculadas_v1_1 acvi
        WHERE
            acvi.proc_id IS NOT NULL
        GROUP BY
            acvi.proc_id
    )                                       prod_orig ON prod_orig.proc_id = proc.proc_id
    LEFT JOIN sica_wl_1.eeprdi_resoluciones_pdis_v1_1 resolucion_inicio ON pdis.pdis_id = resolucion_inicio.pdis_id
                                                                           AND resolucion_inicio.acti_tipo = 'RESOLUCION_INICIO'
    LEFT JOIN sica_wl_1.eeprdi_resoluciones_pdis_v1_1 resolucion_contralor ON pdis.pdis_id = resolucion_contralor.pdis_id
                                                                              AND resolucion_contralor.acti_tipo IN ( 'RESOLUCION_CGR_EXENTA'
                                                                              , 'RESOLUCION_CGR_AFECTA' )
    LEFT JOIN sica_wl_1.eeprdi_resoluciones_pdis_v1_1 resolucion_recurso ON pdis.pdis_id = resolucion_recurso.pdis_id
                                                                            AND resolucion_recurso.acti_tipo IN ( 'RES_RECURSO_JERARQUICO'
                                                                            , 'RES_RECURSO_REPOSICION' )
    LEFT JOIN (
        SELECT
            reen.caso_id,
            LISTAGG(reen.reen_oficio_numero,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                reen.caso_id ASC
            ) oficio_remision_numero,
            LISTAGG(to_char(reen.reen_oficio_fecha, 'DD-MM-YYYY'),
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                reen.caso_id ASC
            ) oficio_remision_fecha,
            LISTAGG(upper(trim(enti_dest.ensv_nombre)),
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                reen.caso_id ASC
            ) oficio_remision_entidad,
            LISTAGG(upper(trim(dest.dest_cargo)),
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                reen.caso_id ASC
            ) oficio_remision_cargo
        FROM
                 siad_glob.siad_remision_exp_entidad reen
            INNER JOIN siad_glob.siad_caso               caso ON caso.caso_id = reen.caso_id
                                                   AND caso.caso_vigencia = 'VIGENTE'
            INNER JOIN siad_glob.siad_proceso            proc ON proc.proc_id = caso.proc_id
                                                      AND proc.proc_vigencia = 'VIGENTE'
            LEFT JOIN siad_glob.siad_destinatario       dest ON reen.reen_id = dest.reen_id
            LEFT JOIN own_glob.glob_entidades_servicios enti_dest ON dest.ensv_id = enti_dest.ensv_id
        WHERE
            reen.reen_vigencia = 'VIGENTE'
        GROUP BY
            reen.caso_id
    )                                       oficio_remision ON caso.caso_id = oficio_remision.caso_id
    LEFT JOIN (
        SELECT
            aafi.caso_id,
            LISTAGG(aafi.aafi_tipo,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.caso_id DESC,
                aafi.aafi_fecha DESC
            ) acto_admin_termino_tipo,
            LISTAGG(aafi.aafi_numero_prox,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.caso_id DESC,
                aafi.aafi_fecha DESC
            ) acto_admin_termino_numero,
            LISTAGG(to_char(aafi.aafi_fecha, 'DD-MM-YYYY'),
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.caso_id DESC,
                aafi.aafi_fecha DESC
            ) acto_admin_termino_fecha,
            LISTAGG(aafi.aafi_conclusion,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.caso_id DESC,
                aafi.aafi_fecha DESC
            ) acto_admin_termino_conclusion,
            LISTAGG(aafi.aafi_nombre_descripcion,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.caso_id DESC,
                aafi.aafi_fecha DESC
            ) acto_admin_termino_descripcion
        FROM
                 siad_glob.siad_acto_administrativo_fin aafi
            INNER JOIN siad_glob.siad_caso caso ON caso.caso_id = aafi.caso_id
        WHERE
                caso.caso_vigencia = 'VIGENTE'
            AND aafi.aafi_estado = 'ACEPTADA'
            AND aafi.aafi_vigencia = 'VIGENTE'
        GROUP BY
            aafi.caso_id
    )                                       acto_admin_termino ON acto_admin_termino.caso_id = caso.caso_id
    LEFT JOIN sica_wl_1.eeprdi_resoluciones_pdis_v1_1 reso_cgr_exenta ON pdis.pdis_id = reso_cgr_exenta.pdis_id
                                                                         AND reso_cgr_exenta.acti_tipo IN ( 'RESOLUCION_CGR_EXENTA', 'RESOLUCION_CGR_AFECTA'
                                                                         )
    LEFT JOIN (
        SELECT
            orof.pdis_id,
            LISTAGG(orof.orof_origen,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                orof.orof_fecha ASC
            ) orof_origen,
            LISTAGG(orof.orof_fuente,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                orof.orof_fecha ASC
            ) orof_fuente,
            LISTAGG(to_char(orof.orof_fecha, 'DD-MM-YYYY'),
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                orof.orof_fecha ASC
            ) orof_fecha
        FROM
            own_eeprdi.eeprdi_origen_oficio orof
        GROUP BY
            orof.pdis_id
    )                                       lista_origenes_oficio ON lista_origenes_oficio.pdis_id = pdis.pdis_id
    LEFT JOIN own_glob3.glob3_materia_info            main ON caso.main_id = main.main_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_prop_medida = 'ABSOLUCION'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       absolucion_propuesta ON absolucion_propuesta.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_prop_medida = 'CENSURA'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       censura_propuesta ON censura_propuesta.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_prop_medida IN ( 'MULTA', 'MULTA_BENEFICIO_FISCAL' )
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       multa_propuesta ON multa_propuesta.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_prop_medida = 'SUSPENSION'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       suspension_propuesta ON suspension_propuesta.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_prop_medida = 'DESTITUCION'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       destitucion_propuesta ON destitucion_propuesta.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_prop_medida = 'OTRAS'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       otra_propuesta ON otra_propuesta.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_inculpados
        FROM
                 siad_glob.siad_caso caso
            INNER JOIN siad_glob.siad_inculpado incu ON caso.caso_id = incu.caso_id
        WHERE
                caso.caso_vigencia = 'VIGENTE'
            AND incu.incu_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       num_inculpados_propuesta ON num_inculpados_propuesta.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            acti_vifi.pdis_id,
            vista_fiscal.vifi_resp_administrativa resp_adm_alcalde_prop
        FROM
            own_eeprdi.eeprdi_vista_fiscal       vista_fiscal
            LEFT JOIN own_eeprdi.eeprdi_actividad          acti_vifi ON ( acti_vifi.acti_id = vista_fiscal.acti_id )
            LEFT JOIN own_eeprdi.eeprdi_revision_actividad revf ON acti_vifi.acti_id = revf.acti_id
                                                                   AND revf.reac_accion = 'FIRMAR'
        WHERE
                acti_vifi.acti_tipo = 'VISTA_FISCAL'
            AND acti_vifi.acti_estado IN ( 'APROBADA', 'FINALIZADA' )
            AND vista_fiscal.vifi_id = (
                SELECT
                    MAX(vifi1.vifi_id)
                FROM
                    own_eeprdi.eeprdi_vista_fiscal vifi1
                    LEFT JOIN own_eeprdi.eeprdi_actividad    acti_vifi1 ON ( acti_vifi1.acti_id = vifi1.acti_id )
                WHERE
                        acti_vifi1.acti_tipo = 'VISTA_FISCAL'
                    AND acti_vifi1.pdis_id = acti_vifi.pdis_id
                    AND acti_vifi1.acti_estado IN ( 'APROBADA', 'FINALIZADA' )
            )
    )                                       resp_adm_alcalde_prop ON resp_adm_alcalde_prop.pdis_id = pdis.pdis_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_apli_medida = 'ABSOLUCION'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       absolucion_aplicada ON absolucion_aplicada.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_apli_medida = 'CENSURA'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       censura_aplicada ON censura_aplicada.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_apli_medida IN ( 'MULTA', 'MULTA_BENEFICIO_FISCAL' )
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       multa_aplicada ON multa_aplicada.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_apli_medida = 'SUSPENSION'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       suspension_aplicada ON suspension_aplicada.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_apli_medida = 'DESTITUCION'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       destitucion_aplicada ON destitucion_aplicada.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_medidas
        FROM
                 siad_glob.siad_inculpado incu
            INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                   AND incu.incu_apli_medida = 'OTRAS'
        WHERE
                incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_vigencia = 'VIGENTE'
        GROUP BY
            caso.caso_id
    )                                       otra_aplicada ON otra_aplicada.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            COUNT(incu.incu_id) numero_inculpados
        FROM
                 siad_glob.siad_caso caso
            INNER JOIN siad_glob.siad_inculpado incu ON caso.caso_id = incu.caso_id
        WHERE
                caso.caso_vigencia = 'VIGENTE'
            AND incu.incu_vigencia = 'VIGENTE'
            AND caso.caso_estado_tramitacion = 'TERMINADO'
            AND incu.incu_apli_medida = 'SOBRESEIMIENTO'
        GROUP BY
            caso.caso_id
    )                                       num_inculpados_aplicada ON num_inculpados_aplicada.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            LISTAGG(actu.actu_numero_prox,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                actu.actu_fecha ASC
            ) acto_inicio_caso_numero,
            LISTAGG(to_char(actu.actu_fecha, 'DD-MM-YYYY'),
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                actu.actu_fecha ASC
            ) acto_inicio_caso_fecha
        FROM
                 siad_glob.siad_caso caso
            INNER JOIN siad_glob.siad_tipo_actuacion tiac ON caso.caso_id = tiac.caso_id
                                                             AND tiac.tiac_nombre = 'COPIA_ACTO_ADMINISTRATIVO_DE_INICIO'
            INNER JOIN siad_glob.siad_actuacion      actu ON actu.tiac_id = tiac.tiac_id
                                                        AND actu.actu_estado IN ( 'ACEPTADA', 'APROBADA' )
        GROUP BY
            caso.caso_id,
            tiac.tiac_nombre,
            actu.actu_estado
    )                                       acto_inicio_caso ON acto_inicio_caso.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            tiac.tiac_nombre,
            actu.actu_estado,
            LISTAGG(actu.actu_numero_prox,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                actu.actu_fecha ASC
            ) acto_adm_reap_caso_numero,
            LISTAGG(to_char(actu.actu_fecha, 'DD-MM-YYYY'),
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                actu.actu_fecha ASC
            ) acto_adm_reap_caso_fecha,
            LISTAGG(actu.actu_tipo_documento,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                actu.actu_fecha ASC
            ) acto_adm_reap_caso_tipo
        FROM
                 siad_glob.siad_caso caso
            INNER JOIN siad_glob.siad_tipo_actuacion tiac ON caso.caso_id = tiac.caso_id
                                                             AND tiac.tiac_nombre = 'COPIA_ACTO_ADMINISTRATIVO_DE_REAPERTURA'
            INNER JOIN siad_glob.siad_actuacion      actu ON actu.tiac_id = tiac.tiac_id
                                                        AND actu.actu_estado IN ( 'ACEPTADA', 'APROBADA' )
        GROUP BY
            caso.caso_id,
            tiac.tiac_nombre,
            actu.actu_estado
    )                                       acto_adm_reap_caso ON acto_adm_reap_caso.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            LISTAGG(aafi.aafi_numero_prox,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.aafi_fecha
            ) acto_ter_ex_caso_numero,
            LISTAGG(to_char(aafi.aafi_fecha, 'DD-MM-YYYY'),
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.aafi_fecha
            ) acto_ter_ex_caso_fecha
        FROM
                 siad_glob.siad_caso caso
            INNER JOIN siad_glob.siad_acto_administrativo_fin aafi ON caso.caso_id = aafi.caso_id
                                                                      AND aafi.aafi_estado IN ( 'ACEPTADA', 'APROBADA' )
                                                                      AND aafi.aafi_tipo = 'EXENTO'
        GROUP BY
            caso.caso_id,
            aafi.aafi_estado,
            aafi.aafi_tipo
    )                                       acto_ter_ex_caso ON acto_ter_ex_caso.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT
            caso.caso_id,
            LISTAGG(aafi.aafi_numero_prox,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.aafi_fecha
            ) acto_ter_af_caso_numero,
            LISTAGG(to_char(aafi.aafi_fecha, 'DD-MM-YYYY'),
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.aafi_fecha
            ) acto_ter_af_caso_fecha,
            LISTAGG(aafi.aafi_conclusion,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.aafi_fecha
            ) acto_ter_af_caso_conclusion,
            LISTAGG(aafi.aafi_nombre_descripcion,
                    CHR(10)) WITHIN GROUP(
            ORDER BY
                aafi.aafi_fecha
            ) acto_ter_af_caso_descripcion
        FROM
                 siad_glob.siad_caso caso
            INNER JOIN siad_glob.siad_acto_administrativo_fin aafi ON caso.caso_id = aafi.caso_id
                                                                      AND aafi.aafi_estado IN ( 'ACEPTADA', 'APROBADA' )
                                                                      AND aafi.aafi_tipo = 'AFECTO'
        GROUP BY
            caso.caso_id,
            aafi.aafi_estado,
            aafi.aafi_tipo
    )                                       acto_ter_af_caso ON acto_ter_af_caso.caso_id = caso.caso_id
    LEFT JOIN (
        SELECT DISTINCT
            caso.caso_id,
            LISTAGG(mage.mage_indice, '|') WITHIN GROUP(
            ORDER BY
                mage.mage_indice
            ) indices_mage,
            LISTAGG(mage.mage_indice
                    || '.'
                    || mage.mage_nombre, '|') WITHIN GROUP(
            ORDER BY
                mage.mage_indice
            ) materias_generales,
            LISTAGG(maes.maes_indice
                    || '.'
                    || maes.maes_nombre, '|') WITHIN GROUP(
            ORDER BY
                maes.maes_indice
            ) materias_especificas
        FROM
            siad_glob.siad_caso                  caso
            LEFT JOIN siad_glob.siad_materia_caso          mate ON caso.caso_id = mate.caso_id
            LEFT JOIN own_eeprdi.eeprdi_materia_especifica maes ON mate.maes_id = maes.maes_id
            LEFT JOIN own_eeprdi.eeprdi_materia_general    mage ON mage.mage_id = maes.mage_id
        GROUP BY
            caso.caso_id
    )                                       materias ON caso.caso_id = materias.caso_id
    left join siad_glob.siad_producto_de_oficio prof on proc.proc_id = prof.proc_id
WHERE
    caso.caso_vigencia = 'VIGENTE' and caso.caso_categoria = 'INSTRUCCION_CGR'
ORDER BY
    proc.proc_numero_siad ASC,
    caso.caso_numero ASC 
"""

# Reporte 2: Productos no vinculados
QUERY_PRODUCTOS_NO_VINCULADOS = """
    SELECT
        SUB1.ACFI_ID,
        SUB1.ACFI_TIPO,
        SUB1.CONTEXTO,
        SUB1.PRODUCTO_NUMERO,
        SUB1.PRODUCTO_PERIODO,
        SUB1.PRODUCTO_FECHA,
        SUB1.NOTIF_FECHA_RECEPCION,
        SUB1.UNIDAD_ORIGEN_ID,
        SUB1.UNIDAD_ORIGEN,
        SUB1.ENTIDAD_SERVICIO_ID,
        SUB1.ENTIDAD_SERVICIO,
        SUB1.ADIN_NOMBRE
    FROM ( SELECT
        v12.*
    FROM
        siad_glob.acfi_origen_view_v1_2 v12
    WHERE v12.producto_fecha >= TO_DATE('01-01-2016', 'DD-MM-YYYY') 
    ) sub1 order by 7 desc
"""

# Reporte 3: PDs y fechas resoluciones
QUERY_PD_FECHAS_RESOLUCIONES = """
    
    SELECT DISTINCT
        REGE.PDIS_ID "PD ID",
        REGE.PDIS_TIPO "PD TIPO",
        REGE.PDIS_NUMERO "PD NÚMERO",
        REGE.PDIS_FECHA "PD FECHA",
        REGE.PDIS_CATEGORIA "PD CATEGORÍA",
        NVL2(REGE.RESINI_NUMERO, 'PD' || LPAD(REGE.RESINI_NUMERO, 5, '0'), NULL) "RESOLUCIÓN INICIO NÚMERO",
        REGE.RESINI_FECHA "RESOLUCIÓN INICIO FECHA",
        REGE.ENSV_NOMBRE "ENTIDAD/SERVICIO",
        REGE.UNIDAD "UNIDAD",
        REGE.ETAPA_TRAMITACION "ETAPA TRAMITACIÓN",
        REGE.VIFI_FALTA_PROBIDAD "FALTA PROBIDAD",
        REGE.VIFI_RESP_CIVIL "RESPONSABILIDAD CIVIL",
        REGE.VIFI_EVENTUAL_DELITO "EVENTUAL DELITO",
        REGE.VIFI_RESP_ADMINISTRATIVA "RESPONSABILIDAD ADMINISTRATIVA",
        REGE.NUMERO_MEDIDAS "NÚMERO MEDIDAS",
        REGE.FISCAL_INSTRUCTOR "FISCAL INSTRUCTOR",
        REGE.OROF_ORIGEN "ORIGEN OFICIO TIPO",
        REGE.OROF_FUENTE "ORIGEN OFICIO FUENTE",
        REGE.OROF_FECHA "ORIGEN OFICIO FECHA",
        REGE.OROF_COMENTARIO "ORIGEN OFICIO COMENTARIO",
        REGE.FECHA_CIERRE_ETAPA_INDAGATORIA "FECHA CIERRE ETAPA INDAGATORIA",
        REGE.FECHA_VISTA_FISCAL "FECHA VISTA FISCAL",
        NVL2(REGE.RES_CONTRALOR_EXENTA_NUMERO, 'PD' || LPAD(REGE.RES_CONTRALOR_EXENTA_NUMERO, 5, '0'), NULL) "RES. CONTRALOR EX. NÚMERO",
        REGE.RES_CONTRALOR_EXENTA_FECHA "RES. CONTRALOR EX. FECHA",
        REGE.RES_CONTRALOR_EXENTA_ACTI_ID "RES. CONTRALOR EX. ID",
        REGE.RES_CONTRALOR_EXENTA_TIPO "RES. CONTRALOR EX. TIPO",
        REGE.RCE_FECHA_JEFATURA "REX.CONTR.FECHA AP. JEF.",
        REGE.RCE_FECHA_FISCAL "REX.CONTR.FECHA AP. FISCAL",
        NVL2(REGE.RES_CONTRALOR_AFECTA_NUMERO, 'PD' || LPAD(REGE.RES_CONTRALOR_AFECTA_NUMERO, 5, '0'), NULL) "RES. CONTRALOR AFECTA NÚMERO",
        REGE.RES_CONTRALOR_AFECTA_FECHA "RES. CONTRALOR AFECTA FECHA",
        REGE.RES_CONTRALOR_AFECTA_ACTI_ID "RES. CONTRALOR AFECTA ID",
        REGE.RES_CONTRALOR_AFECTA_TIPO "RES. CONTRALOR AFECTA TIPO",
        REGE.RCA_FECHA_JEFATURA "RES.AF.CONTR.FECHA AP.JEF.",
        REGE.RCA_FECHA_FISCAL "RES.AF.CONTR.FECHA AP.FISCAL",
        NVL2(REGE.RES_RESREC_NUMERO, 'PD' || LPAD(REGE.RES_RESREC_NUMERO, 5, '0'), NULL) "RES. RESUELVE RECURSO NÚMERO",    
        REGE.RES_RESREC_FECHA "RES. RESUELVE RECURSO FECHA",
        REGE.RES_RESREC_ACTI_ID "RES. RESUELVE RECURSO ID",
        REGE.RES_RESREC_TIPO "RES. RESUELVE RECURSO TIPO", 
        REGE.RES_REC_FECHA_JEFATURA "RES.RESUELVE REC.FECHA.AP.JEF.",
        REGE.RES_REC_FECHA_FISCAL "RES.RESUELVE REC.FECHA AP.FIS.",
        REGEXP_SUBSTR(MATE.MATERIAS_GENERALES, '[^|]+', 1, 1) "MATERIA GENERAL 1",
        DECODE(REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 1) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 1), '.', NULL, REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 1) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 1)) "MATERIA ESPECÍFICA 1",
        REGEXP_SUBSTR(MATE.MATERIAS_GENERALES, '[^|]+', 1, 2) "MATERIA GENERAL 2",
        DECODE(REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 2) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 2), '.', NULL, REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 2) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 2)) "MATERIA ESPECÍFICA 2",
        REGEXP_SUBSTR(MATE.MATERIAS_GENERALES, '[^|]+', 1, 3) "MATERIA GENERAL 3",
        DECODE(REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 3) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 3), '.', NULL, REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 3) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 3)) "MATERIA ESPECÍFICA 3",
        REGEXP_SUBSTR(MATE.MATERIAS_GENERALES, '[^|]+', 1, 4) "MATERIA GENERAL 4",
        DECODE(REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 4) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 4), '.', NULL, REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 4) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 4)) "MATERIA ESPECÍFICA 4",
        REGEXP_SUBSTR(MATE.MATERIAS_GENERALES, '[^|]+', 1, 5) "MATERIA GENERAL 5",
        DECODE(REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 5) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 5), '.', NULL, REGEXP_SUBSTR(MATE.INDICES_MAGE, '[^|]+', 1, 5) || '.' || REGEXP_SUBSTR(MATE.MATERIAS_ESPECIFICAS, '[^|]+', 1, 5)) "MATERIA ESPECÍFICA 5"
    FROM 
        SICA_WL_1.EEPRDI_REPORTE_GENERAL_V3 REGE
        LEFT JOIN
        (
            SELECT DISTINCT
            PDIS.PDIS_ID, 
            LISTAGG(MAGE.MAGE_INDICE, '|') WITHIN GROUP (ORDER BY MAGE.MAGE_INDICE) INDICES_MAGE,
            LISTAGG(MAGE.MAGE_INDICE || '.' || MAGE.MAGE_NOMBRE, '|') WITHIN GROUP (ORDER BY MAGE.MAGE_INDICE) MATERIAS_GENERALES,
            LISTAGG(MAES.MAES_INDICE || '.' || MAES.MAES_NOMBRE, '|') WITHIN GROUP (ORDER BY MAES.MAES_INDICE) MATERIAS_ESPECIFICAS
            FROM OWN_EEPRDI.EEPRDI_PROC_DISCIPLINARIO PDIS
            LEFT JOIN OWN_EEPRDI.EEPRDI_MATERIA_PD MAPD
            ON PDIS.PDIS_ID = MAPD.PDIS_ID
            LEFT JOIN OWN_EEPRDI.EEPRDI_MATERIA_ESPECIFICA MAES
            ON MAPD.MAES_ID = MAES.MAES_ID
            LEFT JOIN OWN_EEPRDI.EEPRDI_MATERIA_GENERAL MAGE
            ON MAGE.MAGE_ID = MAES.MAGE_ID
            WHERE PDIS.PDIS_VIGENCIA = 'VIGENTE'
            GROUP BY PDIS.PDIS_ID
        ) MATE
        ON REGE.PDIS_ID = MATE.PDIS_ID
        WHERE REGE.UNIDAD NOT IN ('UNIDAD PRDI PRUEBAS', 'DTRR')
"""

# Reporte 4: Actos totales SIAD
QUERY_ACTOS_TOTALES_SIAD = """
    WITH v1 AS (
    SELECT DISTINCT
        caso.caso_id,
        proc.proc_id                                                    proc_id,
        proc.proc_numero_siad,
        caso.caso_numero,
        proc.proc_numero_siad
        || '.'
        || caso.caso_numero                                             nro_siad,
        proc.proc_numero_rpd
        || '.'
        || caso.caso_numero                                             caso_rpd,
        proc.proc_numero_rpd                                            proc_rpd,
        to_char(caso.caso_fecha, 'YYYY')                                periodo_siad,
        prof.prof_numero                                                producto_oficio_numero,
        prof.prof_fecha                                                 producto_oficio_fecha,
        prof.prof_periodo                                               producto_oficio_periodo,
        nvl(actos_total_caso.q, 0)                                      cantidad_actuaciones,
        nvl(actos_enviados_cgr.q, 0)                                    cantidad_actuaciones_enviadas_a_cgr,
        nvl(actos_borrador_cgr.q, 0)                                    cantidad_actuaciones_borrador_cgr,
        nvl(actos_aprobados_cgr.q, 0)                                   cantidad_actuaciones_aprobadas,
        nvl(actos_rechazados_cgr.q, 0)                                  cantidad_actuaciones_rechazadas,
        caso.caso_categoria                                             categoria,
        caso.caso_tipo_prdi                                             tipo_prdi,
        caso.caso_estado_tramitacion                                    estado_tramitacion,
        caso.caso_tipo_orden                                            tipo_orden,
        caso.caso_estado_seguimiento                                    estado_seguimiento,
        ensv.ensv_nombre                                                entidad,
        ensv.ensv_id                                                    entidad_id,
        caso.caso_area                                                  area,
        caso.caso_fecha                                                 fecha,
        analista.usua_id                                                analista_id,
        analista.usua_nombre                                            analista_nombres,
        analista.usua_apellido_paterno                                  analista_paterno,
        analista.usua_apellido_materno                                  analista_materno,
        --unce_acfi.unce_nombre                                           nombre_unidad_analista,
        unce_acfi.unce_descripcion                                      analista_unidad,
        pdis.pdis_numero                                                pd_numero,
        pdis.pdis_fecha                                                 pd_fecha,
        unidad_ejecutora.unce_id                                        unidad_ejecutora_id,
        unidad_ejecutora.unce_nombre_ejecutor_pd                        unidad_ejecutora_nombre,
        entidad_ejecutora.ensv_id                                       entidad_ejecutora_id,
        entidad_ejecutora.ensv_nombre                                   entidad_ejecutora_nombre,
        pdad.pdis_id,
        prpd.lista_productos                                            productos_origen_pd,
        prpd.pd_origen_tipos,
        prpd.pd_origen_numeros,
        prpd.pd_origen_fechas,
        prpd.pd_origen_periodos,
        prpd.pd_origen_unidades,
        prod_orig.lista_productos_caso                                  productos_origen_caso,
        prod_orig.prod_tipos,
        prod_orig.prod_numeros,
        prod_orig.prod_fechas,
        prod_orig.prod_periodos,
        prod_orig.prod_unidades,
        sees.seesdescripcion                                            sector_estrategico,
        resolucion_inicio.resolucion_numero                             reso_ini_numero,
        resolucion_inicio.resolucion_fecha                              reso_ini_fecha,
        resolucion_inicio.resolucion_naturaleza                         reso_ini_naturaleza,
        resolucion_contralor.resolucion_numero                          reso_contralor_numero,
        resolucion_contralor.resolucion_fecha                           reso_contralor_fecha,
        resolucion_contralor.resolucion_naturaleza                      reso_contralor_naturaleza,
        resolucion_recurso.resolucion_numero                            reso_recurso_numero,
        resolucion_recurso.resolucion_fecha                             reso_recurso_fecha,
        resolucion_recurso.resolucion_naturaleza                        reso_recurso_naturaleza,
        oficio_remision.oficio_remision_numero,
        oficio_remision.oficio_remision_fecha,
        oficio_remision.oficio_remision_entidad,
        oficio_remision.oficio_remision_cargo,
        acto_admin_termino.acto_admin_termino_tipo,
        acto_admin_termino.acto_admin_termino_numero,
        acto_admin_termino.acto_admin_termino_fecha,
        acto_admin_termino.acto_admin_termino_conclusion,
        acto_admin_termino.acto_admin_termino_descripcion,
        lista_origenes_oficio.orof_origen,
        lista_origenes_oficio.orof_fuente,
        lista_origenes_oficio.orof_fecha,
        main.nombre                                                     materia,
        upper(trim(caso.caso_fi_nombres))
        || ' '
        || upper(trim(caso.caso_fi_apaterno))
        || ' '
        || upper(trim(caso.caso_fi_amaterno))                           fiscal_investigador,
        nvl(resp_adm_alcalde_prop.resp_adm_alcalde_prop, 0)             resp_adm_alcalde_propuesta,
        nvl(absolucion_propuesta.numero_medidas, 0)                     num_absolucion_propuesta,
        nvl(censura_propuesta.numero_medidas, 0)                        num_censura_propuesta,
        nvl(multa_propuesta.numero_medidas, 0)                          num_multa_propuesta,
        nvl(suspension_propuesta.numero_medidas, 0)                     num_suspension_propuesta,
        nvl(destitucion_propuesta.numero_medidas, 0)                    num_destitucion_propuesta,
        nvl(otra_propuesta.numero_medidas, 0)                           num_otra_propuesta,
        nvl(num_inculpados_propuesta.numero_inculpados, 0)              num_inculpados_propuesta,
        nvl(absolucion_aplicada.numero_medidas, 0)                      num_absolucion_aplicada,
        nvl(censura_aplicada.numero_medidas, 0)                         num_censura_aplicada,
        nvl(multa_aplicada.numero_medidas, 0)                           num_multa_aplicada,
        nvl(suspension_aplicada.numero_medidas, 0)                      num_suspension_aplicada,
        nvl(destitucion_aplicada.numero_medidas, 0)                     num_destitucion_aplicada,
        nvl(otra_aplicada.numero_medidas, 0)                            num_otra_aplicada,
        nvl(caso.caso_resp_adm_alcalde, 0)                              resp_adm_alcalde_aplicada,
        nvl(num_inculpados_aplicada.numero_inculpados, 0)               num_inculpados_aplicada,
        acto_inicio_caso.acto_inicio_caso_numero,
        acto_inicio_caso.acto_inicio_caso_fecha,
        acto_ter_ex_caso.acto_ter_ex_caso_numero,
        acto_ter_ex_caso.acto_ter_ex_caso_fecha,
        acto_ter_af_caso.acto_ter_af_caso_numero,
        acto_ter_af_caso.acto_ter_af_caso_fecha,
        acto_ter_af_caso.acto_ter_af_caso_conclusion,
        acto_ter_af_caso.acto_ter_af_caso_descripcion,
        acto_adm_reap_caso.acto_adm_reap_caso_numero,
        acto_adm_reap_caso.acto_adm_reap_caso_fecha,
        acto_adm_reap_caso.acto_adm_reap_caso_tipo,
        CASE
            WHEN materias.materias_generales = '.' THEN
                NULL
            ELSE
                regexp_substr(materias.materias_generales, '[^|]+', 1, 1)
        END                                                             AS materia_general_1,
        CASE
            WHEN materias.materias_especificas = '.' THEN
                NULL
            ELSE
                decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 1)
                       || '.'
                       || regexp_substr(materias.materias_especificas, '[^|]+', 1, 1),
                       '.',
                       NULL,
                       regexp_substr(materias.indices_mage, '[^|]+', 1, 1)
                       || '.'
                       || regexp_substr(materias.materias_especificas, '[^|]+', 1, 1))
        END                                                             AS materia_específica_1,
        regexp_substr(materias.materias_generales, '[^|]+', 1, 2)       materia_general_2,
        decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 2)
               || '.'
               || regexp_substr(materias.materias_especificas, '[^|]+', 1, 2),
               '.',
               NULL,
               regexp_substr(materias.indices_mage, '[^|]+', 1, 2)
               || '.'
               || regexp_substr(materias.materias_especificas, '[^|]+', 1, 2)) materia_específica_2,
        regexp_substr(materias.materias_generales, '[^|]+', 1, 3)       materia_general_3,
        decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 3)
               || '.'
               || regexp_substr(materias.materias_especificas, '[^|]+', 1, 3),
               '.',
               NULL,
               regexp_substr(materias.indices_mage, '[^|]+', 1, 3)
               || '.'
               || regexp_substr(materias.materias_especificas, '[^|]+', 1, 3)) materia_específica_3,
        regexp_substr(materias.materias_generales, '[^|]+', 1, 4)       materia_general_4,
        decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 4)
               || '.'
               || regexp_substr(materias.materias_especificas, '[^|]+', 1, 4),
               '.',
               NULL,
               regexp_substr(materias.indices_mage, '[^|]+', 1, 4)
               || '.'
               || regexp_substr(materias.materias_especificas, '[^|]+', 1, 4)) materia_específica_4,
        regexp_substr(materias.materias_generales, '[^|]+', 1, 5)       materia_general_5,
        decode(regexp_substr(materias.indices_mage, '[^|]+', 1, 5)
               || '.'
               || regexp_substr(materias.materias_especificas, '[^|]+', 1, 5),
               '.',
               NULL,
               regexp_substr(materias.indices_mage, '[^|]+', 1, 5)
               || '.'
               || regexp_substr(materias.materias_especificas, '[^|]+', 1, 5)) materia_específica_5
    FROM
             siad_glob.siad_caso caso
        INNER JOIN siad_glob.siad_proceso                  proc ON caso.proc_id = proc.proc_id
                                                  AND proc.proc_vigencia = 'VIGENTE'
        INNER JOIN own_glob.acfi_actividad_fiscalizacion   acfi ON proc.proc_id = acfi.acfi_id
                                                                 AND acfi.acfi_estado = 'VIGENTE'
        INNER JOIN own_glob.glob_unidades_control_ext      unce_acfi ON acfi.unce_id = unce_acfi.unce_id
        
        INNER JOIN own_glob.glob_entidades_servicios       ensv ON caso.ensv_id = ensv.ensv_id
        LEFT JOIN siad_glob.siad_proceso_producto         prpr ON proc.proc_id = prpr.proc_id
        LEFT JOIN own_arqt.arqt_usuarios                  analista ON analista.usua_id = caso.usua_id
        LEFT JOIN siad_glob.acfi_vinculadas_v1_1          acvi_pdis ON acvi_pdis.proc_id = proc.proc_id
        LEFT JOIN own_eeprdi.eeprdi_proc_disciplinario    pdis ON acvi_pdis.acfi_id = pdis.pdis_id
        LEFT JOIN own_glob.glob_unidades_control_ext      unidad_ejecutora ON unidad_ejecutora.unce_id = pdis.unce_id
        LEFT JOIN own_glob.glob_entidades_servicios       entidad_ejecutora ON caso.caso_entidad_instruye_id = entidad_ejecutora.ensv_id
        LEFT JOIN siad_glob.acfi_vinculadas_v1_1          acvi_acfi ON acvi_acfi.proc_id = proc.proc_id
        LEFT JOIN sica_wl_1.eeprdi_prdi_ad_v1             pdad ON acvi_acfi.acfi_id = pdad.pdis_id
        LEFT JOIN sica_wl_1.eeprdi_prod_origen_pdis_v1_1  prpd ON pdis.pdis_id = prpd.pdis_id
        INNER JOIN parametro.tblsectorestrategico          sees ON sees.seescodigo = ensv.ensv_sector_estrategico
        LEFT JOIN (
            SELECT
                acvi.proc_id,
                LISTAGG(acvi.tipo_producto
                        || ';'
                        || acvi.producto_numero
                        || '/'
                        || acvi.producto_periodo
                        || '; '
                        || acvi.unidad_origen
                        || '; ',
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    acvi.proc_id
                ) lista_productos_caso,
                LISTAGG(acvi.tipo_producto || CHR(10)) WITHIN GROUP(
                ORDER BY
                    acvi.proc_id
                ) prod_tipos,
                LISTAGG(acvi.producto_numero || CHR(10)) WITHIN GROUP(
                ORDER BY
                    acvi.proc_id
                ) prod_numeros,
                LISTAGG(acvi.producto_fecha || CHR(10)) WITHIN GROUP(
                ORDER BY
                    acvi.proc_id
                ) prod_fechas,
                LISTAGG(acvi.producto_periodo || CHR(10)) WITHIN GROUP(
                ORDER BY
                    acvi.proc_id
                ) prod_periodos,
                LISTAGG(acvi.unidad_origen || CHR(10)) WITHIN GROUP(
                ORDER BY
                    acvi.proc_id
                ) prod_unidades
            FROM
                siad_glob.acfi_vinculadas_v1_1 acvi
            WHERE
                acvi.proc_id IS NOT NULL
            GROUP BY
                acvi.proc_id
        )                                       prod_orig ON prod_orig.proc_id = proc.proc_id
        LEFT JOIN sica_wl_1.eeprdi_resoluciones_pdis_v1_1 resolucion_inicio ON pdis.pdis_id = resolucion_inicio.pdis_id
                                                                               AND resolucion_inicio.acti_tipo = 'RESOLUCION_INICIO'
        LEFT JOIN sica_wl_1.eeprdi_resoluciones_pdis_v1_1 resolucion_contralor ON pdis.pdis_id = resolucion_contralor.pdis_id
                                                                                  AND resolucion_contralor.acti_tipo IN ( 'RESOLUCION_CGR_EXENTA'
                                                                                  , 'RESOLUCION_CGR_AFECTA' )
        LEFT JOIN sica_wl_1.eeprdi_resoluciones_pdis_v1_1 resolucion_recurso ON pdis.pdis_id = resolucion_recurso.pdis_id
                                                                                AND resolucion_recurso.acti_tipo IN ( 'RES_RECURSO_JERARQUICO'
                                                                                , 'RES_RECURSO_REPOSICION' )
        LEFT JOIN (
            SELECT
                reen.caso_id,
                LISTAGG(reen.reen_oficio_numero,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    reen.caso_id ASC
                ) oficio_remision_numero,
                LISTAGG(to_char(reen.reen_oficio_fecha, 'DD-MM-YYYY'),
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    reen.caso_id ASC
                ) oficio_remision_fecha,
                LISTAGG(upper(trim(enti_dest.ensv_nombre)),
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    reen.caso_id ASC
                ) oficio_remision_entidad,
                LISTAGG(upper(trim(dest.dest_cargo)),
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    reen.caso_id ASC
                ) oficio_remision_cargo
            FROM
                     siad_glob.siad_remision_exp_entidad reen
                INNER JOIN siad_glob.siad_caso               caso ON caso.caso_id = reen.caso_id
                                                       AND caso.caso_vigencia = 'VIGENTE'
                INNER JOIN siad_glob.siad_proceso            proc ON proc.proc_id = caso.proc_id
                                                          AND proc.proc_vigencia = 'VIGENTE'
                LEFT JOIN siad_glob.siad_destinatario       dest ON reen.reen_id = dest.reen_id
                LEFT JOIN own_glob.glob_entidades_servicios enti_dest ON dest.ensv_id = enti_dest.ensv_id
            WHERE
                reen.reen_vigencia = 'VIGENTE'
            GROUP BY
                reen.caso_id
        )                                       oficio_remision ON caso.caso_id = oficio_remision.caso_id
        LEFT JOIN (
            SELECT
                aafi.caso_id,
                LISTAGG(aafi.aafi_tipo,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.caso_id DESC,
                    aafi.aafi_fecha DESC
                ) acto_admin_termino_tipo,
                LISTAGG(aafi.aafi_numero_prox,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.caso_id DESC,
                    aafi.aafi_fecha DESC
                ) acto_admin_termino_numero,
                LISTAGG(to_char(aafi.aafi_fecha, 'DD-MM-YYYY'),
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.caso_id DESC,
                    aafi.aafi_fecha DESC
                ) acto_admin_termino_fecha,
                LISTAGG(aafi.aafi_conclusion,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.caso_id DESC,
                    aafi.aafi_fecha DESC
                ) acto_admin_termino_conclusion,
                LISTAGG(aafi.aafi_nombre_descripcion,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.caso_id DESC,
                    aafi.aafi_fecha DESC
                ) acto_admin_termino_descripcion
            FROM
                     siad_glob.siad_acto_administrativo_fin aafi
                INNER JOIN siad_glob.siad_caso caso ON caso.caso_id = aafi.caso_id
            WHERE
                    caso.caso_vigencia = 'VIGENTE'
                AND aafi.aafi_estado = 'ACEPTADA'
                AND aafi.aafi_vigencia = 'VIGENTE'
            GROUP BY
                aafi.caso_id
        )                                       acto_admin_termino ON acto_admin_termino.caso_id = caso.caso_id
        LEFT JOIN sica_wl_1.eeprdi_resoluciones_pdis_v1_1 reso_cgr_exenta ON pdis.pdis_id = reso_cgr_exenta.pdis_id
                                                                             AND reso_cgr_exenta.acti_tipo IN ( 'RESOLUCION_CGR_EXENTA'
                                                                             , 'RESOLUCION_CGR_AFECTA' )
        LEFT JOIN (
            SELECT
                orof.pdis_id,
                LISTAGG(orof.orof_origen,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    orof.orof_fecha ASC
                ) orof_origen,
                LISTAGG(orof.orof_fuente,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    orof.orof_fecha ASC
                ) orof_fuente,
                LISTAGG(to_char(orof.orof_fecha, 'DD-MM-YYYY'),
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    orof.orof_fecha ASC
                ) orof_fecha
            FROM
                own_eeprdi.eeprdi_origen_oficio orof
            GROUP BY
                orof.pdis_id
        )                                       lista_origenes_oficio ON lista_origenes_oficio.pdis_id = pdis.pdis_id
        LEFT JOIN own_glob3.glob3_materia_info            main ON caso.main_id = main.main_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_prop_medida = 'ABSOLUCION'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       absolucion_propuesta ON absolucion_propuesta.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_prop_medida = 'CENSURA'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       censura_propuesta ON censura_propuesta.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_prop_medida IN ( 'MULTA', 'MULTA_BENEFICIO_FISCAL' )
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       multa_propuesta ON multa_propuesta.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_prop_medida = 'SUSPENSION'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       suspension_propuesta ON suspension_propuesta.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_prop_medida = 'DESTITUCION'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       destitucion_propuesta ON destitucion_propuesta.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_prop_medida = 'OTRAS'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       otra_propuesta ON otra_propuesta.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_inculpados
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_inculpado incu ON caso.caso_id = incu.caso_id
            WHERE
                    caso.caso_vigencia = 'VIGENTE'
                AND incu.incu_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       num_inculpados_propuesta ON num_inculpados_propuesta.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                acti_vifi.pdis_id,
                vista_fiscal.vifi_resp_administrativa resp_adm_alcalde_prop
            FROM
                own_eeprdi.eeprdi_vista_fiscal       vista_fiscal
                LEFT JOIN own_eeprdi.eeprdi_actividad          acti_vifi ON ( acti_vifi.acti_id = vista_fiscal.acti_id )
                LEFT JOIN own_eeprdi.eeprdi_revision_actividad revf ON acti_vifi.acti_id = revf.acti_id
                                                                       AND revf.reac_accion = 'FIRMAR'
            WHERE
                    acti_vifi.acti_tipo = 'VISTA_FISCAL'
                AND acti_vifi.acti_estado IN ( 'APROBADA', 'FINALIZADA' )
                AND vista_fiscal.vifi_id = (
                    SELECT
                        MAX(vifi1.vifi_id)
                    FROM
                        own_eeprdi.eeprdi_vista_fiscal vifi1
                        LEFT JOIN own_eeprdi.eeprdi_actividad    acti_vifi1 ON ( acti_vifi1.acti_id = vifi1.acti_id )
                    WHERE
                            acti_vifi1.acti_tipo = 'VISTA_FISCAL'
                        AND acti_vifi1.pdis_id = acti_vifi.pdis_id
                        AND acti_vifi1.acti_estado IN ( 'APROBADA', 'FINALIZADA' )
                )
        )                                       resp_adm_alcalde_prop ON resp_adm_alcalde_prop.pdis_id = pdis.pdis_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_apli_medida = 'ABSOLUCION'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       absolucion_aplicada ON absolucion_aplicada.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_apli_medida = 'CENSURA'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       censura_aplicada ON censura_aplicada.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_apli_medida IN ( 'MULTA', 'MULTA_BENEFICIO_FISCAL' )
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       multa_aplicada ON multa_aplicada.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_apli_medida = 'SUSPENSION'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       suspension_aplicada ON suspension_aplicada.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_apli_medida = 'DESTITUCION'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       destitucion_aplicada ON destitucion_aplicada.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_medidas
            FROM
                     siad_glob.siad_inculpado incu
                INNER JOIN siad_glob.siad_caso caso ON incu.caso_id = caso.caso_id
                                                       AND incu.incu_apli_medida = 'OTRAS'
            WHERE
                    incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       otra_aplicada ON otra_aplicada.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(incu.incu_id) numero_inculpados
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_inculpado incu ON caso.caso_id = incu.caso_id
            WHERE
                    caso.caso_vigencia = 'VIGENTE'
                AND incu.incu_vigencia = 'VIGENTE'
                AND caso.caso_estado_tramitacion = 'TERMINADO'
                AND incu.incu_apli_medida = 'SOBRESEIMIENTO'
            GROUP BY
                caso.caso_id
        )                                       num_inculpados_aplicada ON num_inculpados_aplicada.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                LISTAGG(actu.actu_numero_prox,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    actu.actu_fecha ASC
                ) acto_inicio_caso_numero,
                LISTAGG(to_char(actu.actu_fecha, 'DD-MM-YYYY'),
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    actu.actu_fecha ASC
                ) acto_inicio_caso_fecha
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_tipo_actuacion tiac ON caso.caso_id = tiac.caso_id
                                                                 AND tiac.tiac_nombre = 'COPIA_ACTO_ADMINISTRATIVO_DE_INICIO'
                INNER JOIN siad_glob.siad_actuacion      actu ON actu.tiac_id = tiac.tiac_id
                                                            AND actu.actu_estado IN ( 'ACEPTADA', 'APROBADA', 'ENVIADA_CGR')
            GROUP BY
                caso.caso_id,
                tiac.tiac_nombre,
                actu.actu_estado
        )                                       acto_inicio_caso ON acto_inicio_caso.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(actu.actu_id) q
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_tipo_actuacion tiac ON caso.caso_id = tiac.caso_id
                INNER JOIN siad_glob.siad_actuacion      actu ON actu.tiac_id = tiac.tiac_id
            WHERE
                actu.actu_vigencia = 'VIGENTE'
            GROUP BY
                caso.caso_id
        )                                       actos_total_caso ON actos_total_caso.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(actu.actu_id) q
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_tipo_actuacion tiac ON caso.caso_id = tiac.caso_id
                INNER JOIN siad_glob.siad_actuacion      actu ON actu.tiac_id = tiac.tiac_id
            WHERE
                    actu.actu_vigencia = 'VIGENTE'
                AND actu.actu_estado = 'ENVIADA_CGR'
            GROUP BY
                caso.caso_id
        )                                       actos_enviados_cgr ON actos_enviados_cgr.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(actu.actu_id) q
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_tipo_actuacion tiac ON caso.caso_id = tiac.caso_id
                INNER JOIN siad_glob.siad_actuacion      actu ON actu.tiac_id = tiac.tiac_id
            WHERE
                    actu.actu_vigencia = 'VIGENTE'
                AND actu.actu_estado IN ( 'ACEPTADA', 'APROBADA' )
            GROUP BY
                caso.caso_id
        )                                       actos_aprobados_cgr ON actos_aprobados_cgr.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(actu.actu_id) q
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_tipo_actuacion tiac ON caso.caso_id = tiac.caso_id
                INNER JOIN siad_glob.siad_actuacion      actu ON actu.tiac_id = tiac.tiac_id
            WHERE
                    actu.actu_vigencia = 'VIGENTE'
                AND actu.actu_estado = 'RECHAZADA'
            GROUP BY
                caso.caso_id
        )                                       actos_rechazados_cgr ON actos_rechazados_cgr.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                COUNT(actu.actu_id) q
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_tipo_actuacion tiac ON caso.caso_id = tiac.caso_id
                INNER JOIN siad_glob.siad_actuacion      actu ON actu.tiac_id = tiac.tiac_id
            WHERE
                    actu.actu_vigencia = 'VIGENTE'
                AND actu.actu_estado = 'BORRADOR_CGR'
            GROUP BY
                caso.caso_id
        )                                       actos_borrador_cgr ON actos_borrador_cgr.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                tiac.tiac_nombre,
                actu.actu_estado,
                LISTAGG(actu.actu_numero_prox,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    actu.actu_fecha ASC
                ) acto_adm_reap_caso_numero,
                LISTAGG(to_char(actu.actu_fecha, 'DD-MM-YYYY'),
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    actu.actu_fecha ASC
                ) acto_adm_reap_caso_fecha,
                LISTAGG(actu.actu_tipo_documento,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    actu.actu_fecha ASC
                ) acto_adm_reap_caso_tipo
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_tipo_actuacion tiac ON caso.caso_id = tiac.caso_id
                                                                 AND tiac.tiac_nombre = 'COPIA_ACTO_ADMINISTRATIVO_DE_REAPERTURA'
                INNER JOIN siad_glob.siad_actuacion      actu ON actu.tiac_id = tiac.tiac_id
                                                            AND actu.actu_estado IN ( 'ACEPTADA', 'APROBADA', 'ENVIADA_CGR')
            GROUP BY
                caso.caso_id,
                tiac.tiac_nombre,
                actu.actu_estado
        )                                       acto_adm_reap_caso ON acto_adm_reap_caso.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                LISTAGG(aafi.aafi_numero_prox,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.aafi_fecha
                ) acto_ter_ex_caso_numero,
                LISTAGG(to_char(aafi.aafi_fecha, 'DD-MM-YYYY'),
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.aafi_fecha
                ) acto_ter_ex_caso_fecha
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_acto_administrativo_fin aafi ON caso.caso_id = aafi.caso_id
                                                                          AND aafi.aafi_estado IN ( 'ACEPTADA', 'APROBADA', 'ENVIADA_CGR')
                                                                          AND aafi.aafi_tipo = 'EXENTO'
            GROUP BY
                caso.caso_id,
                aafi.aafi_estado,
                aafi.aafi_tipo
        )                                       acto_ter_ex_caso ON acto_ter_ex_caso.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT
                caso.caso_id,
                LISTAGG(aafi.aafi_numero_prox,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.aafi_fecha
                ) acto_ter_af_caso_numero,
                LISTAGG(to_char(aafi.aafi_fecha, 'DD-MM-YYYY'),
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.aafi_fecha
                ) acto_ter_af_caso_fecha,
                LISTAGG(aafi.aafi_conclusion,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.aafi_fecha
                ) acto_ter_af_caso_conclusion,
                LISTAGG(aafi.aafi_nombre_descripcion,
                        CHR(10)) WITHIN GROUP(
                ORDER BY
                    aafi.aafi_fecha
                ) acto_ter_af_caso_descripcion
            FROM
                     siad_glob.siad_caso caso
                INNER JOIN siad_glob.siad_acto_administrativo_fin aafi ON caso.caso_id = aafi.caso_id
                                                                          AND aafi.aafi_estado IN ( 'ACEPTADA', 'APROBADA', 'ENVIADA_CGR')
                                                                          AND aafi.aafi_tipo = 'AFECTO'
            GROUP BY
                caso.caso_id,
                aafi.aafi_estado,
                aafi.aafi_tipo
        )                                       acto_ter_af_caso ON acto_ter_af_caso.caso_id = caso.caso_id
        LEFT JOIN (
            SELECT DISTINCT
                caso.caso_id,
                LISTAGG(mage.mage_indice, '|') WITHIN GROUP(
                ORDER BY
                    mage.mage_indice
                ) indices_mage,
                LISTAGG(mage.mage_indice
                        || '.'
                        || mage.mage_nombre, '|') WITHIN GROUP(
                ORDER BY
                    mage.mage_indice
                ) materias_generales,
                LISTAGG(maes.maes_indice
                        || '.'
                        || maes.maes_nombre, '|') WITHIN GROUP(
                ORDER BY
                    maes.maes_indice
                ) materias_especificas
            FROM
                siad_glob.siad_caso                  caso
                LEFT JOIN siad_glob.siad_materia_caso          mate ON caso.caso_id = mate.caso_id
                LEFT JOIN own_eeprdi.eeprdi_materia_especifica maes ON mate.maes_id = maes.maes_id
                LEFT JOIN own_eeprdi.eeprdi_materia_general    mage ON mage.mage_id = maes.mage_id
            GROUP BY
                caso.caso_id
        )                                       materias ON caso.caso_id = materias.caso_id
        LEFT JOIN (
            SELECT
                proc.proc_id,
                prof.prof_numero,
                prof.prof_periodo,
                prof.prof_fecha
            FROM
                     siad_glob.siad_producto_de_oficio prof
                INNER JOIN siad_glob.siad_proceso proc ON proc.proc_id = prof.proc_id
            WHERE
                prof.prof_vigencia = 'VIGENTE'
        )                                       prof ON prof.proc_id = proc.proc_id
    WHERE
            caso.caso_vigencia = 'VIGENTE'
        --AND caso.caso_categoria = 'PD_ENTIDAD'
    ORDER BY
        proc.proc_numero_siad ASC,
        caso.caso_numero ASC
)
SELECT
    v1.*
FROM
    v1
WHERE 1=1
--and
    /*
    producto_oficio_numero
    || '-'
    || producto_oficio_periodo IN ( 'E82804-2025', 'E84047-2025', 'E95677-2025', 'E109022-2025', 'E128548-2025',
                                    'E128553-2025', 'E128556-2025', 'E128558-2025', 'E128561-2025', 'E128563-2025',
                                    'E128565-2025', 'E131793-2025' , 'E123145-2025') 
    */
    /*producto_oficio_numero
    || '-'
    || producto_oficio_periodo IN ('E123145-2025')*/
    --v1.proc_numero_siad IN (16573, 16574)
    --v1.nro_siad IN ('13997.1', '13965.1')
"""

# Reporte 5: Reporte de contrapartes SIAD
QUERY_CONTRAPARTES_SIAD = """
SELECT
    uses.uses_id USUARIO_ID,
    uses.ensv_id ENTIDAD_ID,
    uses.uses_nombres NOMBRES,
    uses.uses_apaterno "APELLIDO 1",
    uses.uses_amaterno "APELLIDO 2",
    uses.uses_run RUN,
    uses.uses_dv DV,
    ensv.ensv_nombre ENTIDAD,
    uses.uses_email EMAIL,
    uses.uses_cargo CARGO,
    uses.uses_vigencia VIGENCIA
FROM
    sica_escritorio_arqt.sies_usuario_escritorio uses
INNER JOIN
sica_escritorio_arqt.sies_usuario_proceso uspr
ON uses.uses_id = uspr.uses_id
INNER JOIN
own_glob.glob_entidades_servicios ensv
ON ensv.ensv_id = uses.ensv_id
WHERE 
    1=1
    and uses.uses_vigencia = 'VIGENTE'
    and uspr.uspr_rol = 'CONTRAPARTE_SIAD' and uspr.uspr_vigencia = 'VIGENTE'
ORDER BY
    8 asc, 4 asc, 5 asc, 3 asc
"""