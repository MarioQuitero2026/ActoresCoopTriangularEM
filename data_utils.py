"""
Utilidades compartidas para leer y normalizar las hojas del Excel de
matrices de actores. Usado tanto por build_data.py (una vez, para generar
los CSV embebidos) como potencialmente para regenerar datos en el futuro.
"""

import unicodedata

import pandas as pd

# Nombre de hoja en el Excel -> slug interno (nombre de fichero / clave de datos)
SHEET_SLUGS = {
    "Regional - Retrofit y H2": "regional",
    "Mexico - Industria y BE": "mexico",
    "Colombia - Infra de Carga": "colombia",
    "Peru - Patio Talleres": "peru",
    "Chile - Tarifas Diferenciadas": "chile",
}

# slug -> etiqueta para mostrar en la app (tab)
TAB_LABELS = {
    "regional": "🌎 Regional (Retrofit y H2)",
    "mexico": "🇲🇽 México",
    "colombia": "🇨🇴 Colombia",
    "peru": "🇵🇪 Perú",
    "chile": "🇨🇱 Chile",
}


def _strip_accents(text: str) -> str:
    text = str(text)
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
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


def load_sheet(xls: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
    raw = pd.read_excel(xls, sheet_name=sheet_name, header=3)
    raw = raw.dropna(axis=1, how="all")
    df = normalize_columns(raw)
    df = df[df.get("Actor").notna()].copy()

    for numcol in ["Poder", "Interes"]:
        if numcol in df.columns:
            df[numcol] = pd.to_numeric(df[numcol], errors="coerce")

    df = df.dropna(subset=["Poder", "Interes"])
    return df
