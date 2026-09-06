import streamlit as st
import pandas as pd
import io
import importlib
import logging
import traceback
from Proyectos_Cross.log import log, limpiar_log

import Proyectos_Cross.utils as utils
import Proyectos_Cross.procesarCross_Ped as pc
import Proyectos_Cross.procesarCross_Hts as ph
import Proyectos_Cross.procesarCross_Htsnico as phn
import Proyectos_Cross.procesarCross_Sec as ps
import Proyectos_Cross.procesarCross_Impo_SinAF as np_impo_af
import Proyectos_Cross.procesarCross_Expo_SinAF as np_expo_af


# =========================================================
# RECARGAR MÓDULOS
# =========================================================

importlib.reload(utils)
importlib.reload(pc)
importlib.reload(ph)
importlib.reload(phn)
importlib.reload(ps)
importlib.reload(np_impo_af)
importlib.reload(np_expo_af)

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


# def log(mensaje):

#     if "logs" not in st.session_state:
#         st.session_state.logs = []

#     st.session_state.logs.append(mensaje)

# =========================================================
# LOGICA DE EJECUCION
# =========================================================

def ejecutar_subproceso(
    nombre_proceso,
    funcion_proceso,
    clave_resultado
):

    # -------------------------------------------------
    # VALIDAR CARGA
    # -------------------------------------------------

    if st.session_state.dfs_cross is None:

        st.warning(
            "📥 Primero debes cargar los archivos."
        )

        return


    # ---------------------------------------------
    # EJECUTAR
    # ---------------------------------------------

    if st.button(
        f"🚀 EJECUTAR {nombre_proceso}",
        use_container_width=True,
        type="primary"
    ):
        
        # st.session_state.resultado_cross_ped = None
        
        try:

            with st.status(
                f"⚙️ Ejecutando {nombre_proceso}...",
                expanded=True
            ) as status:

                st.write("Ejecutando proceso...")

                # =========================================
                # CROSS X PED
                # =========================================

                if nombre_proceso == "CROSS X PED":

                    resultado = funcion_proceso(
                        st.session_state.dfs_cross
                    )

                    # GUARDAR SOLO EL RESULTADO DE CROSS X PED
                    st.session_state.df_cross_ped = resultado


                # =========================================
                # DEMÁS PROCESOS
                # =========================================

                else:

                    if st.session_state.df_cross_ped is None:

                        st.warning(
                            f"⚠️ No puedes ejecutar {nombre_proceso} sin ejecutar "
                            "primero CROSS X PED."
                        )

                        return

                    resultado = funcion_proceso(
                        st.session_state.dfs_cross,
                        st.session_state.df_cross_ped
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
                        sheet_name=nombre_proceso
                    )


                buffer.seek(0)


                st.session_state[clave_resultado] = (
                    buffer.getvalue()
                )


                status.update(
                    label=f"✅ {nombre_proceso} terminado correctamente",
                    state="complete",
                    expanded=False
                )


        except Exception as e:

            st.error(
                f"❌ Error durante {nombre_proceso}: {e}"
            )

            st.code(
                traceback.format_exc()
            )



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

    if "resultado_cross_hts" not in st.session_state:
        st.session_state.resultado_cross_hts = None

    if "resultado_cross_hts_nico" not in st.session_state:
        st.session_state.resultado_cross_hts_nico = None

    if "resultado_cross_sec" not in st.session_state:
        st.session_state.resultado_cross_sec = None

    if "resultado_cross_impo_np_sin_af" not in st.session_state:
        st.session_state.resultado_cross_impo_np_sin_af = None

    if "resultado_cross_expo_np_sin_af" not in st.session_state:
        st.session_state.resultado_cross_expo_np_sin_af = None


    if "df_cross_ped" not in st.session_state:
        st.session_state.df_cross_ped = None

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

    col1, col2, col3, col4, col5,col6 = st.columns(6)


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
    # CROSS X HTS
    # =====================================================

    with col2:

        if st.button(
            "CROSS X HTS",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "cross_hts"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "cross_hts"
            st.rerun()


    # =====================================================
    # PROCESO 3
    # =====================================================

    with col3:

        if st.button(
            "CROSS X HTSNICO",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "cross_hts_nico"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "cross_hts_nico"
            st.rerun()


    # =====================================================
    # PROCESO 4
    # =====================================================

    with col4:

        if st.button(
            "CROSS X SEC",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "cross_sec"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "cross_sec"
            st.rerun()


    # =====================================================
    # PROCESO 5
    # =====================================================

    with col5:

        if st.button(
            "IMPO NP - SIN AF",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "IMPO_NP_SIN_AF"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "IMPO_NP_SIN_AF"
            st.rerun()

    # =====================================================
    # PROCESO 6
    # =====================================================

    with col6:

        if st.button(
            "EXPO NP - SIN AF",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.subproceso_cross == "EXPO_NP_SIN_AF"
                else "secondary"
            )
        ):

            st.session_state.subproceso_cross = "EXPO_NP_SIN_AF"
            st.rerun()


    st.divider()


    # =====================================================
    # CROSS X PED
    # =====================================================

    if st.session_state.subproceso_cross == "cross_ped":

        st.markdown("#### 🚀 CROSS X PED")

        ejecutar_subproceso(
            nombre_proceso="CROSS X PED",
            funcion_proceso=pc.ejecutar_proceso,
            clave_resultado="resultado_cross_ped"
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
    # CROSS X HTS
    # =====================================================

    elif st.session_state.subproceso_cross == "cross_hts":

        st.markdown("#### 🚀 CROSS X HTS")
        # st.write("HOLA")
        
        ejecutar_subproceso(
            nombre_proceso="CROSS X HTS",
            funcion_proceso=ph.ejecutar_proceso,
            clave_resultado="resultado_cross_hts"
        )
        
        # ---------------------------------------------
        # RESULTADO / DESCARGA
        # ---------------------------------------------

        if st.session_state.resultado_cross_hts is not None:

            st.success(
                "✅ CROSS X HTS terminado correctamente. "
                "El archivo está listo para descargar."
            )


            st.download_button(
                label="⬇️ DESCARGAR CROSS X HTS",
                data=st.session_state.resultado_cross_hts,
                file_name="CROSS X HTS.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )



    # =====================================================
    # PROCESO 3
    # =====================================================

    elif st.session_state.subproceso_cross == "cross_hts_nico":

        st.markdown("#### 🚀 CROSS X HTSNICO")
        # st.write("HOLA")
        
        ejecutar_subproceso(
            nombre_proceso="CROSS X HTSNICO",
            funcion_proceso=phn.ejecutar_proceso,
            clave_resultado="resultado_cross_hts_nico"
        )
        
        # ---------------------------------------------
        # RESULTADO / DESCARGA
        # ---------------------------------------------

        if st.session_state.resultado_cross_hts_nico is not None:

            st.success(
                "✅ CROSS X HTSNICO terminado correctamente. "
                "El archivo está listo para descargar."
            )


            st.download_button(
                label="⬇️ DESCARGAR CROSS X HTSNICO",
                data=st.session_state.resultado_cross_hts_nico,
                file_name="CROSS X HTSNICO.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )


    # =====================================================
    # PROCESO 4
    # =====================================================

    elif st.session_state.subproceso_cross == "cross_sec":

        st.markdown("#### 🚀 CROSS X SEC")
        # st.write("HOLA")
        
        ejecutar_subproceso(
            nombre_proceso="CROSS X SEC",
            funcion_proceso=ps.ejecutar_proceso,
            clave_resultado="resultado_cross_sec"
        )
        
        # ---------------------------------------------
        # RESULTADO / DESCARGA
        # ---------------------------------------------

        if st.session_state.resultado_cross_sec is not None:

            st.success(
                "✅ CROSS X SEC terminado correctamente. "
                "El archivo está listo para descargar."
            )


            st.download_button(
                label="⬇️ DESCARGAR CROSS X SEC",
                data=st.session_state.resultado_cross_sec,
                file_name="CROSS X SEC.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )


    # =====================================================
    # PROCESO 5
    # =====================================================

    elif st.session_state.subproceso_cross == "IMPO_NP_SIN_AF":

        st.markdown("#### 🚀 IMPO NP - SIN AF")


        ejecutar_subproceso(
            nombre_proceso="IMPO_NP_SIN_AF",
            funcion_proceso=np_impo_af.ejecutar_proceso,
            clave_resultado="resultado_cross_impo_np_sin_af"
        )
        
        # ---------------------------------------------
        # RESULTADO / DESCARGA
        # ---------------------------------------------

        if st.session_state.resultado_cross_impo_np_sin_af is not None:

            st.success(
                "✅ CROSS X SEC terminado correctamente. "
                "El archivo está listo para descargar."
            )


            st.download_button(
                label="⬇️ DESCARGAR CROSS IMPO NP - SIN AF",
                data=st.session_state.resultado_cross_impo_np_sin_af,
                file_name="CROSS IMPO NP - SIN AF.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )
            

    # =====================================================
    # PROCESO 6
    # =====================================================

    elif st.session_state.subproceso_cross == "EXPO_NP_SIN_AF":

        st.markdown("#### 🚀 EXPO NP - SIN AF")


        ejecutar_subproceso(
            nombre_proceso="EXPO_NP_SIN_AF",
            funcion_proceso=np_expo_af.ejecutar_proceso,
            clave_resultado="resultado_cross_expo_np_sin_af"
        )
        
        # ---------------------------------------------
        # RESULTADO / DESCARGA
        # ---------------------------------------------

        if st.session_state.resultado_cross_expo_np_sin_af is not None:

            st.success(
                "✅ CROSS X SEC terminado correctamente. "
                "El archivo está listo para descargar."
            )


            st.download_button(
                label="⬇️ DESCARGAR CROSS EXPO NP - SIN AF",
                data=st.session_state.resultado_cross_expo_np_sin_af,
                file_name="CROSS EXPO NP - SIN AF.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )            