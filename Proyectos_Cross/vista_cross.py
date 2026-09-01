import streamlit as st
import pandas as pd
import io
import importlib

import Proyectos_Cross.utils as utils
import Proyectos_Cross.procesarCross_Ped as pc


# =========================================================
# RECARGAR MÓDULOS
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

    # =====================================================
    # ESTADOS
    # =====================================================

    if "subproceso_cross" not in st.session_state:
        st.session_state.subproceso_cross = "cross_ped"

    if "dfs_cross" not in st.session_state:
        st.session_state.dfs_cross = None

    if "resultado_cross_ped" not in st.session_state:
        st.session_state.resultado_cross_ped = None


    # =====================================================
    # CARGA DE ARCHIVOS
    # =====================================================

    st.markdown("# 📁 Subir archivos")


    col1, col2 = st.columns(2)


    # -----------------------------------------------------
    # BASE
    # -----------------------------------------------------

    with col1:

        archivo_base = st.file_uploader(
            "📄 BASE",
            type=["xlsx"],
            key="archivo_base"
        )


    # -----------------------------------------------------
    # CLIENTES
    # -----------------------------------------------------

    with col2:

        archivo_clientes = st.file_uploader(
            "👥 CLIENTES",
            type=["xlsx"],
            key="archivo_clientes"
        )


    # =====================================================
    # PROGRESO
    # =====================================================

    total_archivos = 2

    archivos_cargados = sum([
        archivo_base is not None,
        archivo_clientes is not None
    ])


    st.progress(
        archivos_cargados / total_archivos,
        text=f"Archivos seleccionados: {archivos_cargados}/{total_archivos}"
    )


    # =====================================================
    # ESTADO DE ARCHIVOS
    # =====================================================

    st.markdown("### 📋 Estado de archivos")


    col1, col2 = st.columns(2)


    with col1:

        if archivo_base is not None:

            st.markdown(
                """
                <div class="estado-ok">
                    ✅ BASE cargado
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="estado-pendiente">
                    ⏳ BASE pendiente
                </div>
                """,
                unsafe_allow_html=True
            )


    with col2:

        if archivo_clientes is not None:

            st.markdown(
                """
                <div class="estado-ok">
                    ✅ CLIENTES cargado
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="estado-pendiente">
                    ⏳ CLIENTES pendiente
                </div>
                """,
                unsafe_allow_html=True
            )


    st.divider()


    # =====================================================
    # CARGAR DATAFRAMES
    # =====================================================

    if st.button(
        "📥 CARGAR ARCHIVOS",
        use_container_width=True,
        type="primary"
    ):

        if archivos_cargados < total_archivos:

            st.error(
                f"Faltan {total_archivos - archivos_cargados} "
                "archivos por cargar."
            )

        else:

            with st.status(
                "📥 Cargando archivos...",
                expanded=True
            ) as status:

                st.write("Leyendo BASE...")
                st.write("Leyendo CLIENTES...")
                st.write("Cargando UND HOMOLOGADAS...")
                st.write("Preparando DataFrames...")


                dfs = utils.iniciar_proceso(
                    archivo_base,
                    archivo_clientes
                )

                

                st.session_state.dfs_cross = dfs

                # Limpiar resultado anterior
                st.session_state.resultado_cross_ped = None


                status.update(
                    label="✅ Archivos cargados correctamente",
                    state="complete",
                    expanded=False
                )


    # =====================================================
    # CONFIRMACIÓN DE CARGA
    # =====================================================

    if st.session_state.dfs_cross is not None:

        st.success(
            "✅ Archivos cargados. "
            "Los DataFrames están disponibles para los 5 procesos."
        )


    st.divider()


    # =====================================================
    # MENÚ DE LOS 5 SUBPROCESOS
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
        # VALIDAR CARGA
        # -------------------------------------------------

        if st.session_state.dfs_cross is None:

            st.warning(
                "📥 Primero debes cargar los archivos."
            )

        else:

            # ---------------------------------------------
            # EJECUTAR
            # ---------------------------------------------

            if st.button(
                "🚀 EJECUTAR CROSS X PED",
                use_container_width=True,
                type="primary"
            ):

                try:

                    with st.status(
                        "⚙️ Ejecutando CROSS X PED...",
                        expanded=True
                    ) as status:

                        st.write("Ejecutando proceso...")
                        st.write("CLAVES QUE ESTOY PASANDO:", st.session_state.dfs_cross.keys())
                        resultado = pc.ejecutar_proceso(
                            st.session_state.dfs_cross
                        )


                        st.write("Generando archivo Excel...")


                        # ---------------------------------
                        # GENERAR EXCEL EN MEMORIA
                        # ---------------------------------

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


                        st.session_state.resultado_cross_ped = (
                            buffer.getvalue()
                        )


                        status.update(
                            label="✅ CROSS X PED terminado correctamente",
                            state="complete",
                            expanded=False
                        )


                except Exception as e:

                    st.error(
                        f"❌ Error durante CROSS X PED: {e}"
                    )


            # ---------------------------------------------
            # RESULTADO / DESCARGA
            # ---------------------------------------------

            if st.session_state.resultado_cross_ped is not None:

                st.success(
                    "✅ CROSS X PED terminado correctamente. "
                    "El archivo está listo para descargar."
                )


                st.download_button(
                    label="⬇️ DESCARGAR CROSS X PED",
                    data=st.session_state.resultado_cross_ped,
                    file_name="CROSS X PED.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
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
                "✅ Los DataFrames ya están cargados."
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
                "✅ Los DataFrames ya están cargados."
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
                "✅ Los DataFrames ya están cargados."
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
                "✅ Los DataFrames ya están cargados."
            )

            st.info(
                "Aquí irá el PROCESO 5."
            )