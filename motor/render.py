#!/usr/bin/env python3
"""Motor de diseño de posts de Paygo (JSON -> PNG 1080x1350).

Uso:
    python3 render.py post.json carpeta_salida

Requiere: pip install playwright (con Chromium instalado).
Ver README.md para el formato del JSON.
"""
import json
import os
import sys
import html

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(AQUI, "fonts")
LOGO_B = os.path.join(AQUI, "logo_blanco.png")
LOGO_N = os.path.join(AQUI, "logo_negro.png")

W, H = 1080, 1350

CSS = """
@font-face{font-family:'EBG';font-weight:400;font-style:normal;src:url('file://%(f)s/eb-garamond-latin-400-normal.woff2')}
@font-face{font-family:'EBG';font-weight:500;font-style:normal;src:url('file://%(f)s/eb-garamond-latin-500-normal.woff2')}
@font-face{font-family:'EBG';font-weight:400;font-style:italic;src:url('file://%(f)s/eb-garamond-latin-400-italic.woff2')}
@font-face{font-family:'EBG';font-weight:500;font-style:italic;src:url('file://%(f)s/eb-garamond-latin-500-italic.woff2')}
@font-face{font-family:'Inter';font-weight:400;src:url('file://%(f)s/inter-latin-400-normal.woff2')}
@font-face{font-family:'Inter';font-weight:500;src:url('file://%(f)s/inter-latin-500-normal.woff2')}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px}
.s{position:relative;width:1080px;height:1350px;overflow:hidden;font-family:'Inter',sans-serif}
.dark{background:#000;color:#fff;--mute:#9b9b9b;--body:#d4d4d4;--line:#333;--ghost:rgba(255,255,255,.22)}
.light{background:#F3F3F1;color:#000;--mute:#6b6b6b;--body:#2b2b2b;--line:#c9c9c9;--ghost:rgba(0,0,0,.22)}
.top{position:absolute;left:96px;right:96px;top:82px;display:flex;justify-content:space-between;
  font-size:25px;line-height:34px;color:var(--mute);font-weight:400}
.foot{position:absolute;left:96px;right:96px;bottom:84px;display:flex;justify-content:space-between;align-items:flex-end}
.foot img{height:41px;display:block}
.desliza{display:flex;align-items:center;gap:18px;font-size:26px;color:var(--mute);padding-bottom:4px}
.desliza svg{width:56px;height:14px}
.aviso{position:absolute;left:96px;right:96px;bottom:170px;font-size:23px;color:var(--mute)}
.titulo{font-family:'EBG',serif;font-weight:400;font-variant-ligatures:none}
.num{font-family:'EBG',serif;font-style:italic;font-weight:400;font-size:190px;line-height:1}
.texto{font-size:46px;line-height:1.5;color:var(--body);font-weight:400}
.sub{font-family:'EBG',serif;font-style:italic;font-size:56px;line-height:70px;color:var(--mute)}
.bloque{position:absolute;left:96px;right:96px}
.ghost{position:absolute;font-family:'EBG',serif;font-style:normal;font-weight:400;color:transparent;
  -webkit-text-stroke:2px var(--ghost);line-height:1;white-space:nowrap}
.item{font-size:43px;line-height:1.26;padding:36px 0;border-top:1px solid var(--line);font-weight:400}
.item:last-child{border-bottom:1px solid var(--line)}
.boton{display:inline-block;border:2px solid #fff;border-radius:999px;padding:26px 55px;font-size:30px;font-weight:500;color:#fff}
.light .boton{border-color:#0a0a0a;color:#0a0a0a}
""" % {"f": FONTS}

FLECHA = ('<svg viewBox="0 0 56 14" fill="none" stroke="currentColor" stroke-width="1.6">'
          '<path d="M0 7H54M48 1l6 6-6 6"/></svg>')


def esc(t):
    return html.escape(t).replace("\n", "<br>")


def uri(p):
    return "file://" + p


def lamina_html(l, i, n, etiqueta):
    i = l.get("pos", i + 1) - 1  # opcional: forzar posición/total (útil para rehacer una sola lámina)
    n = l.get("total", n)
    tipo = l.get("tipo", "contenido")
    oscuro = l.get("fondo")
    if oscuro is None:
        # Carrusel: impares oscuras, pares claras; la última siempre oscura. Imagen sola: oscura.
        oscuro = (i % 2 == 0) or (i == n - 1 and n > 1)
    else:
        oscuro = oscuro == "oscuro"
    cls = "dark" if oscuro else "light"
    logo = uri(LOGO_B if oscuro else LOGO_N)
    ultima = i == n - 1
    desliza = l.get("desliza", not ultima and n > 1)
    top = f'<div class="top"><span>{esc(etiqueta)}</span><span>{i + 1} / {n}</span></div>'
    foot = (f'<div class="foot"><img src="{logo}">'
            + (f'<div class="desliza">Desliza {FLECHA}</div>' if desliza else "") + "</div>")
    aviso = (f'<div class="aviso" style="font-size:{l.get("aviso_tam", 23)}px">{esc(l["aviso"])}</div>' if l.get("aviso") else "")
    body = ""
    t = l.get("titulo", "")
    if tipo == "portada":
        fs = l.get("tam", 134)
        ghost = ""
        if l.get("fantasma"):
            g = l["fantasma"]
            # Valores calibrados contra los posts originales: 1 carácter ("5") o palabra corta ("VS").
            if len(g) == 1:
                d_tam, d_x, d_y, ls = 1100, 637, -20, 0
            elif g.isdigit():  # años (ej. "2023"), arriba a la izquierda
                d_tam, d_x, d_y, ls = 520, 101, 168, 0
            else:  # palabra corta (ej. "VS")
                d_tam, d_x, d_y, ls = 500, 520, 320, 0.06
            ghost = (f'<div class="ghost" style="font-size:{l.get("fantasma_tam", d_tam)}px;'
                     f'left:{l.get("fantasma_x", d_x)}px;top:{l.get("fantasma_y", d_y)}px;letter-spacing:{ls}em">{esc(g)}</div>')
        body = (ghost + f'<div class="bloque titulo" style="bottom:{l.get("sube", 198)}px;'
                f'font-size:{fs}px;line-height:0.99">{esc(t)}</div>')
    elif tipo == "contenido":
        num = f'<div class="num">{esc(l["numero"])}</div>' if l.get("numero") else ""
        top_y = 210 if l.get("numero") else 220
        body = (f'<div class="bloque" style="top:{top_y}px">{num}'
                f'<div class="titulo" style="font-size:{l.get("tam", 106)}px;line-height:1.04;'
                f'margin-top:{35 if num else 0}px">{esc(t)}</div>'
                + (f'<div class="texto" style="margin-top:48px">{esc(l["texto"])}</div>' if l.get("texto") else "")
                + "</div>")
    elif tipo == "lista":
        items = "".join(f'<div class="item">{esc(x)}</div>' for x in l.get("items", []))
        body = (f'<div class="bloque" style="top:220px">'
                f'<div class="titulo" style="font-size:{l.get("tam", 106)}px;line-height:1.04">{esc(t)}</div>'
                + (f'<div class="sub" style="margin-top:34px">{esc(l["subtitulo"])}</div>' if l.get("subtitulo") else "")
                + f'<div style="margin-top:{l.get("items_y", 54)}px">{items}</div></div>')
    elif tipo == "frase":
        sub = f'<div class="sub" style="margin-top:41px">{esc(l["subtitulo"])}</div>' if l.get("subtitulo") else ""
        body = (f'<div class="bloque" style="top:{l.get("y", 351)}px">'
                f'<div class="titulo" style="font-size:{l.get("tam", 116)}px;line-height:1.03">{esc(t)}</div>{sub}</div>')
    elif tipo == "cierre":
        boton = f'<div class="boton">{esc(l["boton"])}</div>' if l.get("boton") else ""
        body = (f'<div class="bloque" style="top:219px">'
                f'<div class="titulo" style="font-size:{l.get("tam", 116)}px;line-height:1.02">{esc(t)}</div>'
                + (f'<div class="texto" style="margin-top:51px">{esc(l["texto"])}</div>' if l.get("texto") else "")
                + "</div>"
                + (f'<div class="bloque" style="bottom:{l.get("boton_sube", 211)}px">{boton}</div>' if boton else ""))
    return f'<div class="s {cls}">{top}{body}{aviso}{foot}</div>'


def render(spec, salida):
    from playwright.sync_api import sync_playwright
    os.makedirs(salida, exist_ok=True)
    laminas = spec["laminas"]
    n = len(laminas)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for i, l in enumerate(laminas):
            doc = f"<!doctype html><meta charset=utf-8><style>{CSS}</style>" + lamina_html(l, i, n, spec["etiqueta"])
            tmp = os.path.join(salida, f"_tmp{i}.html")
            open(tmp, "w", encoding="utf-8").write(doc)
            pg.goto("file://" + tmp)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            pg.screenshot(path=os.path.join(salida, f"{i + 1:02d}.png"), clip={"x": 0, "y": 0, "width": W, "height": H})
            os.remove(tmp)
        b.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    render(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
