"""
Descarga las imágenes que muestra una página de resultados de fotop.com.

Uso:
    pip install playwright requests
    playwright install chromium
    python descargar_fotos.py "https://oscarpenaranda.fotop.com/fotos/eventos/busca/evento/353910/rc/1" -o fotos

Flujo:
 1. Se abre un Chrome visible (no headless).
 2. Tú haces la selfie / búsqueda facial manualmente en la página.
 3. Cuando veas los resultados, vuelve a la terminal y presiona Enter.
 4. El script hace scroll (para cargar las imágenes perezosas), recoge las
    URLs de las <img> y las descarga.

Nota: descarga exactamente lo que el sitio sirve al navegador (las vistas
previas con desenfoque/marca de agua). Las fotos originales en alta
resolución requieren comprarlas en el sitio.
"""
import argparse
import hashlib
import mimetypes
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

JS_COLLECT = """
() => {
  const urls = new Set();
  document.querySelectorAll('img').forEach(i => {
    [i.currentSrc, i.src, i.dataset.src, i.dataset.original, i.dataset.lazy]
      .forEach(u => u && urls.add(u));
    if (i.srcset) i.srcset.split(',').forEach(s => urls.add(s.trim().split(' ')[0]));
  });
  document.querySelectorAll('*').forEach(el => {
    const bg = getComputedStyle(el).backgroundImage;
    const m = bg && bg.match(/url\\(["']?(.*?)["']?\\)/);
    if (m) urls.add(m[1]);
  });
  return [...urls];
}
"""


def scroll_all(page, pausa=800, max_vueltas=60):
    """Hace scroll hasta que la altura de la página deja de crecer."""
    ultima = 0
    for _ in range(max_vueltas):
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(pausa)
        alto = page.evaluate("document.body.scrollHeight")
        if alto == ultima:
            break
        ultima = alto


def es_foto(url):
    if not url or url.startswith("data:"):
        return False
    ruta = urlparse(url).path.lower()
    if re.search(r"(logo|icon|sprite|avatar|favicon|\.svg$|\.gif$)", ruta):
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("-o", "--out", default="fotos")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(args.url)

        input("\nHaz la selfie / búsqueda en el navegador. "
              "Cuando veas las fotos, presiona Enter aquí... ")

        # Si la búsqueda abrió otra pestaña, usa la última
        page = ctx.pages[-1]
        scroll_all(page)

        urls = [urljoin(page.url, u) for u in page.evaluate(JS_COLLECT)]
        urls = [u for u in dict.fromkeys(urls) if es_foto(u)]
        print(f"Encontradas {len(urls)} imágenes candidatas.")

        guardadas = 0
        for u in urls:
            try:
                r = ctx.request.get(u, headers={"Referer": page.url})
                if not r.ok:
                    print(f"  SKIP status {r.status}: {u}")
                    continue
                tipo = r.headers.get("content-type", "").split(";")[0]
                ext_url = Path(urlparse(u).path).suffix.lower()
                es_img_url = ext_url in (".jpg", ".jpeg", ".png", ".webp")
                if not tipo.startswith("image/") and not es_img_url:
                    print(f"  SKIP tipo '{tipo}': {u}")
                    continue
                cuerpo = r.body()
                if len(cuerpo) < 1_000:  # descarta pixeles/iconos diminutos
                    print(f"  SKIP muy pequeña ({len(cuerpo)} bytes): {u}")
                    continue
                ext = ext_url if es_img_url else (mimetypes.guess_extension(tipo) or ".jpg")
                nombre = Path(urlparse(u).path).stem + ext
                if (out / nombre).exists():
                    nombre = hashlib.md5(u.encode()).hexdigest()[:10] + ext
                (out / nombre).write_bytes(cuerpo)
                guardadas += 1
                print(f"  OK  {nombre}  <- {u}")
            except Exception as e:
                print(f"  ERR {u}: {e}", file=sys.stderr)

        print(f"\nListo: {guardadas} imágenes guardadas en '{out}/'.")
        browser.close()


if __name__ == "__main__":
    main()
