# app.py — Daily Grace Affirmations
# v4.0.4 — Logo Harmony Fix + Local Fallback + Stable Raw URL

import streamlit as st
import random
import json
import base64
import resend
import re
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

# -----------------------------
# 🌸 Logo: prefer local asset, fallback to stable raw URL
# -----------------------------
APP_DIR = Path(__file__).resolve().parent
LOGO_LOCAL = APP_DIR / "Bythandi Logo.png"
LOGO_REMOTE = "https://raw.githubusercontent.com/bythandi/daily-grace-affirmations/main/Bythandi%20Logo.png"

def _logo_source() -> str | None:
    """Prefer local file for reliability (works offline and avoids GitHub rate limits)."""
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

st.write("👋 App is running — loading affirmations...")

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
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
    import io, requests

    # Brand colors
    COL_BG_CREAM   = HexColor("#fff1ea")
    COL_DEEP_BLUE  = HexColor("#152d69")
    COL_ORANGE     = HexColor("#f7931e")
    COL_BROWN      = HexColor("#521305")
    COL_CARD_FILL  = HexColor("#ffe6c0")
    COL_TEXT_MUTED = HexColor("#666666")

    # Try to load logo
    _logo_reader = None
    if logo_url:
        try:
            if str(logo_url).startswith(("http://", "https://")):
                r = requests.get(logo_url, timeout=6)
                r.raise_for_status()
                _logo_reader = ImageReader(io.BytesIO(r.content))
            else:
                p = Path(logo_url)
                if p.exists():
                    _logo_reader = ImageReader(str(p))
        except Exception:
            _logo_reader = None

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    W, H = letter
    margin = 18 * mm
    inner_w = W - 2 * margin

    def draw_logo():
        if not _logo_reader:
            return
        try:
            img_w, img_h = _logo_reader.getSize()
            scale = min((40 * mm) / img_w, (16 * mm) / img_h)
            c.drawImage(_logo_reader, W - (50 * mm), H - (22 * mm),
                        width=img_w * scale, height=img_h * scale, preserveAspectRatio=True)
        except Exception:
            pass

    # Header + Footer
    def header(date_str=None):
        c.setFillColor(COL_BG_CREAM)
        c.rect(0, H - 28 * mm, W, 28 * mm, stroke=0, fill=1)
        c.setFillColor(COL_DEEP_BLUE)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, H - 15 * mm, "Daily Grace Affirmations")
        if date_str:
            c.setFont("Helvetica", 10)
            c.setFillColor(COL_TEXT_MUTED)
            c.drawString(margin, H - 20 * mm, date_str)
        draw_logo()

    def footer():
        c.setFillColor(COL_TEXT_MUTED)
        c.setFont("Helvetica-Oblique", 9)
        c.drawRightString(W - margin, margin - 2, "Daily Grace Affirmations • bythandi.com")

    # Render
    header(datetime.now().strftime("%Y-%m-%d %H:%M"))
    footer()
    y = H - 40 * mm

    for i, entry in enumerate(session_entries, 1):
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(COL_BROWN)
        c.drawString(margin, y, f"{i}. {entry.get('text','')}")
        y -= 12
        c.setFont("Helvetica", 10)
        c.setFillColor(COL_DEEP_BLUE)
        meta = f"{entry.get('category')} • {entry.get('alignment')} • {entry.get('date')}"
        c.drawString(margin, y, meta)
        y -= 12
        c.setFillColor(COL_BROWN)
        reflection_lines = entry.get("reflection", "").split("\n") or ["—"]
        for line in reflection_lines:
            c.drawString(margin, y, line)
            y -= 12
        y -= 10
    c.save()
    buf.seek(0)
    return buf


# -----------------------------
# 📧 Email Delivery via Resend
# -----------------------------
def _get_secret(name: str, default: str = "") -> str:
    try:
        return st.secrets.get(name, default)
    except Exception:
        import os
        return os.getenv(name, default)

RESEND_API_KEY = _get_secret("RESEND_API_KEY")
FROM_EMAIL = _get_secret("FROM_EMAIL", "affirmations@your-verified-domain.com")

def _validate_email(addr: str) -> bool:
    pat = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return bool(re.match(pat, addr or ""))

def send_affirmation_email_via_resend(to_email: str, pdf_buffer: BytesIO, affirmation_text: str) -> dict:
    if not RESEND_API_KEY:
        return {"ok": False, "error": "Missing RESEND_API_KEY"}
    if not FROM_EMAIL or "@" not in FROM_EMAIL:
        return {"ok": False, "error": "Missing or invalid FROM_EMAIL"}
    try:
        resend.api_key = RESEND_API_KEY
        pdf_buffer.seek(0)
        b64_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")
        html = f"""
        <div style="font-family: Arial, sans-serif; color:#521305; background:#fff1ea; padding:24px">
          <div style="max-width:640px;margin:0 auto;background:#fff;border-radius:12px;padding:28px">
            <h1 style="color:#152d69;text-align:center;margin-top:0">🌿 Daily Grace Affirmations</h1>
            <p>Here is your affirmation PDF for today.</p>
            <div style="background:#ffe6c0;border-left:4px solid #f7931e;padding:14px 16px;margin:20px 0">
              <em>"{affirmation_text}"</em>
            </div>
            <p style="color:#666">May this guide your day with peace and clarity.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:28px 0">
            <p style="text-align:center;font-size:12px;color:#999">
              🌸 ByThandi — Daily Grace Affirmations<br>
              <a href="https://bythandi.com" style="color:#f7931e">bythandi.com</a>
            </p>
          </div>
        </div>
        """.strip()
        resp = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": "🌿 Your Daily Grace Affirmation PDF",
            "html": html,
            "attachments": [{
                "filename": f"affirmation_{datetime.now().strftime('%Y%m%d')}.pdf",
                "content": b64_pdf,
            }],
        })
        return {"ok": True, "data": resp}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# -----------------------------
# 💾 Save / Email Affirmation
# -----------------------------
st.markdown("---")
st.markdown("### 📧 Receive Your Affirmation")

delivery_method = st.radio(
    "Choose how you'd like to receive your personalized PDF:",
    ["📥 Download PDF", "📧 Email me the PDF"],
    index=0
)

user_email = None
if delivery_method == "📧 Email me the PDF":
    user_email = st.text_input("✉️ Your email address (for this one PDF):", placeholder="your@email.com")
    st.caption("_We’ll only use your email to send this PDF. No mailing list, no marketing._")

cta_label = "📧 Save & Email My Affirmation" if delivery_method == "📧 Email me the PDF" else "💾 Save & Get New Affirmation"

if st.button(cta_label) and affirmation:
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

    single_pdf = create_session_pdf([log_entry], logo_url=_logo_source(), category_display=CATEGORY_DISPLAY)

    if delivery_method == "📧 Email me the PDF":
        if not user_email or not _validate_email(user_email):
            st.error("⚠️ Please enter a valid email address.")
            st.stop()
        with st.spinner("📧 Sending your affirmation..."):
            result = send_affirmation_email_via_resend(user_email, single_pdf, affirmation["text"])
        if result.get("ok"):
            st.success(f"✅ Sent to {user_email}. Check your inbox!")
        else:
            st.error("❌ Could not send email.")
            st.info("💡 You can still download the PDF below.")
    else:
        st.success("🗂️ Saved to your affirmation log.")

    new_affirmation = random.choice(filtered_affirmations)
    while new_affirmation.get("id") == affirmation.get("id") and len(filtered_affirmations) > 1:
        new_affirmation = random.choice(filtered_affirmations)

    st.session_state.selected_affirmation = new_affirmation
    st.session_state.last_affirmation_id = new_affirmation.get("id") if new_affirmation else None
    st.rerun()


# -----------------------------
# 🔀 Shuffle Deck
# -----------------------------
if st.button("🔀 Shuffle Deck (optional)"):
    random.shuffle(st.session_state.deck)
    st.success("Deck reshuffled — new grace flow ready!")
    st.rerun()


# -----------------------------
# 📄 Download Full Session
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
    "🌸 ByThandi — Daily Grace Affirmations — v4.0.4 *Grace Wheels IV — Logo Harmony Fix*  \n🔗 [bythandi.com](https://bythandi.com)"
)
