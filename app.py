
elif page == "Admin":
    st.header("🔐 Admin — Add Questions")

    password = st.text_input("Admin password", type="password")

    if password == st.secrets["ADMIN_PASSWORD"]:
        st.success("Admin access granted.")

        st.subheader("📂 Import Questions from CSV")

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

                            if (
                                row["level"] not in levels
                                or not isinstance(answers, list)
                                or len(answers) != 4
                                or row["correct_answer"] not in answers
                            ):
                                raise ValueError(
                                    "A question has an invalid level, "
                                    "answer list, or correct answer."
                                )

                            records.append({
                                "level": row["level"],
                                "question": row["question"],
                                "answers": answers,
                                "correct_answer": row["correct_answer"],
                                "explanation": row["explanation"]
                            })

                        if records:
                            supabase.table("questions").insert(records).execute()
                            st.success(
                                f"Imported {len(records)} questions successfully!"
                            )
                        else:
                            st.warning("The CSV contains no questions.")

                except Exception as e:
                    st.error(f"Import failed: {e}")

        st.divider()
        st.subheader("✍️ Add One Question")

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
                        st.error("Could not save the question. Check database permissions.")

    elif password:
        st.error("Incorrect Admin password.")
