"""
Dashboard interno de Matriz de Mendelow (Poder vs. Interés) por país/proyecto.

Datos embebidos en data/ (generados con build_data.py a partir del Excel
oficial de matrices de actores). No requiere subir ningún archivo: uso
interno del equipo de proyecto.

Identidad visual conforme a la Guía de Identidad Visual de IDOM
(v02.00, 22.05.2026).
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_utils import TAB_LABELS

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "idom_logo.png"  # coloca aquí el PNG oficial (positivo)

# ----------------------------------------------------------------------
# Paleta y tipografía corporativa IDOM (Guía de Identidad Visual v02.00)
# ----------------------------------------------------------------------
IDOM = {
    "azul": "#10069F",         # Azul IDOM (primario)
    "azul_claro": "#00B5E2",   # Azul claro IDOM (secundario)
    "gris": "#86867A",         # Gris medio IDOM
    "gris_claro": "#EFEFED",   # Gris claro IDOM (fondos de tabla/gráfico)
    "gris_texto": "#AFAFA7",   # Gris IDOM (texto)
    "negro": "#000000",
    "blanco": "#FFFFFF",
    "naranja": "#FFA300",      # Complementario
    "rojo": "#DA291C",         # Rojo IDOM (solo para negativos/alertas)
}

FONT_FAMILY = "Arial, Helvetica, sans-serif"

# Clasificación Mendelow -> color corporativo, respetando la jerarquía de la
# guía (Azul IDOM para la información principal / mayor prioridad, Azul
# claro IDOM como secundario, gris para lo de menor prioridad, naranja como
# único acento complementario).
QUADRANT_COLORS = {
    "Manejar de cerca": IDOM["azul"],
    "Mantener satisfecho": IDOM["naranja"],
    "Mantener informado": IDOM["azul_claro"],
    "Hacer seguimiento": IDOM["gris"],
}

MID = 5  # punto medio de la escala 0-10 que separa "alto" de "bajo"

st.set_page_config(
    page_title="Matriz de Mendelow - Actores",
    page_icon="📊",
    layout="wide",
)

# ----------------------------------------------------------------------
# CSS corporativo: tipografía Arial, títulos en Azul IDOM, negro en cuerpo
# ----------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-family: {FONT_FAMILY};
    }}
    h1, h2, h3 {{
        color: {IDOM["azul"]} !important;
        font-family: {FONT_FAMILY};
    }}
    p, span, label, div {{
        color: {IDOM["negro"]};
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
    }}
    .stTabs [aria-selected="true"] {{
        color: {IDOM["azul"]} !important;
        border-bottom-color: {IDOM["azul"]} !important;
    }}
    .idom-footer {{
        text-align: right;
        color: {IDOM["azul"]};
        font-family: {FONT_FAMILY};
        letter-spacing: 0.5px;
        font-size: 0.8rem;
        margin-top: 2rem;
        border-top: 1px solid {IDOM["gris_claro"]};
        padding-top: 0.5rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_all_data() -> dict:
    """Carga los CSV embebidos en data/ (uno por hoja/país)."""
    sheets = {}
    for slug in TAB_LABELS:
        path = DATA_DIR / f"{slug}.csv"
        if path.exists():
            sheets[slug] = pd.read_csv(path)
    return sheets


def quadrant_shapes():
    """Fondos de cuadrante: eje X = Interés, eje Y = Poder."""
    return [
        dict(type="rect", x0=-0.5, x1=MID, y0=MID, y1=10.5,
             fillcolor=QUADRANT_COLORS["Mantener satisfecho"], opacity=0.08, line_width=0),
        dict(type="rect", x0=MID, x1=10.5, y0=MID, y1=10.5,
             fillcolor=QUADRANT_COLORS["Manejar de cerca"], opacity=0.08, line_width=0),
        dict(type="rect", x0=-0.5, x1=MID, y0=-0.5, y1=MID,
             fillcolor=QUADRANT_COLORS["Hacer seguimiento"], opacity=0.10, line_width=0),
        dict(type="rect", x0=MID, x1=10.5, y0=-0.5, y1=MID,
             fillcolor=QUADRANT_COLORS["Mantener informado"], opacity=0.08, line_width=0),
        dict(type="line", x0=MID, x1=MID, y0=-0.5, y1=10.5,
             line=dict(color=IDOM["gris_texto"], dash="dot", width=1)),
        dict(type="line", x0=-0.5, x1=10.5, y0=MID, y1=MID,
             line=dict(color=IDOM["gris_texto"], dash="dot", width=1)),
    ]


def quadrant_annotations():
    return [
        dict(x=MID / 2, y=9.7, text="Mantener satisfecho", showarrow=False,
             font=dict(color=QUADRANT_COLORS["Mantener satisfecho"], size=13, family=FONT_FAMILY)),
        dict(x=MID + (10 - MID) / 2, y=9.7, text="Manejar de cerca", showarrow=False,
             font=dict(color=QUADRANT_COLORS["Manejar de cerca"], size=13, family=FONT_FAMILY)),
        dict(x=MID / 2, y=0.3, text="Hacer seguimiento", showarrow=False,
             font=dict(color=QUADRANT_COLORS["Hacer seguimiento"], size=13, family=FONT_FAMILY)),
        dict(x=MID + (10 - MID) / 2, y=0.3, text="Mantener informado", showarrow=False,
             font=dict(color=QUADRANT_COLORS["Mantener informado"], size=13, family=FONT_FAMILY)),
    ]


def build_hover_text(row: pd.Series) -> str:
    parts = [f"<b>{row.get('Actor', '')}</b>"]
    if pd.notna(row.get("Categoria")):
        parts.append(f"Categoría: {row['Categoria']}")
    if "Alcance" in row and pd.notna(row.get("Alcance")):
        parts.append(f"Alcance: {row['Alcance']}")
    parts.append(f"Poder: {row.get('Poder')} | Interés: {row.get('Interes')}")
    if pd.notna(row.get("Mendelow")):
        parts.append(f"Clasificación: {row['Mendelow']}")
    if pd.notna(row.get("Justificacion_Poder")):
        just = str(row["Justificacion_Poder"])
        parts.append(f"<i>Poder:</i> {just[:180]}{'…' if len(just) > 180 else ''}")
    if pd.notna(row.get("Justificacion_Interes")):
        just = str(row["Justificacion_Interes"])
        parts.append(f"<i>Interés:</i> {just[:180]}{'…' if len(just) > 180 else ''}")
    return "<br>".join(parts)


def render_tab(df: pd.DataFrame, key_prefix: str):
    if df.empty:
        st.info("No hay datos disponibles en esta hoja.")
        return

    categorias = sorted(df["Categoria"].dropna().unique().tolist()) if "Categoria" in df.columns else []
    filtro_cols = st.columns([3, 1])
    with filtro_cols[0]:
        seleccion = st.multiselect(
            "Filtrar por categoría de actor",
            options=categorias,
            default=categorias,
            key=f"{key_prefix}_cat_filter",
        )
    with filtro_cols[1]:
        st.metric("Actores mostrados", len(df[df["Categoria"].isin(seleccion)]) if categorias else len(df))

    plot_df = df[df["Categoria"].isin(seleccion)] if categorias else df
    if plot_df.empty:
        st.warning("No hay actores para los filtros seleccionados.")
        return

    plot_df = plot_df.copy()
    plot_df["hover"] = plot_df.apply(build_hover_text, axis=1)

    fig = go.Figure()

    if "Mendelow" in plot_df.columns:
        groups = plot_df.groupby(plot_df["Mendelow"].fillna("Sin clasificar"))
    else:
        groups = [("Actores", plot_df)]

    for clasif, group in groups:
        color = QUADRANT_COLORS.get(clasif, IDOM["gris_texto"])
        fig.add_trace(go.Scatter(
            x=group["Interes"],
            y=group["Poder"],
            mode="markers",
            name=str(clasif),
            marker=dict(size=13, color=color, opacity=0.85,
                        line=dict(width=1, color=IDOM["blanco"])),
            hovertext=group["hover"],
            hoverinfo="text",
        ))

    fig.update_layout(
        shapes=quadrant_shapes(),
        annotations=quadrant_annotations(),
        xaxis=dict(title="Interés →", range=[-0.5, 10.5], dtick=1, zeroline=False,
                    gridcolor=IDOM["gris_claro"]),
        yaxis=dict(title="Poder →", range=[-0.5, 10.5], dtick=1, zeroline=False,
                    gridcolor=IDOM["gris_claro"]),
        height=650,
        font=dict(family=FONT_FAMILY, color=IDOM["negro"]),
        plot_bgcolor=IDOM["blanco"],
        paper_bgcolor=IDOM["blanco"],
        legend=dict(title="Clasificación Mendelow", orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_chart")


def render_header():
    cols = st.columns([1, 5])
    with cols[0]:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=140)
    with cols[1]:
        st.title("Dashboard de Matriz de Mendelow — Actores por país")


def render_footer():
    st.markdown(
        '<div class="idom-footer">OUR COMMITMENT, YOUR SUCCESS</div>',
        unsafe_allow_html=True,
    )


def main():
    render_header()

    sheets = load_all_data()
    if not sheets:
        st.error(
            "No se encontraron datos en la carpeta data/. Ejecuta build_data.py "
            "con el Excel de origen para generarlos."
        )
        st.stop()

    tab_labels = [TAB_LABELS[slug] for slug in sheets]
    tabs = st.tabs(tab_labels)

    for tab, slug in zip(tabs, sheets):
        with tab:
            df = sheets[slug]
            st.subheader(TAB_LABELS[slug])
            render_tab(df, key_prefix=slug)

    render_footer()


if __name__ == "__main__":
    main()
