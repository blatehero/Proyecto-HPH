import streamlit as st
import pandas as pd
import io
import importlib

import Proyectos_Cross.utils as utils
import Proyectos_Cross.procesarCross_Ped as pc


# =========================================================
# RECARGAR FUNCIONES
# =========================================================

importlib.reload(utils)
importlib.reload(pc)


# =========================================================
# ESTILOS
# =========================================================

st.markdown("""
<style>

.estado-ok {
    padding: 8px 10px;
    margin-bottom: 8px;
    border-radius: 6px;
    background-color: #123d2b;
    color: #00e676;
    font-size: 14px;
}

.estado-pendiente {
    padding: 8px 10px;
    margin-bottom: 8px;
    border-radius: 6px;
    background-color: #403f12;
    color: #ffd740;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# VISTA CROSS
# =========================================================

def mostrar_cross():

    # st.markdown("# 🔄 CROSS")


    # =====================================================
    # SUBPROCESO SELECCIONADO
    # =====================================================

    if "subproceso_cross" not in st.session_state:

        st.session_state.subproceso_cross = "cross_ped"


    # =====================================================
    # DATAFRAMES CARGADOS
    # =====================================================

    if "dfs_cross" not in st.session_state:

        st.session_state.dfs_cross = None


    # =====================================================
    # RESULTADO
    # =====================================================

    if "resultado_cross_ped" not in st.session_state:

        st.session_state.resultado_cross_ped = None


    # =====================================================
    # CARGA DE ARCHIVOS
    # =====================================================

    st.markdown("## 📁 Subir archivos")


    columnas = st.columns(4)


    archivos_config = [
        ("DS.csv", "methode"),
        ("UND HOMOLOGADAS.csv", "homologadas"),
        ("DS VIRGEN 701.csv", "virgen_701"),
        ("DS VIRGEN 512.csv", "virgen_512"),
        ("DS VIRGEN 557.csv", "virgen_557"),
        ("CLIENTE_IMPO.csv", "cliente_impo"),
        ("CLIENTE_EXPO.csv", "cliente_expo")
    ]


    archivos = {}


    for i, (nombre, key) in enumerate(archivos_config):

        with columnas[i % 4]:

            archivos[nombre] = st.file_uploader(
                nombre,
                type=["csv"],
                key=key
            )


    # =====================================================
    # PROGRESO
    # =====================================================

    total_archivos = len(archivos)


    archivos_cargados = sum(
        archivo is not None
        for archivo in archivos.values()
    )


    st.progress(
        archivos_cargados / total_archivos,
        text=f"Archivos seleccionados: {archivos_cargados}/{total_archivos}"
    )


    # =====================================================
    # ESTADO DE ARCHIVOS
    # =====================================================

    st.markdown("### 📋 Estado de archivos")


    columnas_estado = st.columns(4)


    for i, (nombre, archivo) in enumerate(archivos.items()):

        with columnas_estado[i % 4]:

            if archivo is not None:

                st.markdown(
                    f"""
                    <div class="estado-ok">
                        ✅ {nombre}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="estado-pendiente">
                        ⏳ {nombre}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


    st.divider()


    # =====================================================
    # BOTÓN CARGAR ARCHIVOS
    # =====================================================

    if st.button(
        "📥 CARGAR ARCHIVOS",
        use_container_width=True,
        type="primary"
    ):


        # -------------------------------------------------
        # VALIDAR
        # -------------------------------------------------

        if archivos_cargados < total_archivos:

            st.error(
                f"Faltan "
                f"{total_archivos - archivos_cargados} "
                "archivos por cargar."
            )

            return


        # -------------------------------------------------
        # CARGAR DATAFRAMES
        # -------------------------------------------------

        with st.status(
            "📥 Cargando archivos...",
            expanded=True
        ) as status:

            st.write("Leyendo los 7 archivos...")

            dfs = utils.iniciar_proceso(

                archivos["DS.csv"],
                archivos["UND HOMOLOGADAS.csv"],
                archivos["DS VIRGEN 701.csv"],
                archivos["DS VIRGEN 512.csv"],
                archivos["DS VIRGEN 557.csv"],
                archivos["CLIENTE_IMPO.csv"],
                archivos["CLIENTE_EXPO.csv"]

            )

            st.write("Guardando DataFrames en memoria...")

            st.session_state.dfs_cross = dfs

            # Limpiar resultados anteriores
            st.session_state.resultado_cross_ped = None

            status.update(
                label="✅ Archivos cargados correctamente",
                state="complete",
                expanded=False
            )


    # =====================================================
    # ESTADO DE CARGA
    # =====================================================

    if st.session_state.dfs_cross is not None:

        st.success(
            "✅ DataFrames cargados y disponibles para los 5 procesos."
        )


    st.divider()


    # =====================================================
    # SUBPROCESOS CROSS
    # =====================================================

    col1, col2, col3, col4, col5 = st.columns(5)


    # =====================================================
    # CROSS X PED
    # =====================================================

    with col1:

        if st.button(
            "🚀 CROSS X PED",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "cross_ped"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "cross_ped"
            st.rerun()


    # =====================================================
    # PROCESO 2
    # =====================================================

    with col2:

        if st.button(
            "PROCESO 2",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "proceso_2"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "proceso_2"
            st.rerun()


    # =====================================================
    # PROCESO 3
    # =====================================================

    with col3:

        if st.button(
            "PROCESO 3",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "proceso_3"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "proceso_3"
            st.rerun()


    # =====================================================
    # PROCESO 4
    # =====================================================

    with col4:

        if st.button(
            "PROCESO 4",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "proceso_4"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "proceso_4"
            st.rerun()


    # =====================================================
    # PROCESO 5
    # =====================================================

    with col5:

        if st.button(
            "PROCESO 5",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "proceso_5"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "proceso_5"
            st.rerun()


    st.divider()


    # =====================================================
    # CROSS X PED
    # =====================================================

    if st.session_state.subproceso_cross == "cross_ped":

        st.markdown("## 🚀 CROSS X PED")


        # -------------------------------------------------
        # VALIDAR QUE LOS DFS ESTÉN CARGADOS
        # -------------------------------------------------

        if st.session_state.dfs_cross is None:

            st.warning(
                "📥 Primero debes cargar los archivos."
            )

            return


        # -------------------------------------------------
        # EJECUTAR CROSS X PED
        # -------------------------------------------------

        if st.button(
            "🚀 EJECUTAR CROSS X PED",
            use_container_width=True,
            type="primary"
        ):

            with st.status(
                "⚙️ Ejecutando CROSS X PED...",
                expanded=True
            ) as status:

                st.write("Procesando DataFrames...")

                resultado = pc.ejecutar_proceso(
                    st.session_state.dfs_cross
                )

                st.write("Generando archivo Excel...")

                buffer = io.BytesIO()


                with pd.ExcelWriter(
                    buffer,
                    engine="openpyxl"
                ) as writer:

                    resultado.to_excel(
                        writer,
                        index=False,
                        sheet_name="CROSS X PED"
                    )


                buffer.seek(0)


                # Guardamos el resultado
                st.session_state.resultado_cross_ped = buffer.getvalue()


                status.update(
                    label="✅ CROSS X PED terminado correctamente",
                    state="complete",
                    expanded=False
                )


        # -------------------------------------------------
        # DESCARGA
        # -------------------------------------------------

        if st.session_state.resultado_cross_ped is not None:

            st.success(
                "✅ CROSS X PED terminado correctamente. "
                "El archivo está listo para descargar."
            )


            st.download_button(
                label="⬇️ DESCARGAR CROSS X PED",
                data=st.session_state.resultado_cross_ped,
                file_name="CROSS X PED.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


    # =====================================================
    # PROCESO 2
    # =====================================================

    elif st.session_state.subproceso_cross == "proceso_2":

        st.markdown("## 📊 PROCESO 2")

        if st.session_state.dfs_cross is None:

            st.warning(
                "📥 Primero debes cargar los archivos."
            )

        else:

            st.success(
                "✅ Los DataFrames ya están cargados y disponibles."
            )

            st.info(
                "Aquí irá el PROCESO 2."
            )


    # =====================================================
    # PROCESO 3
    # =====================================================

    elif st.session_state.subproceso_cross == "proceso_3":

        st.markdown("## 📊 PROCESO 3")

        if st.session_state.dfs_cross is None:

            st.warning(
                "📥 Primero debes cargar los archivos."
            )

        else:

            st.success(
                "✅ Los DataFrames ya están cargados y disponibles."
            )

            st.info(
                "Aquí irá el PROCESO 3."
            )


    # =====================================================
    # PROCESO 4
    # =====================================================

    elif st.session_state.subproceso_cross == "proceso_4":

        st.markdown("## 📊 PROCESO 4")

        if st.session_state.dfs_cross is None:

            st.warning(
                "📥 Primero debes cargar los archivos."
            )

        else:

            st.success(
                "✅ Los DataFrames ya están cargados y disponibles."
            )

            st.info(
                "Aquí irá el PROCESO 4."
            )


    # =====================================================
    # PROCESO 5
    # =====================================================

    elif st.session_state.subproceso_cross == "proceso_5":

        st.markdown("## 📊 PROCESO 5")

        if st.session_state.dfs_cross is None:

            st.warning(
                "📥 Primero debes cargar los archivos."
            )

        else:

            st.success(
                "✅ Los DataFrames ya están cargados y disponibles."
            )

            st.info(
                "Aquí irá el PROCESO 5."
            )