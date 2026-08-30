import streamlit as st
import importlib
import Proyectos_Cross.vista_cross as cross

importlib.reload(cross)

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Proyecto HPH",
    page_icon="🚀",
    layout="wide"
)


# ============================================================
# ESTADO
# ============================================================

if "proyecto" not in st.session_state:
    st.session_state.proyecto = None


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

.block-container {
    max-width: 1200px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}


/* TITULO */

.titulo {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitulo {
    text-align: center;
    opacity: 0.7;
    margin-bottom: 45px;
}


/* SEPARADOR */

.separador {
    margin-top: 35px;
    margin-bottom: 35px;
    border-top: 1px solid #333;
}


/* TITULO DEL CONTENIDO */

.titulo-proyecto {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 5px;
}

.descripcion-proyecto {
    text-align: center;
    opacity: 0.7;
    margin-bottom: 30px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="titulo">PROYECTO HPH</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">Selecciona un proceso para ejecutar</div>',
    unsafe_allow_html=True
)


# ============================================================
# MENU SUPERIOR
# ============================================================

col1, col2, col3 = st.columns(3)


# ============================================================
# CROSS
# ============================================================

with col1:

    if st.button(
        "🚀\n\nPROCESAR CROSS",
        use_container_width=True,
        type="primary" if st.session_state.proyecto == "cross" else "secondary"
    ):

        st.session_state.proyecto = "cross"
        st.rerun()


# ============================================================
# BOOM
# ============================================================

with col2:

    if st.button(
        "📊\n\nPROCESAR BOOM",
        use_container_width=True,
        type="primary" if st.session_state.proyecto == "boom" else "secondary"
    ):

        st.session_state.proyecto = "boom"
        st.rerun()


# ============================================================
# ACTIVOS FIJOS
# ============================================================

with col3:

    if st.button(
        "🔍\n\nPROCESAR ACTIVOS FIJOS",
        use_container_width=True,
        type="primary" if st.session_state.proyecto == "activos" else "secondary"
    ):

        st.session_state.proyecto = "activos"
        st.rerun()


# ============================================================
# SEPARADOR
# ============================================================

st.markdown(
    '<div class="separador"></div>',
    unsafe_allow_html=True
)


# ============================================================
# LLAMAR AL PROYECTO SELECCIONADO
# ============================================================

if st.session_state.proyecto == "cross":

    cross.mostrar_cross()


elif st.session_state.proyecto == "boom":

    st.markdown(
        '<div class="titulo-proyecto">📊 PROCESAR BOOM</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="descripcion-proyecto">Aquí irá el formulario de BOOM.</div>',
        unsafe_allow_html=True
    )


elif st.session_state.proyecto == "activos":

    st.markdown(
        '<div class="titulo-proyecto">🔍 PROCESAR ACTIVOS FIJOS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="descripcion-proyecto">Aquí irá el formulario de ACTIVOS FIJOS.</div>',
        unsafe_allow_html=True
    )