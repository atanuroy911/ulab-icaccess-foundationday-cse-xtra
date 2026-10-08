"""Vector clipart for the X-banner: a human brain and an AI (circuit) brain, plus small card icons."""

# One side-view cerebrum, built as a union of lobes so the outline looks lumpy like a real brain.
# (cx, cy, r) in a 200 x 160 box, brain facing left.
LOBES = [
    (100, 70, 62), (62, 68, 44), (140, 72, 44),
    (44, 46, 23), (70, 30, 23), (100, 24, 25), (132, 28, 24), (158, 40, 23), (176, 62, 21),
    (28, 70, 21), (32, 94, 19), (50, 108, 20), (176, 86, 19), (152, 104, 19),
    (82, 104, 19), (112, 108, 18), (126, 98, 18),
]
CEREBELLUM = (158, 118, 33, 20)        # cx, cy, rx, ry
STEM = "M118 112 C120 128 122 140 126 150 L142 150 C140 138 138 126 138 112 Z"


def _lobes(fill="none", stroke="none", sw=0, extra_r=0):
    return "".join(
        f'<circle cx="{x}" cy="{y}" r="{r + extra_r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        for x, y, r in LOBES)


FOLDS = [  # gyri / sulci: smooth curves that follow the dome of the cerebrum
    "M34 58 C50 38 76 34 98 36 S146 36 166 54",                      # outer dome
    "M38 76 C54 56 80 52 100 54 S142 54 164 72",                     # second gyrus
    "M34 92 C56 74 82 72 102 76 S138 76 162 90",                     # lateral (Sylvian) fissure
    "M60 106 C78 94 100 92 118 98 S140 102 152 98",                  # temporal
    "M100 26 C94 40 104 48 98 60 S104 74 100 84",                    # central sulcus
    "M64 34 C60 44 68 50 62 60",
    "M140 34 C136 46 146 52 142 64",
    "M76 70 C82 80 76 88 82 96",
    "M126 64 C122 74 132 80 128 90",
]


def human_brain(width_px=600):
    """Pink, organic, outlined: reads instantly as 'human brain'."""
    ow, ol = "#9E3B63", "#E0678C"
    cx, cy, rx, ry = CEREBELLUM
    folds = "".join(f'<path d="{d}" fill="none" stroke="{ol}" stroke-width="4" stroke-linecap="round"/>' for d in FOLDS)
    cerebellum_lines = "".join(
        f'<path d="M{cx - rx + 8} {cy + k * 6 - 8} Q{cx} {cy + k * 6 - 4} {cx + rx - 8} {cy + k * 6 - 8}" fill="none" stroke="#B9577D" stroke-width="2.6" stroke-linecap="round"/>'
        for k in range(0, 4))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -6 212 172" width="{width_px}">
  <defs>
    <radialGradient id="hb" gradientUnits="userSpaceOnUse" cx="70" cy="34" r="150">
      <stop offset="0" stop-color="#FFC9D8"/><stop offset=".6" stop-color="#F59DB8"/><stop offset="1" stop-color="#E8789C"/>
    </radialGradient>
  </defs>
  <path d="{STEM}" fill="#E8789C" stroke="{ow}" stroke-width="4" stroke-linejoin="round"/>
  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#E8789C" stroke="{ow}" stroke-width="5"/>
  {cerebellum_lines}
  {_lobes(stroke=ow, sw=9)}
  {_lobes(fill="url(#hb)")}
  {folds}
  <ellipse cx="62" cy="38" rx="20" ry="9" fill="#fff" opacity=".28" transform="rotate(-24 62 38)"/>
</svg>"""


def _circuit(color, node):
    """Right-angle / 45-degree circuit traces with end nodes."""
    paths = [
        "M30 66 H58 L70 54 H98", "M98 54 V38 H124", "M124 38 L136 26 H160", "M58 66 V90 H84",
        "M36 94 H60 L72 106 H100", "M100 106 V92 H130 L142 80 H172", "M84 90 L96 78 H118 V62 H146",
        "M146 62 L158 50 H176", "M44 50 H52 V34 H74", "M150 98 H168 L176 90", "M116 76 V66",
        "M70 54 V70 H84", "M130 92 V104 H146",
    ]
    nodes = [(30, 66), (98, 54), (124, 38), (160, 26), (84, 90), (100, 106), (172, 80), (118, 62),
            (176, 50), (74, 34), (176, 90), (146, 62), (146, 104), (52, 50), (36, 94)]
    lines = "".join(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>' for d in paths)
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="4.2" fill="#04203F" stroke="{node}" stroke-width="2.4"/>' for x, y in nodes)
    return lines + dots


def ai_brain(width_px=600):
    """Same silhouette, but a glowing blue circuit board with a chip: reads as 'AI brain'."""
    cx, cy, rx, ry = CEREBELLUM
    cb = "".join(
        f'<path d="M{cx - rx + 10} {cy + k * 7 - 9} H{cx + rx - 10}" stroke="#5CE1FF" stroke-width="2.6" stroke-linecap="round"/>'
        for k in range(4))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -6 212 172" width="{width_px}">
  <defs>
    <linearGradient id="ab" gradientUnits="userSpaceOnUse" x1="20" y1="6" x2="184" y2="124">
      <stop offset="0" stop-color="#0F7BD0"/><stop offset=".55" stop-color="#0A4C9A"/><stop offset="1" stop-color="#062C66"/>
    </linearGradient>
    <clipPath id="abclip">{_lobes(fill="#000")}</clipPath>
  </defs>
  <path d="{STEM}" fill="#0A4C9A" stroke="#5CE1FF" stroke-width="4" stroke-linejoin="round"/>
  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#0A4C9A" stroke="#5CE1FF" stroke-width="5"/>
  {cb}
  {_lobes(stroke="#5CE1FF", sw=9)}
  {_lobes(fill="url(#ab)")}
  <g clip-path="url(#abclip)">{_circuit("#7BEBFF", "#FDC300")}</g>
  <rect x="86" y="62" width="30" height="30" rx="5" fill="#04203F" stroke="#FDC300" stroke-width="3.2"/>
  <path d="M94 70 H108 M94 77 H108 M94 84 H102" stroke="#FDC300" stroke-width="2.6" stroke-linecap="round"/>
  {"".join(f'<path d="M{x} 62 v-6 M{x} 92 v6" stroke="#FDC300" stroke-width="2.6" stroke-linecap="round"/>' for x in (94, 101, 108))}
</svg>"""


# ---- icons for the card footer buttons --------------------------------------------------------
PERSON_ICON = """<svg viewBox="0 0 24 24" fill="#111"><circle cx="12" cy="7.5" r="4.2"/><path d="M3.5 21c.6-5 4-7.6 8.5-7.6s7.9 2.6 8.5 7.6z"/></svg>"""
ROBOT_ICON = """<svg viewBox="0 0 24 24" fill="none" stroke="#111" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<rect x="4" y="8" width="16" height="12" rx="3" fill="#111"/><path d="M12 8V4"/><circle cx="12" cy="3.2" r="1.3" fill="#111"/>
<circle cx="9" cy="14" r="1.6" fill="#fff" stroke="none"/><circle cx="15" cy="14" r="1.6" fill="#fff" stroke="none"/><path d="M2 12v4M22 12v4"/></svg>"""


if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).parent / "xbanner"
    out.mkdir(exist_ok=True)
    (out / "_human_brain.svg").write_text(human_brain(), encoding="utf-8")
    (out / "_ai_brain.svg").write_text(ai_brain(), encoding="utf-8")
    print("ok")
