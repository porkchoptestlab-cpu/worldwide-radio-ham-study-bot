```python
import streamlit as st
import hashlib
import pandas as pd
import re
from supabase import create_client

st.set_page_config(
    page_title="Worldwide Radio Ham Study Bot",
    page_icon="📻"
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
    supabase = get_database()
except Exception:
    st.error("Database connection failed. Check your Streamlit Secrets.")
    st.stop()


levels = ["Technician", "General", "Amateur Extra"]


def normalize_header(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def find_column(columns, possible_names):
    normalized = {
        normalize_header(column): column
        for column in columns
    }

    for name in possible_names:
        match = normalized.get(normalize_header(name))
        if match is not None:
            return match

    return None


def convert_correct_answer(value, answers):
    value = str(value).strip()

    # Correct answer is a letter, such as A, B, C, or D.
    match = re.match(r"^[\(\[]?([A-D])[\)\].:\s]*$", value, re.I)

    if match:
        index = "ABCD".index(match.group(1).upper())
        return answers[index]

    # Correct answer is already the full answer text.
    for answer in answers:
        if value.strip().casefold() == answer.strip().casefold():
            return answer

    return None


# Student name and persistent scoreboard identity
st.sidebar.title("🏆 Student Scoreboard")
player_name = st.sidebar.text_input("Enter your name")

player_id = None

if player_name.strip():
    normalized_name = player_name.strip().lower()
    player_id = hashlib.sha256(
        normalized_name.encode()
    ).hexdigest()

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
                f"{i}. {student['display_name']} — "
                f"{student['score']} points"
            )
    else:
        st.sidebar.write("No scores yet. Be the first!")

except Exception:
    st.sidebar.warning("Could not load scoreboard.")


page = st.sidebar.radio(
    "Menu",
    ["Study", "Practice Test", "Admin"]
)


# --------------------------------------------------
# STUDY PAGE
# --------------------------------------------------

if page == "Study":
    st.header("📚 Study")
    st.write("Choose Practice Test to begin studying.")
    st.write("Available license levels:")

    for level_name in levels:
        st.write(f"• {level_name}")


# --------------------------------------------------
# ADMIN PAGE
# --------------------------------------------------

elif page == "Admin":
    st.header("🔐 Admin")

    password = st.text_input(
        "Admin password",
        type="password"
    )

    if password == st.secrets["ADMIN_PASSWORD"]:
        st.success("Admin access granted.")

        st.divider()
        st.subheader("➕ Add a Single Question")

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
                if (
                    not question.strip()
                    or not all(x.strip() for x in answers)
                ):
                    st.error(
                        "Please fill in the question and all four answers."
                    )
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
                        st.error(
                            "Could not save question. "
                            "Check database permissions."
                        )

        # CSV IMPORT
        st.divider()
        st.subheader("📂 Import Questions from CSV")

        st.write(
            "Upload a question-pool CSV file. "
            "You can import Technician, General, or Amateur Extra questions."
        )

        csv_level = st.selectbox(
            "Choose the license level for this file",
            levels,
            key="csv_level"
        )

        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            key="question_csv"
        )

        if uploaded_file is not None:
            try:
                df = pd.read_csv(
                    uploaded_file,
                    dtype=str,
                    keep_default_na=False
                )

                if df.empty:
                    st.error("This CSV file has no questions.")
                else:
                    columns = list(df.columns)

                    st.write("CSV preview:")
                    st.dataframe(df.head(5), use_container_width=True)

                    st.write("Match the CSV columns to the question fields.")

                    question_guess = find_column(
                        columns,
                        ["question", "question_text", "questiontext"]
                    )

                    a_guess = find_column(
                        columns,
                        ["a", "answer_a", "answera", "option_a", "choice_a"]
                    )

                    b_guess = find_column(
                        columns,
                        ["b", "answer_b", "answerb", "option_b", "choice_b"]
                    )

                    c_guess = find_column(
                        columns,
                        ["c", "answer_c", "answerc", "option_c", "choice_c"]
                    )

                    d_guess = find_column(
                        columns,
                        ["d", "answer_d", "answerd", "option_d", "choice_d"]
                    )

                    correct_guess = find_column(
                        columns,
                        [
                            "correct_letter",
                            "correct_answer",
                            "correct",
                            "answer_key",
                            "answer"
                        ]
                    )

                    explanation_guess = find_column(
                        columns,
                        ["explanation", "explain", "notes"]
                    )

                    no_column = "(Not available)"

                    def column_options():
                        return [no_column] + columns

                    def default_index(guess):
                        if guess in columns:
                            return columns.index(guess) + 1
                        return 0

                    question_col = st.selectbox(
                        "Question column",
                        column_options(),
                        index=default_index(question_guess)
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        a_col = st.selectbox(
                            "Answer A column",
                            column_options(),
                            index=default_index(a_guess)
                        )

                        b_col = st.selectbox(
                            "Answer B column",
                            column_options(),
                            index=default_index(b_guess)
                        )

                    with col2:
                        c_col = st.selectbox(
                            "Answer C column",
                            column_options(),
                            index=default_index(c_guess)
                        )

                        d_col = st.selectbox(
                            "Answer D column",
                            column_options(),
                            index=default_index(d_guess)
                        )

                    correct_col = st.selectbox(
                        "Correct answer column",
                        column_options(),
                        index=default_index(correct_guess)
                    )

                    explanation_col = st.selectbox(
                        "Explanation column (optional)",
                        column_options(),
                        index=default_index(explanation_guess)
                    )

                    required_columns = [
                        question_col,
                        a_col,
                        b_col,
                        c_col,
                        d_col,
                        correct_col
                    ]

                    if no_column in required_columns:
                        st.warning(
                            "Select a column for the question, "
                            "all four answers, and correct answer."
                        )

                    else:
                        preview_rows = []
                        valid_rows = []
                        invalid_count = 0

                        for _, row in df.iterrows():
                            question_text = str(
                                row[question_col]
                            ).strip()

                            answers = [
                                str(row[a_col]).strip(),
                                str(row[b_col]).strip(),
                                str(row[c_col]).strip(),
                                str(row[d_col]).strip()
                            ]

                            correct_answer = convert_correct_answer(
                                row[correct_col],
                                answers
                            )

                            if (
                                not question_text
                                or not all(answers)
                                or correct_answer is None
                            ):
                                invalid_count += 1
                                continue

                            explanation = ""

                            if explanation_col != no_column:
                                explanation = str(
                                    row[explanation_col]
                                ).strip()

                            record = {
                                "level": csv_level,
                                "question": question_text,
                                "answers": answers,
                                "correct_answer": correct_answer,
                                "explanation": explanation
                            }

                            valid_rows.append(record)

                            if len(preview_rows) < 5:
                                preview_rows.append({
                                    "Question": question_text,
                                    "Correct answer": correct_answer
                                })

                        st.write("Import preview:")
                        st.dataframe(
                            pd.DataFrame(preview_rows),
                            use_container_width=True
                        )

                        st.write(f"Valid questions: {len(valid_rows)}")
                        st.write(f"Rows skipped: {invalid_count}")

                        if st.button(
                            "Import Questions into Supabase",
                            disabled=len(valid_rows) == 0
                        ):
                            try:
                                # Read existing questions in pages.
                                existing_questions = set()
                                start = 0

                                while True:
                                    result = (
                                        supabase.table("questions")
                                        .select("question")
                                        .eq("level", csv_level)
                                        .range(start, start + 999)
                                        .execute()
                                    )

                                    batch = result.data or []

                                    for item in batch:
                                        existing_questions.add(
                                            item["question"].strip().casefold()
                                        )

                                    if len(batch) < 1000:
                                        break

                                    start += 1000

                                new_questions = []
                                duplicate_count = 0

                                for record in valid_rows:
                                    key = record["question"].strip().casefold()

                                    if key in existing_questions:
                                        duplicate_count += 1
                                        continue

                                    existing_questions.add(key)
                                    new_questions.append(record)

                                imported_count = 0

                                # Insert in batches of 100.
                                for i in range(0, len(new_questions), 100):
                                    batch = new_questions[i:i + 100]

                                    supabase.table("questions").insert(
                                        batch
                                    ).execute()

                                    imported_count += len(batch)

                                st.success(
                                    f"Import complete! "
                                    f"{imported_count} questions added."
                                )

                                st.info(
                                    f"{duplicate_count} duplicate questions "
                                    f"were skipped."
                                )

                                if invalid_count:
                                    st.warning(
                                        f"{invalid_count} invalid rows "
                                        f"were skipped."
                                    )

                            except Exception as error:
                                st.error(
                                    "Import failed. Check your Supabase "
                                    "permissions and database connection."
                                )
                                st.caption(str(error))

            except Exception as error:
                st.error(
                    "Could not read this CSV file. "
                    "Make sure it is a valid CSV."
                )
                st.caption(str(error))

    elif password:
        st.error("Incorrect Admin password.")


# --------------------------------------------------
# PRACTICE TEST PAGE
# --------------------------------------------------

else:
    st.header("📝 Practice Test")

    level = st.selectbox(
        "Choose your license level",
        levels
    )

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

            # Save the student's best score permanently.
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

                    best_score = max(
                        old_score,
                        st.session_state.score
                    )

                    supabase.table("leaderboard").upsert({
                        "player_id": player_id,
                        "display_name": player_name.strip(),
                        "score": best_score
                    }, on_conflict="player_id").execute()

                    st.session_state.completion_saved = True

                    st.success(
                        "Your score has been saved to the leaderboard!"
                    )

                except Exception:
                    st.error(
                        "Your score could not be saved. "
                        "Check leaderboard permissions."
                    )

            elif not player_id:
                st.warning(
                    "Enter your name in the sidebar to save your score."
                )

            if st.button("Start Again"):
                st.session_state.question_number = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.session_state.completion_saved = False
                st.rerun()

        else:
            q = questions[number]

            st.progress((number + 1) / len(questions))

            st.write(
                f"Question {number + 1} of {len(questions)}"
            )

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
                    st.error(
                        "Please enter your name in the sidebar first."
                    )
                else:
                    st.session_state.answered = True

                    if answer == q["correct_answer"]:
                        st.session_state.score += 1

            if st.session_state.answered:
                if answer == q["correct_answer"]:
                    st.success("Correct!")
                else:
                    st.error(
                        "Incorrect. Correct answer: "
                        + q["correct_answer"]
                    )

                if q.get("explanation"):
                    st.info(q["explanation"])

                if st.button(
                    "Next Question",
                    key=f"next_{level}_{number}"
                ):
                    st.session_state.question_number += 1
                    st.session_state.answered = False
                    st.rerun()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Worldwide Radio Ham Study Bot")
st.caption("Created by Porkchop")
```
