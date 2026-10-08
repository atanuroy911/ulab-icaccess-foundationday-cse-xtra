"""
Build the iCACCESS 2026 Program Schedule (HTML + PDF) from the planning workbook.

    python build_program.py

Reads  : ICACCESS2026-Plan_Dynamic_V4.xlsx, icaccess-logo.png, hero-background.jpg
Writes : ICACCESS2026_Program_Schedule.html, ICACCESS2026_Program_Schedule.pdf

Re-run after editing the spreadsheet; everything is regenerated from it.
"""
import base64
import html
import io
import re
from datetime import date
from pathlib import Path

import openpyxl
from PIL import Image

ROOT = Path(__file__).parent
# newest copy of the planning workbook (downloads may be saved as "... (1).xlsx")
XLSX = max(ROOT.glob("ICACCESS2026-Plan_Dynamic_V4*.xlsx"), key=lambda f: f.stat().st_mtime)
# ---------------------------------------------------------------- edition
# FINAL edition: cover says "Final Program"; detailed session pages only for the listed sessions.
# Set FINAL = False to rebuild the earlier "Tentative Program (Subject to Change)" version.
FINAL = True
DETAIL_SESSIONS = ["T1P1", "T1P2", "T1P3", "T2P1", "T2P2", "T2P3", "T2P4",
                   "T4P1", "T4P2", "T4P3", "T4P4", "T4P5", "T4P6"]

_name = "ICACCESS2026_Final_Program" if FINAL else "ICACCESS2026_Program_Schedule"
OUT_HTML = ROOT / f"{_name}.html"
OUT_PDF = ROOT / f"{_name}.pdf"

# ---------------------------------------------------------------- conference facts
CONF_SHORT = "iCACCESS 2026"
CONF_FULL = ("2nd International Conference on Advances in Computing, Communication, "
             "Electrical, and Smart Systems")
DAYS = {1: date(2026, 10, 2), 2: date(2026, 10, 3)}
VENUE = "ULAB Campus, Dhaka, Bangladesh"
DATES = "October 2–3, 2026"
SPONSOR_LABEL = "Technical Co-Sponsor"
ORGANIZER = "School of Science and Engineering, University of Liberal Arts Bangladesh"

esc = html.escape


# ---------------------------------------------------------------- helpers
def day_label(d, short=False):
    dt = DAYS[d]
    if short:
        return dt.strftime("%a, %d %b").replace(" 0", " ")
    return f"Day {d} · {dt.strftime('%A')}, {dt.day} {dt.strftime('%B %Y')}"


def t12(hm):
    h, m = map(int, hm.split(":"))
    return f"{(h - 1) % 12 + 1:02d}:{m:02d} {'AM' if h < 12 else 'PM'}"


def span(rng):
    a, b = [x.strip() for x in rng.split("-")]
    return f"{t12(a)} – {t12(b)}"


# Spelling fixes for names typed inconsistently in the workbook (applied wherever chairs are read)
NAME_FIXES = {
    "Dr. Mohammaed Ashikur Rahman": "Dr. Mohammed Ashikur Rahman",
    "Dr. Md.Ruhul Amin": "Dr. Md. Ruhul Amin",
}
fix_name = lambda n: NAME_FIXES.get(n, n)


def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def parse_authors(raw):
    """'Name (Affil)*; Name2 (Affil)' -> [('Name', True), ('Name2', False)]"""
    out = []
    for part in str(raw or "").split(";"):
        part = part.strip()
        if not part:
            continue
        star = part.endswith("*")
        name = clean(part.rstrip("*").split("(")[0])  # affiliations may nest parens
        out.append((name, star))
    return out


def img_data_uri(path, crop_top=None, max_w=None, fmt="PNG"):
    im = Image.open(path)
    im.load()
    if crop_top:
        im = im.crop((0, 0, im.width, crop_top))
    if max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if fmt == "JPEG":
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[3])  # composite alpha onto white
            im_rgb = bg
        else:
            im_rgb = im.convert("RGB")
        im_rgb.save(buf, "JPEG", quality=86)
    else:
        im.save(buf, "PNG", optimize=True)
    return f"data:image/{fmt.lower()};base64,{base64.b64encode(buf.getvalue()).decode()}"


def ulab_logo_uri(path, navy=(11, 31, 58)):
    """ULAB SSE logo ships with white lettering; recolour the text (not the crest) navy for a white footer."""
    im = Image.open(path).convert("RGBA")
    px = im.load()
    crest_w = int(im.width * 0.165)
    for y in range(im.height):
        for x in range(crest_w, im.width):
            r, g, b, a = px[x, y]
            if a and min(r, g, b) > 200:
                px[x, y] = (*navy, a)
    buf = io.BytesIO()
    im.resize((640, round(im.height * 640 / im.width)), Image.LANCZOS).save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def trimmed_logo_uri(path, width=400):
    """Crop surrounding white/transparent padding."""
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(bg, im).convert("L").point(lambda v: 255 if v < 235 else 0)
    im = im.crop(flat.getbbox())
    buf = io.BytesIO()
    im.resize((width, round(im.height * width / im.width)), Image.LANCZOS).save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def link_label(url):
    return "Google Meet" if "meet.google" in url else "Zoom" if "zoom" in url else "Online"


# ---------------------------------------------------------------- read workbook
wb = openpyxl.load_workbook(XLSX, data_only=True)

tracks = {}
for row in wb["Sessions"].iter_rows(min_row=2, values_only=True):
    if row[1]:
        tracks[row[1]] = clean(row[0])


def read_session(code):
    ws = wb[code]
    # header block: label in column A, value in column B (rows shift when chairs are added)
    header_end = next((r for r in range(1, 40) if clean(ws.cell(r, 1).value) in ("ID", "Papers")), 11)
    labels = [(clean(ws.cell(r, 1).value), ws.cell(r, 2).value) for r in range(1, header_end)]
    kv = {k: v for k, v in labels}
    chairs = [fix_name(clean(v)) for k, v in labels if k.startswith("Session Chair") and clean(v)]
    first_paper = next((r + 1 for r in range(1, 40) if clean(ws.cell(r, 1).value) == "ID"), 12)
    papers = []
    for r in range(first_paper, ws.max_row + 1):
        pid, title, authors = (ws.cell(r, c).value for c in (1, 2, 3))
        if pid in (None, "") or not title:
            continue
        papers.append({"id": int(pid), "title": clean(title), "authors": parse_authors(authors)})
    t = clean(kv.get("Session Time"))  # "Day 1, 11:40-12:40"
    m = re.match(r"Day\s*(\d),\s*([\d:]+-[\d:]+)", t)
    rapp = []
    for k in ("Rappoteur 1", "Rappoteur 2"):
        v = clean(kv.get(k))
        if v and v not in rapp:
            rapp.append(v)
    room = clean(kv.get("Session Room"))
    return {
        "code": code,
        "title": clean(kv.get("Session Title")),
        "track": tracks.get(code, ""),
        "day": int(m.group(1)) if m else None,
        "time": m.group(2) if m else "",
        "room": room,
        "online": room.startswith("http"),
        "chairs": chairs,
        "moderator": clean(kv.get("Session Moderator")),
        "rapporteurs": rapp,
        "papers": papers,
    }


def read_special(sheet):
    ws = wb[sheet]
    return {clean(ws.cell(r, 1).value): ws.cell(r, 2).value for r in range(1, 14)}


tech_codes = [c for c in wb["_Lists"]["A"][1:] if c.value and str(c.value).strip()]
sessions = [read_session(c.value.strip()) for c in tech_codes]
skipped = [s["code"] for s in sessions if not s["papers"]]
sessions = [s for s in sessions if s["papers"]]  # drop sessions with no papers yet
by_code = {s["code"]: s for s in sessions}

k1, k2, k3 = (read_special(f"Keynote {i}") for i in (1, 2, 3))
ws_ = read_special("Workshop")


def keynote_speaker(k):
    info = clean(k.get("Speakers Info"))
    return info.split(",")[0] if info else ""


def slot_sessions(prefix):
    return [s for s in sessions if s["code"].startswith(prefix)]


# ---------------------------------------------------------------- HTML fragments
def room_html(s, small=False):
    if s["online"]:
        return (f'<span class="inline-flex items-center gap-1 font-semibold text-azure">'
                f'<span class="w-1.5 h-1.5 rounded-full bg-teal"></span>{link_label(s["room"])}</span>')
    return f'<span class="font-semibold text-navy">{esc(s["room"])}</span>'


def parallel_list(items):
    rows = "".join(
        f'<div class="flex items-baseline gap-2 py-[2px]">'
        f'<span class="code-chip">{esc(s["code"])}</span>'
        f'<span class="text-slate-700 leading-snug">{esc(s["title"])}</span>'
        f'<span class="ml-auto shrink-0 text-[9.5px]">{room_html(s)}</span></div>'
        for s in items)
    return f'<div class="mt-1 space-y-0">{rows}</div>'


def sched_row(time, body, kind="event"):
    styles = {
        "event": ("bg-white", "bg-slate-300"),
        "break": ("bg-slate-50", "bg-slate-300"),
        "keynote": ("bg-teal-50/60", "bg-teal"),
        "tech": ("bg-white", "bg-azure"),
        "social": ("bg-amber-50/70", "bg-amber-400"),
    }
    bg, bar = styles[kind]
    return f"""
    <tr class="{bg} avoid-break">
      <td class="relative w-[33mm] align-top py-[7px] pl-4 pr-2 font-semibold text-navy text-[10.5px] whitespace-nowrap tabular-nums">
        <span class="absolute left-0 top-0 bottom-0 w-[3px] {bar}"></span>{time}</td>
      <td class="py-[7px] pr-4 text-[10.5px] text-slate-800">{body}</td>
    </tr>"""


def day_table(rows):
    return f"""
    <table class="w-full border-collapse overflow-hidden rounded-lg ring-1 ring-slate-200 divide-y divide-slate-200">
      <thead><tr class="bg-navy text-white text-[9px] uppercase tracking-[0.14em]">
        <th class="text-left py-2 pl-4 font-semibold">Time</th>
        <th class="text-left py-2 font-semibold">Program</th></tr></thead>
      <tbody class="divide-y divide-slate-200">{''.join(rows)}</tbody>
    </table>"""


def day_heading(d, mode):
    tone = "bg-teal text-white" if mode == "On-site" else "bg-azure text-white"
    return f"""
    <div class="flex items-end justify-between mb-2 avoid-after">
      <div>
        <div class="text-[9px] font-bold uppercase tracking-[0.22em] text-teal">Day {d}</div>
        <h2 class="font-display text-[20px] font-bold text-navy leading-tight">
          {DAYS[d].strftime('%A')}, {DAYS[d].day} {DAYS[d].strftime('%B %Y')}</h2>
      </div>
      <span class="text-[9px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full {tone}">{mode}</span>
    </div>"""


def section_title(kicker, title):
    return f"""
    <div class="mb-4 avoid-after">
      <div class="text-[9px] font-bold uppercase tracking-[0.22em] text-teal">{kicker}</div>
      <h2 class="font-display text-[20px] font-bold text-navy leading-tight">{title}</h2>
      <div class="mt-1.5 h-[3px] w-14 rounded-full bg-gradient-to-r from-teal to-azure"></div>
    </div>"""


# ---- Day 1 --------------------------------------------------------------------
k1_speaker = keynote_speaker(k1)
day1 = [
    sched_row(span("8:00-9:00"), "<b>Registration</b>", "break"),
    sched_row(span("9:30-10:30"), "<b>Opening Ceremony</b>", "event"),
    sched_row(span("10:40-11:40"),
              '<b class="text-navy text-[11px]">Keynote Session I</b>', "keynote"),
    sched_row(span("11:40-12:40"),
              '<div class="font-bold text-navy">Parallel Sessions</div>'
              '<div class="mt-1.5 flex items-baseline gap-2 py-[2px]">'
              '<span class="code-chip !bg-amber-500">WS</span>'
              f'<span class="text-slate-700"><b>IEEE Workshop:</b> {esc(clean(ws_.get("Session Title")))}</span>'
              f'<span class="ml-auto shrink-0 text-[9.5px] font-semibold text-navy">{esc(clean(ws_.get("Session Room")))}</span></div>'
              '<div class="mt-1 text-[9px] font-bold uppercase tracking-widest text-azure">Technical Session 1</div>'
              + parallel_list(slot_sessions("T1")), "tech"),
    sched_row(span("12:40-14:30"), "<b>Prayer &amp; Lunch Break</b>", "break"),
    *[sched_row(span(slot_sessions(pre)[0]["time"]),
                f'<div class="font-bold text-navy">Technical Session {pre[1]} <span class="font-normal text-slate-500">· Parallel</span></div>'
                + parallel_list(slot_sessions(pre)), "tech")
      for pre in ("T2", "T3") if slot_sessions(pre)],
    sched_row(span("16:30-17:30"),
              '<b class="text-navy text-[11px]">Keynote Session II</b>', "keynote"),
    sched_row(span("18:30-20:30"), "<b>Cultural Ceremony &amp; Dinner</b>", "social"),
]

# ---- Day 2 --------------------------------------------------------------------
day2 = [
    sched_row(span("11:00-13:00"),
              '<div class="font-bold text-navy">Technical Session 4 <span class="font-normal text-slate-500">· Parallel, Online</span></div>'
              + parallel_list(slot_sessions("T4")), "tech"),
    sched_row(span("14:30-15:30"),
              '<b class="text-navy text-[11px]">Keynote Session III</b> <span class="text-slate-500">· Online</span>', "keynote"),
    sched_row(span("18:00-19:00"), "<b>Closing &amp; Award Ceremony</b> <span class='text-slate-500'>· Online</span>", "social"),
]


# ---- At a glance ----------------------------------------------------------------
def glance_table(day):
    rows = []
    for s in [x for x in sessions if x["day"] == day]:
        ids = ", ".join(str(p["id"]) for p in s["papers"])
        rows.append(f"""
        <tr class="avoid-break even:bg-slate-50">
          <td class="py-1.5 pl-3 pr-2 align-top"><span class="code-chip">{s['code']}</span></td>
          <td class="py-1.5 pr-2 align-top text-slate-800 leading-snug">{esc(s['title'])}</td>
          <td class="py-1.5 pr-2 align-top whitespace-nowrap tabular-nums text-slate-700">{span(s['time'])}</td>
          <td class="py-1.5 pr-2 align-top whitespace-nowrap">{room_html(s)}</td>
          <td class="py-1.5 pr-3 align-top tabular-nums text-slate-600">{ids}</td>
        </tr>""")
    mode = "On-site" if day == 1 else "Online"
    return f"""
    <div class="mb-5">
      <div class="flex items-center gap-2 mb-1.5 avoid-after">
        <span class="font-display font-bold text-navy text-[12px]">{day_label(day)}</span>
        <span class="text-[8.5px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full
          {'bg-teal/15 text-teal-700' if day == 1 else 'bg-azure/15 text-azure'}">{mode}</span>
      </div>
      <table class="w-full text-[9.5px] border-collapse rounded-lg overflow-hidden ring-1 ring-slate-200">
        <thead><tr class="bg-navy text-white text-[8.5px] uppercase tracking-[0.12em]">
          <th class="text-left py-1.5 pl-3 font-semibold w-[14mm]">ID</th>
          <th class="text-left py-1.5 font-semibold">Session</th>
          <th class="text-left py-1.5 font-semibold w-[33mm]">Time</th>
          <th class="text-left py-1.5 font-semibold w-[20mm]">Room</th>
          <th class="text-left py-1.5 font-semibold w-[34mm] pr-3">Paper IDs</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>"""


# ---- Keynotes & workshop --------------------------------------------------------
def first_sentences(text, n):
    parts = re.split(r"(?<=[.!?])\s+", clean(text))
    return " ".join(parts[:n])


def role_line(label, value):
    if not value:
        return ""
    return (f'<div><span class="text-[8.5px] font-bold uppercase tracking-widest text-slate-500">{label}</span>'
            f'<div class="font-semibold text-navy">{esc(value)}</div></div>')


def keynote_card(num, k, time, where, link="", bio_n=3):
    speaker_info = clean(k.get("Speakers Info"))
    title = clean(k.get("Session Title"))
    abstract = str(k.get("Abstract") or "").strip()
    bio = k.get("Speakers Intro")
    body = ""
    if abstract:
        paras = "".join(f'<p class="mb-1.5">{esc(clean(p))}</p>' for p in abstract.split("\n") if p.strip())
        body += f'<div class="mt-3"><div class="label">Abstract</div><div class="text-justify text-slate-700">{paras}</div></div>'
    if bio:
        body += (f'<div class="mt-2"><div class="label">About the Speaker</div>'
                 f'<p class="text-justify text-slate-700">{esc(first_sentences(bio, bio_n))}</p></div>')
    speaker = (f'<div class="font-display text-[14px] font-bold text-navy">{esc(speaker_info)}</div>'
               if speaker_info else
               '<div class="font-display text-[14px] font-bold text-slate-400 italic">Speaker to be announced</div>')
    return f"""
    <div class="rounded-xl ring-1 ring-slate-200 overflow-hidden mb-4 avoid-break-soft">
      <div class="flex items-center justify-between bg-gradient-to-r from-navy to-azure px-4 py-2 text-white">
        <span class="font-display font-bold tracking-wide text-[12px]">Keynote Session {num}</span>
        <span class="text-[9.5px] font-semibold opacity-90">{time} · {where}</span>
      </div>
      <div class="px-4 py-3 text-[9.8px] leading-relaxed">
        {speaker}
        {f'<div class="italic text-teal-700 font-semibold text-[11px] mt-0.5">“{esc(title)}”</div>' if title else ''}
        <div class="grid grid-cols-2 gap-3 mt-2.5">
          {role_line("Session Chair", clean(k.get("Session Chair")))}
          {role_line("Session Moderator", clean(k.get("Session Moderator")))}
        </div>
        {f'<div class="mt-2.5"><span class="text-[8.5px] font-bold uppercase tracking-widest text-slate-500">Join online</span><div class="font-semibold text-azure break-all">{esc(link)}</div></div>' if link else ''}
        {body}
      </div>
    </div>"""


def mini_card(title, when, headline, roles, tone="from-navy to-azure", muted=False):
    roles_html = "".join(
        f'<div class="mt-1.5"><div class="label">{l}</div><div class="font-semibold text-navy">{esc(v)}</div></div>'
        for l, v in roles if v)
    head_cls = "text-slate-400 italic" if muted else "text-navy"
    return f"""
    <div class="rounded-xl ring-1 ring-slate-200 overflow-hidden avoid-break">
      <div class="bg-gradient-to-r {tone} px-3 py-1.5 text-white">
        <div class="font-display font-bold text-[11.5px]">{title}</div>
        <div class="text-[8.5px] font-semibold opacity-90">{when}</div>
      </div>
      <div class="px-3 py-2 text-[9.5px]">
        <div class="font-display text-[12px] font-bold leading-snug {head_cls}">{esc(headline)}</div>
        {roles_html}
      </div>
    </div>"""


keynotes_html = (
    keynote_card("I", k1, f"{day_label(1, True)}, {span('10:40-11:40')}", "On-site")
    + '<div class="grid grid-cols-3 gap-3 avoid-break">'
    + mini_card("IEEE Workshop", f"{day_label(1, True)}, {span('11:40-12:40')} · {esc(clean(ws_.get('Session Room')))}",
                clean(ws_.get("Session Title")),
                [("Facilitated by", clean(ws_.get("Session Facillitator"))),
                 ("Session Moderator", clean(ws_.get("Session Moderator")))],
                tone="from-amber-500 to-amber-400")
    + mini_card("Keynote Session II", f"{day_label(1, True)}, {span('16:30-17:30')} · On-site",
                keynote_speaker(k2) or "Speaker to be announced",
                [("Session Chair", clean(k2.get("Session Chair"))),
                 ("Session Moderator", clean(k2.get("Session Moderator")))],
                muted=not keynote_speaker(k2))
    + mini_card("Keynote Session III", f"{day_label(2, True)}, {span('14:30-15:30')} · Online",
                keynote_speaker(k3) or "Speaker to be announced",
                [("Session Chair", clean(k3.get("Session Chair"))),
                 ("Session Moderator", clean(k3.get("Session Moderator")))],
                muted=not keynote_speaker(k3))
    + "</div>")


# ---- Session detail cards --------------------------------------------------------
def session_card(s):
    papers = "".join(f"""
      <tr class="avoid-break even:bg-slate-50/70">
        <td class="py-1 pl-3 pr-1 align-top text-slate-400 tabular-nums">{i}</td>
        <td class="py-1 pr-2 align-top font-bold text-azure tabular-nums">{p['id']}</td>
        <td class="py-1 pr-3 align-top text-slate-800 leading-snug">{esc(p['title'])}</td>
        <td class="py-1 pr-3 align-top leading-[1.28] text-slate-700">{'<br>'.join(
            f"<span class='{'font-semibold text-navy' if star else ''}'>{esc(n)}{'*' if star else ''}</span>"
            for n, star in p['authors'])}</td>
      </tr>""" for i, p in enumerate(s["papers"], 1))

    if s["online"]:
        where = (f'<div class="col-span-2"><div class="label">Join Online ({link_label(s["room"])})</div>'
                 f'<a href="{esc(s["room"])}" class="font-mono text-[8.5px] text-azure underline break-all">{esc(s["room"])}</a></div>')
    else:
        where = f'<div><div class="label">Room</div><div class="font-bold text-navy text-[11px]">{esc(s["room"])}</div></div>'

    rapp = ", ".join(s["rapporteurs"])
    return f"""
    <section class="session mb-4 avoid-break">
      <div class="avoid-break">
        <div class="rounded-t-xl bg-navy text-white px-4 pt-2.5 pb-2">
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2.5">
              <span class="font-display text-[15px] font-bold text-teal-300">{s['code']}</span>
              <span class="font-display text-[12.5px] font-semibold leading-tight">{esc(s['title'])}</span>
            </div>
            <span class="shrink-0 text-[9.5px] font-semibold tabular-nums bg-white/10 rounded-full px-2.5 py-0.5">
              {day_label(s['day'], True)} · {span(s['time'])}</span>
          </div>
          <div class="mt-0.5 text-[8.5px] uppercase tracking-[0.12em] text-slate-300">{esc(s['track'])}</div>
        </div>
        <div class="grid grid-cols-4 gap-3 bg-teal-50 ring-1 ring-inset ring-teal-100 px-4 py-2 text-[9.5px]">
          {where}
          <div><div class="label">Session Chair{'s' if len(s['chairs']) > 1 else ''}</div><div class="font-semibold text-navy">{'<br>'.join(esc(c) for c in s['chairs'])}</div></div>
          <div><div class="label">Moderator</div><div class="font-semibold text-navy">{esc(s['moderator'])}</div></div>
          {'' if s['online'] else f'<div><div class="label">Rapporteur(s)</div><div class="text-slate-700">{esc(rapp)}</div></div>'}
          {f'<div class="col-span-2"><div class="label">Rapporteur(s)</div><div class="text-slate-700">{esc(rapp)}</div></div>' if s['online'] else ''}
        </div>
      </div>
      <table class="w-full text-[9.5px] border-collapse ring-1 ring-slate-200 rounded-b-xl overflow-hidden">
        <thead><tr class="bg-slate-100 text-[8.5px] uppercase tracking-[0.12em] text-slate-500">
          <th class="text-left py-1.5 pl-3 w-[8mm] font-semibold">#</th>
          <th class="text-left py-1.5 w-[17mm] font-semibold">Paper ID</th>
          <th class="text-left py-1.5 font-semibold">Paper Title</th>
          <th class="text-left py-1.5 w-[52mm] font-semibold">Author(s)</th></tr></thead>
        <tbody class="divide-y divide-slate-200">{papers}</tbody>
      </table>
    </section>"""


def sessions_for_day(d):
    return "".join(session_card(s) for s in sessions
                   if s["day"] == d and (not FINAL or s["code"] in DETAIL_SESSIONS))


# ---------------------------------------------------------------- page assembly
logo = img_data_uri(ROOT / "icaccess-logo.png", max_w=600)
hero_file = next(f for f in (ROOT / "hero-background (1).jpg", ROOT / "hero-background.jpg") if f.exists())
hero = img_data_uri(hero_file, max_w=1400, fmt="JPEG")
n_papers = sum(len(s["papers"]) for s in sessions)

html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{CONF_SHORT} {"Final" if FINAL else "Tentative"} Program</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {{
  theme: {{ extend: {{
    colors: {{ navy: '#0B1F3A', teal: {{ DEFAULT: '#12A594', 50: '#EEFBF8', 100: '#D3F4EE', 300: '#5EE0CD', 700: '#0B7A6D' }}, azure: '#1E5AA8' }},
    fontFamily: {{ sans: ['Inter', 'sans-serif'], display: ['Outfit', 'sans-serif'] }},
  }} }}
}}
</script>
<style type="text/tailwindcss">
  @page {{ size: A4; }}
  html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  body {{ @apply font-sans text-slate-800 bg-white; font-size: 10px; }}
  .code-chip {{ @apply inline-block shrink-0 rounded bg-azure px-1.5 py-[1px] text-[8.5px] font-bold text-white tracking-wide tabular-nums; }}
  .label {{ @apply text-[8px] font-bold uppercase tracking-[0.14em] text-slate-500 mb-0.5; }}
  .avoid-break {{ break-inside: avoid; }}
  .avoid-after {{ break-after: avoid; }}
  .page-break {{ break-before: page; }}
  thead {{ display: table-header-group; }}
  a {{ color: inherit; }}
</style>
</head>
<body>

<!-- ============ COVER + DAY 1 ============ -->
<div class="relative overflow-hidden rounded-2xl mb-5 text-white"
     style="background-image: linear-gradient(100deg, rgba(11,31,58,.95) 0%, rgba(11,31,58,.82) 42%, rgba(30,90,168,.35) 75%, rgba(18,165,148,.15) 100%), url('{hero}');
            background-size: cover; background-position: center 62%;">
  <div class="px-7 pt-5 pb-5">
    <div class="text-[9px] font-bold tracking-[0.3em] text-teal-300">{CONF_SHORT}</div>
    <h1 class="font-display text-[32px] font-extrabold leading-none mt-1">{"FINAL PROGRAM" if FINAL else "TENTATIVE PROGRAM"}</h1>
    {"" if FINAL else '<div class="font-display text-[13px] font-semibold tracking-[0.18em] text-amber-300 mt-1">(SUBJECT TO CHANGE)</div>'}
    <div class="mt-2 max-w-[120mm] text-[10.5px] leading-snug text-slate-200">{CONF_FULL} <b class="text-white">({CONF_SHORT})</b></div>
    <div class="mt-4 flex flex-wrap gap-2 text-[9.5px] font-semibold">
      <span class="rounded-full bg-white/15 px-3 py-1 backdrop-blur">📅 {DATES}</span>
      <span class="rounded-full bg-white/15 px-3 py-1">📍 {VENUE}</span>
    </div>
  </div>
  <div class="grid grid-cols-4 border-t border-white/15 bg-navy/60 text-center">
    {''.join(f'<div class="py-1.5 {"border-l border-white/15" if i else ""}"><div class="font-display text-[18px] font-bold text-teal-300">{v}</div><div class="text-[8px] uppercase tracking-widest text-slate-300">{l}</div></div>'
             for i, (v, l) in enumerate([("2", "Days"), ("3", "Keynotes"), (str(len(sessions)), "Technical Sessions"), (str(n_papers), "Papers")]))}
  </div>
</div>

{day_heading(1, "On-site")}
{day_table(day1)}

<!-- ============ DAY 2 (always starts on a new page, with Keynote Session III) ============ -->
<div class="page-break"></div>
<div>
{day_heading(2, "Online")}
{day_table(day2)}
</div>

<!-- ============ AT A GLANCE ============ -->
<div class="page-break"></div>
{section_title("Technical Program", "Sessions at a Glance")}
{glance_table(1)}
{glance_table(2)}
<p class="text-[8.5px] text-slate-500 -mt-2">Day 2 sessions run online; joining links are listed with each session on the following pages.</p>

<!-- ============ SESSION DETAILS ============ -->
<div class="page-break"></div>
{section_title(day_label(1) + " · On-site", "Technical Sessions")}
{sessions_for_day(1)}

<div class="page-break"></div>
{section_title(day_label(2) + " · Online", "Technical Sessions")}
{sessions_for_day(2)}

<p class="mt-2 text-[8.5px] text-slate-500">* Corresponding / presenting author.</p>

<!-- ============ KEYNOTE SESSION III (details, last page) ============ -->
<div class="page-break"></div>
{section_title(day_label(2) + " · Online", "Keynote Session III")}
{keynote_card("III", k3, f"{day_label(2, True)}, {span('14:30-15:30')}", "Online", link=clean(k3.get("Session Room")), bio_n=99)}

<!-- ============ CLOSING & AWARD CEREMONY (last page) ============ -->
<div class="page-break"></div>
{section_title(day_label(2) + " · Online", "Closing &amp; Award Ceremony")}
<div class="rounded-xl ring-1 ring-slate-200 overflow-hidden mb-4 avoid-break-soft">
  <div class="flex items-center justify-between bg-gradient-to-r from-navy to-azure px-4 py-2 text-white">
    <span class="font-display font-bold tracking-wide text-[12px]">Closing &amp; Award Ceremony</span>
    <span class="text-[9.5px] font-semibold opacity-90">{day_label(2, True)}, {span('18:00-19:00')} · Online</span>
  </div>
  <div class="px-4 py-4 text-[10.5px] leading-relaxed">
    <div class="grid grid-cols-2 gap-3">
      <div><span class="text-[8.5px] font-bold uppercase tracking-widest text-slate-500">Event</span><div class="font-display text-[14px] font-bold text-navy">Closing &amp; Award Ceremony (Online)</div></div>
      <div><span class="text-[8.5px] font-bold uppercase tracking-widest text-slate-500">Time</span><div class="font-display text-[14px] font-bold text-navy">{span('18:00-19:00')}</div></div>
    </div>
    <div class="mt-3"><span class="text-[8.5px] font-bold uppercase tracking-widest text-slate-500">Closing ceremony link</span>
      <div class="font-semibold text-azure break-all">https://bdren.zoom.us/j/3426823862?pwd=qdTx7T0wafu1iseMaIbFJzZkwB20Gq.1&amp;omn=9670458221</div></div>
  </div>
</div>
</body>
</html>"""

OUT_HTML.write_text(html_doc, encoding="utf-8")

# ---------------------------------------------------------------- repeating header/footer
ulab_logo = ulab_logo_uri(ROOT / "ulab-science-logo.png")
ieee_logo = trimmed_logo_uri(ROOT / "ieee-bangladesh-logo.png")
ICON_CAL = '<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="#12A594" stroke-width="2.4" style="vertical-align:-1px"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'
ICON_PIN = '<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="#12A594" stroke-width="2.4" style="vertical-align:-1px"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>'

HEADER = f"""
<div style="width:100%; margin:0 14mm; font-family:'Segoe UI',Arial,sans-serif; -webkit-print-color-adjust:exact;">
  <div style="display:flex; align-items:center; gap:10px; padding-top:6mm; padding-bottom:2.5mm;">
    <img src="{logo}" style="height:15mm;">
    <div style="flex:1; border-left:1px solid #cbd5e1; padding-left:10px;">
      <div style="font-size:12px; font-weight:800; color:#0B1F3A; letter-spacing:.02em;">{CONF_SHORT}</div>
      <div style="font-size:8.5px; font-weight:600; color:#1E5AA8; line-height:1.25; margin-top:1px;">{CONF_FULL}</div>
      <div style="font-size:8px; font-weight:600; color:#334155; margin-top:3px;">
        {ICON_CAL}&nbsp;{DATES} &nbsp;<span style="color:#cbd5e1">|</span>&nbsp; {ICON_PIN}&nbsp;{VENUE}</div>
    </div>
  </div>
  <div style="height:2px; background:linear-gradient(90deg,#12A594,#1E5AA8 60%,#0B1F3A);"></div>
</div>"""

FOOTER = f"""
<div style="width:100%; margin:0 14mm; font-family:'Segoe UI',Arial,sans-serif; -webkit-print-color-adjust:exact;">
  <div style="height:2px; background:linear-gradient(90deg,#0B1F3A,#1E5AA8 40%,#12A594); margin-bottom:2.5mm;"></div>
  <div style="display:flex; justify-content:space-between; align-items:flex-end; padding-bottom:5mm;">
    <div>
      <div style="font-size:6.5px; font-weight:700; color:#12A594; text-transform:uppercase; letter-spacing:.14em; margin-bottom:1.5mm;">Organized by</div>
      <img src="{ulab_logo}" style="height:9.5mm;">
    </div>
    <div style="font-size:8px; font-weight:700; color:#0B1F3A; padding-bottom:1mm;">
      <span class="pageNumber"></span> <span style="color:#94a3b8;">/ <span class="totalPages"></span></span></div>
    <div style="text-align:right;">
      <div style="font-size:6.5px; font-weight:700; color:#12A594; text-transform:uppercase; letter-spacing:.14em; margin-bottom:1.5mm;">{SPONSOR_LABEL}</div>
      <img src="{ieee_logo}" style="height:9.5mm;">
    </div>
  </div>
</div>"""


def render_pdf():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(OUT_HTML.resolve().as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        data = page.pdf(format="A4", print_background=True,
                 display_header_footer=True, header_template=HEADER, footer_template=FOOTER,
                 margin={"top": "32mm", "bottom": "25mm", "left": "14mm", "right": "14mm"})
        browser.close()
    # If the PDF is open in a viewer (Windows locks it), save next to it under a new name instead.
    global OUT_PDF
    try:
        OUT_PDF.write_bytes(data)
    except PermissionError:
        alt = OUT_PDF.with_name(OUT_PDF.stem + "_updated" + OUT_PDF.suffix)
        alt.write_bytes(data)
        print(f"NOTE: {OUT_PDF.name} is open elsewhere, so the new PDF was saved as {alt.name}")
        OUT_PDF = alt


render_pdf()
print(f"Sessions: {len(sessions)}  Papers: {n_papers}")
if skipped:
    print("Skipped (no papers assigned yet):", ", ".join(skipped))
print("Wrote", OUT_HTML.name, "and", OUT_PDF.name)
