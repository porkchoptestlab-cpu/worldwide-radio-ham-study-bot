
import streamlit as st
import uuid
from supabase import create_client
st.title("📻 Worldwide Radio Ham Study Bot")
st.caption("Learn, practice, and prepare for your amateur radio license.")

@st.cache_resource
def get_database():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
supabase = get_database()

# Display top 10 students
try:
    leaderboard = (
        supabase.table("leaderboard")
        .select("display_name, score")
        .order("score", desc=True)
        .limit(10)
        .execute()
    )

    st.sidebar.subheader("🏆 Top 10 Students")

    for i, student in enumerate(leaderboard.data, 1):
        st.sidebar.write(
            f"{i}. {student['display_name']} — {student['score']} points"
        )

except Exception as e:
    st.sidebar.warning("Scoreboard is loading.")
try:
    db = get_database()
except Exception:
    st.error("Database connection failed. Check your Streamlit Secrets.")
    st.stop()

page = st.sidebar.radio("Menu", ["Study", "Admin"])

levels = ["Technician", "General", "Amateur Extra"]

if page == "Admin":
    st.header("🔐 Admin — Add Questions")

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
                        db.table("questions").insert({
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
                        st.error("Could not save the question. Check your database settings.")

    elif password:
        st.error("Incorrect Admin password.")

else:
    st.header("📚 Practice Test")

    level = st.selectbox("Choose your license level", levels)

    try:
        questions = (
            db.table("questions")
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
        st.write("The Admin can add questions using the Admin menu.")
    else:
        if st.session_state.get("active_level") != level:
            st.session_state.active_level = level
            st.session_state.question_number = 0
            st.session_state.score = 0
            st.session_state.answered = False

        number = st.session_state.get("question_number", 0)

        if number >= len(questions):
            st.success("Practice test complete!")
            st.subheader(
                f"Your score: {st.session_state.score} / {len(questions)}"
            )

            if st.button("Start Again"):
                st.session_state.question_number = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.rerun()

        else:
            q = questions[number]

            st.progress((number + 1) / len(questions))
            st.write(f"Question {number + 1} of {len(questions)}")
            st.subheader(q["question"])

        File "/mount/src/worldwide-radio-ham-study-bot/app.py", line 144
              answer = st.radio(
                               ^
SyntaxError: '(' was never closed
                "Choose your answer:",
                
         
               
            
st.divider()
st.caption("Worldwide Radio Ham Study Bot")

import streamlit as st








questions = {
    "Technician": [
        {
            "question": "What does CQ mean?",
            "answers": [
                "Calling any station",
                "Emergency only",
                "Goodbye"
            ],
            "correct": "Calling any station",
            "explanation": "CQ is a general call to any amateur radio station."
        },
        {
            "question": "What organization regulates amateur radio in the United States?",
            "answers": ["FCC", "NASA", "FEMA"],
            "correct": "FCC",
            "explanation": "The Federal Communications Commission regulates amateur radio."
        }
    ],
    "General": [
        {
            "question": "What is the purpose of an antenna?",
            "answers": [
                "Transmit and receive radio waves",
                "Store electricity",
                "Measure temperature"
            ],
            "correct": "Transmit and receive radio waves",
            "explanation": "An antenna converts electrical signals into radio waves and vice versa."
        }
    ],
    "Amateur Extra": [
        {
            "question": "What does impedance matching help maximize?",
            "answers": [
                "Power transfer",
                "Battery size",
                "Audio volume"
            ],
            "correct": "Power transfer",
            "explanation": "Impedance matching helps transfer power efficiently."
        }
    ]
}

if "question_number" not in st.session_state:
    st.session_state.question_number = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "answered" not in st.session_state:
    st.session_state.answered = False

if st.session_state.get("selected_level") != level:
    st.session_state.selected_level = level
    st.session_state.question_number = 0
    st.session_state.score = 0
    st.session_state.answered = False
st.sidebar.title("🏆 Student Scoreboard")

player_name = st.sidebar.text_input("Enter your name")

if "player_id" not in st.session_state:
    st.session_state.player_id = str(uuid.uuid4())

if player_name.strip():
    st.sidebar.success(f"Welcome, {player_name}!")
else:
    st.sidebar.info("Enter your name to start.")
quiz = questions[level]
number = st.session_state.question_number

