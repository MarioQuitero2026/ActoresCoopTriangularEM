# Dashboard Matriz de Mendelow — Actores por país

App interna en Streamlit que muestra la matriz de Mendelow (Poder–Interés)
de los actores de cada país/proyecto (Proyecto A GIZ/TransCERO y Proyecto B
DNP/BID), con un tab por hoja:

- 🌎 Regional (Retrofit y H2)
- 🇲🇽 México
- 🇨🇴 Colombia
- 🇵🇪 Perú
- 🇨🇱 Chile

Los datos vienen **embebidos en el repo** (carpeta `data/`), no hay que
subir ningún Excel al abrir la app.

Sigue la **Guía de Identidad Visual de IDOM** (v02.00, 22.05.2026): tipografía
Arial, Azul IDOM (#10069F) para títulos y la clasificación de mayor
prioridad ("Manejar de cerca"), Azul claro IDOM (#00B5E2) como color
secundario, Gris medio IDOM (#86867A) para lo de menor prioridad y Naranja
como único acento complementario — respetando el criterio de la guía de no
saturar los gráficos con colores complementarios.

## Estructura del repo

```
mendelow-dashboard/
├── app.py               # App de Streamlit (lee data/*.csv)
├── data_utils.py         # Normalización de columnas del Excel de origen
├── build_data.py          # Regenera data/*.csv a partir del Excel de origen
├── data/
│   ├── regional.csv
│   ├── mexico.csv
│   ├── colombia.csv
│   ├── peru.csv
│   └── chile.csv
├── assets/
│   ├── idom_logo.png     # (opcional) logo oficial positivo, ver assets/README.md
│   └── README.md
├── .streamlit/
│   └── config.toml       # tema con colores corporativos IDOM
├── requirements.txt
└── README.md
```

## Cómo actualizar los datos

Cuando el Excel de actores cambie (nuevas filas, puntajes actualizados,
etc.):

```bash
python build_data.py "Matriz_de_Actores_-_Identificación_y_análisis.xlsx"
git add data/
git commit -m "Actualiza datos de matriz de actores"
git push
```

Streamlit Community Cloud redespliega automáticamente al hacer push a `main`.

## Logo corporativo

Descarga el logotipo IDOM en versión positiva (PNG) desde el Workplace,
pestaña *Corporate/Commercial*, y guárdalo como `assets/idom_logo.png`. La
app lo detecta automáticamente. Si no está presente, la app funciona igual
sin logo (nunca se reconstruye el logotipo con texto/tipografía, tal como
indica la guía).

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud vía GitHub

1. Crea un repositorio en GitHub y sube todos estos archivos:

   ```bash
   git init
   git add .
   git commit -m "Dashboard Mendelow - actores (identidad IDOM)"
   git branch -M main
   git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
   git push -u origin main
   ```

2. Ve a [share.streamlit.io](https://share.streamlit.io), inicia sesión con
   tu cuenta de GitHub.
3. **New app** → selecciona el repo, la rama `main` y `app.py` como entry
   point → **Deploy**.
4. Cada `git push` a `main` redespliega la app automáticamente.

## Notas

- `data_utils.py` es el único lugar donde vive la lógica de mapeo de
  columnas heterogéneas entre hojas — si el Excel de origen cambia nombres
  de columnas, ajusta ahí `normalize_columns`.
- Si en el futuro se agregan más países/proyectos, añade la hoja al
  diccionario `SHEET_SLUGS` / `TAB_LABELS` en `data_utils.py` y vuelve a
  correr `build_data.py`.
