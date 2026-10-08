"""
Landscape banner (6 ft x 3 ft = 182.88 x 91.44 cm, 2:1) for the ULAB 23rd Foundation Day, CSE.
Follows the full Foundation Day poster: sky + campus photo, blue panel with the 23rd Anniversary mark, gold ribbon, ULAB logo top-right.

    python build_landscape_banner.py      ->  ./landscape_banner/  (.html, .pdf, .svg, preview.png)
The campus photo (bg2.png) sits on the right at full height; the sky / lawn on its left are a gradient built from the photo's own
left-edge colours, so the join is invisible. Change W_CM / H_CM for another size with the same 2:1 shape.
"""
import base64, io, re
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).parent
OUT = ROOT / "landscape_banner"
OUT.mkdir(exist_ok=True)
W_CM, H_CM = 182.88, 91.44
NAME = "ULAB_23rd_Foundation_Day_CSE_Banner_6x3ft"
W, H = 2000, 1000
NAVY, GOLD, PANEL = "#0A2A5B", "#FFC745", "#2C7BC8"
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"


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


# ----------------------------------------------------------------------------- the campus photo
PH = 1000                                           # photo is placed square, full height, flush right
px0 = W - PH
src = Image.open(ROOT / "bg2.png").convert("RGB")
sw, sh = src.size
arr = np.asarray(src).astype(float)


def edge_colour(y):                                  # average colour of the photo's left edge around source row y
    y0, y1 = max(0, y - 10), min(sh, y + 10)
    c = arr[y0:y1, 0:8].mean(axis=(0, 1))
    return "#%02X%02X%02X" % tuple(int(v) for v in c)


SKY_ROWS = [0, 120, 240, 340, 400]
LAWN = [(430, "#A9D08A"), (520, "#7FBA4C"), (700, "#62A235"), (1253, "#4B8A27")]      # horizon haze -> bright lawn
STOPS = "".join(f'<stop offset="{r / (sh - 1):.3f}" stop-color="{edge_colour(r)}"/>' for r in SKY_ROWS) +         "".join(f'<stop offset="{r / (sh - 1):.3f}" stop-color="{c}"/>' for r, c in LAWN)

yy, xx = np.mgrid[0:sh, 0:sw]
t = np.clip(xx / (0.42 * sw), 0, 1)
alpha = (t * t * (3 - 2 * t) * 255).astype("uint8")
rgba = src.convert("RGBA"); rgba.putalpha(Image.fromarray(alpha))
buf = io.BytesIO(); rgba.save(buf, "PNG", optimize=True)
PHOTO = uri(buf.getvalue(), "image/png")

U_URI, U_R = ulab_logo()
A_URI, A_R = anniversary()

# ----------------------------------------------------------------------------- layout
PX, PY, PW, PHH = 110, 205, 830, 520               # blue panel
ST_W = 440                                         # white sticker holding the anniversary mark (overlaps the panel's top edge)
IN = 30                                            # padding inside the sticker
ST_X, ST_Y = PX + 30, PY - 120
IM_W = ST_W - 2 * IN
IM_H = IM_W / A_R
ST_H = IM_H + 2 * IN
TX = PX + PW / 2                                   # text centre
LOGO_W = 400

svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W_CM}cm" height="{H_CM}cm" font-family="{FONT}">
  <defs>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">{STOPS}</linearGradient>
    <linearGradient id="rib" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#E58E00"/><stop offset=".35" stop-color="#F7B01A"/><stop offset="1" stop-color="#FFD24D"/></linearGradient>
    <linearGradient id="ribD" x1="0" x2="1"><stop offset="0" stop-color="#B86A00"/><stop offset="1" stop-color="#E58E00"/></linearGradient>
    <clipPath id="stk"><rect x="{ST_X + IN}" y="{ST_Y + IN}" width="{IM_W}" height="{IM_H:.1f}" rx="14"/></clipPath>
  </defs>

  <!-- sky + lawn: the photo's own left-edge colours, stretched across the whole banner -->
  <rect width="{W}" height="{H}" fill="url(#ground)"/>

  <!-- clouds (clusters of circles, soft shade underneath) -->
  <g fill="#fff">
    <g opacity=".95"><circle cx="90" cy="70" r="72"/><circle cx="190" cy="48" r="70"/><circle cx="290" cy="74" r="62"/><circle cx="380" cy="86" r="48"/><rect x="40" y="70" width="380" height="64" rx="32"/></g>
    <g opacity=".9"><circle cx="1020" cy="86" r="42"/><circle cx="1090" cy="66" r="52"/><circle cx="1170" cy="92" r="40"/><rect x="990" y="88" width="210" height="44" rx="22"/></g>
    <g opacity=".85"><circle cx="560" cy="60" r="34"/><circle cx="615" cy="44" r="40"/><circle cx="680" cy="64" r="32"/><rect x="530" y="60" width="180" height="34" rx="17"/></g>
  </g>

  <!-- gold ribbon (behind the photo, so it tucks behind the trees) -->
  <path d="M-10 735 C170 690 330 760 520 828 S900 900 1500 872 L1500 986 C1000 1016 700 940 520 906 S170 800 -10 842 Z" fill="url(#rib)"/>
  <path d="M-10 735 C60 722 110 736 150 758 L150 830 C110 812 60 808 -10 842 Z" fill="url(#ribD)"/>
  <path d="M-10 735 C170 690 330 760 520 828 S900 900 1500 872" fill="none" stroke="#FFE08A" stroke-width="5" opacity=".7"/>

  <!-- campus photo, full height, flush right; its left edge dissolves into the sky/lawn gradient -->
  <image href="{PHOTO}" x="{px0}" y="0" width="{PH}" height="{PH}"/>

  <!-- blue panel -->
  <rect x="{PX}" y="{PY}" width="{PW}" height="{PHH}" rx="44" fill="{PANEL}" opacity=".94"/>
  <rect x="{PX}" y="{PY}" width="{PW}" height="{PHH}" rx="44" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="3"/>

  <!-- 23rd anniversary mark (white sticker, like the poster's outlined logo) -->
  <rect x="{ST_X}" y="{ST_Y}" width="{ST_W}" height="{ST_H:.1f}" rx="52" fill="#fff"/>
  <image href="{A_URI}" x="{ST_X + IN}" y="{ST_Y + IN}" width="{IM_W}" height="{IM_H:.1f}" clip-path="url(#stk)"/>

  <!-- text -->
  <g text-anchor="middle" fill="#fff">
    <text id="a" x="{TX}" y="{PY + 232}" font-size="88" font-weight="400" letter-spacing="2">23<tspan font-size="48" dy="-38">rd</tspan><tspan dy="38"> ULAB</tspan></text>
    <text id="b" x="{TX}" y="{PY + 322}" font-size="76" font-weight="800">FOUNDATION DAY</text>
    <rect x="{TX - 100}" y="{PY + 352}" width="200" height="7" rx="3.5" fill="{GOLD}"/>
    <text id="c" x="{TX}" y="{PY + 410}" font-size="38" font-weight="400">Department of Computer Science</text>
    <text id="d" x="{TX}" y="{PY + 456}" font-size="38" font-weight="400">and Engineering</text>
    <text id="e" x="{TX}" y="{PY + 506}" font-size="40" font-weight="800" fill="{GOLD}">4 October 2026</text>
  </g>

  <!-- ULAB logo, top-right on the sky (as on the poster) -->
  <image href="{U_URI}" x="{W - 80 - LOGO_W}" y="70" width="{LOGO_W}" height="{LOGO_W / U_R:.1f}"/>
</svg>"""

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{NAME}</title>
<style>@page {{ size: {W_CM}cm {H_CM}cm; margin: 0 }} html,body {{ margin:0; padding:0; overflow:hidden; background:#fff }} svg {{ display:block }}</style></head>
<body>{svg}</body></html>"""
(OUT / f"{NAME}.html").write_text(html, encoding="utf-8")

from playwright.sync_api import sync_playwright
import fitz

pdf_path = OUT / f"{NAME}.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 2000, "height": 1000})
    pg.goto((OUT / f"{NAME}.html").as_uri()); pg.wait_for_timeout(600)
    print("text extents (x0,x1) of 2000; panel", PX, "-", PX + PW,
          pg.evaluate("() => [...document.querySelectorAll('text[id]')].map(t => { const r = t.getBBox(); return [t.id, Math.round(r.x), Math.round(r.x + r.width)]; })"))
    pdf_path.write_bytes(pg.pdf(width=f"{W_CM}cm", height=f"{H_CM}cm", print_background=True, prefer_css_page_size=True))
    b.close()

doc = fitz.open(str(pdf_path))
print("pages:", doc.page_count, "size cm:", round(doc[0].rect.width / 72 * 2.54, 1), "x", round(doc[0].rect.height / 72 * 2.54, 1))
doc[0].get_pixmap(matrix=fitz.Matrix(0.4, 0.4)).save(str(OUT / "preview.png"))
(OUT / f"{NAME}.svg").write_text(doc[0].get_svg_image(text_as_path=True), encoding="utf-8")
print("done")
