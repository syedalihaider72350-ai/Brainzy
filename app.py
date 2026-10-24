# ===== BRAINZY: AI LEARNING & LIFE PLATFORM (FINAL VERSION) =====
import re
import time

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Brainzy | AI Learning & Life Platform", page_icon="🧠", layout="wide")
MODEL = "gemini-3.8-flash"

# ---------- Plan & security settings ----------
FREE_LIMIT = 20               # AI requests per session on the free plan
MAX_CHARS = 4000              # longest message a user can send
MAX_FILE_MB = 10              # biggest photo / PDF / voice file allowed
MAX_FILES = 3                 # files per message

# ---------- Brainzy logo (drawn in code, so it is always sharp) ----------
def logo(size=40, gid="g"):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#818CF8"/><stop offset="1" stop-color="#4338CA"/></linearGradient></defs>'
            f'<rect width="64" height="64" rx="16" fill="url(#{gid})"/>'
            '<path d="M22 16h12a9 9 0 0 1 0 18H22z M22 34h14a9 9 0 0 1 0 18H22z" fill="none" stroke="#FFFFFF" '
            'stroke-width="5" stroke-linejoin="round"/>'
            '<circle cx="48" cy="16" r="4.5" fill="#E0E7FF"/></svg>')


# ---------- Splash screen with the logo, shown once when someone opens the app ----------
if "splash_done" not in st.session_state:
    splash = st.empty()
    splash.markdown(f"""
<style>
@keyframes bz-in {{ 0% {{ opacity: 0; transform: scale(.85); }} 100% {{ opacity: 1; transform: scale(1); }} }}
@keyframes bz-bar {{ 0% {{ width: 0; }} 100% {{ width: 160px; }} }}
.bz-splash {{ position: fixed; inset: 0; z-index: 999999; background: radial-gradient(800px 400px at 50% 35%, #1E1B4B, #0B0F19 70%);
             display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; }}
.bz-splash .mark {{ animation: bz-in .7s ease-out both; filter: drop-shadow(0 12px 40px rgba(99,102,241,.45)); }}
.bz-splash .word {{ font-family: 'Inter', sans-serif; font-size: 2.6rem; font-weight: 800; color: #fff; letter-spacing: -.03em;
                    animation: bz-in .7s .15s ease-out both; }}
.bz-splash .word span {{ color: #818CF8; }}
.bz-splash .tag {{ color: #9CA3AF; font-size: 1rem; animation: bz-in .7s .3s ease-out both; }}
.bz-splash .bar {{ height: 3px; border-radius: 3px; background: #6366F1; animation: bz-bar 1.4s ease-in-out both; }}
</style>
<div class="bz-splash"><div class="mark">{logo(96, "gs")}</div>
<div class="word">Brain<span>zy</span></div><div class="tag">Your expert for study, career and life</div>
<div class="bar"></div></div>
""", unsafe_allow_html=True)
    time.sleep(1.6)
    splash.empty()
    st.session_state.splash_done = True

# ---------- Professional styling ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, button, input, textarea { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1100px; }
.hero { padding: 2.8rem 2.4rem; border-radius: 22px;
        background: radial-gradient(1200px 400px at 10% -20%, rgba(129,140,248,.35), transparent 60%),
                    linear-gradient(135deg, #1E1B4B 0%, #312E81 55%, #4338CA 100%);
        border: 1px solid rgba(255,255,255,.08); margin-bottom: 1.6rem; }
.hero h1 { font-size: 2.7rem; font-weight: 800; margin: 0; color: #fff; letter-spacing: -.025em; line-height: 1.12; }
.hero p { color: #C7D2FE; font-size: 1.08rem; margin: .8rem 0 0; max-width: 660px; line-height: 1.55; }
.badge { display: inline-block; padding: .28rem .75rem; border-radius: 999px;
         background: rgba(255,255,255,.12); color: #E0E7FF; font-size: .76rem;
         font-weight: 600; letter-spacing: .05em; text-transform: uppercase; margin-bottom: .9rem; }
.card { background: #131A2A; border: 1px solid #1F2937; border-radius: 16px;
        padding: 1.3rem 1.3rem 1.2rem; margin-bottom: 1rem; min-height: 140px;
        transition: border-color .2s ease, transform .2s ease; }
.card:hover { border-color: #4F46E5; transform: translateY(-2px); }
.card .tag { color: #818CF8; font-size: .74rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
.card h3 { font-size: 1.08rem; margin: .35rem 0 .45rem; color: #F3F4F6; font-weight: 700; }
.card p { color: #9CA3AF; font-size: .93rem; margin: 0; line-height: 1.5; }
.section { font-size: 1.25rem; font-weight: 800; color: #F3F4F6; margin: 1.6rem 0 .8rem; }
.page-title { font-size: 1.9rem; font-weight: 800; color: #F3F4F6; margin: 0; letter-spacing: -.015em; }
.page-sub { color: #9CA3AF; margin: .3rem 0 1.4rem; }
.brand { font-size: 1.55rem; font-weight: 800; color: #fff; letter-spacing: -.02em;
         display: flex; align-items: center; gap: .6rem; }
.brand span { color: #818CF8; }
.brand-sub { color: #9CA3AF; font-size: .85rem; margin-bottom: 1rem; }
.plan { background: #131A2A; border: 1px solid #1F2937; border-radius: 12px; padding: .8rem .9rem; }
.plan b { color: #E5E7EB; }
.price { background: #131A2A; border: 1px solid #1F2937; border-radius: 16px; padding: 1.4rem; }
.price.pro { border-color: #6366F1; box-shadow: 0 0 0 1px #6366F1 inset; }
.price h3 { margin: 0; color: #F3F4F6; }
.price .amt { font-size: 2rem; font-weight: 800; color: #fff; margin: .4rem 0; }
.price li { color: #9CA3AF; margin: .25rem 0; }
.privacy { color: #6B7280; font-size: .75rem; line-height: 1.45; margin-top: .8rem; }
[data-testid="stMetricValue"] { font-weight: 800; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


client = get_client()

# ---------- Safety rules added to EVERY agent ----------
SAFETY = """Safety rules (always follow):
- Refuse requests that could cause harm (weapons, hacking others, self-harm methods, illegal activity, cheating others).
- For medical, legal or financial decisions, give general educational information and advise seeing a qualified professional.
- If someone seems to be in danger or crisis, respond with care and urge them to contact local emergency services
  (in Pakistan: Rescue 1122) or a trusted person or mental health professional right away.
- Never ask for passwords, card numbers or other private data. Never invent facts, sources or statistics.
"""

FORMAT = """Formatting: write like a premium AI assistant. Start with a direct answer, then use clear
Markdown headings, short paragraphs, bullet points, numbered steps, tables for comparisons,
**bold** key terms and code blocks for code. End with a short summary or next step when helpful."""


def stream_ai(contents, system=None):
    """Stream the AI answer word by word, so it appears instantly."""
    config = types.GenerateContentConfig(system_instruction=SAFETY + "\n" + (system or ""))
    for attempt in range(3):
        sent_any = False
        try:
            for chunk in client.models.generate_content_stream(
                model=MODEL, contents=contents, config=config
            ):
                if chunk.text:
                    sent_any = True
                    yield chunk.text
            return
        except Exception:
            if sent_any:
                yield "\n\n_Connection interrupted. Please try again._"
                return
            time.sleep(3)
    yield "The AI service is busy right now. Please try again in a moment."


def ask_ai(contents, system=None):
    """Get a full answer at once (used when we need to read the result)."""
    return "".join(stream_ai(contents, system))


def page_header(title, subtitle):
    st.markdown(f'<p class="page-title">{title}</p><p class="page-sub">{subtitle}</p>', unsafe_allow_html=True)


# ---------- Memory for this visitor ----------
for key, value in {"quiz": None, "quiz_result": None, "student_data": [], "chats": {},
                   "current_chat": None, "last_audio": None, "used": 0, "pending": None}.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- Free plan ----------
@st.dialog("Brainzy plans", width="large")
def show_plans():
    st.markdown("**Big AI quality at a student price.** Leading AI apps cost about Rs 5,600 a month. "
                "Brainzy Pro yearly works out to about Rs 417 a month.")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""<div class="price"><h3>Free</h3><div class="amt">Rs 0</div>
<ul><li>{FREE_LIMIT} AI requests per session</li><li>All 5 AI agents</li><li>21 modes, 50+ languages</li></ul></div>""",
                unsafe_allow_html=True)
    c2.markdown("""<div class="price"><h3>Pro Monthly</h3><div class="amt">Rs 2,000<span style="font-size:1rem;color:#9CA3AF">/month</span></div>
<ul><li>Unlimited AI requests</li><li>Saved chat history</li><li>Priority speed</li><li>Parent progress reports</li></ul></div>""",
                unsafe_allow_html=True)
    c3.markdown("""<div class="price pro"><h3>Pro Yearly · Best value</h3><div class="amt">Rs 5,000<span style="font-size:1rem;color:#9CA3AF">/year</span></div>
<ul><li>Everything in Pro</li><li>About Rs 417 a month</li><li>Save Rs 19,000 a year</li></ul></div>""",
                unsafe_allow_html=True)
    st.markdown("""
| Price | ChatGPT Plus | Google AI Pro | **Brainzy Pro** |
|---|---|---|---|
| Per month | $20 (about Rs 5,600) | about Rs 5,600 | **Rs 2,000** |
| Per year | about Rs 67,000 | about Rs 67,000 | **Rs 5,000** |
""")
    st.caption("Competitor prices are approximate and change over time. "
               "Payments are coming soon: Brainzy Pro is not available to buy yet.")


def spend_credit():
    """Use one free request. Returns False (and shows the upgrade box) when the limit is reached."""
    if st.session_state.used >= FREE_LIMIT:
        st.warning(f"You've used all {FREE_LIMIT} free requests for this session. "
                   "Click **See plans** in the sidebar: Brainzy Pro is just Rs 5,000 a year.")
        return False
    st.session_state.used += 1
    return True


def too_long(text):
    if len(text) > MAX_CHARS:
        st.error(f"Your message is too long. Please keep it under {MAX_CHARS:,} characters.")
        return True
    return False


# ---------- Chats ----------
def new_chat():
    chat_id = str(time.time())
    st.session_state.chats[chat_id] = {"title": "New chat", "messages": []}
    st.session_state.current_chat = chat_id


if st.session_state.current_chat is None:
    new_chat()


def current_messages():
    return st.session_state.chats[st.session_state.current_chat]["messages"]


def to_contents(messages):
    """Turn the chat (text, photos, PDFs, voice) into the format Gemini understands."""
    contents = []
    for m in messages:
        parts = [types.Part.from_bytes(data=data, mime_type=mime) for data, mime, _ in m["files"]]
        if m["text"]:
            parts.append(types.Part.from_text(text=m["text"]))
        contents.append(types.Content(role="user" if m["role"] == "user" else "model", parts=parts))
    return contents


def show_message(m):
    with st.chat_message(m["role"]):
        for data, mime, name in m["files"]:
            if mime.startswith("image/"):
                st.image(data, width=280)
            elif mime == "application/pdf":
                st.caption(f"📄 {name}")
        st.markdown(m["display"])


# ---------- Modes: each one turns the AI into a specialist ----------
FIELDS = {
    # Study fields
    "General / School": "Teach like an excellent school teacher who follows the board syllabus.",
    "Medicine (MBBS)": "Act as a senior medical professor. Use correct medical terminology, explain anatomy, "
                       "physiology, pathology and clinical relevance, and add exam tips for MCQs and vivas.",
    "Nursing & Pharmacy": "Act as a senior nursing and pharmacy lecturer. Explain drugs, mechanisms and patient care clearly.",
    "Engineering": "Act as an engineering professor. Show formulas, units, assumptions and full worked solutions.",
    "Computer Science & IT": "Act as a senior software engineer and CS professor. Give clean, commented code, "
                             "explain the logic, time complexity and best practices, and help debug errors.",
    "Data Science & Analytics": "Act as a senior data scientist. Explain statistics, Python/R/SQL/Excel, "
                                "machine learning and visualisation with practical, worked examples.",
    "Business & Management": "Act as a business school professor. Use real frameworks (SWOT, 4Ps, Porter, PESTLE) "
                             "and practical case-study style examples.",
    "Accounting & Finance": "Act as a chartered accountant and finance lecturer. Show journal entries, "
                            "calculations and ratios step by step.",
    "Law": "Act as a law professor. Explain legal principles, statutes and landmark cases clearly. "
           "Note that laws differ by country and that this is study help, not legal advice.",
    "Economics": "Act as an economics professor. Use models, diagrams described in words and real-world examples.",
    "Psychology & Social Sciences": "Act as a psychology and social science lecturer. Explain theories, "
                                    "key researchers and research methods clearly.",
    "Arts, English & Languages": "Act as a literature and language professor. Help with analysis, grammar, "
                                 "vocabulary and writing style.",
    "Agriculture & Environment": "Act as an agriculture and environmental science expert with practical field examples.",
    # Life modes
    "Life · Career & Jobs": "Act as an experienced career coach. Help with career choices, CVs, LinkedIn, "
                            "interviews, freelancing and workplace skills, with practical action steps.",
    "Life · Personal Finance": "Act as a personal finance educator. Explain budgeting, saving, debt and investing basics "
                               "clearly. Give general education, not personalised investment advice.",
    "Life · Health & Fitness": "Act as a certified fitness and wellness coach. Give general, safe guidance on exercise, "
                               "sleep and healthy habits. For symptoms or conditions, advise seeing a doctor.",
    "Life · Cooking & Nutrition": "Act as a friendly chef and nutrition educator. Give clear recipes, "
                                  "budget meal ideas and balanced eating tips.",
    "Life · Mental Wellbeing": "Act as a warm, supportive wellbeing coach. Listen, validate feelings and suggest healthy "
                               "coping strategies. You are not a therapist: encourage professional help when needed.",
    "Life · Relationships & Communication": "Act as a wise communication coach. Help with difficult conversations, "
                                            "family, friendships and teamwork, respectfully and fairly.",
    "Life · Travel": "Act as an experienced travel planner. Give itineraries, budgets and practical tips, "
                     "and remind users to check current visa and safety rules.",
    "Life · Everyday Problem Solving": "Act as a smart, practical life assistant. Break problems into clear options "
                                       "and recommend the best next step.",
}

SUGGESTIONS = {
    "Life": ["Help me plan my week", "How do I start freelancing?", "Make me a simple monthly budget",
             "How can I stop procrastinating?"],
    "Study": ["Explain this topic simply with an example", "Give me 5 exam tips for my field",
              "Make a 7-day study plan", "What are the most important topics to revise?"],
}

LANGUAGES = [
    "English", "Urdu", "Arabic", "Chinese", "Spanish", "French", "German", "Hindi", "Bengali", "Punjabi",
    "Pashto", "Sindhi", "Balochi", "Saraiki", "Kashmiri", "Persian", "Turkish", "Russian", "Portuguese",
    "Indonesian", "Malay", "Japanese", "Korean", "Italian", "Dutch", "Swahili", "Hausa", "Yoruba", "Amharic",
    "Somali", "Zulu", "Tamil", "Telugu", "Gujarati", "Marathi", "Kannada", "Malayalam", "Nepali", "Sinhala",
    "Burmese", "Khmer", "Thai", "Vietnamese", "Filipino", "Greek", "Hebrew", "Polish", "Ukrainian", "Czech",
    "Romanian", "Hungarian", "Swedish", "Norwegian", "Danish", "Finnish", "Azerbaijani", "Kazakh", "Uzbek", "Kurdish",
]

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(f'<div class="brand">{logo(38, "gb")}<div>Brain<span>zy</span></div></div>'
                '<div class="brand-sub">AI learning & life platform</div>',
                unsafe_allow_html=True)
    page = st.radio("Navigate", ["Home", "AI Assistant", "Writing Studio", "Practice Quiz",
                                 "Marketing Studio", "Progress Analytics"])
    st.divider()
    field = st.selectbox("Mode", list(FIELDS))
    level = st.selectbox("Your level", ["9th", "10th", "11th", "12th", "Diploma", "BS / Bachelor's",
                                        "Master's", "Working professional"], index=5)
    language = st.selectbox("Language", LANGUAGES)
    depth = st.select_slider("Answer depth", ["Simple", "Balanced", "Deep expert"], value="Balanced")

    st.divider()
    left = max(FREE_LIMIT - st.session_state.used, 0)
    st.markdown(f'<div class="plan"><b>Free plan</b><br>'
                f'<span style="color:#9CA3AF;font-size:.85rem">{left} of {FREE_LIMIT} requests left</span></div>',
                unsafe_allow_html=True)
    st.progress(min(st.session_state.used / FREE_LIMIT, 1.0))
    if st.button("See plans · Rs 5,000/year", use_container_width=True):
        show_plans()
    st.markdown('<div class="privacy">🔒 Private by design: chats are not stored after you close this page. '
                'Never share passwords or card numbers with any AI.</div>', unsafe_allow_html=True)

is_life = field.startswith("Life")
DEPTH = {
    "Simple": "Answer depth: SIMPLE. Use everyday words, short sentences and one relatable example, "
              "as if explaining to a smart 12-year-old. Avoid jargon; if a technical word is needed, define it.",
    "Balanced": "Answer depth: BALANCED. Give a clear, complete explanation with key terms defined, "
                "examples and practical tips.",
    "Deep expert": "Answer depth: DEEP EXPERT. Give a rich, university-level answer: precise technical terminology, "
                   "underlying principles and mechanisms, edge cases, common misconceptions, real-world applications, "
                   "and connections to related topics. Then ALWAYS finish with a section titled "
                   "'In simple words' that explains the whole idea in 3-4 easy sentences.",
}
STUDENT = f"{level} learner using {field} mode"
TUTOR_RULES = f"""You are Brainzy, a brilliant, professional AI assistant and tutor for a {STUDENT}.
{FIELDS[field]}
You can help with ANY question in life or knowledge: every study subject, coding and debugging, math,
assignments, research, exams, careers, money basics, health habits, cooking, travel, relationships,
writing and everyday problems.
Always reply in clear, simple {language}, with a polished, professional and warm tone.
Think carefully before answering and be accurate. If you are unsure, say so honestly.
If the user sends a photo, read it carefully and solve or explain what is shown.
If the user sends a PDF or notes, answer using that document.
If the user sends a voice recording, treat it as their spoken question.
{DEPTH[depth]}
{FORMAT}
When teaching, end with one short question to check understanding."""

# ---------- HOME ----------
if page == "Home":
    st.markdown(
        """
<div class="hero">
  <div style="margin-bottom:1rem">LOGO_HERO</div>
  <div class="badge">Powered by a team of AI agents</div>
  <h1>Your expert for study,<br>career and life.</h1>
  <p>Brainzy is run entirely by AI agents. Ask by text, voice, photo or PDF, switch between 20+ expert modes,
  practise with smart quizzes and track your progress, in 50+ languages, 24/7.</p>
</div>
""".replace("LOGO_HERO", logo(56, "gh")),
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Availability", "24/7")
    m2.metric("AI agents", "5")
    m3.metric("Expert modes", str(len(FIELDS)))
    m4.metric("Languages", str(len(LANGUAGES)))

    st.markdown('<p class="section">Meet your AI team</p>', unsafe_allow_html=True)
    cards = [
        ("Agent 01", "AI Assistant", "Ask anything by text, voice, photo or PDF. Expert answers for study and life."),
        ("Agent 02", "Writing Agent", "Professional articles, essays, reports, emails and cover letters, ready to download."),
        ("Agent 03", "Quiz Agent", "Generates practice tests, marks answers and hands weak topics back to the tutor."),
        ("Agent 04", "Marketing Agent", "Creates social media campaigns that bring new learners to Brainzy."),
        ("Agent 05", "Analytics Agent", "Tracks every score, finds weak areas and builds a personal study plan."),
        ("Expert modes", f"{len(FIELDS)} specialists in one app", "Medicine, engineering, IT, law, finance, careers, "
                                                                  "fitness, wellbeing, cooking, travel and more."),
    ]
    rows = st.columns(2) + st.columns(2) + st.columns(2)
    for col, (tag, title, text) in zip(rows, cards):
        col.markdown(f'<div class="card"><div class="tag">{tag}</div><h3>{title}</h3><p>{text}</p></div>',
                     unsafe_allow_html=True)

    st.markdown('<p class="section">Why Brainzy is different</p>', unsafe_allow_html=True)
    st.markdown("""
| | General AI chatbots | **Brainzy** |
|---|---|---|
| Expert modes for your field | Write your own prompts | **20+ ready-made specialists** |
| Quizzes that are marked for you | ✗ | **✓** |
| Weak topics re-taught automatically | ✗ | **✓ Agents work together** |
| Progress tracking & study plan | ✗ | **✓ Analytics Agent** |
| Choose simple or deep-expert answers | Ask every time | **✓ One slider** |
| One-click "simpler / deeper / quiz me" | ✗ | **✓** |
| Built for local students, 50+ languages incl. Urdu | Partly | **✓** |
| Yearly price | About Rs 67,000 | **Rs 5,000** |
""")
    st.markdown('<p class="section">The road ahead</p>', unsafe_allow_html=True)
    road = [
        ("Live now", "Smart learning", "5 AI agents, 21 expert modes, voice, photo and PDF questions, "
                                         "adjustable answer depth and progress analytics."),
        ("Next", "Your own syllabus", "Upload textbooks and past papers so answers follow your exact course."),
        ("Next", "Accounts & saved progress", "Secure login, chat history and progress saved across devices."),
        ("Coming", "Parent & teacher dashboards", "Weekly reports and class-wide analytics for schools."),
        ("Coming", "Brainzy on mobile & WhatsApp", "Learn anywhere, even with weak internet."),
        ("Vision", "A lifelong AI mentor", "One companion that grows with you from 9th class to your career."),
    ]
    rows = st.columns(3) + st.columns(3)
    for col, (tag, title, text) in zip(rows, road):
        col.markdown(f'<div class="card"><div class="tag">{tag}</div><h3>{title}</h3><p>{text}</p></div>',
                     unsafe_allow_html=True)

    st.info("Choose **AI Assistant** in the sidebar to get started.")

# ---------- AGENT 1: AI ASSISTANT ----------
elif page == "AI Assistant":
    with st.sidebar:
        st.divider()
        if st.button("＋  New chat", use_container_width=True):
            new_chat()
            st.rerun()
        st.caption("Your chats")
        for chat_id, chat in reversed(list(st.session_state.chats.items())):
            is_open = chat_id == st.session_state.current_chat
            if st.button(chat["title"], key=f"chat_{chat_id}", use_container_width=True,
                         type="primary" if is_open else "secondary"):
                st.session_state.current_chat = chat_id
                st.rerun()

    page_header("AI Assistant", f"{field} · {level} · {language} · {depth}")
    messages = current_messages()

    if not messages:
        st.caption("Ask anything, attach a photo or PDF, or ask by voice. Try one of these:")
        ideas = SUGGESTIONS["Life" if is_life else "Study"]
        cols = st.columns(2)
        for i, idea in enumerate(ideas):
            if cols[i % 2].button(idea, key=f"idea_{i}", use_container_width=True):
                st.session_state.pending = idea
                st.rerun()

    for m in messages:
        show_message(m)

    # One-click follow-ups on the latest answer
    if messages and messages[-1]["role"] == "assistant":
        actions = {"Explain simpler": "Explain your last answer again in much simpler words.",
                   "Go deeper": "Go deeper on your last answer, at an advanced expert level.",
                   "More examples": "Give me 3 more real-life examples of your last answer.",
                   "Quiz me on this": "Quiz me with 3 short questions on your last answer, one at a time.",
                   "Summarise": "Summarise your last answer in 5 bullet points for quick revision."}
        cols = st.columns(len(actions))
        for col, (label, ask) in zip(cols, actions.items()):
            if col.button(label, key=f"act_{label}_{len(messages)}", use_container_width=True):
                st.session_state.pending = ask
                st.rerun()

    with st.popover("🎙  Ask by voice"):
        audio = st.audio_input("Record your question", key=f"voice_{st.session_state.current_chat}")

    prompt = st.chat_input(
        "Ask anything, or attach a photo or PDF...",
        accept_file="multiple",
        file_type=["png", "jpg", "jpeg", "webp", "pdf"],
    )

    new_msg = None
    if st.session_state.pending:
        text = st.session_state.pending
        st.session_state.pending = None
        new_msg = {"role": "user", "text": text, "display": text, "files": []}
    elif prompt:
        text = prompt.text.strip() if prompt.text else ""
        uploads = list(prompt.files)[:MAX_FILES]
        too_big = [f.name for f in uploads if f.size > MAX_FILE_MB * 1024 * 1024]
        if too_big:
            st.error(f"These files are bigger than {MAX_FILE_MB} MB: {', '.join(too_big)}")
        elif not too_long(text):
            files = [(f.getvalue(), f.type, f.name) for f in uploads]
            if not text and files:
                text = "Please explain this step by step."
            if text or files:
                new_msg = {"role": "user", "text": text, "display": text, "files": files}
    elif audio is not None:
        data = audio.getvalue()
        if hash(data) != st.session_state.last_audio and len(data) <= MAX_FILE_MB * 1024 * 1024:
            st.session_state.last_audio = hash(data)
            new_msg = {"role": "user", "text": "", "display": "🎙 Voice question",
                       "files": [(data, "audio/wav", "voice.wav")]}

    if new_msg and spend_credit():
        chat = st.session_state.chats[st.session_state.current_chat]
        if chat["title"] == "New chat":
            title = new_msg["display"]
            chat["title"] = title[:30] + "…" if len(title) > 30 else title
        messages.append(new_msg)
        show_message(new_msg)
        with st.chat_message("assistant"):
            reply = st.write_stream(stream_ai(to_contents(messages), system=TUTOR_RULES))
        messages.append({"role": "assistant", "text": reply, "display": reply, "files": []})
        st.rerun()

# ---------- AGENT 2: WRITING ----------
elif page == "Writing Studio":
    page_header("Writing Studio", "The Writing Agent creates polished, professional documents in seconds.")

    with st.form("write_form"):
        c1, c2 = st.columns(2)
        doc_type = c1.selectbox("What do you need?", ["Article", "Blog post", "Essay", "Report", "Email",
                                                       "Cover letter", "CV summary", "Summary", "Speech"])
        tone = c2.selectbox("Tone", ["Professional", "Academic", "Persuasive", "Friendly", "Simple"])
        topic = st.text_area("Topic or instructions", max_chars=MAX_CHARS,
                             placeholder="e.g. How artificial intelligence is changing businesses in Pakistan")
        c3, c4 = st.columns(2)
        length = c3.select_slider("Length", ["Short", "Medium", "Long"], value="Medium")
        notes = c4.text_input("Extra details (optional)", max_chars=500,
                              placeholder="e.g. audience, key points, word limit")
        write = st.form_submit_button("Write it", type="primary")

    if write and topic and spend_credit():
        words = {"Short": "about 300", "Medium": "about 700", "Long": "about 1,200"}[length]
        with st.container(border=True):
            draft = st.write_stream(stream_ai(
                f"""Write a high-quality {tone.lower()} {doc_type.lower()} in {language} for a {STUDENT}.
Topic / instructions: {topic}
Extra details: {notes or 'none'}
Length: {words} words.
Make it polished and professional: a strong title, a clear introduction, well-organised
sections with headings where suitable, smooth transitions and a strong conclusion.
Use Markdown formatting. Do not invent fake statistics, quotes or sources;
where a real figure would help, write [add source] so the writer can fill it in."""
            ))
        st.session_state.last_draft = draft
        st.session_state.last_draft_name = re.sub(r"[^a-z0-9]+", "-", topic.lower())[:40].strip("-") or "brainzy"

    if st.session_state.get("last_draft"):
        st.download_button("Download as file", st.session_state.last_draft,
                           file_name=f"{st.session_state.last_draft_name}.md", mime="text/markdown")
        st.caption("Tip: if you use this for schoolwork, read it, edit it in your own words and "
                   "follow your teacher's rules on AI use.")

# ---------- AGENT 3: QUIZ ----------
elif page == "Practice Quiz":
    page_header("Practice Quiz", "Test yourself. Low scores are sent to the AI Assistant automatically.")

    with st.form("make_quiz"):
        topic = st.text_input("Quiz topic", max_chars=200,
                              placeholder="e.g. Python loops, photosynthesis, interview skills")
        make = st.form_submit_button("Generate quiz", type="primary")

    if make and topic and spend_credit():
        with st.container(border=True):
            quiz_text = st.write_stream(stream_ai(
                f"""Create 3 multiple choice questions about {topic} for a {STUDENT}.
Write in simple {language}. Number them 1 to 3, with options A, B, C, D, each option on its own line.
Do NOT show the correct answers."""
            ))
        st.session_state.quiz = {"topic": topic, "text": quiz_text}
        st.session_state.quiz_result = None
    elif st.session_state.quiz:
        with st.container(border=True):
            st.markdown(st.session_state.quiz["text"])

    if st.session_state.quiz:
        with st.form("check_quiz"):
            answers = st.text_input("Your answers", max_chars=50, placeholder="e.g. A, C, B")
            check = st.form_submit_button("Check answers", type="primary")

        if check and answers and spend_credit():
            with st.spinner("Marking your answers..."):
                result = ask_ai(
                    f"""Quiz:\n{st.session_state.quiz['text']}\nStudent answers: {answers}
Start your reply with exactly one line: SCORE: X/3
Then mark each answer correct or wrong and explain mistakes simply in {language}.
Be encouraging."""
                )
            match = re.search(r"SCORE:\s*(\d)\s*/\s*3", result)
            score = int(match.group(1)) if match else None
            st.session_state.student_data.append({"topic": st.session_state.quiz["topic"], "score": score})
            st.session_state.quiz_result = result

            # TEAMWORK: low score -> AI Assistant prepares a lesson in a new chat
            if score is not None and score < 2:
                quiz_topic = st.session_state.quiz["topic"]
                with st.spinner("The AI Assistant is preparing a lesson for you..."):
                    lesson = ask_ai(
                        f"I got a low score in a quiz on {quiz_topic}. Please re-teach me the basics simply.",
                        system=TUTOR_RULES,
                    )
                new_chat()
                st.session_state.chats[st.session_state.current_chat]["title"] = f"Review: {quiz_topic}"[:31]
                text = "**The Quiz Agent sent you here.** Let's review this topic together.\n\n" + lesson
                current_messages().append({"role": "assistant", "text": text, "display": text, "files": []})
                st.session_state.quiz_result += (
                    "\n\n---\n**Low score detected.** The AI Assistant has prepared a lesson for you. "
                    "Open **AI Assistant** in the sidebar."
                )

    if st.session_state.quiz_result:
        with st.container(border=True):
            st.markdown(st.session_state.quiz_result)

# ---------- AGENT 4: MARKETING ----------
elif page == "Marketing Studio":
    page_header("Marketing Studio", "The Marketing Agent writes campaigns to grow Brainzy.")

    c1, c2 = st.columns(2)
    audience = c1.selectbox("Target audience", ["9th-12th class students", "University students",
                                                "IT students", "Young professionals"])
    platform = c2.selectbox("Platform", ["TikTok", "Facebook", "Instagram", "WhatsApp", "LinkedIn"])

    if st.button("Write posts", type="primary") and spend_credit():
        with st.container(border=True):
            st.write_stream(stream_ai(
                f"""You are a marketing expert for "Brainzy", an AI learning and life platform run by AI agents,
available 24/7 with a free plan and a Pro plan at Rs 2,000 a month or just Rs 5,000 a year, far cheaper than other AI apps. It offers 20+ expert modes (medicine, engineering,
IT, business, law, careers, fitness, wellbeing and more), quizzes, progress tracking and a writing studio,
in 50+ languages. Users can ask by text, voice, photo or PDF.
Write 3 different {platform} posts for {audience} in {language}.
Catchy, short, professional, with a clear call to action like "Try it free today".
Add 3-5 hashtags to each post."""
            ))

# ---------- AGENT 5: ANALYTICS ----------
elif page == "Progress Analytics":
    page_header("Progress Analytics", "The Analytics Agent tracks your results and plans your next steps.")
    data = st.session_state.student_data

    if not data:
        st.info("No quiz data yet. Take a quiz in **Practice Quiz** first.")
    else:
        df = pd.DataFrame(data)
        df.index = [f"{i + 1}. {t}" for i, t in enumerate(df["topic"])]
        scores = df["score"].dropna()

        c1, c2, c3 = st.columns(3)
        c1.metric("Quizzes taken", len(df))
        if len(scores):
            c2.metric("Average score", f"{scores.mean():.1f} / 3")
            c3.metric("Accuracy", f"{scores.mean() / 3 * 100:.0f}%")

        with st.container(border=True):
            st.markdown("**Scores by quiz**")
            st.bar_chart(df["score"], color="#6366F1")

        if st.button("Get my study plan", type="primary") and spend_credit():
            with st.container(border=True):
                st.write_stream(stream_ai(
                    f"""A {STUDENT} has these quiz results: {data}.
In simple {language}, give a short study plan: their strong topics,
weak topics, and 3 practical tips. {FORMAT}"""
                ))
