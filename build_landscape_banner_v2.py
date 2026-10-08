"""
Landscape banner (6 ft x 3 ft = 182.88 x 91.44 cm, 2:1) for the ULAB 23rd Foundation Day, CSE.
Version 2: full-bleed campus photo under a navy glow, ULAB logo top-left, 23rd Anniversary mark top-right, title centred, gold ribbon + brand colour bar.

    python build_landscape_banner.py      ->  ./landscape_banner_v2/  (.html, .pdf, .svg, preview.png)
The campus photo (bg2.png) sits on the right at full height; the sky / lawn on its left are a gradient built from the photo's own
left-edge colours, so the join is invisible. Change W_CM / H_CM for another size with the same 2:1 shape.
"""
import base64, io, re
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).parent
OUT = ROOT / "landscape_banner_v2"
OUT.mkdir(exist_ok=True)
W_CM, H_CM = 182.88, 91.44
NAME = "ULAB_23rd_Foundation_Day_CSE_Banner_6x3ft_v2"
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


# ----------------------------------------------------------------------------- full-bleed photo (cover crop of the square bg2.png)
src = Image.open(ROOT / "bg2.png").convert("RGB")
sw, sh = src.size
SCALE = W / sw                                        # photo is scaled to the banner width...
OFFSET = -(0.24 * sh) * SCALE                         # ...and the 2:1 band starting 24% down (sky + building + trees) is kept
b = io.BytesIO(); src.save(b, "JPEG", quality=93, optimize=True)
PHOTO = uri(b.getvalue(), "image/jpeg")
U_URI, U_R = ulab_logo()
A_URI, A_R = anniversary()

CARD = dict(x=60, y=50)
UL_W = 380
UL_CARD_W, UL_CARD_H = UL_W + 70, UL_W / U_R + 64
AN_W = 340
AN_H = AN_W / A_R
AN_CARD_W, AN_CARD_H = AN_W + 56, AN_H + 56
BRAND = [("#0A6EB8", "Discover"), ("#B8791F", "Develop"), ("#0D9367", "Demonstrate"), ("#6B3E9F", "Distinguish"), ("#E81F49", "Belong")]
bar = "".join(f'<rect x="{i * W / 5}" y="936" width="{W / 5}" height="64" fill="{c}"/><text x="{i * W / 5 + W / 10}" y="979" text-anchor="middle" font-size="30" font-weight="700" letter-spacing="3" fill="#fff">{t.upper()}</text>'
              for i, (c, t) in enumerate(BRAND))


def spark(x, y, r, c=GOLD, o=1):
    k = r * 0.2
    return f'<polygon points="{x},{y - r} {x + k},{y - k} {x + r},{y} {x + k},{y + k} {x},{y + r} {x - k},{y + k} {x - r},{y} {x - k},{y - k}" fill="{c}" opacity="{o}"/>'


sparks = (spark(600, 110, 24) + spark(1580, 330, 20) + spark(300, 560, 16, "#fff", .9) + spark(1720, 600, 28) + spark(640, 190, 14, "#fff", .8)
          + spark(1400, 215, 18, "#fff", .9) + spark(250, 760, 22) + spark(1790, 800, 16, "#fff", .9))

svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W_CM}cm" height="{H_CM}cm" font-family="{FONT}">
  <defs>
    <radialGradient id="glow" cx=".5" cy=".5" r=".75">
      <stop offset="0" stop-color="#06224F" stop-opacity=".86"/><stop offset=".55" stop-color="#0A3A7A" stop-opacity=".6"/><stop offset="1" stop-color="#0B4C9A" stop-opacity=".18"/>
    </radialGradient>
    <linearGradient id="rib" x1="0" x2="1"><stop offset="0" stop-color="#E58E00"/><stop offset=".5" stop-color="#FFC745"/><stop offset="1" stop-color="#E58E00"/></linearGradient>
    <clipPath id="ancl"><rect x="{W - 60 - AN_CARD_W + 28}" y="{CARD['y'] + 28}" width="{AN_W}" height="{AN_H:.1f}" rx="12"/></clipPath>
  </defs>

  <!-- photo, full bleed -->
  <image href="{PHOTO}" x="0" y="{OFFSET:.1f}" width="{W}" height="{sh * SCALE:.1f}"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>

  <!-- giant outlined 23 behind the title -->
  <text x="{W / 2}" y="830" text-anchor="middle" font-size="880" font-weight="900" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="7">23</text>

  <!-- gold ribbon sweeping under the title -->
  <path d="M-10 770 C260 700 520 830 1000 800 S1740 700 2010 780 L2010 872 C1740 800 1300 906 1000 890 S260 800 -10 862 Z" fill="url(#rib)"/>
  <path d="M-10 770 C260 700 520 830 1000 800 S1740 700 2010 780" fill="none" stroke="#FFE9A8" stroke-width="5" opacity=".8"/>

  {sparks}

  <!-- logos: ULAB top-left, 23rd anniversary top-right (white cards, hard offset shadow) -->
  <rect x="{CARD['x'] + 10}" y="{CARD['y'] + 12}" width="{UL_CARD_W}" height="{UL_CARD_H:.1f}" rx="30" fill="{NAVY}" opacity=".55"/>
  <rect x="{CARD['x']}" y="{CARD['y']}" width="{UL_CARD_W}" height="{UL_CARD_H:.1f}" rx="30" fill="#fff"/>
  <image href="{U_URI}" x="{CARD['x'] + 35}" y="{CARD['y'] + 32}" width="{UL_W}" height="{UL_W / U_R:.1f}"/>

  <rect x="{W - 60 - AN_CARD_W + 10}" y="{CARD['y'] + 12}" width="{AN_CARD_W}" height="{AN_CARD_H:.1f}" rx="30" fill="{NAVY}" opacity=".55"/>
  <rect x="{W - 60 - AN_CARD_W}" y="{CARD['y']}" width="{AN_CARD_W}" height="{AN_CARD_H:.1f}" rx="30" fill="#fff"/>
  <image href="{A_URI}" x="{W - 60 - AN_CARD_W + 28}" y="{CARD['y'] + 28}" width="{AN_W}" height="{AN_H:.1f}" clip-path="url(#ancl)"/>

  <!-- title, centred -->
  <g text-anchor="middle">
    <text id="a" x="{W / 2}" y="400" font-size="150" font-weight="800" fill="#fff" stroke="{NAVY}" stroke-width="10" paint-order="stroke" stroke-linejoin="round">23<tspan font-size="80" dy="-66">rd</tspan><tspan dy="66"> ULAB</tspan></text>
    <text id="b" x="{W / 2}" y="540" font-size="124" font-weight="900" fill="{GOLD}" stroke="{NAVY}" stroke-width="10" paint-order="stroke" stroke-linejoin="round">FOUNDATION DAY</text>
    <rect x="{W / 2 - 130}" y="580" width="260" height="8" rx="4" fill="#fff"/>
    <text id="c" x="{W / 2}" y="660" font-size="54" font-weight="600" fill="#fff" stroke="{NAVY}" stroke-width="8" paint-order="stroke" stroke-linejoin="round">Department of Computer Science and Engineering</text>
    <text id="d" x="{W / 2}" y="728" font-size="40" font-weight="800" letter-spacing="3" fill="{GOLD}" stroke="{NAVY}" stroke-width="7" paint-order="stroke" stroke-linejoin="round">SUNDAY · 4 OCTOBER 2026</text>
  </g>

  <!-- brand colour bar (the five colours of the 23rd anniversary mark) -->
  {bar}
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
