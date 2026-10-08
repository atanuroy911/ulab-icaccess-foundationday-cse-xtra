"""
Patch the cue_cards.html to add text-based cards section.
Run: python patch_html.py
"""
import re

# ── Extra CSS for text cards ─────────────────────────────────────────────────
EXTRA_CSS = """
/* TEXT CARD BODY */
.ct {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 3.5mm 3.5mm 2mm;
  gap: 2mm;
  overflow: hidden;
}
.ct-topic {
  font-size: 6pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: #888;
  flex-shrink: 0;
}
.ct-text {
  font-size: 7.8pt;
  font-weight: 400;
  color: #111;
  line-height: 1.55;
  font-style: italic;
  overflow: hidden;
}
/* TEXT ANSWER CARD overrides */
.ta-verdict-block { display: flex; flex-direction: column; gap: 2mm; }
.ta-topic { font-size: 6pt; font-weight: 700; text-transform: uppercase; letter-spacing:.08em; color:#888; margin-bottom:1mm; }
.ta-row { display:flex; align-items:flex-start; gap:1.5mm; padding:2mm; border-radius:1.5mm; border:1px solid #e8e8e8; background:#fafafa; }
.ta-card-id { font-size:5.5pt; font-weight:800; color:#999; flex-shrink:0; padding-top:0.5mm; }
.ta-badge { font-size:5.5pt; font-weight:800; letter-spacing:.06em; text-transform:uppercase; padding:1px 4px; border-radius:2px; flex-shrink:0; white-space:nowrap; }
.ta-b-human { background:#e8f8f0; color:#1a6644; border:1px solid #b6e8d0; }
.ta-b-ai    { background:#f0f0ff; color:#3333aa; border:1px solid #c8c8f0; }
.ta-snip { font-size:5.5pt; font-style:italic; color:#555; line-height:1.45; }
.ta-hint { font-size:5.5pt; color:#999; text-align:center; font-style:italic; padding:1.5mm 2mm; border-top:1px dashed #e0e0e0; margin-top:auto; }
"""

# ── Helper to build one question text card ────────────────────────────────────
def qcard(num, topic, emoji, text):
    return f"""
  <div class="card text-card" id="t{num}">
    <div class="ch">
      <div class="ch-left">
        <img class="logo" src="ulab-logo.svg" alt="ULAB">
        <div class="ch-titles">
          <div class="ch-event">ULAB · 23rd Foundation Day</div>
          <div class="ch-game">AI or Human?</div>
        </div>
      </div>
      <div class="ch-num">#T{num}</div>
    </div>
    <div class="ct">
      <div class="ct-topic">{emoji} {topic}</div>
      <p class="ct-text">{text}</p>
    </div>
    <div class="cf">
      <div class="cf-btn"><span class="cf-icon">🧑</span><span class="cf-label">Human</span><span class="cf-sub">Real writing</span></div>
      <div class="cf-btn"><span class="cf-icon">🤖</span><span class="cf-label">AI</span><span class="cf-sub">Generated</span></div>
    </div>
  </div>"""

# ── Helper to build one answer text card ──────────────────────────────────────
def acard(num, topic, emoji, a_id, a_badge_cls, a_badge, a_snip,
          b_id, b_badge_cls, b_badge, b_snip, hint):
    return f"""
  <div class="card answer-card text-ans-card" id="ta{num}">
    <div class="ch">
      <div class="ch-left">
        <img class="logo" src="ulab-logo.svg" alt="ULAB">
        <div class="ch-titles">
          <div class="ch-event">ULAB · 23rd Foundation Day</div>
          <div class="ch-game">Answer — Text #{num}</div>
        </div>
      </div>
      <div class="ch-num">ANS</div>
    </div>
    <div class="ca-body">
      <div class="ta-verdict-block">
        <div class="ta-topic">{emoji} {topic}</div>
        <div class="ta-row">
          <span class="ta-card-id">{a_id}</span>
          <span class="ta-badge {a_badge_cls}">{a_badge}</span>
          <span class="ta-snip">{a_snip}</span>
        </div>
        <div class="ta-row">
          <span class="ta-card-id">{b_id}</span>
          <span class="ta-badge {b_badge_cls}">{b_badge}</span>
          <span class="ta-snip">{b_snip}</span>
        </div>
      </div>
      <div class="ta-hint">{hint}</div>
    </div>
  </div>"""

# ── Text pairs data ────────────────────────────────────────────────────────────
# Each pair: (num_A, num_B, topic, emoji, human_text, ai_text, hint)
PAIRS = [
    ("1A", "1B", "Restaurant Review", "🍛",
     '"Tried the biryani — wow! A bit too oily but the aroma alone was worth the trip. Will definitely come back, just maybe order the smaller portion next time lol 😅"',
     '"The restaurant offered a diverse menu with various culinary options. The biryani was prepared with aromatic spices and presented in an aesthetically pleasing manner. The dining experience was satisfactory and I would recommend it to food enthusiasts."',
     "Clue: emoji + informal opinion = Human"),

    ("2A", "2B", "Birthday Wish", "🎂",
     '"Happy Birthday! On this special occasion, I extend my warmest greetings. May this day bring you immense joy and happiness. Wishing you all the success and prosperity in the coming year ahead."',
     '"Happy birthday you absolute disaster!! Remember the time you got us all lost in Sylhet at 2am? Never changing. Love you loads though ❤️ — Same time next year?"',
     "Clue: specific shared memory & playful insults = Human"),

    ("3A", "3B", "Complaint Letter", "😤",
     '"Dear Customer Service, I am writing to formally express my dissatisfaction regarding the service outage. The issue commenced Tuesday and has persisted for an extended duration. I kindly request immediate resolution of this matter."',
     '"I\'ve called THREE times now and nobody picks up. The internet has been down since Tuesday and my work is suffering. This is completely unacceptable — I\'m paying for a service that doesn\'t work!"',
     "Clue: CAPS for emphasis & raw anger = Human"),

    ("4A", "4B", "Motivational", "💪",
     '"Look — you\'re going to fail. You\'ll fall flat on your face. But every single time you get back up, you get a little bit harder to knock down. That\'s the whole game."',
     '"Success is a journey that requires dedication and perseverance. It is important to maintain a positive mindset and continuously strive towards your goals. Every challenge is an opportunity for growth."',
     "Clue: vague clichés with no edge = AI"),

    ("5A", "5B", "Describing Nature", "🌿",
     '"Nature is a beautiful and complex system encompassing diverse ecosystems. It provides valuable resources contributing to the well-being of all living organisms. It is essential to appreciate and preserve nature for future generations."',
     '"The pond behind our old house went completely still at dawn. You\'d hear frogs — then suddenly nothing. It smelled like mud and rain. I\'ve never found that smell anywhere else."',
     "Clue: specific sensory memory = Human"),

    ("6A", "6B", "Cooking Tip", "🍳",
     '"To prepare this dish, gather all necessary ingredients. Combine the specified components in the appropriate cooking vessel. Apply heat at the recommended temperature and stir at regular intervals to ensure uniform cooking."',
     '"Okay so the SECRET is — don\'t stir the dal for the first 5 minutes. Let it sit, get a tiny bit crispy on the bottom. THAT\'S where all the flavour lives. My nanu taught me this."',
     "Clue: family attribution & personality = Human"),

    ("7A", "7B", "Describing a Friend", "🤝",
     '"Rafi shows up 45 minutes late to everything. But when you actually need him — 3am, flat tyre on the highway — he\'s the first one there. No questions asked. That\'s the whole person."',
     '"My friend is a kind and reliable individual who possesses many admirable qualities. They are always willing to help others and demonstrate a strong sense of loyalty and positivity."',
     "Clue: specific scenario = Human; vague adjectives = AI"),

    ("8A", "8B", "Travel Experience", "✈️",
     '"Cox\'s Bazar is a renowned tourist destination featuring an extensive coastline. Visitors can enjoy various recreational activities and experience the natural beauty of the scenic environment."',
     '"Arrived in Cox\'s Bazar completely exhausted — but the sea just... fixed everything. Ate some chips on the beach and watched the sun do its thing. That was the perfect day."',
     "Clue: 'chips on the beach' — mundane specifics = Human"),

    ("9A", "9B", "University Life", "🎓",
     '"University life presents students with numerous opportunities for academic and personal growth. Students are encouraged to engage with extracurricular activities and form meaningful relationships with peers."',
     '"First week of uni I was absolutely convinced I was in the wrong major. Cried twice. By week three I\'d found my people and completely forgot what I was even worried about."',
     "Clue: 'Cried twice' — specific & vulnerable = Human"),

    ("10A", "10B", "About AI", "🤖",
     '"I asked ChatGPT to write a poem about my cat. It wrote 16 lines about \'feline companions\'. My cat has a specific grudge against Tuesdays. It missed the point entirely."',
     '"Artificial intelligence is a rapidly evolving field transforming human society. AI systems process large amounts of data and perform complex tasks efficiently. It is important to develop AI responsibly for the benefit of humanity."',
     "Clue: absurd specifics ('Tuesdays') = Human"),
]

# ── Build question cards HTML ─────────────────────────────────────────────────
q_cards_html = '\n<div class="section-label page-break" id="tlabel">Text Cards — Human or AI Writing? (10 pairs × 2 = 20 cards)</div>\n<div class="cards-grid" id="tgrid">\n'
a_cards_html = '\n<div class="section-label page-break" id="talabel">Text Answer Cards (10 cards)</div>\n<div class="cards-grid" id="tagrid">\n'

for i, (a_id, b_id, topic, emoji, human_text, ai_text, hint) in enumerate(PAIRS, 1):
    # Card A layout alternates: some pairs have A=Human, some A=AI
    # For pairs 1,4,7,10 → A=Human; rest → A=AI
    if i in (1, 4, 7, 10):
        card_a_text, card_a_label = human_text, "Human"
        card_b_text, card_b_label = ai_text, "AI"
        ans_a_badge, ans_b_badge = "ta-b-human", "ta-b-ai"
        ans_a_txt, ans_b_txt = "🧑 Human", "🤖 AI"
    else:
        card_a_text, card_a_label = ai_text, "AI"
        card_b_text, card_b_label = human_text, "Human"
        ans_a_badge, ans_b_badge = "ta-b-ai", "ta-b-human"
        ans_a_txt, ans_b_txt = "🤖 AI", "🧑 Human"

    q_cards_html += qcard(a_id, topic, emoji, card_a_text)
    q_cards_html += qcard(b_id, topic, emoji, card_b_text)

    # Snippets (first 60 chars)
    snip_a = card_a_text[:65].rstrip() + "..."
    snip_b = card_b_text[:65].rstrip() + "..."

    a_cards_html += acard(
        i, topic, emoji,
        f"#T{a_id}", ans_a_badge, ans_a_txt, snip_a,
        f"#T{b_id}", ans_b_badge, ans_b_txt, snip_b,
        hint
    )

q_cards_html += '\n</div><!-- end tgrid -->\n'
a_cards_html += '\n</div><!-- end tagrid -->\n'

# ── Rebuild the print-controls / script with updated IDs ─────────────────────
CLOSING = """
<!-- print controls -->
<div class="print-controls">
  <button class="print-btn" onclick="window.print()" id="btn-all">&#128424; Print All</button>
  <button class="print-btn sec" onclick="printOnly('q')" id="btn-q">&#128203; Questions Only</button>
  <button class="print-btn sec" onclick="printOnly('a')" id="btn-a">&#10003; Answers Only</button>
</div>
<script>
function printOnly(type) {
  var qIds = ['qgrid','tgrid','qlabel','tlabel'];
  var aIds = ['agrid','tagrid','alabel','talabel'];
  var hide = type === 'q' ? aIds : qIds;
  hide.forEach(function(id){ var e=document.getElementById(id); if(e) e.style.display='none'; });
  window.print();
  setTimeout(function() {
    qIds.concat(aIds).forEach(function(id){ var e=document.getElementById(id); if(e) e.style.display=''; });
  }, 800);
}
</script>
</body>
</html>
"""

# ── Read & patch the existing HTML ───────────────────────────────────────────
with open("cue_cards.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Inject extra CSS before </style>
html = html.replace("</style>", EXTRA_CSS + "\n</style>", 1)

# 2. Find where the old print-controls block starts and cut everything after it
cut = html.find("<!-- print controls -->")
html = html[:cut]

# 3. Append new sections + closing
html = html + q_cards_html + a_cards_html + CLOSING

with open("cue_cards.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Done! File size: {len(html):,} bytes")
