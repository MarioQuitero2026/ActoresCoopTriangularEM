# Dashboard Matriz de Mendelow — Actores por país

App en Streamlit que convierte el Excel de matrices de actores (Proyecto A GIZ/TransCERO
y Proyecto B DNP/BID) en un scatter interactivo Poder–Interés (matriz de Mendelow),
con un tab por hoja/país:

- 🌎 Regional (Retrofit y H2)
- 🇲🇽 México
- 🇨🇴 Colombia
- 🇵🇪 Perú
- 🇨🇱 Chile

## Cómo funciona

1. Al abrir la app, se sube el archivo `.xlsx` con el mismo formato de columnas
   usado en `Matriz_de_Actores_-_Identificación_y_análisis.xlsx`
   (columnas: Actor, Categorización de actores, Clasificación en Matriz Mendelow,
   Interés (0-10), Poder (0-10), justificaciones, etc.).
2. La app detecta las hojas por nombre, normaliza encabezados (tolera pequeñas
   variaciones de mayúsculas/tildes entre hojas) y genera:
   - Un scatter Interés (eje X) vs. Poder (eje Y) con los 4 cuadrantes de Mendelow
     (Manejar de cerca / Mantener satisfecho / Mantener informado / Hacer seguimiento).
   - Tooltip por actor con categoría, alcance (solo hoja Regional), puntajes y
     un extracto de las justificaciones de poder e interés.
   - Filtro multiselección por categoría de actor.

No se guarda ningún dato: el Excel se procesa en memoria de la sesión (`st.cache_data`
solo cachea mientras la sesión está activa).

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud (gratis) vía GitHub

1. Crea un repositorio en GitHub y sube estos archivos (`app.py`, `requirements.txt`,
   este `README.md`):

   ```bash
   git init
   git add .
   git commit -m "Dashboard Mendelow - actores"
   git branch -M main
   git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
   git push -u origin main
   ```

2. Ve a [share.streamlit.io](https://share.streamlit.io) (Streamlit Community Cloud),
   inicia sesión con tu cuenta de GitHub.
3. Click en **"New app"** → selecciona el repositorio, la rama `main` y el archivo
   `app.py` como entry point.
4. Click en **Deploy**. Streamlit instalará `requirements.txt` automáticamente y la
   app quedará disponible en una URL pública tipo
   `https://<tu-app>.streamlit.app`.
5. Cada vez que hagas `git push` a `main`, la app se redepliega sola.

## Estructura del repo

```
mendelow-dashboard/
├── app.py             # App de Streamlit
├── requirements.txt   # Dependencias
└── README.md
```

## Notas

- Si en el futuro quieres que los datos vengan embebidos en el repo (en vez de
  subir el Excel cada vez), basta con guardar el `.xlsx` dentro del repo y
  reemplazar el `st.file_uploader` por una lectura directa del archivo con
  `pd.ExcelFile("data/matriz.xlsx")`.
- Si agregas más países/proyectos en el futuro, solo hace falta añadir la hoja
  correspondiente al diccionario `SHEET_TABS` en `app.py`.
