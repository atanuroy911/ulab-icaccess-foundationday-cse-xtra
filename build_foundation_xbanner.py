"""
X-banner (60 x 160 cm) version of ULAB_Foundation_Day_2026_Poster_Editable.pdf  (CSE department, ULAB 23rd Foundation Day).

    python build_foundation_xbanner.py

Writes to ./foundation_xbanner/ :  .html (editable)  .pdf (exact size, vector)  .svg (text as outlines)  preview.png
Bottom ~10 cm is left free of content because the stand's clip hides it.
"""
import base64, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
OUT = ROOT / "foundation_xbanner"
OUT.mkdir(exist_ok=True)
NAME = "ULAB_Foundation_Day_2026_XBanner_60x160cm"
W, H = 600, 1600                       # viewBox units = millimetres (60 x 160 cm)

BLUE, GOLD, ORANGE, CREAM, NAVY, RED = "#1F7ED0", "#FFC745", "#F5A622", "#FFF8EA", "#0A2A5B", "#E81F49"
TILES = [("#0A6EB8", ["Are You a", "Robot?"], "q"), ("#B8791F", ["Treasure", "Hunt"], "x"),
         ("#0D9367", ["Draw", "Yourself"], "smile"), ("#6B3E9F", ["Hole", "Escape"], "table"),
         ("#E81F49", ["Dart"], "dart"), ("#0A2A5B", ["Project", "Showcase"], "bulb"),
         ("#0A6EB8", ["Wish", "Tree"], "tree"), ("#B8791F", ["Departmental", "Photo Point"], "camera")]


def uri(buf, mime):
    return f"data:{mime};base64,{base64.b64encode(buf).decode()}"


def ulab_logo():
    s = (ROOT / "cue-cards" / "ulab-logo.svg").read_text(encoding="utf-8")
    x0, y0, x1, y1 = 117, 20, 1683, 592
    s = re.sub(r'viewBox="[^"]*"', f'viewBox="{x0} {y0} {x1 - x0} {y1 - y0}"', s, count=1)
    s = re.sub(r'\swidth="[^"]*"', f' width="{x1 - x0}"', s, count=1)
    s = re.sub(r'\sheight="[^"]*"', f' height="{y1 - y0}"', s, count=1)
    return uri(s.encode(), "image/svg+xml"), (x1 - x0) / (y1 - y0)


def anniversary_logo():
    """The 23rd-anniversary mark exists only as a 447 px image in the poster: upscale it smoothly for print."""
    im = Image.open(ROOT / "anniversary_logo_23rd.png").convert("RGB")
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return uri(b.getvalue(), "image/png"), im.width / im.height


U_URI, U_R = ulab_logo()
A_URI, A_R = anniversary_logo()


# ----------------------------------------------------------------------------- icons (drawn in a 100x100 box, glyph colour c)
def glyph(kind, c):
    st = f'fill="none" stroke="{c}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "q":
        return f'<text x="50" y="72" text-anchor="middle" font-size="76" font-weight="700" fill="{c}">?</text>'
    if kind == "x":
        return f'<path d="M25 25 L75 75 M75 25 L25 75" {st} stroke-width="11"/>'
    if kind == "smile":
        return (f'<circle cx="50" cy="50" r="33" {st}/><circle cx="39" cy="42" r="4.5" fill="{c}"/><circle cx="61" cy="42" r="4.5" fill="{c}"/>'
                f'<path d="M34 58 Q50 76 66 58" {st}/>')
    if kind == "table":
        return (f'<rect x="12" y="26" width="76" height="48" rx="8" fill="#16A34A" stroke="#7A4A12" stroke-width="7"/>'
                '<circle cx="34" cy="44" r="6" fill="#0A2A5B"/><circle cx="62" cy="40" r="6" fill="#0A2A5B"/><circle cx="48" cy="60" r="6" fill="#0A2A5B"/>'
                '<circle cx="74" cy="58" r="5" fill="#E81F49"/>')
    if kind == "dart":
        return (f'<circle cx="50" cy="50" r="36" {st}/><circle cx="50" cy="50" r="21" {st}/><circle cx="50" cy="50" r="7" fill="{c}"/>')
    if kind == "bulb":
        return (f'<path d="M50 14 C30 14 22 30 28 46 C32 56 38 60 38 70 L62 70 C62 60 68 56 72 46 C78 30 70 14 50 14 Z" {st}/>'
                f'<path d="M40 82 H60 M44 92 H56" {st}/>')
    if kind == "tree":
        return (f'<circle cx="50" cy="36" r="22" {st}/><circle cx="38" cy="30" r="4" fill="{c}"/><circle cx="58" cy="28" r="4" fill="{c}"/>'
                f'<circle cx="50" cy="44" r="4" fill="{c}"/><path d="M50 58 V88 M50 74 L36 64 M50 78 L64 68" {st}/>')
    if kind == "camera":
        return (f'<path d="M14 34 H32 L38 24 H62 L68 34 H86 V78 H14 Z" {st}/><circle cx="50" cy="55" r="15" {st}/>')
    return ""


def tile(i, x, y, w, h, color, lines, kind):
    cx = x + w / 2
    icon_cy = y + 36
    label = ""
    ys = [y + 86, y + 111] if len(lines) == 2 else [y + 98]
    for t, yy in zip(lines, ys):
        label += f'<text x="{cx}" y="{yy}" text-anchor="middle" font-size="26" font-weight="700" fill="#fff">{t}</text>'
    return f"""
  <g>
    <rect x="{x}" y="{y + 7}" width="{w}" height="{h}" rx="24" fill="{NAVY}" opacity=".35"/>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" fill="{color}" stroke="#fff" stroke-width="3"/>
    <circle cx="{cx}" cy="{icon_cy}" r="28" fill="#fff"/>
    <g transform="translate({cx - 23} {icon_cy - 23}) scale(.46)">{glyph(kind, color)}</g>
    {label}
    <circle cx="{x + w - 20}" cy="{y + 20}" r="17" fill="#fff" stroke="{color}" stroke-width="3"/>
    <text x="{x + w - 20}" y="{y + 26}" text-anchor="middle" font-size="16" font-weight="700" font-family="Arial, Helvetica, sans-serif" fill="{NAVY}">{i + 1:02d}</text>
  </g>"""


# ----------------------------------------------------------------------------- scene
tiles = "".join(tile(i, 30 + (i % 2) * 278, 890 + (i // 2) * 128, 262, 118, c, l, k) for i, (c, l, k) in enumerate(TILES))

CARD_Y, CARD_H = 26, 112
svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W / 10}cm" height="{H / 10}cm"
     font-family="'Comic Sans MS', 'Comic Sans', cursive">
  <defs>
    <pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="13" cy="13" r="2.6" fill="#F0DDB0"/></pattern>
  </defs>

  <!-- background -->
  <rect width="{W}" height="{H}" fill="{BLUE}"/>
  <path d="M0 700 C120 640 230 690 330 722 S520 790 600 690 L600 {H} L0 {H} Z" fill="{GOLD}"/>
  <path d="M0 730 C120 672 230 722 330 754 S520 822 600 722 L600 {H} L0 {H} Z" fill="{ORANGE}"/>
  <path d="M0 782 C130 730 240 776 340 806 S520 862 600 780 L600 {H} L0 {H} Z" fill="{CREAM}"/>
  <path d="M0 782 C130 730 240 776 340 806 S520 862 600 780 L600 {H} L0 {H} Z" fill="url(#dots)"/>

  <!-- confetti -->
  <polygon points="578,168 596,196 560,196" fill="{GOLD}"/>
  <rect x="14" y="196" width="20" height="20" fill="{RED}" transform="rotate(-12 24 206)"/>
  <circle cx="566" cy="252" r="10" fill="{RED}"/><circle cx="24" cy="330" r="9" fill="{GOLD}"/>
  <polygon points="40,560 62,596 18,596" fill="#FF8A5C" transform="rotate(-10 40 580)"/>
  <circle cx="300" cy="150" r="8" fill="#fff"/><circle cx="214" cy="150" r="5" fill="{GOLD}"/>
  <rect x="320" y="150" width="14" height="14" fill="{GOLD}" transform="rotate(20 327 157)"/>

  <!-- logo cards (hard offset shadow, no blur) -->
  <g transform="rotate(-2.5 150 {CARD_Y + CARD_H / 2})">
    <rect x="32" y="{CARD_Y + 8}" width="262" height="{CARD_H}" rx="22" fill="{NAVY}"/>
    <rect x="28" y="{CARD_Y}" width="262" height="{CARD_H}" rx="22" fill="#fff" stroke="{NAVY}" stroke-width="3"/>
    <image href="{U_URI}" x="{28 + 131 - 108}" y="{CARD_Y + (CARD_H - 216 / U_R) / 2}" width="216" height="{216 / U_R:.1f}"/>
  </g>
  <g transform="rotate(2 450 {CARD_Y + CARD_H / 2})">
    <rect x="320" y="{CARD_Y + 8}" width="262" height="{CARD_H}" rx="22" fill="{NAVY}"/>
    <rect x="316" y="{CARD_Y}" width="262" height="{CARD_H}" rx="22" fill="#fff" stroke="{NAVY}" stroke-width="3"/>
    <image href="{A_URI}" x="{316 + 131 - 106}" y="{CARD_Y + (CARD_H - 212 / A_R) / 2}" width="212" height="{212 / A_R:.1f}"/>
  </g>

  <!-- headline -->
  <text x="36" y="196" font-size="23" font-weight="700" letter-spacing="9" fill="{GOLD}">DEPARTMENT OF</text>
  <text id="t1" x="34" y="258" font-size="45" font-weight="700" fill="#fff">COMPUTER SCIENCE</text>
  <text id="t2" x="34" y="312" font-size="45" font-weight="700" fill="#fff">&amp; ENGINEERING (CSE)</text>
  <text x="36" y="366" font-size="23" font-weight="700" letter-spacing="5" fill="#fff">INVITES YOU TO THE ULAB</text>
  <text id="t3" x="30" y="446" font-size="56" font-weight="700" fill="{GOLD}">FOUNDATION</text>
  <text id="t4" x="30" y="510" font-size="56" font-weight="700" fill="{GOLD}">DAY 2026</text>

  <!-- date badge -->
  <g>
    <circle cx="478" cy="430" r="60" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="3"/>
    <circle cx="560" cy="446" r="46" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="3"/>
    <circle cx="524" cy="482" r="78" fill="{NAVY}" opacity=".3" transform="translate(4 8)"/>
    <circle cx="524" cy="482" r="78" fill="{GOLD}"/>
    <text x="524" y="446" text-anchor="middle" font-size="17" font-weight="700" letter-spacing="4" fill="{NAVY}">SUNDAY</text>
    <text x="524" y="512" text-anchor="middle" font-size="82" font-weight="700" fill="{NAVY}">4</text>
    <text x="524" y="542" text-anchor="middle" font-size="17" font-weight="700" letter-spacing="3" fill="{NAVY}">OCT 2026</text>
  </g>

  <!-- venue / time pill -->
  <rect x="24" y="568" width="552" height="84" rx="42" fill="{NAVY}"/>
  <text id="t5" x="52" y="618" font-size="15" font-weight="700" letter-spacing="3" fill="#fff">VENUE:</text>
  <text id="t6" x="136" y="624" font-size="30" font-weight="700" fill="{GOLD}">PD-210</text>
  <text x="270" y="618" font-size="15" font-weight="700" letter-spacing="3" fill="#fff">TIME:</text>
  <text id="t7" x="332" y="624" font-size="24" font-weight="700" fill="{GOLD}">9.00 AM onwards</text>

  <!-- what's waiting -->
  <rect x="30" y="796" width="410" height="64" rx="32" fill="{NAVY}"/>
  <text x="235" y="838" text-anchor="middle" font-size="25" font-weight="700" fill="{GOLD}" id="t8">WHAT'S WAITING FOR YOU</text>
  <circle cx="512" cy="826" r="56" fill="{NAVY}" opacity=".35" transform="translate(3 6)"/>
  <circle cx="512" cy="826" r="56" fill="{RED}" stroke="#fff" stroke-width="3"/>
  <text x="512" y="828" text-anchor="middle" font-size="56" font-weight="700" fill="#fff">8</text>
  <text x="512" y="848" text-anchor="middle" font-size="16" font-weight="700" letter-spacing="1.5" fill="#fff">FUN</text>
  <text x="512" y="866" text-anchor="middle" font-size="16" font-weight="700" letter-spacing="1.5" fill="#fff">ZONES</text>

  <!-- tiles -->
  {tiles}

  <!-- closing line (ends at 148 cm: the clip hides the bottom ~10 cm) -->
  <text x="300" y="1438" text-anchor="middle" font-size="27" font-weight="700" fill="{NAVY}">Bring your friends and batchmates.</text>
  <text x="300" y="1472" text-anchor="middle" font-size="27" font-weight="700" fill="{NAVY}" id="t9">Come play, learn and celebrate!</text>
</svg>"""

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{NAME}</title>
<style>@page {{ size: 60cm 160cm; margin: 0 }} html,body {{ margin:0; padding:0; overflow:hidden; background:#fff }} svg {{ display:block }}</style></head>
<body>{svg}</body></html>"""
(OUT / f"{NAME}.html").write_text(html, encoding="utf-8")

from playwright.sync_api import sync_playwright
import fitz

pdf_path = OUT / f"{NAME}.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 3200})
    pg.goto((OUT / f"{NAME}.html").as_uri()); pg.wait_for_timeout(500)
    boxes = pg.evaluate("""() => [...document.querySelectorAll('text[id]')].map(t => { const r = t.getBBox(); return [t.id, Math.round(r.x), Math.round(r.x + r.width)]; })""")
    print("text extents (x0,x1) in mm of 600:", boxes)
    pdf_path.write_bytes(pg.pdf(width="60cm", height="160cm", print_background=True, prefer_css_page_size=True))
    b.close()

doc = fitz.open(str(pdf_path))
print("pages:", doc.page_count, "size cm:", round(doc[0].rect.width / 72 * 2.54, 1), "x", round(doc[0].rect.height / 72 * 2.54, 1))
doc[0].get_pixmap(matrix=fitz.Matrix(0.3, 0.3)).save(str(OUT / "preview.png"))
(OUT / f"{NAME}.svg").write_text(doc[0].get_svg_image(text_as_path=True), encoding="utf-8")
print("done")
