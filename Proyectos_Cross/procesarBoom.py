import os
import shutil
import tempfile
import pandas as pd
import csv

from Proyectos_Cross.log import log


# ============================================================
# ENVIAR MENSAJE DE PROGRESO
# ============================================================

def enviar_progreso(progreso, mensaje):

    log(mensaje)

    if progreso is not None:
        progreso(mensaje)


# ============================================================
# GENERAR INFO BOM
# ============================================================

def generarInfo(
    ruta_proyecto,
    ruta_archivo,
    año,
    progreso=None
):

    enviar_progreso(
        progreso,
        f"📅 Iniciando procesamiento del año {año}"
    )

    # ========================================================
    # CREAR CARPETA TEMPORAL DEL AÑO
    # ========================================================

    ruta_año = os.path.join(
        ruta_proyecto,
        str(año)
    )

    os.makedirs(
        ruta_año,
        exist_ok=True
    )

    enviar_progreso(
        progreso,
        f"📁 Carpeta temporal creada: {año}"
    )

    # ========================================================
    # LEER HOJA DEL AÑO
    # ========================================================

    enviar_progreso(
        progreso,
        f"📥 Leyendo hoja {año}..."
    )

    df = pd.read_excel(
        ruta_archivo,
        sheet_name=str(año),
        dtype=str
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    enviar_progreso(
        progreso,
        f"✅ Hoja {año} leída: {len(df):,} registros"
    )

    # ========================================================
    # CONSTRUIR ESTRUCTURA BOM
    # ========================================================

    padres = set(
        df["MATERIAL_PADRE"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    hijos = set(
        df["MATERIAL_HIJO"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    # ========================================================
    # DICCIONARIO BOM
    # ========================================================

    bom_dict = (
        df.groupby(
            "MATERIAL_PADRE"
        )["MATERIAL_HIJO"]
        .apply(
            lambda x: [
                str(v).strip()
                for v in x
                if pd.notna(v)
                and str(v).strip() != ""
            ]
        )
        .to_dict()
    )

    # ========================================================
    # PADRES DE EXPORTACIÓN
    # ========================================================

    padres_exportacion = sorted(
        [
            padre
            for padre in padres
            if padre not in hijos
        ]
    )

    total_padres = len(
        padres_exportacion
    )

    enviar_progreso(
        progreso,
        f"📋 Total de PADRES DE EXPORTACIÓN: "
        f"{total_padres:,} para el año {año}"
    )

    # ========================================================
    # RECORRER BOM
    # ========================================================

    def recorrer_bom(
        material,
        ruta_actual,
        visitados
    ):

        if material in visitados:
            return []

        visitados = visitados | {
            material
        }

        hijos_material = bom_dict.get(
            material,
            []
        )

        # ----------------------------------------------------
        # ÚLTIMO HIJO
        # ----------------------------------------------------

        if not hijos_material:

            return [
                ruta_actual + [material]
            ]

        rutas = []

        for hijo in hijos_material:

            rutas.extend(
                recorrer_bom(
                    hijo,
                    ruta_actual + [material],
                    visitados
                )
            )

        return rutas

    # ========================================================
    # PROCESAR PADRES
    # ========================================================

    registros = []

    for posicion, padre_exportacion in enumerate(
        padres_exportacion,
        start=1
    ):

        enviar_progreso(
            progreso,
            f"[{posicion}/{total_padres}] "
            f"Procesando PADRE: {padre_exportacion}"
        )

        rutas = recorrer_bom(
            padre_exportacion,
            [],
            set()
        )

        for ruta in rutas:

            if not ruta:
                continue

            ultimo_hijo = ruta[-1]

            subensambles = ruta[1:-1]

            registro = {
                "ULTIMO_HIJO": ultimo_hijo,
                "PADRE_EXPORTACION": padre_exportacion
            }

            # ------------------------------------------------
            # ORDEN ORIGINAL DEL PROCESO
            # ------------------------------------------------

            subensambles = list(
                reversed(
                    subensambles
                )
            )

            for i, subensamble in enumerate(
                subensambles,
                start=1
            ):

                registro[
                    f"SUBENSAMBLE_{i}"
                ] = subensamble

            registros.append(
                registro
            )

    # ========================================================
    # CREAR DATAFRAME
    # ========================================================

    enviar_progreso(
        progreso,
        f"📊 Armando resultado del año {año}..."
    )

    if registros:

        df_resultado = pd.DataFrame(
            registros
        )

    else:

        df_resultado = pd.DataFrame(
            columns=[
                "ULTIMO_HIJO",
                "PADRE_EXPORTACION"
            ]
        )

    # ========================================================
    # ORDENAR SUBENSAMBLES
    # ========================================================

    columnas_subensamble = sorted(
        [
            columna
            for columna in df_resultado.columns
            if columna.startswith(
                "SUBENSAMBLE_"
            )
        ],
        key=lambda x: int(
            x.split("_")[-1]
        )
    )

    columnas_finales = (
        ["ULTIMO_HIJO"]
        + columnas_subensamble
        + ["PADRE_EXPORTACION"]
    )

    df_resultado = df_resultado[
        columnas_finales
    ]

    df_resultado = (
        df_resultado
        .fillna("")
        .astype(str)
    )

    # ========================================================
    # EXPORTAR CSV POR PADRE
    # ========================================================

    enviar_progreso(
        progreso,
        f"📤 Exportando resultados temporales del año {año}..."
    )

    grupos = df_resultado.groupby(
        "PADRE_EXPORTACION",
        sort=True
    )

    total_archivos = len(
        grupos
    )

    contador = 0

    for padre, df_padre in grupos:

        padre = str(
            padre
        ).strip()

        if not padre:
            continue

        contador += 1

        nombre_archivo = (
            f"bom_{padre}.csv"
        )

        ruta_salida = os.path.join(
            ruta_año,
            nombre_archivo
        )

        df_padre.to_csv(
            ruta_salida,
            index=False,
            encoding="utf-8-sig",
            quoting=csv.QUOTE_ALL
        )

        enviar_progreso(
            progreso,
            f"✅ Archivo {año} generado: "
            f"{nombre_archivo}"
        )

    enviar_progreso(
        progreso,
        f"🎉 Año {año} terminado. "
        f"Archivos temporales generados: {contador:,}"
    )


# ============================================================
# GENERAR EXCEL CONSOLIDADO FINAL
# ============================================================

def generar_excel_consolidado(
    ruta_proyecto,
    nombre_excel,
    progreso=None
):

    enviar_progreso(
        progreso,
        "=========================================="
    )

    enviar_progreso(
        progreso,
        "📊 INICIANDO CONSOLIDACIÓN FINAL"
    )

    enviar_progreso(
        progreso,
        "=========================================="
    )

    # ========================================================
    # CARPETA OUTPUT
    # ========================================================

    ruta_output = os.path.join(
        ruta_proyecto,
        "output"
    )

    os.makedirs(
        ruta_output,
        exist_ok=True
    )

    ruta_excel_final = os.path.join(
        ruta_output,
        f"{nombre_excel}.xlsx"
    )

    # ========================================================
    # PROCESAR CARPETAS POR AÑO
    # ========================================================

    def procesar_carpeta(carpeta):

        archivos_csv = [
            archivo
            for archivo in os.listdir(carpeta)
            if archivo.lower().endswith(".csv")
        ]

        enviar_progreso(
            progreso,
            f"📂 {os.path.basename(carpeta)}: "
            f"{len(archivos_csv):,} archivos CSV"
        )

        dataframes = []

        columnas_normales = set()

        columnas_especiales = set()

        # ----------------------------------------------------
        # LEER CSV
        # ----------------------------------------------------

        for posicion, archivo in enumerate(
            archivos_csv,
            start=1
        ):

            ruta_csv = os.path.join(
                carpeta,
                archivo
            )

            df = pd.read_csv(
                ruta_csv,
                dtype=str
            )

            dataframes.append(
                df
            )

            for columna in df.columns:

                if (
                    columna == "ULTIMO_HIJO"
                    or columna == "PADRE_EXPORTACION"
                    or columna.startswith(
                        "SUBENSAMBLE_"
                    )
                ):

                    columnas_especiales.add(
                        columna
                    )

                else:

                    columnas_normales.add(
                        columna
                    )

        if not dataframes:
            return pd.DataFrame()

        # ====================================================
        # ORDENAR SUBENSAMBLES
        # ====================================================

        columnas_subensamble = sorted(
            [
                columna
                for columna in columnas_especiales
                if columna.startswith(
                    "SUBENSAMBLE_"
                )
            ],
            key=lambda x: int(
                x.split("_")[-1]
            )
        )

        columnas_finales = (
            ["ULTIMO_HIJO"]
            + columnas_subensamble
            + ["PADRE_EXPORTACION"]
        )

        # ====================================================
        # ASEGURAR COLUMNAS
        # ====================================================

        for df in dataframes:

            for columna in columnas_finales:

                if columna not in df.columns:

                    df[columna] = "-"

        # ====================================================
        # CONCATENAR
        # ====================================================

        df_final = pd.concat(
            [
                df[columnas_finales]
                for df in dataframes
            ],
            ignore_index=True
        )

        return df_final

    # ========================================================
    # DETECTAR AÑOS
    # ========================================================

    años = sorted(
        [
            carpeta
            for carpeta in os.listdir(
                ruta_proyecto
            )
            if (
                carpeta.isdigit()
                and len(carpeta) == 4
                and os.path.isdir(
                    os.path.join(
                        ruta_proyecto,
                        carpeta
                    )
                )
            )
        ]
    )

    enviar_progreso(
        progreso,
        f"📅 Años encontrados para consolidar: "
        f"{', '.join(años)}"
    )

    # ========================================================
    # CREAR EXCEL
    # ========================================================

    with pd.ExcelWriter(
        ruta_excel_final,
        engine="openpyxl"
    ) as writer:

        for año in años:

            enviar_progreso(
                progreso,
                f"📊 Consolidando año {año}..."
            )

            ruta_año = os.path.join(
                ruta_proyecto,
                año
            )

            df_año = procesar_carpeta(
                ruta_año
            )

            if df_año.empty:

                enviar_progreso(
                    progreso,
                    f"⚠️ Año {año} sin información."
                )

                continue

            df_año.to_excel(
                writer,
                index=False,
                sheet_name=str(año)
            )

            enviar_progreso(
                progreso,
                f"✅ Año {año} consolidado: "
                f"{len(df_año):,} registros"
            )

    enviar_progreso(
        progreso,
        "=========================================="
    )

    enviar_progreso(
        progreso,
        "🎉 CONSOLIDACIÓN FINAL TERMINADA"
    )

    enviar_progreso(
        progreso,
        f"📗 Excel final generado: {nombre_excel}.xlsx"
    )

    enviar_progreso(
        progreso,
        "=========================================="
    )

    return ruta_excel_final


# ============================================================
# PROCESO BOM COMPLETO
# ============================================================

def procesar_BOM_completo(
    ruta_excel,
    progreso=None
):

    ruta_temporal = None

    try:

        enviar_progreso(
            progreso,
            "=========================================="
        )

        enviar_progreso(
            progreso,
            "🚀 INICIO PROCESO BOM"
        )

        enviar_progreso(
            progreso,
            "=========================================="
        )

        # ====================================================
        # CARPETA TEMPORAL
        # ====================================================

        ruta_temporal = tempfile.mkdtemp(
            prefix="BOM_"
        )

        enviar_progreso(
            progreso,
            "📁 Carpeta temporal creada."
        )

        # ====================================================
        # COPIAR EXCEL
        # ====================================================

        nombre_original = os.path.basename(
            ruta_excel
        )

        excel_temporal = os.path.join(
            ruta_temporal,
            nombre_original
        )

        shutil.copy2(
            ruta_excel,
            excel_temporal
        )

        enviar_progreso(
            progreso,
            f"📥 Excel recibido: {nombre_original}"
        )

        # ====================================================
        # OBTENER AÑOS
        # ====================================================

        enviar_progreso(
            progreso,
            "🔎 Identificando años del Excel..."
        )

        excel = pd.ExcelFile(
            excel_temporal
        )

        años = sorted(
            [
                str(hoja).strip()
                for hoja in excel.sheet_names
                if str(hoja).strip().isdigit()
                and len(str(hoja).strip()) == 4
            ]
        )

        if not años:

            raise ValueError(
                "No se encontraron hojas correspondientes "
                "a años de 4 dígitos."
            )

        enviar_progreso(
            progreso,
            f"📅 Años encontrados: "
            f"{', '.join(años)}"
        )

        # ====================================================
        # PROCESAR BOM POR AÑO
        # ====================================================

        for posicion, año in enumerate(
            años,
            start=1
        ):

            enviar_progreso(
                progreso,
                ""
            )

            enviar_progreso(
                progreso,
                "=========================================="
            )

            enviar_progreso(
                progreso,
                f"📅 PROCESANDO AÑO {año} "
                f"({posicion}/{len(años)})"
            )

            enviar_progreso(
                progreso,
                "=========================================="
            )

            generarInfo(
                ruta_temporal,
                excel_temporal,
                año,
                progreso=progreso
            )

        # ====================================================
        # CONSOLIDAR RESULTADOS
        # ====================================================

        enviar_progreso(
            progreso,
            ""
        )

        enviar_progreso(
            progreso,
            "=========================================="
        )

        enviar_progreso(
            progreso,
            "📊 CONSOLIDANDO RESULTADO FINAL"
        )

        enviar_progreso(
            progreso,
            "=========================================="
        )

        ruta_excel_final = generar_excel_consolidado(
            ruta_temporal,
            "BOM_RESULTADO",
            progreso=progreso
        )

        # ====================================================
        # LEER EXCEL FINAL EN MEMORIA
        # ====================================================

        with open(
            ruta_excel_final,
            "rb"
        ) as archivo:

            datos_excel = archivo.read()

        # ====================================================
        # FINAL
        # ====================================================

        enviar_progreso(
            progreso,
            ""
        )

        enviar_progreso(
            progreso,
            "🎉 EXPORTACIÓN COMPLETADA"
        )

        enviar_progreso(
            progreso,
            "📗 Resultado final: BOM_RESULTADO.xlsx"
        )

        return datos_excel

    except Exception as e:

        enviar_progreso(
            progreso,
            f"❌ ERROR PROCESO BOM: {str(e)}"
        )

        raise

    finally:

        # ====================================================
        # ELIMINAR TODO LO TEMPORAL
        # ====================================================

        if (
            ruta_temporal
            and os.path.exists(
                ruta_temporal
            )
        ):

            shutil.rmtree(
                ruta_temporal,
                ignore_errors=True
            )

            log(
                "🗑️ Carpetas y archivos temporales eliminados."
            )