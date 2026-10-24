# ===== BRAINZY: AI TUTORING PLATFORM (PRO VERSION) =====
import re
import time

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Brainzy | AI Learning Platform", page_icon="🧠", layout="wide")
MODEL = "gemini-3.8-flash"

# ---------- Professional styling ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, button, input, textarea { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1100px; }
.hero { padding: 2.6rem 2.2rem; border-radius: 20px;
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 55%, #4338CA 100%);
        border: 1px solid rgba(255,255,255,.08); margin-bottom: 1.6rem; }
.hero h1 { font-size: 2.6rem; font-weight: 800; margin: 0; color: #fff; letter-spacing: -.02em; line-height: 1.15; }
.hero p { color: #C7D2FE; font-size: 1.08rem; margin: .7rem 0 0; max-width: 640px; }
.badge { display: inline-block; padding: .28rem .75rem; border-radius: 999px;
         background: rgba(255,255,255,.12); color: #E0E7FF; font-size: .78rem;
         font-weight: 600; letter-spacing: .04em; text-transform: uppercase; margin-bottom: .9rem; }
.card { background: #131A2A; border: 1px solid #1F2937; border-radius: 16px;
        padding: 1.3rem 1.3rem 1.2rem; margin-bottom: 1rem; min-height: 140px; }
.card .tag { color: #818CF8; font-size: .75rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
.card h3 { font-size: 1.08rem; margin: .35rem 0 .45rem; color: #F3F4F6; font-weight: 700; }
.card p { color: #9CA3AF; font-size: .93rem; margin: 0; line-height: 1.5; }
.page-title { font-size: 1.9rem; font-weight: 800; color: #F3F4F6; margin: 0; letter-spacing: -.01em; }
.page-sub { color: #9CA3AF; margin: .3rem 0 1.4rem; }
.brand { font-size: 1.5rem; font-weight: 800; color: #fff; letter-spacing: -.02em; }
.brand span { color: #818CF8; }
.brand-sub { color: #9CA3AF; font-size: .85rem; margin-bottom: 1rem; }
[data-testid="stMetricValue"] { font-weight: 800; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


client = get_client()


def stream_ai(contents, system=None):
    """Stream the AI answer word by word, so it appears instantly."""
    config = types.GenerateContentConfig(system_instruction=system) if system else None
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
defaults = {"messages": [], "quiz": None, "quiz_result": None, "student_data": []}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div class="brand">Brain<span>zy</span></div><div class="brand-sub">AI learning platform</div>',
                unsafe_allow_html=True)
    page = st.radio("Navigate", ["Home", "AI Tutor", "Practice Quiz", "Marketing Studio", "Progress Analytics"])
    st.divider()
    level = st.selectbox("Your level", ["9th", "10th", "11th", "12th", "BS", "IT"], index=4)
    language = st.radio("Language", ["English", "Urdu"], horizontal=True)

TUTOR_RULES = f"""You are Brainzy, an expert, friendly tutor for a {level} student.
Always reply in clear, simple {language}. Explain step by step with easy examples.
Use short paragraphs and bullet points where helpful.
After explaining, ask one short question to check understanding."""

# ---------- HOME ----------
if page == "Home":
    st.markdown(
        """
<div class="hero">
  <div class="badge">Powered by AI agents</div>
  <h1>Learn smarter.<br>Grow faster.</h1>
  <p>Brainzy is a learning platform run entirely by a team of AI agents. Personal tutoring,
  smart quizzes and progress analytics, for school, university and IT students, 24/7.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Availability", "24/7")
    m2.metric("AI agents", "4")
    m3.metric("Languages", "2")
    m4.metric("Levels", "9th → IT")

    st.markdown("&nbsp;")
    cards = [
        ("Agent 01", "AI Tutor", "A patient personal teacher that explains any topic step by step, in English or Urdu."),
        ("Agent 02", "Quiz Agent", "Generates practice tests, marks answers and hands weak topics back to the tutor."),
        ("Agent 03", "Marketing Agent", "Writes ready-to-post social media campaigns to bring in new students."),
        ("Agent 04", "Analytics Agent", "Tracks every score, finds weak areas and builds a personal study plan."),
    ]
    row1 = st.columns(2)
    row2 = st.columns(2)
    for col, (tag, title, text) in zip(row1 + row2, cards):
        col.markdown(f'<div class="card"><div class="tag">{tag}</div><h3>{title}</h3><p>{text}</p></div>',
                     unsafe_allow_html=True)

    st.info("Choose an agent from the sidebar to get started.")

# ---------- AGENT 1: TUTOR ----------
elif page == "AI Tutor":
    page_header("AI Tutor", f"Your personal tutor · {level} · {language}")

    if not st.session_state.messages:
        st.caption("Try: “Explain standard deviation with an example” or “What is a Python loop?”")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["text"])

    question = st.chat_input("Ask anything about your studies...")
    if question:
        st.session_state.messages.append({"role": "user", "text": question})
        with st.chat_message("user"):
            st.markdown(question)

        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["text"]}]}
            for m in st.session_state.messages
        ]
        with st.chat_message("assistant"):
            reply = st.write_stream(stream_ai(history, system=TUTOR_RULES))
        st.session_state.messages.append({"role": "assistant", "text": reply})

# ---------- AGENT 2: QUIZ ----------
elif page == "Practice Quiz":
    page_header("Practice Quiz", "Test yourself. Low scores are sent to the AI Tutor automatically.")

    with st.form("make_quiz"):
        topic = st.text_input("Quiz topic", placeholder="e.g. Python loops, photosynthesis, probability")
        make = st.form_submit_button("Generate quiz", type="primary")

    just_made = False
    if make and topic:
        with st.container(border=True):
            quiz_text = st.write_stream(stream_ai(
                f"""Create 3 multiple choice questions about {topic} for a {level} student.
Write in simple {language}. Number them 1 to 3, with options A, B, C, D, each option on its own line.
Do NOT show the correct answers."""
            ))
        st.session_state.quiz = {"topic": topic, "text": quiz_text}
        st.session_state.quiz_result = None
        just_made = True
    elif st.session_state.quiz:
        with st.container(border=True):
            st.markdown(st.session_state.quiz["text"])

    if st.session_state.quiz:
        with st.form("check_quiz"):
            answers = st.text_input("Your answers", placeholder="e.g. A, C, B")
            check = st.form_submit_button("Check answers", type="primary")

        if check and answers:
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

            # TEAMWORK: low score -> Tutor Agent prepares a lesson
            if score is not None and score < 2:
                with st.spinner("The AI Tutor is preparing a lesson for you..."):
                    lesson = ask_ai(
                        f"I got a low score in a quiz on {st.session_state.quiz['topic']}. "
                        "Please re-teach me the basics simply.",
                        system=TUTOR_RULES,
                    )
                st.session_state.messages.append({
                    "role": "assistant",
                    "text": "**The Quiz Agent sent you here.** Let's review this topic together.\n\n" + lesson,
                })
                st.session_state.quiz_result += (
                    "\n\n---\n**Low score detected.** The AI Tutor has prepared a lesson for you. "
                    "Open **AI Tutor** in the sidebar."
                )

    if st.session_state.quiz_result:
        with st.container(border=True):
            st.markdown(st.session_state.quiz_result)

# ---------- AGENT 3: MARKETING ----------
elif page == "Marketing Studio":
    page_header("Marketing Studio", "The Marketing Agent writes campaigns to grow Brainzy.")

    c1, c2 = st.columns(2)
    audience = c1.selectbox("Target students", ["9th-12th class", "BS", "IT"])
    platform = c2.selectbox("Platform", ["TikTok", "Facebook", "Instagram", "WhatsApp"])

    if st.button("Write posts", type="primary"):
        with st.container(border=True):
            st.write_stream(stream_ai(
                f"""You are a marketing expert for "Brainzy", an AI tutoring platform
available 24/7 at a low monthly price. It helps with school subjects (9th-12th),
BS university subjects, and IT skills like coding, in English or Urdu.
Write 3 different {platform} posts for {audience} students in {language}.
Catchy, short, professional, with a clear call to action like "Try it free today".
Add 3-5 hashtags to each post."""
            ))

# ---------- AGENT 4: ANALYTICS ----------
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

        if st.button("Get my study plan", type="primary"):
            with st.container(border=True):
                st.write_stream(stream_ai(
                    f"""A {level} student has these quiz results: {data}.
In simple {language}, give a short study plan: their strong topics,
weak topics, and 3 practical tips."""
                ))
