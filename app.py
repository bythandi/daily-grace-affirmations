# app.py — Daily Grace Affirmations
# v3.8 — Grace Wheels II “The Paper Bloom” (No Email Version)

import streamlit as st
import random
import json
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import requests
import io

# -----------------------------
# 🌸 Logo: prefer local asset, fallback to stable raw URL
# -----------------------------
APP_DIR = Path(__file__).resolve().parent
LOGO_LOCAL = APP_DIR / "Bythandi Logo.png"
LOGO_REMOTE = "https://raw.githubusercontent.com/bythandi/daily-grace-affirmations/main/Bythandi%20Logo.png"

def _logo_source() -> str | None:
    try:
        if LOGO_LOCAL.exists():
            return str(LOGO_LOCAL)
        return LOGO_REMOTE
    except Exception:
        return None


# -----------------------------
# 🌿 Page setup
# -----------------------------
st.set_page_config(page_title="🌿 Daily Grace Affirmations", layout="centered")

# --- Logo section (centered) ---
logo_src = _logo_source()
if logo_src:
    st.markdown(
        f"""
        <div style="
            display:flex;
            justify-content:center;
            align-items:center;
            margin-bottom:-40px;
            padding-top:10px;
        ">
            <img src="{logo_src}" width="120" alt="ByThandi logo">
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# 💾 Session State Initialization
# -----------------------------
if "session_entries" not in st.session_state:
    st.session_state.session_entries = []
if "deck" not in st.session_state:
    st.session_state.deck = []
if "last_affirmation_id" not in st.session_state:
    st.session_state.last_affirmation_id = None
if "selected_affirmation" not in st.session_state:
    st.session_state.selected_affirmation = None

# --- Load affirmation bank ---
try:
    with open("affirmation_bank.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        affirmations = data.get("affirmations", [])
except Exception as e:
    st.error(f"⚠️ Could not load affirmation_bank.json: {e}")
    affirmations = [{"text": "Affirmation data not loaded.", "category": "Error"}]

# -----------------------------
# ✨ Display Categories
# -----------------------------
CATEGORY_DISPLAY = {
    "Create": "Create Flow",
    "Build": "Build Discipline",
    "Believe": "Believe Again",
    "Weave": "Weave Wholeness"
}

affirmations = [a for a in affirmations if a.get("category") in CATEGORY_DISPLAY.keys()]

if not st.session_state.deck:
    st.session_state.deck = affirmations.copy()
    random.shuffle(st.session_state.deck)


# -----------------------------
# 🎨 Custom CSS Styling
# -----------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@500;700&family=Roboto:wght@400;500&display=swap');

        body {
            background-color: #fff1ea;
            font-family: 'Roboto', sans-serif;
            color: #521305;
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

        .affirmation-box {
            background-color: rgba(247,147,30,0.15);
            border: 2px solid #f7931e;
            border-radius: 16px;
            padding: 1.2rem;
            margin-top: 1rem;
            box-shadow: 0px 3px 8px rgba(21,45,105,0.1);
            font-size: 1.2rem;
            line-height: 1.6;
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
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# 🌸 Header
# -----------------------------
st.markdown("<div class='main-title'>🌿 Daily Grace Affirmations</div>", unsafe_allow_html=True)
st.caption("_A ByThandi Creation_")

# -----------------------------
# 🧭 Category selection
# -----------------------------
display_options = ["All"] + list(CATEGORY_DISPLAY.values())
selected_display = st.selectbox("🌸 Explore a Pillar of Truth", display_options, index=0)

if selected_display == "All":
    filtered_affirmations = st.session_state.deck
else:
    internal_category = next(k for k, v in CATEGORY_DISPLAY.items() if v == selected_display)
    filtered_affirmations = [a for a in st.session_state.deck if a["category"] == internal_category]

st.markdown("---")

# -----------------------------
# 💬 Select and show affirmation
# -----------------------------
if st.session_state.selected_affirmation is None and filtered_affirmations:
    st.session_state.selected_affirmation = random.choice(filtered_affirmations)
    st.session_state.last_affirmation_id = st.session_state.selected_affirmation.get("id")

affirmation = st.session_state.selected_affirmation

if affirmation:
    st.markdown("<div class='sub-title'>✨ Today's Affirmation</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='affirmation-box'>📖 {affirmation['text']}</div>", unsafe_allow_html=True)
    display_category = CATEGORY_DISPLAY.get(affirmation["category"], affirmation["category"])
    st.write(f"🏷️ **Category:** {display_category}")
else:
    st.warning("No affirmations available. Please check your affirmation bank.")

# -----------------------------
# 🪶 Reflection section
# -----------------------------
st.markdown("<h3 class='align-title'>✨ How aligned do you feel today?</h3>", unsafe_allow_html=True)
alignment = st.radio(
    "Alignment",
    ["Aligned 🌿", "Integrating 🌸", "Unaligned 🌧️"],
    label_visibility="collapsed"
)
reflection = st.text_area("🪶 Reflection (optional):", placeholder="Write your thoughts here...")

# -----------------------------
# 📄 PDF Generation Helper
# -----------------------------
def create_session_pdf(session_entries, logo_url=None, category_display=None):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    W, H = letter
    margin = 40
    y = H - margin

    # brand colours
    COL_BROWN = HexColor("#521305")
    COL_ORANGE = HexColor("#f7931e")

    # Try logo
    _logo_reader = None
    if logo_url:
        try:
            if logo_url.startswith("http"):
                r = requests.get(logo_url, timeout=5)
                _logo_reader = ImageReader(io.BytesIO(r.content))
            else:
                p = Path(logo_url)
                if p.exists():
                    _logo_reader = ImageReader(str(p))
        except Exception:
            _logo_reader = None

    # header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(COL_BROWN)
    c.drawString(margin, y, "Daily Grace Affirmations")
    if _logo_reader:
        c.drawImage(_logo_reader, W - 120, H - 90, width=70, height=70, preserveAspectRatio=True)
    y -= 40

    for i, entry in enumerate(session_entries, 1):
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(COL_BROWN)
        c.drawString(margin, y, f"{i}. {entry.get('text', '')}")
        y -= 16
        c.setFont("Helvetica", 10)
        c.setFillColor(COL_ORANGE)
        cat = entry.get("category", "")
        align = entry.get("alignment", "")
        date = entry.get("date", "")
        c.drawString(margin, y, f"{cat} • {align} • {date}")
        y -= 14
        c.setFillColor(COL_BROWN)
        reflection = entry.get("reflection", "")
        for line in reflection.splitlines() or ["—"]:
            c.drawString(margin, y, line)
            y -= 12
        y -= 10
        if y < 100:
            c.showPage()
            y = H - margin

    c.save()
    buf.seek(0)
    return buf

# -----------------------------
# 💾 Save and Get New
# -----------------------------
if st.button("💾 Save & Get New Affirmation") and affirmation:
    log_entry = {
        "text": affirmation["text"],
        "category": affirmation.get("category", ""),
        "alignment": alignment,
        "reflection": reflection,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.session_entries.append(log_entry)

    try:
        with open("affirmation_log.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    new_affirmation = random.choice(filtered_affirmations)
    while new_affirmation.get("id") == affirmation.get("id") and len(filtered_affirmations) > 1:
        new_affirmation = random.choice(filtered_affirmations)

    st.session_state.selected_affirmation = new_affirmation
    st.session_state.last_affirmation_id = new_affirmation.get("id")
    st.rerun()

# -----------------------------
# 📄 Download Session PDF
# -----------------------------
if st.session_state.session_entries:
    st.markdown("### 💾 Download your full session")
    pdf_buffer = create_session_pdf(st.session_state.session_entries, logo_url=_logo_source(), category_display=CATEGORY_DISPLAY)
    st.download_button(
        label="📄 Download Full Session (.pdf)",
        data=pdf_buffer,
        file_name=f"affirmation_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )
else:
    st.info("💡 Save at least one affirmation to enable PDF download.")

# -----------------------------
# 🌸 Footer
# -----------------------------
st.markdown(
    "🌸 ByThandi — Daily Grace Affirmations — v3.8.0 *Grace Wheels II — The Paper Bloom*  \n🔗 [bythandi.com](https://bythandi.com)"
)
