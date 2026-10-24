# ===== BRAINZY: AI TUTORING BUSINESS (WEBSITE VERSION) =====
import re
import time

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Brainzy", page_icon="🧠")
MODEL = "gemini-3.8-flash"


@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


client = get_client()


def ask_ai(contents, system=None):
    """Ask the AI. Retries automatically if Google's server is busy."""
    config = types.GenerateContentConfig(system_instruction=system) if system else None
    for attempt in range(5):
        try:
            return client.models.generate_content(
                model=MODEL, contents=contents, config=config
            ).text
        except Exception:
            time.sleep(5)
    return "Sorry, the server is busy right now. Please try again in a minute."


# ---------- Memory for this visitor ----------
defaults = {"messages": [], "quiz": None, "quiz_result": None, "student_data": []}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------- Sidebar ----------
st.sidebar.title("🧠 Brainzy")
st.sidebar.caption("Your AI tutor, 24/7")
level = st.sidebar.selectbox("Your level", ["9th", "10th", "11th", "12th", "BS", "IT"])
language = st.sidebar.radio("Language", ["English", "Urdu"])
page = st.sidebar.radio(
    "Choose an agent",
    ["🧑‍🏫 Tutor", "📝 Quiz", "📢 Marketing", "📊 Progress Report"],
)

TUTOR_RULES = f"""You are a friendly, patient tutor for a {level} student.
Always reply in simple {language}. Explain step by step with easy examples.
After explaining, ask one small question to check understanding."""

# ---------- AGENT 1: TUTOR ----------
if page == "🧑‍🏫 Tutor":
    st.title("🧑‍🏫 Tutor Agent")
    st.caption("Ask any question about your studies.")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["text"])

    question = st.chat_input("Ask anything...")
    if question:
        st.session_state.messages.append({"role": "user", "text": question})
        with st.chat_message("user"):
            st.markdown(question)

        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["text"]}]}
            for m in st.session_state.messages
        ]
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = ask_ai(history, system=TUTOR_RULES)
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "text": reply})

# ---------- AGENT 2: QUIZ ----------
elif page == "📝 Quiz":
    st.title("📝 Quiz Agent")
    topic = st.text_input("Quiz topic (e.g. Python loops, photosynthesis)")

    if st.button("Create quiz") and topic:
        with st.spinner("Creating your quiz..."):
            quiz_text = ask_ai(
                f"""Create 3 multiple choice questions about {topic} for a {level} student.
Write in simple {language}. Number them 1 to 3, with options A, B, C, D.
Do NOT show the correct answers."""
            )
        st.session_state.quiz = {"topic": topic, "text": quiz_text}
        st.session_state.quiz_result = None

    if st.session_state.quiz:
        st.markdown(st.session_state.quiz["text"])
        answers = st.text_input("Your answers (example: A, C, B)")

        if st.button("Check answers") and answers:
            with st.spinner("Checking..."):
                result = ask_ai(
                    f"""Quiz:\n{st.session_state.quiz['text']}\nStudent answers: {answers}
Start your reply with exactly one line: SCORE: X/3
Then mark each answer correct or wrong and explain mistakes simply in {language}.
Be encouraging."""
                )
            match = re.search(r"SCORE:\s*(\d)\s*/\s*3", result)
            score = int(match.group(1)) if match else None
            st.session_state.student_data.append(
                {"topic": st.session_state.quiz["topic"], "score": score}
            )
            st.session_state.quiz_result = result

            # TEAMWORK: low score -> Tutor Agent prepares a lesson
            if score is not None and score < 2:
                with st.spinner("Tutor Agent is preparing a lesson for you..."):
                    lesson = ask_ai(
                        f"I got a low score in a quiz on {st.session_state.quiz['topic']}. "
                        "Please re-teach me the basics simply.",
                        system=TUTOR_RULES,
                    )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "text": "🤝 **The Quiz Agent sent you here.** Let's review this topic together.\n\n"
                        + lesson,
                    }
                )
                st.session_state.quiz_result += (
                    "\n\n---\n🤝 **Low score detected!** The Tutor Agent has prepared "
                    "a lesson for you. Open **🧑‍🏫 Tutor** in the sidebar."
                )

    if st.session_state.quiz_result:
        st.markdown(st.session_state.quiz_result)

# ---------- AGENT 3: MARKETING ----------
elif page == "📢 Marketing":
    st.title("📢 Marketing Agent")
    audience = st.selectbox("Target students", ["9th-12th class", "BS", "IT"])
    platform = st.selectbox("Platform", ["TikTok", "Facebook", "Instagram", "WhatsApp"])

    if st.button("Write posts"):
        with st.spinner("Writing posts..."):
            posts = ask_ai(
                f"""You are a marketing expert for "Brainzy", an AI tutoring service
available 24/7 at a low monthly price. It helps with school subjects (9th-12th),
BS university subjects, and IT skills like coding, in English or Urdu.
Write 3 different {platform} posts for {audience} students in {language}.
Catchy, short, friendly, with emojis and a call to action like "Try it free today!".
Add 3-5 hashtags to each post."""
            )
        st.markdown(posts)

# ---------- AGENT 4: ANALYTICS ----------
elif page == "📊 Progress Report":
    st.title("📊 Analytics Agent")
    data = st.session_state.student_data

    if not data:
        st.info("No quiz data yet. Take a quiz first!")
    else:
        df = pd.DataFrame(data)
        df.index = [f"{i + 1}. {t}" for i, t in enumerate(df["topic"])]
        scores = df["score"].dropna()

        col1, col2 = st.columns(2)
        col1.metric("Quizzes taken", len(df))
        if len(scores):
            col2.metric("Average score", f"{scores.mean():.1f}/3 ({scores.mean() / 3 * 100:.0f}%)")

        st.subheader("Scores by quiz")
        st.bar_chart(df["score"])
        st.dataframe(df, use_container_width=True)

        if st.button("Get study advice"):
            with st.spinner("Analyzing your results..."):
                advice = ask_ai(
                    f"""A {level} student has these quiz results: {data}.
In simple {language}, give a short study plan: their strong topics,
weak topics, and 3 practical tips."""
                )
            st.markdown(advice)
