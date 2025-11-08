import streamlit as st
import random
import json
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- Page setup ---
st.set_page_config(page_title="🌸 Divine Systems Daily Affirmation", layout="centered")

# --- Initialize session variables ---
if "session_entries" not in st.session_state:
    st.session_state.session_entries = []
if "deck" not in st.session_state:
    st.session_state.deck = []
if "last_affirmation_id" not in st.session_state:
    st.session_state.last_affirmation_id = None
if "selected_affirmation" not in st.session_state:
    st.session_state.selected_affirmation = None

# --- Safety check & load affirmation bank ---
st.write("👋 App is running — loading affirmations...")

try:
    with open("affirmation_bank.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        affirmations = data.get("affirmations", [])
except Exception as e:
    st.error(f"⚠️ Could not load affirmation_bank.json: {e}")
    affirmations = [{"text": "Affirmation data not loaded.", "category": "Error"}]

# --- Friendly display names (UI only) ---
CATEGORY_DISPLAY = {
    "Create": "Create Flow",
    "Build": "Build Discipline",
    "Believe": "Believe Again",
    "Weave": "Weave Wholeness"
}

# --- Filter affirmations to 4 canon categories only ---
affirmations = [a for a in affirmations if a.get("category") in CATEGORY_DISPLAY.keys()]

# --- Initialize deck once per app run ---
if not st.session_state.deck:
    st.session_state.deck = affirmations.copy()
    random.shuffle(st.session_state.deck)

# --- Custom CSS (Fonts, Colours, Layout) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@500;700&family=Roboto:wght@400;500&display=swap');

        body {
            background-color: #fff1ea;
            font-family: 'Roboto', sans-serif;
            color: #521305;
        }

        h1, h2, h3, h4, h5, h6, .main-title, .sub-title, .align-title {
            font-family: 'Raleway', sans-serif;
            letter-spacing: 0.3px;
        }

        .main-title {
            background-color: #152d69;
            color: white;
            padding: 0.8rem;
            border-radius: 12px;
            text-align: center;
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .sub-title {
            background-color: #f7931e;
            color: #521305;
            padding: 0.6rem;
            border-radius: 8px;
            text-align: center;
            font-size: 1.3rem;
            font-weight: 600;
        }

        /* 🧡 Affirmation highlight box */
        .affirmation-box {
            background-color: rgba(247,147,30,0.15);
            border: 2px solid #f7931e;
            border-radius: 16px;
            padding: 1.2rem;
            margin-top: 1rem;
            box-shadow: 0px 3px 8px rgba(21,45,105,0.1);
            font-family: 'Roboto', sans-serif;
            font-size: 1.2rem;
            line-height: 1.6;
        }

        .align-box {
            background-color: transparent;
            border: none;
            padding: 0;
            margin-top: 30px;
            margin-bottom: 25px;
        }

        .align-title {
            color: #152d69;
            background-color: #ffe6c0; /* gentle cream */
            padding: 8px 16px;
            border-radius: 8px;
            text-align: center;
            font-weight: 700;
            font-family: 'Raleway', sans-serif;
        }

        textarea, input, .stTextInput, .stTextArea {
            font-family: 'Roboto', sans-serif !important;
            background-color: #ffffff !important;
        }

        /* Grace Wheels Patch — remove yellow padding */
        [data-testid="stVerticalBlock"] div[data-testid="stBlock"] > div:first-child {
            background-color: transparent !important;
            padding: 0 !important;
            border: none !important;
        }

        div.stRadio > div {
            margin-top: 0.3rem !important;
            margin-bottom: 0.3rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<div class='main-title'>🌸 Divine Systems Daily Affirmation</div>", unsafe_allow_html=True)

# --- Category selection ---
display_options = ["All"] + list(CATEGORY_DISPLAY.values())
selected_display = st.selectbox("🌸 Explore a Pillar of Truth", display_options, index=0)

if selected_display == "All":
    filtered_affirmations = st.session_state.deck
else:
    internal_category = next(k for k, v in CATEGORY_DISPLAY.items() if v == selected_display)
    filtered_affirmations = [a for a in st.session_state.deck if a["category"] == internal_category]

st.markdown("---")

# --- Choose affirmation (stable between reruns) ---
if st.session_state.selected_affirmation is None:
    st.session_state.selected_affirmation = random.choice(filtered_affirmations)
    st.session_state.last_affirmation_id = st.session_state.selected_affirmation["id"]

affirmation = st.session_state.selected_affirmation

# --- Display affirmation section ---
st.markdown("<div class='sub-title'>✨ Today's Affirmation</div>", unsafe_allow_html=True)
st.markdown(f"<div class='affirmation-box'>📖 {affirmation['text']}</div>", unsafe_allow_html=True)

display_category = CATEGORY_DISPLAY.get(affirmation["category"], affirmation["category"])
st.write(f"🏷️ **Category:** {display_category}")

# --- Reflection / Alignment section ---
st.markdown("<div class='align-box'>", unsafe_allow_html=True)
st.markdown("<h3 class='align-title'>✨ How aligned do you feel today?</h3>", unsafe_allow_html=True)

alignment = st.radio("", ["Aligned 🌿", "Integrating 🌸", "Unaligned 🌧️"], horizontal=False)
reflection = st.text_area("🪶 Reflection (optional):", placeholder="Write your thoughts here...")

st.markdown("</div>", unsafe_allow_html=True)

# --- Save and refresh ---
if st.button("💾 Save & Get New Affirmation"):
    log_entry = {
        "text": affirmation["text"],
        "category": affirmation.get("category", ""),
        "alignment": alignment,
        "reflection": reflection,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    st.session_state.session_entries.append(log_entry)

    with open("affirmation_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    st.success("🗂️ Saved to your affirmation log.")

    new_affirmation = random.choice(filtered_affirmations)
    while new_affirmation["id"] == affirmation["id"] and len(filtered_affirmations) > 1:
        new_affirmation = random.choice(filtered_affirmations)

    st.session_state.selected_affirmation = new_affirmation
    st.session_state.last_affirmation_id = new_affirmation["id"]
    st.rerun()

# --- Manual Shuffle Deck (optional) ---
if st.button("🔀 Shuffle Deck (optional)"):
    random.shuffle(st.session_state.deck)
    st.success("Deck reshuffled — new divine flow ready!")
    st.rerun()

# --- PDF generation helper ---
def create_session_pdf(session_entries):
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor

    # --- Brand palette ---
    COL_BG_CREAM   = HexColor("#fff1ea")
    COL_DEEP_BLUE  = HexColor("#152d69")
    COL_ORANGE     = HexColor("#f7931e")
    COL_BROWN      = HexColor("#521305")
    COL_CARD_FILL  = HexColor("#ffe6c0")
    COL_TEXT_MUTED = HexColor("#666666")

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    W, H = letter

    margin = 18 * mm
    inner_w = W - 2 * margin

    # --- helpers -------------------------------------------------------------
    def header(page_dt_str=None):
        # cream page background band at top
        c.setFillColor(COL_BG_CREAM)
        c.rect(0, H - 28*mm, W, 28*mm, stroke=0, fill=1)

        # title
        c.setFillColor(COL_DEEP_BLUE)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, H - 15*mm, "Divine Systems – Daily Affirmation")

        # datestamp / muted
        c.setFont("Helvetica", 10)
        c.setFillColor(COL_TEXT_MUTED)
        if page_dt_str:
            c.drawString(margin, H - 20*mm, page_dt_str)

        # thin orange accent line
        c.setStrokeColor(COL_ORANGE)
        c.setLineWidth(2)
        c.line(margin, H - 22*mm, W - margin, H - 22*mm)

    def footer():
        c.setStrokeColor(COL_BG_CREAM)
        c.setLineWidth(14)
        c.line(0, margin - 6, W, margin - 6)

        c.setFillColor(COL_TEXT_MUTED)
        c.setFont("Helvetica-Oblique", 9)
        c.drawRightString(W - margin, margin - 2, "Divine Systems • bythandi.com")

    def wrap_text(text, max_width, font_name="Helvetica", font_size=10):
        """Simple word-wrap using ReportLab width metrics."""
        if not text:
            return ["—"]
        words = text.split()
        lines, line = [], ""
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, font_name, font_size) <= max_width:
                line = test
            else:
                lines.append(line or w)
                line = w
        if line:
            lines.append(line)
        return lines

    def new_page(include_dt=False):
        c.showPage()
        header(datetime.now().strftime("%Y-%m-%d %H:%M") if include_dt else None)
        footer()
        return H - 30*mm  # reset y below header

    # ------------------------------------------------------------------------
    # first page header/footer
    header(datetime.now().strftime("%Y-%m-%d %H:%M"))
    footer()

    y = H - 32*mm

    # Summary block
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(COL_BROWN)
    c.drawString(margin, y, f"Session Summary")
    y -= 6*mm
    c.setFillColor(COL_TEXT_MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Total entries: {len(session_entries)}")
    y -= 6*mm

    # divider
    c.setStrokeColor(COL_BG_CREAM)
    c.setLineWidth(3)
    c.line(margin, y, W - margin, y)
    y -= 4*mm

    # Entry cards
    card_pad = 6 * mm
    min_y = margin + 20  # keep footer area clear

    for i, entry in enumerate(session_entries, 1):
        # compute card height dynamically (wrap reflection)
        title_text = f"{i}. {entry.get('text','')}"
        reflection = entry.get('reflection', '')
        category = entry.get('category', '')
        alignment = entry.get('alignment', '')
        date_str = entry.get('date', '')

        # metrics
        c.setFont("Helvetica-Bold", 12)
        title_height = 5*mm + 12  # rough line height

        c.setFont("Helvetica", 10)
        meta_height = 5*mm + 10

        # available text width inside card
        inner_text_w = inner_w - 2*card_pad

        # wrap reflection
        refl_lines = wrap_text(reflection, inner_text_w, "Helvetica", 10)
        refl_height = (len(refl_lines) * 12) + 2*mm

        # total card height
        card_h = card_pad + title_height + 2*mm + meta_height + 2*mm + 10 + refl_height + card_pad

        # page break if needed
        if y - card_h < min_y:
            y = new_page(include_dt=True)

        # card background
        c.setFillColor(COL_CARD_FILL)
        c.setStrokeColor(COL_ORANGE)
        c.setLineWidth(1.5)
        c.roundRect(margin, y - card_h, inner_w, card_h, 6, stroke=1, fill=1)

        # content inside card
        cx = margin + card_pad
        cy = y - card_pad

        # title
        c.setFillColor(COL_BROWN)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(cx, cy - 12, title_text)
        cy -= title_height

        # meta row (category • alignment • date)
        c.setFont("Helvetica", 10)
        c.setFillColor(COL_DEEP_BLUE)
        # Use external map if available
        try:
            display_cat = CATEGORY_DISPLAY.get(category, category)
        except Exception:
            display_cat = category
        meta = f"{display_cat}  •  {alignment}  •  {date_str}"
        c.drawString(cx, cy - 10, meta)
        cy -= meta_height

        # small divider
        c.setStrokeColor(COL_ORANGE)
        c.setLineWidth(0.6)
        c.line(cx, cy, margin + inner_w - card_pad, cy)
        cy -= 6

        # reflection label
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(COL_BROWN)
        c.drawString(cx, cy, "Reflection")
        cy -= 12

        # reflection body (wrapped)
        c.setFont("Helvetica", 10)
        c.setFillColor(COL_BROWN)
        for line in refl_lines:
            c.drawString(cx, cy, line)
            cy -= 12

        # move to next card
        y -= (card_h + 4*mm)

    c.save()
    buf.seek(0)
    return buf

# --- PDF download section ---
if st.session_state.session_entries:
    st.markdown("### 💾 Download your full session")
    pdf_buffer = create_session_pdf(st.session_state.session_entries)
    st.download_button(
        label="📄 Download Full Session (.pdf)",
        data=pdf_buffer,
        file_name=f"affirmation_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )
else:
    st.info("💡 Save at least one affirmation to enable PDF download.")

st.markdown("---")
st.write("🌸 ByThandi Divine Systems — v3.4.5 “Grace Wheels Patch”")

