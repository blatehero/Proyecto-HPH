import streamlit as st
import pandas as pd
import importlib
import Proyectos_Cross.utils as utils


# =========================================================
# RECARGAR UTILS
# =========================================================

importlib.reload(utils)


# =========================================================
# MOSTRAR RESULTADOS
# =========================================================

def obtener_resultados(datos, nombre_padre=""):

    resultado = []

    for nombre, valor in datos.items():

        nombre_completo = (
            f"{nombre_padre} - {nombre}"
            if nombre_padre
            else nombre
        )

        # ---------------------------------------------
        # SI ES OTRO DICCIONARIO, ENTRAR DENTRO
        # ---------------------------------------------

        if isinstance(valor, dict):

            resultado.extend(
                obtener_resultados(
                    valor,
                    nombre_completo
                )
            )

        # ---------------------------------------------
        # SI ES DATAFRAME
        # ---------------------------------------------

        elif isinstance(valor, pd.DataFrame):

            resultado.append({
                "ARCHIVO": nombre_completo,
                "FILAS": len(valor),
                "COLUMNAS": len(valor.columns)
            })

    return resultado


# =========================================================
# FORMULARIO CROSS
# =========================================================

def mostrar_cross():

    st.markdown("# 📁 Subir archivos")


    # =====================================================
    # CARGA DE ARCHIVOS
    # =====================================================

    col1, col2 = st.columns(2)


    with col1:

        archivo_ds = st.file_uploader(
            "DS.csv",
            type=["csv"],
            key="methode"
        )


        archivo_homo = st.file_uploader(
            "UND HOMOLOGADAS.csv",
            type=["csv"],
            key="homologadas"
        )


        archivo_v701 = st.file_uploader(
            "DS VIRGEN 701.csv",
            type=["csv"],
            key="virgen_701"
        )


        archivo_v512 = st.file_uploader(
            "DS VIRGEN 512.csv",
            type=["csv"],
            key="virgen_512"
        )


    with col2:

        archivo_v557 = st.file_uploader(
            "DS VIRGEN 557.csv",
            type=["csv"],
            key="virgen_557"
        )


        archivo_cli_impo = st.file_uploader(
            "CLIENTE_IMPO.csv",
            type=["csv"],
            key="cliente_impo"
        )


        archivo_cli_expo = st.file_uploader(
            "CLIENTE_EXPO.csv",
            type=["csv"],
            key="cliente_expo"
        )


    # =====================================================
    # DICCIONARIO DE ARCHIVOS
    # =====================================================

    archivos = {

        "DS.csv": archivo_ds,

        "UND HOMOLOGADAS.csv": archivo_homo,

        "DS VIRGEN 701.csv": archivo_v701,

        "DS VIRGEN 512.csv": archivo_v512,

        "DS VIRGEN 557.csv": archivo_v557,

        "CLIENTE_IMPO.csv": archivo_cli_impo,

        "CLIENTE_EXPO.csv": archivo_cli_expo

    }


    # =====================================================
    # PROGRESO
    # =====================================================

    total_archivos = len(archivos)


    archivos_cargados = sum(
        archivo is not None
        for archivo in archivos.values()
    )


    progreso_archivos = archivos_cargados / total_archivos


    st.progress(
        progreso_archivos,
        text=f"Archivos cargados: {archivos_cargados}/{total_archivos}"
    )


    # =====================================================
    # ESTADO DE ARCHIVOS
    # =====================================================

    st.markdown("### 📋 Estado de archivos")


    for nombre, archivo in archivos.items():

        if archivo is not None:

            st.success(
                f"✅ {nombre} cargado"
            )

        else:

            st.warning(
                f"⏳ {nombre} pendiente"
            )


    st.divider()


    # =====================================================
    # EJECUTAR PROCESO
    # =====================================================

    if st.button(
        "🚀 EJECUTAR PROCESO",
        use_container_width=True,
        type="primary"
    ):


        # -------------------------------------------------
        # VALIDAR ARCHIVOS
        # -------------------------------------------------

        if archivos_cargados < total_archivos:

            st.error(
                f"Faltan {total_archivos - archivos_cargados} archivos por cargar."
            )


        else:

            # -------------------------------------------------
            # EJECUTAR
            # -------------------------------------------------

            with st.spinner("🚀 Procesando archivos..."):

                dfs = utils.iniciar_proceso(

                    archivo_ds,

                    archivo_homo,

                    archivo_v701,

                    archivo_v512,

                    archivo_v557,

                    archivo_cli_impo,

                    archivo_cli_expo

                )


            st.success(
                "🚀 Proceso ejecutado correctamente"
            )


            # =================================================
            # RESULTADO DEL PROCESO
            # =================================================

            st.markdown(
                "## 📊 Resultado del proceso"
            )


            resultado = obtener_resultados(dfs)


            if resultado:

                df_resultado = pd.DataFrame(
                    resultado
                )


                st.dataframe(
                    df_resultado,
                    use_container_width=True,
                    hide_index=True
                )


            else:

                st.warning(
                    "No se encontraron DataFrames para mostrar."
                )