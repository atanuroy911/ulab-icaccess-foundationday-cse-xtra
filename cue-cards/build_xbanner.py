"""
Build the "AI or Human?" X-banner for ULAB's 23rd Foundation Day booth.

    python build_xbanner.py

Writes to ./xbanner/ :
    ULAB_AI_or_Human_XBanner_60x160cm.html   (editable source)
    ULAB_AI_or_Human_XBanner_60x160cm.pdf    (print file, exact size, fonts embedded, logo + clipart vector)
    ULAB_AI_or_Human_XBanner_60x160cm.svg    (print file, text converted to outlines)
    preview.png                              (small preview rendered from the PDF)

The two slanted decks copy the real cue cards (header strip, image or italic text, Human | AI footer).
Change W_CM / H_CM for another stand size, CARDS_* to change which photos/texts appear.
"""
import base64
import io
import re
from pathlib import Path

from PIL import Image, ImageFilter

import banner_art as art

HERE = Path(__file__).parent
OUT = HERE / "xbanner"
OUT.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------- settings
W_CM, H_CM = 60, 160                # standard X-banner stand size
NAME = f"ULAB_AI_or_Human_XBanner_{W_CM}x{H_CM}cm"
BLUE, YELLOW, NAVY = "#0069B4", "#FDC300", "#04203F"
ORGANIZER = "Department of CSE"

# vertical plan (cm). The stand's clip hides ~10 cm at the bottom and ~3 cm at the top.
CTA_TOP, CTA_H = 127.0, 14.0
CREDIT_TOP, CREDIT_H = 143.4, 5.8   # ends at 149.2 cm

CARD = 25.5                         # card size on the banner (cm); the real card is 8 cm
# photos with NO people in them (pair file, topic label, card id) from the game's image set: front card last
PHOTO_DECK = [("pair7_right", "Heart in Beach Sand", "7B"), ("pair7_left", "Heart in Beach Sand", "7A"), ("pair10_right", "Disco Ball", "10B")]
# text cards (topic, text, id): front card last
TEXT_DECK = [
    ("Winter", "First day I could see my breath in the air. Finally can wear that one jacket I spent way too much money on.", "20A"),
    ("Cooking Tip", "Okay so the SECRET is don't stir the dal for the first 5 minutes. Let it sit. THAT'S where all the flavour lives.", "6A"),
    ("Morning Routine", "Hit snooze three times, drank cold coffee from yesterday, and sprinted to the bus stop. Peak productivity, I tell you.", "14A"),
]


# ----------------------------------------------------------------------------- assets
def data_uri(buf, mime):
    return f"data:{mime};base64,{base64.b64encode(buf).decode()}"


def photo(path, w_cm, h_cm):
    """Crop to the frame's aspect and upscale 1.8x so the print is not blocky when viewed up close."""
    im = Image.open(path).convert("RGB")
    ratio = w_cm / h_cm
    cw, ch = im.size
    if cw / ch > ratio:
        nw = round(ch * ratio); im = im.crop(((cw - nw) // 2, 0, (cw - nw) // 2 + nw, ch))
    else:
        nh = round(cw / ratio); top = int((ch - nh) * 0.4); im = im.crop((0, top, cw, top + nh))
    im = im.resize((round(im.width * 1.8), round(im.height * 1.8)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=93)
    return data_uri(buf.getvalue(), "image/jpeg")


def logo_svg(x0=117, x1=1683):
    """ULAB logo cropped tight to the artwork (the source file has a lot of empty canvas).
    x1=630 gives the crest only (used in the small card headers)."""
    s = (HERE / "ulab-logo.svg").read_text(encoding="utf-8")
    y0, y1 = 20, 592
    s = re.sub(r'viewBox="[^"]*"', f'viewBox="{x0} {y0} {x1 - x0} {y1 - y0}"', s, count=1)
    s = re.sub(r'\swidth="[^"]*"', f' width="{x1 - x0}"', s, count=1)
    s = re.sub(r'\sheight="[^"]*"', f' height="{y1 - y0}"', s, count=1)
    return data_uri(s.encode("utf-8"), "image/svg+xml"), (x1 - x0) / (y1 - y0)


logo_uri, logo_ratio = logo_svg()
crest_uri, crest_ratio = logo_svg(117, 630)
LOGO_H = 11.4
human_uri = data_uri(art.human_brain(600).encode("utf-8"), "image/svg+xml")
ai_uri = data_uri(art.ai_brain(600).encode("utf-8"), "image/svg+xml")

# ----------------------------------------------------------------------------- cue cards
HEAD_H, FOOT_H = 4.4, 4.6
BODY_W, BODY_H = CARD - 0.18, CARD - HEAD_H - FOOT_H - 0.18


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card_shell(badge, body_html, back=False):
    return f"""
    <div class="cc-head">
      <div class="cc-left"><img class="cc-crest" src="{crest_uri}" alt=""><div>
        <div class="cc-event">ULAB · 23rd Foundation Day</div><div class="cc-game">AI or Human?</div></div></div>
      <div class="cc-num">{badge}</div>
    </div>
    {body_html}
    <div class="cc-foot{' back' if back else ''}">
      <div class="cc-btn"><div class="cc-ico">{art.PERSON_ICON}</div><div class="cc-lbl">Human</div><div class="cc-sub">Real</div></div>
      <div class="cc-btn"><div class="cc-ico">{art.ROBOT_ICON}</div><div class="cc-lbl">AI</div><div class="cc-sub">Generated</div></div>
    </div>"""


def photo_card(item, back=False):
    f, topic, cid = item
    uri = photo(HERE / "images" / f"{f}.webp", BODY_W, BODY_H)
    body = f'<div class="cc-img"><img src="{uri}" alt=""><div class="cc-topic">{esc(topic)}</div></div>'
    return card_shell(f"PHOTO #{cid}", body, back)


def text_card(item, back=False):
    topic, text, cid = item
    body = f'<div class="cc-txt"><div class="cc-ttopic">{esc(topic)}</div><p>“{esc(text)}”</p></div>'
    return card_shell(f"TEXT #{cid}", body, back)


def deck(cx, cy, specs, make):
    """specs: list of (dx, dy, rotation_deg, item), back -> front. (cx, cy) = centre of the deck, in cm."""
    out = []
    for i, (dx, dy, rot, item) in enumerate(specs):
        out.append(f'<div class="abs card" style="left:{cx + dx - CARD / 2:.2f}cm; top:{cy + dy - CARD / 2:.2f}cm; '
                   f'transform: rotate({rot}deg); z-index:{3 + i};">{make(item, back=(i < len(specs) - 1))}</div>')
    return "".join(out)


# two decks, slanted opposite ways, staggered diagonally; each shows 3 cards fanned
LEFT_CX, LEFT_CY = 18.8, 80.4
RIGHT_CX, RIGHT_CY = 41.2, 106.6
left_deck = deck(LEFT_CX, LEFT_CY, [(-1.9, -.6, -13, PHOTO_DECK[0]), (-1.0, -.3, -8.5, PHOTO_DECK[1]), (0, 0, -4, PHOTO_DECK[2])], photo_card)
right_deck = deck(RIGHT_CX, RIGHT_CY, [(1.9, -.6, 13, TEXT_DECK[0]), (1.0, -.3, 8.5, TEXT_DECK[1]), (0, 0, 4, TEXT_DECK[2])], text_card)

# brains fill the two free corners and label themselves
BRAIN_W = 21.5
BRAIN_H = BRAIN_W * 172 / 212

# ----------------------------------------------------------------------------- page
html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>AI or Human? · ULAB 23rd Foundation Day · X-banner</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&family=Outfit:wght@600;700;800;900&display=swap" rel="stylesheet">
<style>
  @page {{ size: {W_CM}cm {H_CM}cm; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ width: {W_CM}cm; height: {H_CM}cm; overflow: hidden; }}
  body {{ position: relative; overflow: hidden; font-family: Inter, sans-serif; color: #fff;
          -webkit-print-color-adjust: exact; print-color-adjust: exact;
          background: radial-gradient(120% 55% at 50% 30%, #0B5CA3 0%, {BLUE} 0%, #0A4C86 38%, {NAVY} 100%); }}
  .abs {{ position: absolute; }}

  .dots {{ inset: 0; opacity: .10;
           background-image: radial-gradient(#fff 22%, transparent 24%); background-size: 2.2cm 2.2cm; }}
  .glow {{ left: 0; right: 0; top: 24cm; height: 46cm;
           background: radial-gradient(closest-side, rgba(253,195,0,.33), rgba(253,195,0,0)); }}

  /* ---- header ---- */
  .logo-panel {{ left: 8cm; right: 8cm; top: 6cm; height: 16cm; background: #fff; border-radius: 3cm;
                 display: grid; place-items: center; box-shadow: 0 .5cm 1.4cm rgba(0,0,0,.35); }}
  .logo-panel img {{ height: {LOGO_H}cm; width: {LOGO_H * logo_ratio:.2f}cm; display: block; }}
  .ribbon {{ left: 4cm; right: 4cm; top: 24.6cm; height: 7cm; background: {YELLOW}; color: {NAVY};
             border-radius: 4cm; display: flex; align-items: center; justify-content: center; gap: 1.2cm;
             font-family: Outfit, sans-serif; font-weight: 800; letter-spacing: .02em;
             box-shadow: 0 .4cm 1.2cm rgba(0,0,0,.3); }}
  .ribbon .n {{ font-size: 4.7cm; line-height: 1; }}
  .ribbon .n sup {{ font-size: 2.2cm; vertical-align: top; position: relative; top: .2cm; }}
  .ribbon .t {{ font-size: 2.3cm; line-height: 1.04; text-transform: uppercase; text-align: left; font-weight: 800; }}

  /* ---- headline ---- */
  .headline {{ left: 0; right: 0; top: 34.2cm; text-align: center; font-family: Outfit, sans-serif;
               font-weight: 900; line-height: .92; text-transform: uppercase; }}
  .headline .l1 {{ font-size: 12.2cm; color: {YELLOW}; display: block; text-shadow: 0 .5cm 0 rgba(0,0,0,.25); }}
  .headline .l1 small {{ font-size: 6.4cm; color: #fff; font-weight: 800; letter-spacing: .01em; }}
  .headline .l2 {{ font-size: 11.4cm; color: #fff; display: block; text-shadow: 0 .5cm 0 rgba(0,0,0,.25); margin-top: .4cm; }}
  .sub {{ left: 4cm; right: 4cm; top: 60.8cm; text-align: center; font-family: Outfit, sans-serif;
          font-weight: 700; font-size: 3.3cm; line-height: 1.1; }}
  .sub b {{ color: {YELLOW}; font-weight: 800; }}

  /* ---- cue cards (same structure as the printed cards) ---- */
  .card {{ width: {CARD}cm; height: {CARD}cm; background: #fff; color: #111; border: .09cm solid #222; border-radius: .7cm;
           display: flex; flex-direction: column; overflow: hidden; transform-origin: 50% 50%;
           box-shadow: 0 .6cm 1.5cm rgba(0,0,0,.5); }}
  .cc-head {{ height: {HEAD_H}cm; display: flex; align-items: center; justify-content: space-between;
              padding: 0 1cm; border-bottom: .09cm solid #222; flex-shrink: 0; background: #fff; }}
  .cc-left {{ display: flex; align-items: center; gap: .8cm; }}
  .cc-crest {{ height: 3cm; width: {3 * crest_ratio:.2f}cm; display: block; }}
  .cc-event {{ font-size: .72cm; font-weight: 700; color: #777; letter-spacing: .06em; text-transform: uppercase; line-height: 1.2; }}
  .cc-game {{ font-size: 1.2cm; font-weight: 800; color: #111; line-height: 1.2; }}
  .cc-num {{ font-size: .92cm; font-weight: 800; color: #444; background: #e9e9e9; padding: .22cm .5cm; border-radius: .25cm; white-space: nowrap; }}
  .cc-img {{ flex: 1; position: relative; overflow: hidden; }}
  .cc-img img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .cc-topic {{ position: absolute; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,.6); color: #fff; font-size: 1.25cm;
               font-weight: 700; letter-spacing: .04em; text-align: center; padding: .6cm 0 .5cm; }}
  .cc-txt {{ flex: 1; padding: 1cm 1.2cm .6cm; display: flex; flex-direction: column; gap: .5cm; overflow: hidden; }}
  .cc-ttopic {{ font-size: .98cm; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: #888; }}
  .cc-txt p {{ font-size: 1.74cm; line-height: 1.46; font-style: italic; color: #111; }}
  .cc-foot {{ height: {FOOT_H}cm; display: flex; border-top: .09cm solid #222; flex-shrink: 0; background: #fff; }}
  .cc-btn {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .1cm; }}
  .cc-btn:first-child {{ border-right: .09cm solid #222; }}
  .cc-ico {{ width: 1.8cm; height: 1.8cm; }}
  .cc-ico svg {{ width: 100%; height: 100%; display: block; }}
  .cc-lbl {{ font-size: 1.3cm; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; line-height: 1.1; }}
  .cc-sub {{ font-size: .72cm; color: #777; line-height: 1; }}
  .cc-foot.back .cc-btn > * {{ visibility: hidden; }}

  /* ---- brains ---- */
  .brain {{ width: {BRAIN_W}cm; height: {BRAIN_H:.2f}cm; z-index: 8; }}
  .b-ai {{ left: 36.2cm; top: 66.6cm; transform: rotate(5deg); }}
  .b-human {{ left: 2.8cm; top: 98.6cm; transform: rotate(-5deg); }}
  .bl {{ z-index: 9; font-family: Outfit, sans-serif; font-weight: 900; font-size: 2.5cm; letter-spacing: .06em; text-transform: uppercase;
         padding: .25cm 1.3cm .1cm; border-radius: 2cm; box-shadow: 0 .3cm .8cm rgba(0,0,0,.4); border: .3cm solid #fff; }}
  .bl-ai {{ left: 41.3cm; top: 83.8cm; background: {NAVY}; color: {YELLOW}; }}
  .bl-human {{ left: 5.6cm; top: 115.6cm; background: {YELLOW}; color: {NAVY}; }}

  /* ---- call to action + credit ---- */
  .cta {{ left: 4cm; right: 4cm; top: {CTA_TOP}cm; height: {CTA_H}cm; background: #fff; color: {NAVY};
          border-radius: 3.2cm; text-align: center; display: flex; flex-direction: column;
          align-items: center; justify-content: center; box-shadow: 0 .5cm 1.4cm rgba(0,0,0,.4); z-index: 10; }}
  .cta .k {{ font-family: Outfit, sans-serif; font-weight: 800; font-size: 2.1cm; letter-spacing: .1em;
             text-transform: uppercase; color: {BLUE}; }}
  .cta .big {{ font-family: Outfit, sans-serif; font-weight: 900; font-size: 5.2cm; line-height: .98;
               text-transform: uppercase; margin-top: .6cm; }}
  .cta .big span {{ color: {BLUE}; }}
  .credit {{ left: 11cm; right: 11cm; top: {CREDIT_TOP}cm; height: {CREDIT_H}cm; border-radius: 4cm;
             background: rgba(4,32,63,.88); border: .35cm solid {YELLOW}; display: flex; align-items: center; justify-content: center;
             font-family: Outfit, sans-serif; font-weight: 800; font-size: 3.2cm; color: #fff; white-space: nowrap; z-index: 10; }}
</style></head>
<body>
  <div class="abs dots"></div>
  <div class="abs glow"></div>

  <div class="abs logo-panel"><img src="{logo_uri}" alt="University of Liberal Arts Bangladesh"></div>
  <div class="abs ribbon"><div class="n">23<sup>rd</sup></div><div class="t">Foundation<br>Day</div></div>

  <div class="abs headline"><span class="l1">AI <small>or</small></span><span class="l2">Human?</span></div>
  <div class="abs sub">Can you spot the <b>AI-made</b> one?</div>

  {left_deck}
  {right_deck}
  <img class="abs brain b-ai" src="{ai_uri}" alt="AI brain">
  <img class="abs brain b-human" src="{human_uri}" alt="Human brain">
  <div class="abs bl bl-ai">AI</div>
  <div class="abs bl bl-human">Human</div>

  <div class="abs cta">
    <div class="k">Cue card game · Photos &amp; text</div>
    <div class="big">Play at our <span>booth!</span></div>
  </div>
  <div class="abs credit">{ORGANIZER}</div>
</body></html>"""

# Soft (blurred) CSS shadows are stored in the PDF as image tiles and leave faint seams, so use crisp offset
# shadows instead: they stay pure vector in both the PDF and the SVG.
html = re.sub(r"box-shadow:\s*0\s+([\d.]+)cm\s+[\d.]+cm\s+rgba\(([^)]*)\)", r"box-shadow: 0 cm 0 rgba()", html)

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
        except PermissionError:               # PDF open in a viewer
            pdf_path = pdf_path.with_name(pdf_path.stem + "_new.pdf"); pdf_path.write_bytes(data)
            print("NOTE: PDF is open elsewhere; saved as", pdf_path.name)
        b.close()
    return pdf_path


pdf_path = render()

import fitz  # PyMuPDF

doc = fitz.open(str(pdf_path))
page = doc[0]
page.get_pixmap(matrix=fitz.Matrix(0.35, 0.35)).save(str(OUT / "preview.png"))   # preview of the real PDF
svg = page.get_svg_image(text_as_path=True)
svg_path = OUT / f"{NAME}.svg"
svg_path.write_text(svg, encoding="utf-8")
print(f"pages: {len(doc)}  page size: {page.rect.width / 72 * 2.54:.1f} x {page.rect.height / 72 * 2.54:.1f} cm")
print("wrote:", html_path.name, pdf_path.name, svg_path.name)
