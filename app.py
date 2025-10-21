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
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 80

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "🌸 Divine Systems Daily Affirmation Session")
    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(72, y, f"Total entries: {len(session_entries)}")
    y -= 30

    for i, entry in enumerate(session_entries, 1):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, f"{i}. ✨ {entry['text'][:70]}...")
        y -= 20

        c.setFont("Helvetica", 11)
        c.drawString(72, y, f"🏷️ {CATEGORY_DISPLAY.get(entry['category'], entry['category'])}")
        y -= 15
        c.drawString(72, y, f"🌿 {entry['alignment']}")
        y -= 15

        c.drawString(72, y, "🪶 Reflection:")
        y -= 15
        text = c.beginText(90, y)
        text.setFont("Helvetica", 10)
        text.textLines(entry['reflection'] if entry['reflection'] else "—")
        c.drawText(text)
        y -= 80

        if y < 100:
            c.showPage()
            y = height - 80

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

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

