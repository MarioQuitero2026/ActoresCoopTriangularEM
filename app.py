"""
Dashboard de Matriz de Mendelow (Poder vs. Interés) por país / proyecto.

Lee un Excel con una hoja por país/proyecto (mismo formato usado por IDOM
para las matrices de actores de GIZ/TransCERO y DNP/BID) y genera un
scatter interactivo Poder-Interés con los 4 cuadrantes de Mendelow.
"""

import unicodedata

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Matriz de Mendelow - Actores",
    page_icon="📊",
    layout="wide",
)

# ----------------------------------------------------------------------
# Configuración de hojas esperadas (nombre de hoja -> etiqueta del tab)
# ----------------------------------------------------------------------
SHEET_TABS = {
    "Regional - Retrofit y H2": "🌎 Regional (Retrofit y H2)",
    "Mexico - Industria y BE": "🇲🇽 México",
    "Colombia - Infra de Carga": "🇨🇴 Colombia",
    "Peru - Patio Talleres": "🇵🇪 Perú",
    "Chile - Tarifas Diferenciadas": "🇨🇱 Chile",
}

QUADRANT_COLORS = {
    "Manejar de cerca": "#d62728",       # alto poder, alto interés
    "Mantener satisfecho": "#ff7f0e",    # alto poder, bajo interés
    "Mantener informado": "#1f77b4",     # bajo poder, alto interés
    "Hacer seguimiento": "#7f7f7f",      # bajo poder, bajo interés
}

MID = 5  # punto medio de la escala 0-10 que separa "alto" de "bajo"


def _strip_accents(text: str) -> str:
    text = str(text)
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra columnas heterogéneas del Excel a nombres estándar internos."""
    colmap = {}
    for col in df.columns:
        raw = str(col)
        c = _strip_accents(raw).lower().strip()

        if c == "actor":
            colmap[col] = "Actor"
        elif "alcance" in c:
            colmap[col] = "Alcance"
        elif "categorizacion" in c:
            colmap[col] = "Categoria"
        elif "justificacion" in c and "inclusion" in c:
            colmap[col] = "Justificacion_Inclusion"
        elif "mendelow" in c:
            colmap[col] = "Mendelow"
        elif c.startswith("interes") and "justificacion" not in c:
            colmap[col] = "Interes"
        elif "justificacion" in c and "interes" in c:
            colmap[col] = "Justificacion_Interes"
        elif c.startswith("poder") and "justificacion" not in c:
            colmap[col] = "Poder"
        elif "justificacion" in c and "poder" in c:
            colmap[col] = "Justificacion_Poder"
        elif c.startswith("legitimidad"):
            colmap[col] = "Legitimidad"
        elif "justificacion" in c and "legitimidad" in c:
            colmap[col] = "Justificacion_Legitimidad"
        elif c.startswith("urgencia"):
            colmap[col] = "Urgencia"
        elif "justificacion" in c and "urgencia" in c:
            colmap[col] = "Justificacion_Urgencia"
        elif "articulacion" in c and "justificacion" not in c:
            colmap[col] = "Capacidad_Articulacion"
        elif "justificacion" in c and "articulacion" in c:
            colmap[col] = "Justificacion_Articulacion"
        elif "genero" in c and "justificacion" not in c:
            colmap[col] = "Genero"
        elif "genero" in c and "justificacion" in c:
            colmap[col] = "Justificacion_Genero"
        elif "observ" in c:
            colmap[col] = "Observaciones"
        else:
            colmap[col] = raw
    return df.rename(columns=colmap)


@st.cache_data(show_spinner=False)
def load_workbook(file_bytes: bytes) -> dict:
    """Lee todas las hojas relevantes del Excel y devuelve un dict {sheet: df}."""
    xls = pd.ExcelFile(file_bytes)
    sheets = {}
    for sheet_name in SHEET_TABS:
        if sheet_name not in xls.sheet_names:
            continue
        raw = pd.read_excel(xls, sheet_name=sheet_name, header=3)
        raw = raw.dropna(axis=1, how="all")
        df = _normalize_columns(raw)

        # Quitar filas sin actor (separadores / filas vacías)
        df = df[df.get("Actor").notna()].copy()

        # Forzar numérico en Poder / Interés
        for numcol in ["Poder", "Interes"]:
            if numcol in df.columns:
                df[numcol] = pd.to_numeric(df[numcol], errors="coerce")

        df = df.dropna(subset=["Poder", "Interes"])
        sheets[sheet_name] = df
    return sheets


def quadrant_shapes():
    """Fondos de cuadrante: eje X = Interés, eje Y = Poder (convención clásica Mendelow)."""
    shapes = [
        dict(type="rect", x0=-0.5, x1=MID, y0=MID, y1=10.5,
             fillcolor=QUADRANT_COLORS["Mantener satisfecho"], opacity=0.07, line_width=0),
        dict(type="rect", x0=MID, x1=10.5, y0=MID, y1=10.5,
             fillcolor=QUADRANT_COLORS["Manejar de cerca"], opacity=0.07, line_width=0),
        dict(type="rect", x0=-0.5, x1=MID, y0=-0.5, y1=MID,
             fillcolor=QUADRANT_COLORS["Hacer seguimiento"], opacity=0.07, line_width=0),
        dict(type="rect", x0=MID, x1=10.5, y0=-0.5, y1=MID,
             fillcolor=QUADRANT_COLORS["Mantener informado"], opacity=0.07, line_width=0),
        dict(type="line", x0=MID, x1=MID, y0=-0.5, y1=10.5, line=dict(color="grey", dash="dot", width=1)),
        dict(type="line", x0=-0.5, x1=10.5, y0=MID, y1=MID, line=dict(color="grey", dash="dot", width=1)),
    ]
    return shapes


def quadrant_annotations():
    return [
        dict(x=MID / 2, y=9.7, text="Mantener satisfecho", showarrow=False,
             font=dict(color=QUADRANT_COLORS["Mantener satisfecho"], size=13)),
        dict(x=MID + (10 - MID) / 2, y=9.7, text="Manejar de cerca", showarrow=False,
             font=dict(color=QUADRANT_COLORS["Manejar de cerca"], size=13)),
        dict(x=MID / 2, y=0.3, text="Hacer seguimiento", showarrow=False,
             font=dict(color=QUADRANT_COLORS["Hacer seguimiento"], size=13)),
        dict(x=MID + (10 - MID) / 2, y=0.3, text="Mantener informado", showarrow=False,
             font=dict(color=QUADRANT_COLORS["Mantener informado"], size=13)),
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
        color = QUADRANT_COLORS.get(clasif, "#9467bd")
        fig.add_trace(go.Scatter(
            x=group["Interes"],
            y=group["Poder"],
            mode="markers",
            name=str(clasif),
            marker=dict(size=13, color=color, opacity=0.8, line=dict(width=1, color="white")),
            hovertext=group["hover"],
            hoverinfo="text",
        ))

    fig.update_layout(
        shapes=quadrant_shapes(),
        annotations=quadrant_annotations(),
        xaxis=dict(title="Interés →", range=[-0.5, 10.5], dtick=1, zeroline=False),
        yaxis=dict(title="Poder →", range=[-0.5, 10.5], dtick=1, zeroline=False),
        height=650,
        legend=dict(title="Clasificación Mendelow", orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_chart")


def main():
    st.title("📊 Dashboard de Matriz de Mendelow — Actores por país")
    st.caption(
        "Proyecto A (GIZ/TransCERO) y Proyecto B (DNP/BID) · "
        "Sube el Excel de matrices de actores para visualizar cada hoja como matriz Poder-Interés."
    )

    uploaded = st.file_uploader(
        "Sube el archivo Excel de matrices de actores (.xlsx)",
        type=["xlsx"],
    )

    if not uploaded:
        st.info(
            "⬆️ Sube el archivo `Matriz_de_Actores_-_Identificación_y_análisis.xlsx` "
            "(o cualquier Excel con el mismo formato de hojas) para generar el dashboard."
        )
        st.stop()

    with st.spinner("Leyendo el Excel..."):
        sheets = load_workbook(uploaded)

    if not sheets:
        st.error(
            "No se encontraron hojas con los nombres esperados: "
            + ", ".join(SHEET_TABS.keys())
        )
        st.stop()

    tab_labels = [SHEET_TABS[s] for s in sheets]
    tabs = st.tabs(tab_labels)

    for tab, sheet_name in zip(tabs, sheets):
        with tab:
            df = sheets[sheet_name]
            st.subheader(SHEET_TABS[sheet_name])
            render_tab(df, key_prefix=sheet_name.replace(" ", "_"))


if __name__ == "__main__":
    main()
