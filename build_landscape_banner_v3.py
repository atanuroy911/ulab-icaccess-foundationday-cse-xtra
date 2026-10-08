"""
Landscape banner (6 ft x 3 ft = 182.88 x 91.44 cm, 2:1) for the ULAB 23rd Foundation Day, CSE.
Version 3: airy light design. No overlay, no ribbon, no bar. Campus photo pushed down; its sky fades into white / light sky blue where the title sits.

    python build_landscape_banner.py      ->  ./landscape_banner_v3/  (.html, .pdf, .svg, preview.png)
The campus photo (bg2.png) sits on the right at full height; the sky / lawn on its left are a gradient built from the photo's own
left-edge colours, so the join is invisible. Change W_CM / H_CM for another size with the same 2:1 shape.
"""
import base64, io, re
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).parent
OUT = ROOT / "landscape_banner_v3"
OUT.mkdir(exist_ok=True)
W_CM, H_CM = 182.88, 91.44
NAME = "ULAB_23rd_Foundation_Day_CSE_Banner_6x3ft_v3"
W, H = 2000, 1000
NAVY, GOLD, PANEL = "#0A2A5B", "#FFC745", "#2C7BC8"
BLUE = "#1260B8"
FONT = "Poppins, 'Segoe UI', Arial, sans-serif"


def uri(buf, mime):
    return f"data:{mime};base64,{base64.b64encode(buf).decode()}"


def ulab_logo():
    s = (ROOT / "cue-cards" / "ulab-logo.svg").read_text(encoding="utf-8")
    x0, y0, x1, y1 = 117, 20, 1683, 592
    s = re.sub(r'viewBox="[^"]*"', f'viewBox="{x0} {y0} {x1 - x0} {y1 - y0}"', s, count=1)
    s = re.sub(r'\swidth="[^"]*"', f' width="{x1 - x0}"', s, count=1)
    s = re.sub(r'\sheight="[^"]*"', f' height="{y1 - y0}"', s, count=1)
    return uri(s.encode(), "image/svg+xml"), (x1 - x0) / (y1 - y0)


def anniversary():
    im = Image.open(ROOT / "anniversary_logo_23rd.png").convert("RGB")
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return uri(b.getvalue(), "image/png"), im.width / im.height


# ----------------------------------------------------------------------------- campus photo: pushed down, sky fades up into the page
src = Image.open(ROOT / "bg2.png").convert("RGB")
sw, sh = src.size
S = 0.95                                              # photo scale on the banner
PW_, PH_ = sw * S, sh * S
PX0 = W - PW_                                         # flush right
PY0 = 160                                             # roof line lands around y = 540, well below the title
yy, xx = np.mgrid[0:sh, 0:sw]
sm = lambda t: t * t * (3 - 2 * t)
alpha = sm(np.clip(yy / (0.34 * sh), 0, 1)) * sm(np.clip(xx / (0.30 * sw), 0, 1))     # sky dissolves upward and to the left
rgba = src.convert("RGBA"); rgba.putalpha(Image.fromarray((alpha * 255).astype("uint8")))
bb = io.BytesIO(); rgba.save(bb, "PNG", optimize=True)
PHOTO = uri(bb.getvalue(), "image/png")
U_URI, U_R = ulab_logo()
A_URI, A_R = anniversary()

UL_W = 345
AN_W = 285
AN_H = AN_W / A_R
AN_CARD_W, AN_CARD_H = AN_W + 50, AN_H + 50


def spark(x, y, r, c=GOLD, o=1):
    k = r * 0.2
    return f'<polygon points="{x},{y - r} {x + k},{y - k} {x + r},{y} {x + k},{y + k} {x},{y + r} {x - k},{y + k} {x - r},{y} {x - k},{y - k}" fill="{c}" opacity="{o}"/>'


sparks = spark(300, 300, 22) + spark(1700, 350, 28) + spark(1760, 520, 16, "#fff") + spark(240, 480, 18, "#fff")

svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W_CM}cm" height="{H_CM}cm" font-family="{FONT}">
  <defs>
    <linearGradient id="page" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF"/><stop offset=".22" stop-color="#F2F9FE"/><stop offset=".5" stop-color="#C9E4F8"/>
      <stop offset=".64" stop-color="#D3EAC2"/><stop offset=".8" stop-color="#93C762"/><stop offset="1" stop-color="#5E9E34"/>
    </linearGradient>
    <radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset=".6" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <linearGradient id="ink" x1="0" x2="1"><stop offset="0" stop-color="#0A2A5B"/><stop offset="1" stop-color="#1260B8"/></linearGradient>
    <clipPath id="ancl"><rect x="{W - 70 - AN_CARD_W + 25}" y="{42 + 25}" width="{AN_W}" height="{AN_H:.1f}" rx="12"/></clipPath>
  </defs>

  <!-- page: white -> light sky blue -> lawn -->
  <rect width="{W}" height="{H}" fill="url(#page)"/>

  <!-- campus photo, pushed down; its sky melts into the page above -->
  <image href="{PHOTO}" x="{PX0:.1f}" y="{PY0}" width="{PW_:.1f}" height="{PH_:.1f}"/>

  <!-- giant outlined 23 on the lawn -->
  <text x="270" y="1090" text-anchor="middle" font-size="470" font-weight="900" fill="none" stroke="#fff" stroke-opacity=".38" stroke-width="8">23</text>

  <!-- soft halo behind the title -->
  <ellipse cx="{W / 2}" cy="390" rx="900" ry="300" fill="url(#halo)"/>

  {sparks}

  <!-- logos -->
  <image href="{U_URI}" x="70" y="52" width="{UL_W}" height="{UL_W / U_R:.1f}"/>
  <rect x="{W - 70 - AN_CARD_W}" y="42" width="{AN_CARD_W}" height="{AN_CARD_H:.1f}" rx="28" fill="#fff" stroke="#BFD9EE" stroke-width="4"/>
  <image href="{A_URI}" x="{W - 70 - AN_CARD_W + 25}" y="67" width="{AN_W}" height="{AN_H:.1f}" clip-path="url(#ancl)"/>

  <!-- title -->
  <g text-anchor="middle">
    <text id="a" x="{W / 2}" y="292" font-size="178" font-weight="800" letter-spacing="-2" fill="{NAVY}">23<tspan font-size="92" dy="-80" font-weight="700">rd</tspan><tspan dy="80"> ULAB</tspan></text>
    <text id="b" x="{W / 2}" y="427" font-size="118" font-weight="800" letter-spacing="2" fill="url(#ink)">FOUNDATION DAY</text>
    <path d="M{W / 2 - 330} 467 Q {W / 2} 447 {W / 2 + 330} 467" fill="none" stroke="{GOLD}" stroke-width="13" stroke-linecap="round"/>
    <text id="c" x="{W / 2}" y="545" font-size="40" font-weight="600" letter-spacing="3" fill="{NAVY}">Department of</text>
    <text id="d" x="{W / 2}" y="625" font-size="68" font-weight="700" fill="{NAVY}">Computer Science and Engineering</text>
  </g>
</svg>"""

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{NAME}</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>@page {{ size: {W_CM}cm {H_CM}cm; margin: 0 }} html,body {{ margin:0; padding:0; overflow:hidden; background:#fff }} svg {{ display:block }}</style></head>
<body>{svg}</body></html>"""
(OUT / f"{NAME}.html").write_text(html, encoding="utf-8")

from playwright.sync_api import sync_playwright
import fitz

pdf_path = OUT / f"{NAME}.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 2000, "height": 1000})
    pg.goto((OUT / f"{NAME}.html").as_uri(), wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(800)
    print("text extents (x0,x1) of 2000:",
          pg.evaluate("() => [...document.querySelectorAll('text[id]')].map(t => { const r = t.getBBox(); return [t.id, Math.round(r.x), Math.round(r.x + r.width)]; })"))
    pdf_path.write_bytes(pg.pdf(width=f"{W_CM}cm", height=f"{H_CM}cm", print_background=True, prefer_css_page_size=True))
    b.close()

doc = fitz.open(str(pdf_path))
print("pages:", doc.page_count, "size cm:", round(doc[0].rect.width / 72 * 2.54, 1), "x", round(doc[0].rect.height / 72 * 2.54, 1))
doc[0].get_pixmap(matrix=fitz.Matrix(0.4, 0.4)).save(str(OUT / "preview.png"))
(OUT / f"{NAME}.svg").write_text(doc[0].get_svg_image(text_as_path=True), encoding="utf-8")
print("done")
