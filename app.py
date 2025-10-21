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

# --- Load affirmation bank ---
st.write("👋 App is running — loading affirmations...")

try:
    with open("affirmation_bank.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        affirmations = data.get("affirmations", [])
except Exception as e:
    st.error(f"⚠️ Could not load affirmation_bank.json: {e}")
    affirmations = [{"text": "Affirmation data not loaded.", "category": "Error"}]

# --- Category display mapping ---
CATEGORY_DISPLAY = {
    "Create": "Create Flow",
    "Build": "Build Discipline",
    "Believe": "Believe Again",
    "Weave": "Weave Wholeness"
}

# --- Filter to canonical categories ---
affirmations = [a for a in affirmations if a.get("category") in CATEGORY_DISPLAY.keys()]

# --- Initialize shuffled deck ---
if not st.session_state.deck:
    st.session_state.deck = affirmations.copy()
    random.shuffle(st.session_state.deck)

# --- Custom CSS ---
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
        }

        .main-title {
            background-color: #152d69;
            color: white;
            padding: 0.8rem;
            border-radius: 12px;
            text-align: center;
            font-size: 1.8rem;
            font-weight: 700;
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

        .align-box {
            background-color: transparent;
            border: none;
            padding: 0;
            margin-top: 30px;
            margin-bottom: 25px;
        }

        .align-title {
            color: #152d69;
            background-color: #ffe6c0;
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

# --- Choose affirmation ---
if st.session_state.selected_affirmation is None:
    st.session_state.selected_affirmation = random.choice(filtered_affirmations)
    st.session_state.last_affirmation_id = st.session_state.selected_affirmation["id"]

affirmation = st.session_state.selected_affirmation

# --- Alignment & reflection inputs ---
alignment = st.radio("", ["Aligned 🌿", "Integrating 🌸", "Unaligned 🌧️"], horizontal=False)
reflection = st.text_area("🪶 Reflection (optional):", placeholder="Write your thoughts here...")

# --- Emoji map ---
category_emojis = {
    "Create Flow": "🪷",
    "Build Discipline": "💪🏾",
    "Believe Again": "✝️",
    "Weave Wholeness": "🧵"
}
display_category = CATEGORY_DISPLAY.get(affirmation["category"], affirmation["category"])
emoji = category_emojis.get(display_category, "🌸")

# --- Affirmation card ---
affirmation_html = f"""
<div style='background-color:#ffffff; border-radius:20px; padding:1.5rem;
            box-shadow:0px 3px 8px rgba(21,45,105,0.1); margin-top:1.5rem;'>
    <h3 style='color:#152d69; font-family:Raleway, sans-serif; font-size:1.4rem;'>
        <b>{emoji} {affirmation['text']}</b>
    </h3>
    <p style='margin:0.4rem 0; font-size:1rem; color:#521305;'>
        🏷️ <b>{display_category}</b>
    </p>
    <p style='margin:0.2rem 0; font-size:1rem;'>✅ integrating</p>
    <div style='background-color:#fff1ea; border-left:4px solid #f7931e;
                padding:0.8rem 1rem; border-radius:8px; margin-top:0.6rem;'>
        <p style='margin:0; color:#521305;'><b>🪶 Reflection:</b><br>
        {reflection if reflection else "I will do so going forward, this is something I need to work on."}</p>
    </div>
</div>
"""
st.markdown(affirmation_html, unsafe_allow_html=True)

# --- Save + new affirmation ---
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

# --- Shuffle option ---
if st.button("🔀 Shuffle Deck (optional)"):
    random.shuffle(st.session_state.deck)
    st.success("Deck reshuffled — new divine flow ready!")
    st.rerun()

# --- PDF generator ---
def create_session_pdf(session_entries):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 80

    # Consistent header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.08, 0.18, 0.41)  # ByThandi Blue
    c.drawString(72, y, "🌸 Divine Systems Daily Affirmation")
    y -= 50

    c.setFillColorRGB(0, 0, 0)
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
            c.setFont("Helvetica-Bold", 18)
            c.setFillColorRGB(0.08, 0.18, 0.41)
            c.drawString(72, y, "🌸 Divine Systems Daily Affirmation")
            y -= 50
            c.setFillColorRGB(0, 0, 0)

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
st.write("🌸 ByThandi Divine Systems — v3.6 “Header Harmony Patch”")
