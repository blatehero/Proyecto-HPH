import streamlit as st
import os
import tempfile

import Proyectos_Cross.procesarBoom as boom


def mostrar_boom():

    # ========================================================
    # SESSION STATE
    # ========================================================

    if "bom_cargado" not in st.session_state:
        st.session_state.bom_cargado = False

    if "bom_archivo" not in st.session_state:
        st.session_state.bom_archivo = None


    # ========================================================
    # SUBIR ARCHIVOS
    # ========================================================

    st.markdown("# 📁 Subir archivos")

    archivo_bom = st.file_uploader(
        "📄 BOM",
        type=["xlsx", "xls"],
        accept_multiple_files=False,
        key="upload_bom"
    )


    # ========================================================
    # SI NO HAY ARCHIVO
    # ========================================================

    if archivo_bom is None:

        st.session_state.bom_cargado = False
        st.session_state.bom_archivo = None


    # ========================================================
    # CONTADOR
    # ========================================================

    cantidad = (
        1
        if archivo_bom is not None
        else 0
    )

    st.write(
        f"Archivos seleccionados: {cantidad}/1"
    )

    st.progress(
        cantidad / 1
    )


    # ========================================================
    # ESTADO DE ARCHIVOS
    # ========================================================

    st.markdown(
        "## 📋 Estado de archivos"
    )


    if st.session_state.bom_cargado:

        st.success(
            "✅ BOM cargado"
        )

    else:

        st.warning(
            "⏳ BOM pendiente"
        )


    st.divider()


    # ========================================================
    # CARGAR ARCHIVOS
    # ========================================================

    if st.button(
        "📥 CARGAR ARCHIVOS",
        use_container_width=True,
        type="primary"
    ):

        if archivo_bom is None:

            st.error(
                "❌ Debes seleccionar el archivo BOM."
            )

        else:

            st.session_state.bom_archivo = (
                archivo_bom
            )

            st.session_state.bom_cargado = True

            st.rerun()


    # ========================================================
    # PROCESO BOM
    # ========================================================

    st.divider()

    st.markdown(
        "## 📦 BOM"
    )


    if not st.session_state.bom_cargado:

        st.warning(
            "📥 Primero debes cargar los archivos."
        )

        return


    # ========================================================
    # BOTÓN PROCESAR
    # ========================================================

    if st.button(
        "🚀 PROCESAR BOM",
        use_container_width=True,
        type="primary"
    ):

        archivo_bom = (
            st.session_state.bom_archivo
        )

        ruta_excel = None

        try:

            # =================================================
            # GUARDAR TEMPORAL
            # =================================================

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(
                    archivo_bom.name
                )[1]
            ) as archivo_temp:

                archivo_temp.write(
                    archivo_bom.getbuffer()
                )

                ruta_excel = archivo_temp.name


            # =================================================
            # PROCESAR
            # =================================================

            with st.status(
                "⚙️ Procesando BOM...",
                expanded=True
            ) as status:

                contenedor_mensajes = st.empty()

                mensajes = []


                def actualizar_progreso(
                    mensaje
                ):

                    mensajes.append(
                        mensaje
                    )

                    # Mostrar los últimos 30
                    # para no hacer infinita la página

                    contenedor_mensajes.code(
                        "\n".join(
                            mensajes[-30:]
                        )
                    )


                datos_excel = (
                    boom.procesar_BOM_completo(
                        ruta_excel,
                        progreso=actualizar_progreso
                    )
                )


                status.update(
                    label="✅ BOM procesado correctamente",
                    state="complete",
                    expanded=False
                )


            # =================================================
            # RESULTADO
            # =================================================

            st.success(
                "✅ Proceso BOM terminado."
            )


            # =================================================
            # DESCARGAR EXCEL FINAL
            # =================================================

            st.download_button(
                label="⬇️ DESCARGAR BOM RESULTADO",
                data=datos_excel,
                file_name="BOM_RESULTADO.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )


        except Exception as e:

            st.error(
                f"❌ Error durante el proceso BOM: {str(e)}"
            )


        finally:

            if (
                ruta_excel
                and os.path.exists(
                    ruta_excel
                )
            ):

                try:

                    os.remove(
                        ruta_excel
                    )

                except Exception:
                    pass