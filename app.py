
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Worldwide Radio Ham Study Bot",
    page_icon="📻",
    layout="centered"
)

st.title("📻 Worldwide Radio Ham Study Bot")
st.caption("Learn, practice, and prepare for your amateur radio license.")

@st.cache_resource
def get_database():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

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

            answer = st.radio(
                "Choose your answer:",
                q["answers"],
                key=f"answer_{level}_{q['id']}"
            )

            if st.button(
                "Check Answer",
                disabled=st.session_state.get("answered", False)
            ):
                st.session_state.answered = True

                if answer == q["correct_answer"]:
                    st.session_state.score += 1

                st.rerun()

            if st.session_state.get("answered", False):
                if answer == q["correct_answer"]:
                    st.success("Correct!")
                else:
                    st.error(
                        "Incorrect. Correct answer: "
                        + q["correct_answer"]
                    )

                st.info(q.get("explanation") or "Keep studying!")

                if st.button("Next Question"):
                    st.session_state.question_number += 1
                    st.session_state.answered = False
                    st.rerun()

st.divider()
st.caption("Worldwide Radio Ham Study Bot")

import streamlit as st

st.set_page_config(
    page_title="Worldwide Radio Ham Study Bot",
    page_icon="📻",
    layout="centered"
)

st.title("📻 Worldwide Radio Ham Study Bot")
st.subheader("Amateur Radio License Practice")

st.write("Welcome! Choose your license class and test your knowledge.")

level = st.selectbox(
    "Choose your license:",
    ["Technician", "General", "Amateur Extra"]
)

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

quiz = questions[level]
number = st.session_state.question_number

if number < len(quiz):
    q = quiz[number]
    st.   st.write(f"Question {number + 1} of {len(quiz)}")     st.subheader(q["question"])      answer = st.radio(         "Select your answer:",         q["answers"],         key=f"{level}_{number}"     )      if st.button(         "Check Answer",         disabled=st.session_state.answered,         key=f"check_answer_button_{level}_{number}"     ):         st.session_state.answered = True         if answer == q["correct"]:             st.session_state.score += 1      if st.session_state.answered:         st.write("Answer checked!")progress((number + 1) / len(quiz))
     
    st.subheader(q["question"])

    answer = st.radio(
        "Select your answer:",
        q["answers"],
        key=f"{level}_{number}"
    )

    if st.button(
        "Check Answer",
        disabled=st.session_state.answered,
        key=f"check_answer_button_{level}_{number}"
    ):
        st.session_state.answered = True
        if answer == q["correct"]:
            st.session_state.score += 1

    if st.session_state.answered:
        st.write(f"Question {number + 1} of {len(quiz)}")     st.subheader(q["question"])      answer = st.radio(         "Select your answer:",         q["answers"],         key=f"{level}_{number}"     )      if st.button(         "Check Answer",         disabled=st.session_state.answered,         key=f"check_answer_button_{level}_{number}"     ):         st.session_state.answered = True         if answer == q["correct"]:             st.session_state.score += 1      if st.session_state.answered:         st.write("Answer checked!")
    st.subheader(q["question"])

    answer = st.radio(
        "Select your answer:",
        q["answers"],
        key=f"{level}_{number}"
    )

  if st.button("Check Answer", disabled=st.session_state.answered, key="check_answer_button"):
        st.session_state.answered = True
        if answer == q["correct"]:
            st.session_state.score += 1

    if st.session_state.answered:
        if answer == q["correct"]:
            st.success("Correct!")
        else:
            st.error("Not quite. The correct answer is: " + q["correct"])

        st.info(q["explanation"])

        if st.button("Next Question"):
            st.session_state.question_number += 1
            st.session_state.answered = False
            st.rerun()

else:
    st.success("Practice test complete!")
    st.write(f"Your score: {st.session_state.score} / {len(quiz)}")

    if st.button("Try Again"):
        st.session_state.question_number = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.rerun()

st.caption("Worldwide Radio Ham Study Bot")
