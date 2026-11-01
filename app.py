
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

    st.progress((number + 1) / len(quiz))
    st.write(f"Question {number + 1} of {len(quiz)}")
    st.subheader(q["question"])

    answer = st.radio(
        "Select your answer:",
        q["answers"],
        key=f"{level}_{number}"
    )

    if st.button("Check Answer", disabled=st.session_state.answered):
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
