
import streamlit as st
import hashlib
from supabase import create_client

st.set_page_config(page_title="Worldwide Radio Ham Study Bot", page_icon="📻")

st.title("📻 Worldwide Radio Ham Study Bot")
st.caption("Learn, practice, and prepare for your amateur radio license.")

@st.cache_resource
def get_database():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

try:
    supabase = get_database()
except Exception:
    st.error("Database connection failed. Check your Streamlit Secrets.")
    st.stop()

levels = ["Technician", "General", "Amateur Extra"]

# Student name and persistent scoreboard identity
st.sidebar.title("🏆 Student Scoreboard")
player_name = st.sidebar.text_input("Enter your name")

player_id = None
if player_name.strip():
    normalized_name = player_name.strip().lower()
    player_id = hashlib.sha256(normalized_name.encode()).hexdigest()
    st.sidebar.success(f"Welcome, {player_name.strip()}!")
else:
    st.sidebar.info("Enter your name to take a test.")

# Public Top 10 leaderboard
st.sidebar.subheader("🏆 Top 10 Students")

try:
    leaderboard = (
        supabase.table("leaderboard")
        .select("display_name, score")
        .order("score", desc=True)
        .limit(10)
        .execute()
    )

    if leaderboard.data:
        for i, student in enumerate(leaderboard.data, 1):
            st.sidebar.write(
                f"{i}. {student['display_name']} — {student['score']} points"
            )
    else:
        st.sidebar.write("No scores yet. Be the first!")
except Exception:
    st.sidebar.warning("Could not load scoreboard.")

page = st.sidebar.radio("Menu", ["Study", "Practice Test", "Admin"])

# Study page
if page == "Study":
    st.header("📚 Study")
    st.write("Choose Practice Test to begin studying.")
    st.write("Available license levels:")
    for level_name in levels:
        st.write(f"• {level_name}")

# Admin page
elif page == "Admin":
    st.header("🔐 Admin — Add Questions")
    password = st.text_input("Admin password", type="Rr4v$2$l5")
    
uploaded_csv = st.file_uploader(
    "Upload a question CSV file",
    type=["csv"]
)

if uploaded_csv is not None:
    if st.button("Import CSV Questions"):
        import pandas as pd
        import json

        try:
            df = pd.read_csv(uploaded_csv)

            required_columns = [
                "level",
                "question",
                "answers",
                "correct_answer",
                "explanation"
            ]

            if not all(col in df.columns for col in required_columns):
                st.error("CSV columns do not match the required format.")
            else:
                records = []

                for _, row in df.iterrows():
                    answers = row["answers"]

                    if isinstance(answers, str):
                        answers = json.loads(answers)

                    records.append({
                        "level": str(row["level"]),
                        "question": str(row["question"]),
                        "answers": answers,
                        "correct_answer": str(row["correct_answer"]),
                        "explanation": str(row["explanation"])
                    })

                supabase.table("questions").insert(records).execute()
                st.success(f"Imported {len(records)} questions!")
                st.rerun()

        except Exception as e:
            st.error(f"Import failed: {e}")


    password = st.text_input("Admin password", type="password")

    if password == st.secrets["ADMIN_PASSWORD"]:
        st.success("Admin access granted.")

        with st.form("add_question"):
            level = st.selectbox("License level", levels)
            question = st.text_area("Your question")

            a = st.text_input("Answer A")
            b = st.text_input("Answer B")
            c = st.text_input("Answer C")
            d = st.text_input("Answer D")

            answers = [a, b, c, d]

            correct = st.selectbox(
                "Correct answer",
                ["A", "B", "C", "D"]
            )

            explanation = st.text_area("Explanation")

            submitted = st.form_submit_button("Save Question")

            if submitted:
                if not question.strip() or not all(x.strip() for x in answers):
                    st.error("Please fill in the question and all four answers.")
                else:
                    try:
                        supabase.table("questions").insert({
                            "level": level,
                            "question": question.strip(),
                            "answers": answers,
                            "correct_answer": answers[
                                ["A", "B", "C", "D"].index(correct)
                            ],
                            "explanation": explanation.strip()
                        }).execute()

                        st.success("Question saved permanently!")
                    except Exception:
                        st.error("Could not save question. Check database permissions.")

    elif password:
        st.error("Incorrect Admin password.")

# Practice Test page
else:
    st.header("📝 Practice Test")

    level = st.selectbox("Choose your license level", levels)

    try:
        questions = (
            supabase.table("questions")
            .select("*")
            .eq("level", level)
            .order("id")
            .execute()
            .data
        )
    except Exception:
        st.error("Could not load questions from the database.")
        st.stop()

    if not questions:
        st.info("No questions have been added for this level yet.")
    else:
        if st.session_state.get("active_level") != level:
            st.session_state.active_level = level
            st.session_state.question_number = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.completion_saved = False

        if "question_number" not in st.session_state:
            st.session_state.question_number = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.completion_saved = False

        number = st.session_state.question_number

        if number >= len(questions):
            st.success("Practice test complete!")

            st.subheader(
                f"Your score: {st.session_state.score} / {len(questions)}"
            )

            # Save the student's best score permanently
            if player_id and not st.session_state.completion_saved:
                try:
                    existing = (
                        supabase.table("leaderboard")
                        .select("score")
                        .eq("player_id", player_id)
                        .execute()
                    )

                    old_score = (
                        existing.data[0]["score"]
                        if existing.data else 0
                    )

                    best_score = max(old_score, st.session_state.score)

                    supabase.table("leaderboard").upsert({
                        "player_id": player_id,
                        "display_name": player_name.strip(),
                        "score": best_score
                    }, on_conflict="player_id").execute()

                    st.session_state.completion_saved = True
                    st.success("Your score has been saved to the leaderboard!")

                except Exception:
                    st.error("Your score could not be saved. Check leaderboard permissions.")
            elif not player_id:
                st.warning("Enter your name in the sidebar to save your score.")

            if st.button("Start Again"):
                st.session_state.question_number = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.session_state.completion_saved = False
                st.rerun()

        else:
            q = questions[number]

            st.progress((number + 1) / len(questions))
            st.write(f"Question {number + 1} of {len(questions)}")
            st.subheader(q["question"])

            answer = st.radio(
                "Choose your answer:",
                q["answers"],
                key=f"answer_{level}_{number}"
            )

            if st.button(
                "Check Answer",
                disabled=st.session_state.answered,
                key=f"check_{level}_{number}"
            ):
                if not player_id:
                    st.error("Please enter your name in the sidebar first.")
                else:
                    st.session_state.answered = True

                    if answer == q["correct_answer"]:
                        st.session_state.score += 1

            if st.session_state.answered:
                if answer == q["correct_answer"]:
                    st.success("Correct!")
                else:
                    st.error(
                        "Incorrect. Correct answer: " + q["correct_answer"]
                    )

                if q.get("explanation"):
                    st.info(q["explanation"])

                if st.button("Next Question", key=f"next_{level}_{number}"):
                    st.session_state.question_number += 1
                    st.session_state.answered = False
                    st.rerun()

st.divider()
st.caption("Worldwide Radio Ham Study Bot")
st.caption("Created by Porkchop")
