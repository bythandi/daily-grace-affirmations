# app.py — Daily Grace Affirmations (with Resend transactional email)

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

# --- Toggleable logo (set to None to disable) ---
LOGO_URL = "https://github.com/bythandi/divine-systems-dashboard/blob/main/Bythandi%20Logo.png?raw=true"
# LOGO_URL = None  # <- uncomment this line to disable the logo quickly

# --- Page setup ---
st.set_page_config(page_title="🌿 Daily Grace Affirmations", layout="centered")

# --- Logo section (centered) ---
if LOGO_URL:
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: -40px;
            padding-top: 10px;
        ">
            <img src="{LOGO_URL}" width="120">
        </div>
        """,
        unsafe_allow_html=True,
    )

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
st.markdown("<div class='main-title'>🌿 Daily Grace Affirmations</div>", unsafe_allow_html=True)
st.caption("_A ByThandi Creation_")

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

# -----------------------------
# Resend (transactional email)
# -----------------------------
def _get_secret(name: str, default: str = "") -> str:
    """Prefer Streamlit secrets; fall back to env vars."""
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
    """Transactional-only email via Resend with base64 PDF attachment."""
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
            <p style="font-size:16px;line-height:1.6">Here is your affirmation PDF for today.</p>
            <div style="background:#ffe6c0;border-left:4px solid #f7931e;padding:14px 16px;margin:20px 0">
              <em>"{affirmation_text}"</em>
            </div>
            <p style="font-size:14px;color:#666">May this guide your day with peace and clarity.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:28px 0">
            <p style="text-align:center;font-size:12px;color:#999">
              🌸 ByThandi — Daily Grace Affirmations<br>
              <a href="https://bythandi.com" style="color:#f7931e">bythandi.com</a>
            </p>
          </div>
        </div>
        """.strip()

        resp = resend.Emails.send({
            "from": FROM_EMAIL,                  # must be verified in Resend
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

# --- Email/Download choice ---
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

# --- Save and (optionally) email, then refresh ---
cta_label = "📧 Save & Email My Affirmation" if delivery_method == "📧 Email me the PDF" else "💾 Save & Get New Affirmation"

if st.button(cta_label):
    log_entry = {
        "text": affirmation["text"],
        "category": affirmation.get("category", ""),
        "alignment": alignment,
        "reflection": reflection,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    st.session_state.session_entries.append(log_entry)

    # Ephemeral append (may not persist across deployments)
    try:
        with open("affirmation_log.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # Generate a one-item PDF for this affirmation
    single_pdf = create_session_pdf([log_entry], logo_url=LOGO_URL)

    if delivery_method == "📧 Email me the PDF":
        if not user_email or not _validate_email(user_email):
            st.error("⚠️ Please enter a valid email address.")
            st.stop()

        with st.spinner("📧 Sending your affirmation..."):
            result = send_affirmation_email_via_resend(
                to_email=user_email,
                pdf_buffer=single_pdf,
                affirmation_text=affirmation["text"]
            )
        if result.get("ok"):
            st.success(f"✅ Sent to {user_email}. Check your inbox!")
        else:
            st.error("❌ We couldn’t send the email.")
            st.info("💡 You can still download the PDF below.")
    else:
        st.success("🗂️ Saved to your affirmation log.")

    # Pick a new affirmation (avoid immediate repeat)
    new_affirmation = random.choice(filtered_affirmations)
    while new_affirmation["id"] == affirmation["id"] and len(filtered_affirmations) > 1:
        new_affirmation = random.choice(filtered_affirmations)

    st.session_state.selected_affirmation = new_affirmation
    st.session_state.last_affirmation_id = new_affirmation["id"]
    st.rerun()

# --- Manual Shuffle Deck (optional) ---
if st.button("🔀 Shuffle Deck (optional)"):
    random.shuffle(st.session_state.deck)
    st.success("Deck reshuffled — new grace flow ready!")
    st.rerun()

# --- PDF generation helper (brand-styled, optional logo) ---
def create_session_pdf(session_entries, logo_url=LOGO_URL):
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
    import io

    # Brand palette
    COL_BG_CREAM   = HexColor("#fff1ea")
    COL_DEEP_BLUE  = HexColor("#152d69")
    COL_ORANGE     = HexColor("#f7931e")
    COL_BROWN      = HexColor("#521305")
    COL_CARD_FILL  = HexColor("#ffe6c0")
    COL_TEXT_MUTED = HexColor("#666666")

    # Optional: fetch logo (fail silently)
    _logo_reader = None
    if logo_url:
        try:
            import requests
            r = requests.get(logo_url, timeout=6)
            r.raise_for_status()
            _logo_reader = ImageReader(io.BytesIO(r.content))
        except Exception:
            _logo_reader = None

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    W, H = letter
    margin = 18 * mm
    inner_w = W - 2 * margin

    def draw_logo(x_right, y_top, max_h_mm=16, max_w_mm=40):
        if not _logo_reader:
            return
        try:
            img_w, img_h = _logo_reader.getSize()
            max_h = max_h_mm * mm
            max_w = max_w_mm * mm
            scale = min(max_w / float(img_w), max_h / float(img_h))
            draw_w = img_w * scale
            draw_h = img_h * scale
            inset = 4 * mm
            c.drawImage(
                _logo_reader,
                x_right - draw_w - inset,
                y_top - draw_h - inset,
                width=draw_w,
                height=draw_h,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception:
            pass

    def header(page_dt_str=None):
        band_h = 28 * mm
        c.setFillColor(COL_BG_CREAM)
        c.rect(0, H - band_h, W, band_h, stroke=0, fill=1)

        c.setFillColor(COL_DEEP_BLUE)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, H - 15*mm, "Daily Grace Affirmations")

        c.setFont("Helvetica", 10)
        c.setFillColor(COL_TEXT_MUTED)
        if page_dt_str:
            c.drawString(margin, H - 20*mm, page_dt_str)

        draw_logo(W, H)

        c.setStrokeColor(COL_ORANGE)
        c.setLineWidth(2)
        c.line(margin, H - 22*mm, W - margin, H - 22*mm)

    def footer():
        c.setStrokeColor(COL_BG_CREAM)
        c.setLineWidth(14)
        c.line(0, margin - 6, W, margin - 6)
        c.setFillColor(COL_TEXT_MUTED)
        c.setFont("Helvetica-Oblique", 9)
        c.drawRightString(W - margin, margin - 2, "Daily Grace Affirmations • bythandi.com")

    def wrap_text(text, max_width, font_name="Helvetica", font_size=10):
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
        return H - 30*mm

    # first page
    header(datetime.now().strftime("%Y-%m-%d %H:%M"))
    footer()
    y = H - 32*mm

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(COL_BROWN)
    c.drawString(margin, y, "Session Summary")
    y -= 6*mm
    c.setFillColor(COL_TEXT_MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Total entries: {len(session_entries)}")
    y -= 6*mm

    c.setStrokeColor(COL_BG_CREAM)
    c.setLineWidth(3)
    c.line(margin, y, W - margin, y)
    y -= 4*mm

    card_pad = 6 * mm
    min_y = margin + 20

    for i, entry in enumerate(session_entries, 1):
        title_text = f"{i}. {entry.get('text','')}"
        reflection = entry.get('reflection', '')
        category = entry.get('category', '')
        alignment = entry.get('alignment', '')
        date_str = entry.get('date', '')

        c.setFont("Helvetica-Bold", 12)
        title_height = 5*mm + 12

        c.setFont("Helvetica", 10)
        meta_height = 5*mm + 10

        inner_text_w = inner_w - 2*card_pad

        refl_lines = wrap_text(reflection, inner_text_w, "Helvetica", 10)
        refl_height = (len(refl_lines) * 12) + 2*mm

        card_h = card_pad + title_height + 2*mm + meta_height + 2*mm + 10 + refl_height + card_pad

        if y - card_h < min_y:
            y = new_page(include_dt=True)

        c.setFillColor(COL_CARD_FILL)
        c.setStrokeColor(COL_ORANGE)
        c.setLineWidth(1.5)
        c.roundRect(margin, y - card_h, inner_w, card_h, 6, stroke=1, fill=1)

        cx = margin + card_pad
        cy = y - card_pad

        c.setFillColor(COL_BROWN)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(cx, cy - 12, title_text)
        cy -= title_height

        c.setFont("Helvetica", 10)
        c.setFillColor(COL_DEEP_BLUE)
        try:
            display_cat = CATEGORY_DISPLAY.get(category, category)
        except Exception:
            display_cat = category
        meta = f"{display_cat}  •  {alignment}  •  {date_str}"
        c.drawString(cx, cy - 10, meta)
        cy -= meta_height

        c.setStrokeColor(COL_ORANGE)
        c.setLineWidth(0.6)
        c.line(cx, cy, margin + inner_w - card_pad, cy)
        cy -= 6

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(COL_BROWN)
        c.drawString(cx, cy, "Reflection")
        cy -= 12

        c.setFont("Helvetica", 10)
        c.setFillColor(COL_BROWN)
        for line in refl_lines:
            c.drawString(cx, cy, line)
            cy -= 12

        y -= (card_h + 4*mm)

    c.save()
    buf.seek(0)
    return buf

# --- PDF download section ---
if st.session_state.session_entries:
    st.markdown("### 💾 Download your full session")
    pdf_buffer = create_session_pdf(st.session_state.session_entries, logo_url=LOGO_URL)
    st.download_button(
        label="📄 Download Full Session (.pdf)",
        data=pdf_buffer,
        file_name=f"affirmation_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )
else:
    st.info("💡 Save at least one affirmation to enable PDF download.")

st.markdown(
    "🌸 ByThandi — Daily Grace Affirmations — v4.0.1 *Grace Wheels III — Email Bloom Patch I*  \n🔗 [bythandi.com](https://bythandi.com)"
)
