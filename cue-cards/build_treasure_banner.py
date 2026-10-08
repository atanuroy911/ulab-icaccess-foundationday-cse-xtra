"""
Build the "Treasure Hunt" X-banner for ULAB's 23rd Foundation Day booth.

    python build_treasure_banner.py

Writes to ./treasure_banner/ :
    ULAB_Treasure_Hunt_XBanner_60x160cm.html   (editable source; needs internet only for the Google fonts)
    ULAB_Treasure_Hunt_XBanner_60x160cm.pdf    (print file, exact size, fonts embedded, all art is vector)
    ULAB_Treasure_Hunt_XBanner_60x160cm.svg    (print file, text converted to outlines)
    preview.png

Concept: an old treasure map. A dotted trail winds past three X-marked clue stops to an open chest of gold.
Everything is hand-drawn vector (no photos), so it prints crisp at any size.
"""
import base64
import re
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "treasure_banner"
OUT.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------- settings
W_CM, H_CM = 60, 160
NAME = f"ULAB_Treasure_Hunt_XBanner_{W_CM}x{H_CM}cm"
ORGANIZER = "Department of CSE"
INK, RED, GOLD, NAVY, BLUE = "#4A2C12", "#C8201A", "#FDC300", "#04203F", "#0069B4"
PARCH, PARCH_D = "#F6E6BC", "#D9B070"

CTA_TOP, CTA_H = 127.0, 14.0
CREDIT_TOP, CREDIT_H = 143.4, 5.8      # ends at 149.2 cm, above the ~10 cm the stand's clip hides


def data_uri(buf, mime):
    return f"data:{mime};base64,{base64.b64encode(buf).decode()}"


def logo_svg():
    s = (HERE / "ulab-logo.svg").read_text(encoding="utf-8")
    x0, y0, x1, y1 = 117, 20, 1683, 592        # tight crop of the artwork
    s = re.sub(r'viewBox="[^"]*"', f'viewBox="{x0} {y0} {x1 - x0} {y1 - y0}"', s, count=1)
    s = re.sub(r'\swidth="[^"]*"', f' width="{x1 - x0}"', s, count=1)
    s = re.sub(r'\sheight="[^"]*"', f' height="{y1 - y0}"', s, count=1)
    return data_uri(s.encode("utf-8"), "image/svg+xml"), (x1 - x0) / (y1 - y0)


logo_uri, logo_ratio = logo_svg()
LOGO_H = 10.6


# ----------------------------------------------------------------------------- vector art (units = mm; scene is 600 x 540)
def star4(cx, cy, r, fill="#fff", op=1):
    k = r * 0.22
    pts = f"{cx},{cy - r} {cx + k},{cy - k} {cx + r},{cy} {cx + k},{cy + k} {cx},{cy + r} {cx - k},{cy + k} {cx - r},{cy} {cx - k},{cy - k}"
    return f'<polygon points="{pts}" fill="{fill}" opacity="{op}"/>'


def coin(cx, cy, r=15):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#goldg)" stroke="#A87000" stroke-width="3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.62:.1f}" fill="none" stroke="#B8860B" stroke-width="2.2"/>'
            f'<path d="M{cx - r * .35:.1f} {cy - r * .45:.1f} Q{cx} {cy - r * .75:.1f} {cx + r * .4:.1f} {cy - r * .35:.1f}" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity=".7"/>')


def x_mark(cx, cy, s=17):
    return (f'<g stroke="{RED}" stroke-width="11" stroke-linecap="round">'
            f'<path d="M{cx - s} {cy - s} L{cx + s} {cy + s}"/><path d="M{cx + s} {cy - s} L{cx - s} {cy + s}"/></g>')


def badge(cx, cy, n):
    return (f'<circle cx="{cx}" cy="{cy}" r="21" fill="{GOLD}" stroke="{INK}" stroke-width="5"/>'
            f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" font-family="Rye" font-size="38" fill="{INK}">{n}</text>')


def palm(x, y, s=1.0):
    leaves = "".join(
        f'<path d="M0 0 C 28 -30, 64 -28, 86 -2 C 56 -14, 28 -14, 0 0 Z" fill="{c}" stroke="#14452B" stroke-width="2.5" '
        f'transform="rotate({a})"/>'
        for a, c in ((-158, "#2E8B57"), (-118, "#237A49"), (-78, "#2E8B57"), (-30, "#237A49"), (14, "#2E8B57"), (58, "#237A49")))
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<ellipse cx="0" cy="2" rx="74" ry="16" fill="#E4C27B" stroke="#B88A44" stroke-width="3"/>'
            f'<ellipse cx="-4" cy="-3" rx="58" ry="9" fill="#F0D79A"/>'
            f'<path d="M-4 -4 C 4 -34, 2 -66, 14 -98" fill="none" stroke="#6B3E16" stroke-width="10" stroke-linecap="round"/>'
            f'<g transform="translate(14 -98)">{leaves}<circle cx="-5" cy="6" r="7" fill="#5B3414"/><circle cx="7" cy="8" r="7" fill="#5B3414"/></g></g>')


def compass(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<circle r="44" fill="#F9EFCF" stroke="{INK}" stroke-width="4"/><circle r="36" fill="none" stroke="{INK}" stroke-width="1.8" stroke-dasharray="3 5"/>'
            f'<polygon points="0,-60 9,-9 60,0 9,9 0,60 -9,9 -60,0 -9,-9" fill="{INK}"/>'
            f'<polygon points="0,-60 9,-9 -9,-9" fill="{RED}"/>'
            f'<g transform="rotate(45) scale(.62)"><polygon points="0,-60 9,-9 60,0 9,9 0,60 -9,9 -60,0 -9,-9" fill="{GOLD}" stroke="{INK}" stroke-width="3"/></g>'
            f'<circle r="7" fill="{GOLD}" stroke="{INK}" stroke-width="3"/>'
            f'<text y="-68" text-anchor="middle" font-family="Rye" font-size="26" fill="{INK}">N</text></g>')


def magnifier(x, y):
    return (f'<g transform="translate({x} {y}) rotate(-12)">'
            f'<path d="M20 22 L58 62" stroke="#6B3E16" stroke-width="13" stroke-linecap="round"/>'
            f'<circle r="29" fill="#BFE6FF" fill-opacity=".55" stroke="{INK}" stroke-width="8"/>'
            f'<path d="M-14 -8 Q-8 -20 6 -20" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".9"/></g>')


def key(x, y):
    return (f'<g transform="translate({x} {y}) rotate(-18)" stroke="#8A6200" stroke-width="3" fill="{GOLD}">'
            f'<circle r="15" /><circle r="6" fill="{PARCH}" stroke="#8A6200"/>'
            f'<rect x="12" y="-4.5" width="62" height="9" rx="3"/><rect x="52" y="4" width="8" height="15" rx="2"/><rect x="65" y="4" width="8" height="11" rx="2"/></g>')


def chest(x, y):
    coins_top = "".join(coin(cx, cy, r) for cx, cy, r in
                        ((-52, -80, 15), (-18, -92, 16), (20, -90, 15), (54, -78, 15), (-34, -62, 14), (0, -70, 16), (34, -60, 14), (70, -56, 13), (-70, -54, 13)))
    spill = "".join(coin(cx, cy, r) for cx, cy, r in ((-122, 30, 15), (-100, 44, 14), (-76, 48, 13), (118, 36, 15), (140, 46, 13), (98, 52, 14)))
    rivets = "".join(f'<circle cx="{rx}" cy="{ry}" r="3.6" fill="#B9B1A5"/>' for rx in (-62, 62) for ry in (-14, 0, 14, 28))
    return (f'<g transform="translate({x} {y})">'
            f'<circle r="190" fill="url(#glow)"/>'
            # open lid (behind)
            f'<path d="M-90 -44 L-80 -124 Q0 -156 80 -124 L90 -44 Z" fill="#A8642A" stroke="#5B3414" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M-70 -50 L-64 -108 Q0 -128 64 -108 L70 -50 Z" fill="#6B3E16"/>'
            f'<path d="M-86 -92 Q0 -118 86 -92" fill="none" stroke="#3E3A36" stroke-width="9"/>'
            # gold pile
            f'<path d="M-94 -40 Q-62 -96 0 -102 Q62 -96 94 -40 Z" fill="url(#goldg)" stroke="#A87000" stroke-width="4"/>{coins_top}'
            # body
            f'<rect x="-100" y="-42" width="200" height="86" rx="9" fill="#B26A2B" stroke="#5B3414" stroke-width="6"/>'
            f'<path d="M-50 -42 V44 M0 -42 V44 M50 -42 V44" stroke="#7C4519" stroke-width="3"/>'
            f'<rect x="-100" y="-42" width="200" height="16" rx="6" fill="#3E3A36"/>'
            f'<rect x="-76" y="-42" width="18" height="86" fill="#3E3A36"/><rect x="58" y="-42" width="18" height="86" fill="#3E3A36"/>{rivets}'
            f'<rect x="-17" y="-30" width="34" height="40" rx="6" fill="{GOLD}" stroke="#A87000" stroke-width="4"/>'
            f'<circle cx="0" cy="-12" r="5.5" fill="{INK}"/><rect x="-2.6" y="-10" width="5.2" height="13" rx="2" fill="{INK}"/>'
            f'{spill}</g>')


TRAIL = "M 70 55 C 200 5, 350 15, 430 95 C 500 165, 480 235, 365 250 C 240 262, 105 258, 118 345 C 126 410, 200 410, 232 428"

scene = f"""<svg class="scene" viewBox="0 0 600 540" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="goldg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFE063"/><stop offset=".55" stop-color="{GOLD}"/><stop offset="1" stop-color="#E0A200"/></linearGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="#FFE98A" stop-opacity=".95"/><stop offset=".55" stop-color="#FDC300" stop-opacity=".28"/><stop offset="1" stop-color="#FDC300" stop-opacity="0"/></radialGradient>
  </defs>
  {palm(104, 512, .62)}{palm(512, 505, .6)}
  <path d="{TRAIL}" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round" stroke-dasharray="0.1 19"/>
  {x_mark(430, 95)}{x_mark(365, 250)}{x_mark(118, 345)}
  {badge(404, 128, 1)}{badge(338, 285, 2)}{badge(150, 318, 3)}
  <g><path d="M70 55 V4" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><path d="M72 6 L122 22 L72 40 Z" fill="{RED}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>
     <circle cx="70" cy="55" r="11" fill="{GOLD}" stroke="{INK}" stroke-width="5"/>
     <text x="90" y="84" font-family="Rye" font-size="30" fill="{INK}">START</text></g>
  {compass(500, 60, .95)}
  {magnifier(466, 322)}
  {key(58, 176)}
  {chest(335, 448)}
  {star4(210, 380, 17, "#fff", .95)}{star4(478, 412, 14, "#fff", .9)}{star4(150, 130, 12, GOLD, .9)}{star4(556, 214, 12, GOLD, .9)}
  {star4(408, 380, 20, "#fff", .95)}{star4(292, 348, 14, "#fff", .85)}{star4(70, 262, 11, GOLD, .85)}
</svg>"""

# ----------------------------------------------------------------------------- page
html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Treasure Hunt · ULAB 23rd Foundation Day · X-banner</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800;900&family=Rye&display=swap" rel="stylesheet">
<style>
  @page {{ size: {W_CM}cm {H_CM}cm; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ width: {W_CM}cm; height: {H_CM}cm; overflow: hidden; }}
  body {{ position: relative; overflow: hidden; font-family: Outfit, sans-serif; color: {INK};
          -webkit-print-color-adjust: exact; print-color-adjust: exact;
          background: radial-gradient(95% 62% at 50% 38%, {PARCH} 0%, #EBD29A 55%, {PARCH_D} 100%); }}
  .abs {{ position: absolute; }}

  /* faint map grid + burnt-paper edges */
  .grid {{ inset: 0; opacity: .5;
           background-image: linear-gradient(rgba(107,62,22,.10) .08cm, transparent .08cm), linear-gradient(90deg, rgba(107,62,22,.10) .08cm, transparent .08cm);
           background-size: 6cm 6cm; }}
  .burn {{ inset: 0; background: radial-gradient(120% 88% at 50% 45%, rgba(120,70,20,0) 55%, rgba(120,70,20,.42) 100%); }}
  .frame {{ left: 2.4cm; right: 2.4cm; top: 2.4cm; bottom: 8.6cm; border: .3cm solid {INK}; border-radius: 1.4cm; }}
  .frame2 {{ left: 3.4cm; right: 3.4cm; top: 3.4cm; bottom: 9.6cm; border: .1cm solid {INK}; border-radius: .8cm; opacity: .7; }}

  /* ---- header ---- */
  .logo-panel {{ left: 8cm; right: 8cm; top: 6.2cm; height: 15cm; background: #fff; border: .3cm solid {INK}; border-radius: 2.6cm;
                 display: grid; place-items: center; box-shadow: 0 .45cm 0 rgba(74,44,18,.35); }}
  .logo-panel img {{ height: {LOGO_H}cm; width: {LOGO_H * logo_ratio:.2f}cm; display: block; }}
  .rib-shadow, .rib {{ left: 4.5cm; right: 4.5cm; height: 7cm; clip-path: polygon(0 0, 100% 0, 96.5% 50%, 100% 100%, 0 100%, 3.5% 50%); }}
  .rib-shadow {{ top: 24.9cm; background: #B98A00; }}
  .rib {{ top: 24.1cm; background: {GOLD}; display: flex; align-items: center; justify-content: center; gap: 1.2cm;
          font-family: Rye, serif; color: {INK}; }}
  .rib .n {{ font-size: 4.6cm; line-height: 1; }}
  .rib .n sup {{ font-size: 2.1cm; vertical-align: top; position: relative; top: .35cm; }}
  .rib .t {{ font-family: Outfit, sans-serif; font-weight: 900; font-size: 2.3cm; line-height: 1.04; text-transform: uppercase; text-align: left; }}

  /* ---- headline ---- */
  .headline {{ left: 0; right: 0; top: 33.6cm; text-align: center; font-family: Rye, serif; text-transform: uppercase; line-height: .94; }}
  .headline .l1 {{ display: block; font-size: 8.9cm; color: {INK}; text-shadow: 0 .35cm 0 rgba(255,255,255,.55); }}
  .headline .l2 {{ display: block; font-size: 15.4cm; color: {RED}; margin-top: .2cm; text-shadow: .35cm .4cm 0 {INK}; }}
  .tag {{ left: 4cm; right: 4cm; top: 61.2cm; text-align: center; font-weight: 800; font-size: 3.2cm; line-height: 1.1; }}
  .tag b {{ color: {RED}; font-weight: 900; }}

  /* ---- map scene ---- */
  .scene {{ position: absolute; left: 0; top: 67cm; width: 60cm; height: 54cm; }}

  /* ---- call to action + credit ---- */
  .cta {{ left: 4cm; right: 4cm; top: {CTA_TOP}cm; height: {CTA_H}cm; background: {NAVY}; border: .3cm solid {INK}; border-radius: 3.2cm;
          text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;
          box-shadow: 0 .5cm 0 rgba(74,44,18,.45); }}
  .cta .big {{ font-family: Rye, serif; font-size: 4.25cm; line-height: 1.12; white-space: nowrap; text-transform: uppercase; color: {GOLD}; }}
  .cta .big span {{ color: #fff; }}
  .credit {{ left: 11cm; right: 11cm; top: {CREDIT_TOP}cm; height: {CREDIT_H}cm; border-radius: 4cm; background: #FFF3D1;
             border: .3cm solid {INK}; display: flex; align-items: center; justify-content: center;
             font-weight: 900; font-size: 3.2cm; color: {NAVY}; white-space: nowrap; }}
</style></head>
<body>
  <div class="abs grid"></div>
  <div class="abs burn"></div>
  <div class="abs frame"></div><div class="abs frame2"></div>

  <div class="abs logo-panel"><img src="{logo_uri}" alt="University of Liberal Arts Bangladesh"></div>
  <div class="abs rib-shadow"></div>
  <div class="abs rib"><div class="n">23<sup>rd</sup></div><div class="t">Foundation<br>Day</div></div>

  <div class="abs headline"><span class="l1">Treasure</span><span class="l2">Hunt</span></div>
  <div class="abs tag">Follow the clues. Find the <b>treasure!</b></div>

  {scene}

  <div class="abs cta"><div class="big">Start the hunt<br><span>at our booth!</span></div></div>
  <div class="abs credit">{ORGANIZER}</div>
</body></html>"""

html_path = OUT / f"{NAME}.html"
html_path.write_text(html, encoding="utf-8")


# ----------------------------------------------------------------------------- render
def render():
    from playwright.sync_api import sync_playwright
    pdf_path = OUT / f"{NAME}.pdf"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        data = pg.pdf(width=f"{W_CM}cm", height=f"{H_CM}cm", print_background=True, prefer_css_page_size=True,
                      margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        try:
            pdf_path.write_bytes(data)
        except PermissionError:
            pdf_path = pdf_path.with_name(pdf_path.stem + "_new.pdf"); pdf_path.write_bytes(data)
            print("NOTE: PDF is open elsewhere; saved as", pdf_path.name)
        b.close()
    return pdf_path


pdf_path = render()

import fitz  # PyMuPDF

doc = fitz.open(str(pdf_path))
page = doc[0]
page.get_pixmap(matrix=fitz.Matrix(0.35, 0.35)).save(str(OUT / "preview.png"))
svg_path = OUT / f"{NAME}.svg"
svg_path.write_text(page.get_svg_image(text_as_path=True), encoding="utf-8")
print(f"pages: {len(doc)}  page size: {page.rect.width / 72 * 2.54:.1f} x {page.rect.height / 72 * 2.54:.1f} cm")
print("wrote:", html_path.name, pdf_path.name, svg_path.name)
