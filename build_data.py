"""
Regenera los CSV embebidos en data/ a partir del Excel fuente de matrices
de actores.

Uso:
    python build_data.py "Matriz_de_Actores_-_Identificación_y_análisis.xlsx"

Ejecutar cada vez que el Excel de origen se actualice, y hacer commit de
los CSV resultantes en data/. La app en producción NUNCA lee el Excel
directamente: siempre lee los CSV de data/.
"""

import sys
from pathlib import Path

import pandas as pd

from data_utils import SHEET_SLUGS, load_sheet

DATA_DIR = Path(__file__).parent / "data"


def main(xlsx_path: str):
    xls = pd.ExcelFile(xlsx_path)
    DATA_DIR.mkdir(exist_ok=True)

    for sheet_name, slug in SHEET_SLUGS.items():
        if sheet_name not in xls.sheet_names:
            print(f"⚠️  Hoja no encontrada, se omite: {sheet_name}")
            continue
        df = load_sheet(xls, sheet_name)
        out_path = DATA_DIR / f"{slug}.csv"
        df.to_csv(out_path, index=False)
        print(f"✅ {sheet_name} -> {out_path} ({len(df)} actores)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
