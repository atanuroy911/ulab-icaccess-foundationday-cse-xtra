"""
Landscape banner (6 ft x 3 ft = 182.88 x 91.44 cm, 2:1) for the ULAB 23rd Foundation Day, CSE.
Replica of the reference vinyl banner: pale fabric, ULAB logo top-left, 23rd mark top-right, serif title, thin rule, department, green swoosh bottom-left, soft pastel campus picture bottom-right.

    python build_landscape_banner.py      ->  ./landscape_banner_replica/  (.html, .pdf, .svg, preview.png)
The campus photo (bg2.png) sits on the right at full height; the sky / lawn on its left are a gradient built from the photo's own
left-edge colours, so the join is invisible. Change W_CM / H_CM for another size with the same 2:1 shape.
"""
import base64, io, re
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).parent
OUT = ROOT / "landscape_banner_replica"
OUT.mkdir(exist_ok=True)
W_CM, H_CM = 182.88, 91.44
NAME = "ULAB_23rd_Foundation_Day_CSE_Banner_6x3ft_replica"
W, H = 2000, 1000
NAVY, GOLD, PANEL = "#0A2A5B", "#FFC745", "#2C7BC8"
BLUE = "#1260B8"
FONT = "Georgia, 'Times New Roman', serif"


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


# ----------------------------------------------------------------------------- pastel campus picture (soft wash, faded top + left)
src = Image.open(ROOT / "bg2.png").convert("RGB")
sw, sh = src.size
a = np.asarray(src).astype(float)
grey = a.mean(axis=2, keepdims=True)
a = a * 0.80 + grey * 0.20                           # slightly desaturated
a = a * 0.80 + 255 * 0.20                            # soft white wash: the printed picture looks pastel on vinyl
yy, xx = np.mgrid[0:sh, 0:sw]
sm = lambda t: t * t * (3 - 2 * t)
alpha = sm(np.clip(yy / (0.36 * sh), 0, 1)) * sm(np.clip(xx / (0.34 * sw), 0, 1))
rgba = Image.fromarray(a.clip(0, 255).astype("uint8")).convert("RGBA"); rgba.putalpha(Image.fromarray((alpha * 255).astype("uint8")))
bb = io.BytesIO(); rgba.save(bb, "PNG", optimize=True)
PHOTO = uri(bb.getvalue(), "image/png")
S = 0.90
PW_, PH_ = sw * S, sh * S
PX0, PY0 = W - PW_ + 40, 265

U_URI, U_R = ulab_logo()
A_URI, A_R = anniversary()
INK, INK2, TEAL = "#3E5F58", "#56766F", "#2F5F50"

svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W_CM}cm" height="{H_CM}cm" font-family="{FONT}">
  <defs>
    <radialGradient id="cloth" cx=".5" cy=".4" r=".85"><stop offset="0" stop-color="#FBFCFB"/><stop offset=".7" stop-color="#EEF1EE"/><stop offset="1" stop-color="#E1E6E2"/></radialGradient>
    <linearGradient id="fold" x1="0" x2="1">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#9AA59F" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="sw1" x1="0" x2="1" y1="1" y2="0"><stop offset="0" stop-color="#244E43"/><stop offset=".6" stop-color="#3A6C5C"/><stop offset="1" stop-color="#7FA894"/></linearGradient>
    <linearGradient id="sw2" x1="0" x2="1"><stop offset="0" stop-color="#9DBFAF"/><stop offset="1" stop-color="#DDEBE3"/></linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA59F" stop-opacity=".28"/><stop offset=".06" stop-color="#9AA59F" stop-opacity="0"/><stop offset=".94" stop-color="#9AA59F" stop-opacity="0"/><stop offset="1" stop-color="#9AA59F" stop-opacity=".30"/></linearGradient>
  </defs>

  <!-- vinyl: pale cloth with soft vertical folds -->
  <rect width="{W}" height="{H}" fill="url(#cloth)"/>
  <rect x="180" width="360" height="{H}" fill="url(#fold)"/><rect x="760" width="300" height="{H}" fill="url(#fold)"/>
  <rect x="1240" width="380" height="{H}" fill="url(#fold)"/><rect x="1700" width="240" height="{H}" fill="url(#fold)"/>

  <!-- picture, bottom-right -->
  <image href="{PHOTO}" x="{PX0:.1f}" y="{PY0}" width="{PW_:.1f}" height="{PH_:.1f}"/>

  <!-- green swooshes, bottom-left -->
  <path d="M0 800 C260 790 470 880 700 1000 L0 1000 Z" fill="url(#sw2)"/>
  <path d="M0 700 C220 700 400 780 560 880 C640 930 740 975 860 1000 L0 1000 Z" fill="url(#sw1)"/>
  <path d="M0 760 C200 770 380 850 520 940 C560 965 600 985 640 1000 L0 1000 Z" fill="{TEAL}" opacity=".55"/>

  <!-- corner tab, top-left -->
  <polygon points="0,0 70,0 0,70" fill="{TEAL}"/>

  <!-- logos -->
  <image href="{U_URI}" x="170" y="72" width="350" height="{350 / U_R:.1f}"/>
  <image href="{A_URI}" x="1590" y="60" width="310" height="{310 / A_R:.1f}" style="mix-blend-mode:multiply"/>

  <!-- title -->
  <g text-anchor="middle">
    <text id="a" x="975" y="290" font-size="150" font-weight="700" letter-spacing="3" fill="{INK}">ULAB</text>
    <text id="b" x="975" y="415" font-size="112" font-weight="700" fill="{INK2}">Foundation Day</text>
    <rect x="690" y="462" width="570" height="3" fill="{INK2}" opacity=".85"/>
    <text x="975" y="512" font-size="27" font-style="italic" font-weight="400" fill="{INK}">Department of</text>
    <text id="c" x="975" y="560" font-size="40" font-weight="700" fill="{INK}">Computer Science and Engineering</text>
  </g>

  <!-- vinyl edge shading -->
  <rect width="{W}" height="{H}" fill="url(#edge)"/>
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
    print("text extents (x0,x1) of 2000:",
          pg.evaluate("() => [...document.querySelectorAll('text[id]')].map(t => { const r = t.getBBox(); return [t.id, Math.round(r.x), Math.round(r.x + r.width)]; })"))
    pdf_path.write_bytes(pg.pdf(width=f"{W_CM}cm", height=f"{H_CM}cm", print_background=True, prefer_css_page_size=True))
    b.close()

doc = fitz.open(str(pdf_path))
print("pages:", doc.page_count, "size cm:", round(doc[0].rect.width / 72 * 2.54, 1), "x", round(doc[0].rect.height / 72 * 2.54, 1))
doc[0].get_pixmap(matrix=fitz.Matrix(0.4, 0.4)).save(str(OUT / "preview.png"))
(OUT / f"{NAME}.svg").write_text(doc[0].get_svg_image(text_as_path=True), encoding="utf-8")
print("done")
