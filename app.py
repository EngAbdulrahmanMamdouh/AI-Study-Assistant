
import os
import json
import re
import uuid

import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader


# ==========================================
# 1. CONFIGURATION
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.6-flash"

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide"
)


# ==========================================
# 2. CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1120, #111827);
    color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    max-width: 1100px;
}

h1, h2, h3, p, label {
    color: #f8fafc;
}

.stTextArea textarea,
.stTextInput input,
.stNumberInput input {
    background-color: #1e293b;
    color: white;
    border-radius: 12px;
}

.stButton button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
}

.stButton button:hover {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
    color: white;
    border: none;
}

.stRadio label {
    color: #f8fafc !important;
}

div[data-testid="stForm"] {
    background-color: rgba(30, 41, 59, 0.45);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px;
}

div[data-testid="stMetric"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    padding: 15px;
    border-radius: 12px;
}

hr {
    border-color: #334155;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. HEADER
# ==========================================

st.title("🎓 AI Study Assistant")

st.caption(
    "Your intelligent learning companion — upload, understand, and learn."
)


# ==========================================
# 4. SIDEBAR SETTINGS
# ==========================================

with st.sidebar:

    st.header("⚙️ Settings")

    language = st.selectbox(
        "Response Language",
        ["English", "العربية"]
    )

    task = st.selectbox(
        "Choose a Tool",
        [
            "AI Chat",
            "Explain a Topic",
            "Summarize Notes",
            "Generate MCQ Quiz"
        ]
    )

    st.divider()

    st.caption("Powered by Gemini AI")


# ==========================================
# 5. FILE UPLOAD
# ==========================================

st.subheader("📚 Upload Your Study Material")

uploaded_file = st.file_uploader(
    "Upload your lecture or notes",
    type=["pdf", "txt"],
    help="Supported formats: PDF and TXT"
)

lecture_text = ""

if uploaded_file is not None:

    try:

        if uploaded_file.name.lower().endswith(".pdf"):

            reader = PdfReader(uploaded_file)

            pages_text = [
                page.extract_text() or ""
                for page in reader.pages
            ]

            lecture_text = "\n".join(pages_text)

            st.success(
                f"PDF uploaded successfully — {len(reader.pages)} pages."
            )

        else:

            lecture_text = uploaded_file.getvalue().decode(
                "utf-8-sig",
                errors="replace"
            )

            st.success("TXT file uploaded successfully.")

        st.info(
            f"Extracted {len(lecture_text):,} characters."
        )

        if not lecture_text.strip():

            st.warning(
                "No readable text was found. "
                "This may be a scanned PDF."
            )

    except Exception as error:

        st.error(f"Could not read the uploaded file: {error}")


# ==========================================
# 6. ADDITIONAL NOTES
# ==========================================

st.subheader("✍️ Additional Notes")

manual_text = st.text_area(
    "You can also add text or specific instructions here:",
    placeholder="Write your notes or questions...",
    height=130
)

study_material = "\n\n".join(
    part for part in [lecture_text, manual_text]
    if part.strip()
)

st.divider()


# ==========================================
# 7. GEMINI FUNCTIONS
# ==========================================

def generate_response(prompt, json_mode=False):

    if not API_KEY:

        st.error(
            "Gemini API key is missing. Check your .env file."
        )

        return None

    try:

        client = genai.Client(api_key=API_KEY)

        if json_mode:

            config = genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
                max_output_tokens=8192
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config
            )

        else:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

        return response.text

    except Exception as error:

        st.error(f"Gemini API Error: {error}")

        return None


def parse_json_response(response_text):

    if not response_text:
        return None

    try:

        return json.loads(response_text)

    except json.JSONDecodeError:

        # Handle responses wrapped in Markdown code blocks

        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            response_text.strip(),
            flags=re.IGNORECASE
        )

        try:

            return json.loads(cleaned)

        except json.JSONDecodeError:

            # Try extracting the JSON object

            match = re.search(
                r"\{.*\}",
                cleaned,
                re.DOTALL
            )

            if match:

                try:
                    return json.loads(match.group())

                except json.JSONDecodeError:
                    return None

            return None


# ==========================================
# 8. AI CHAT
# ==========================================

if task == "AI Chat":

    st.subheader("💬 Chat with Your Study Assistant")

    if "messages" not in st.session_state:

        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    user_question = st.chat_input(
        "Ask anything about your study material..."
    )

    if user_question:

        st.session_state.messages.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):

            st.markdown(user_question)

        context = (
            study_material[:30000]
            if study_material
            else "No study material has been uploaded."
        )

        prompt = f"""
You are a helpful AI study assistant.

Answer in {language}.

Use the following study material when relevant.

Study Material:
{context}

Conversation:
{st.session_state.messages[-10:]}

Student Question:
{user_question}
"""

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                answer = generate_response(prompt)

            if answer:

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })


# ==========================================
# 9. EXPLAIN A TOPIC
# ==========================================

elif task == "Explain a Topic":

    st.subheader("🧠 Explain a Topic")

    topic = st.text_input(
        "What topic would you like explained?"
    )

    if st.button("Explain Topic"):

        if topic:

            prompt = f"""
Explain this topic in {language} in a simple educational way.

Topic: {topic}

Study Material:
{study_material[:30000]}

Include:

1. Simple definition
2. Detailed explanation
3. Practical examples
4. Key points to remember
"""

            with st.spinner("Preparing explanation..."):

                result = generate_response(prompt)

            if result:
                st.markdown(result)

        else:

            st.warning("Please enter a topic first.")


# ==========================================
# 10. SUMMARIZE NOTES
# ==========================================

elif task == "Summarize Notes":

    st.subheader("📝 Summarize Your Notes")

    if st.button("Generate Summary"):

        if study_material.strip():

            prompt = f"""
Summarize the following study material in {language}.

Organize the summary using headings and bullet points.

Highlight important definitions and key concepts.

Study Material:
{study_material[:30000]}
"""

            with st.spinner("Summarizing your material..."):

                result = generate_response(prompt)

            if result:
                st.markdown(result)

        else:

            st.warning(
                "Please upload a PDF/TXT file or enter notes."
            )


# ==========================================
# 11. EXAM FUNCTIONS
# ==========================================

def generate_exam_questions(
    material,
    question_count,
    difficulty,
    exam_type,
    language
):

    if exam_type == "Multiple Choice":

        question_instructions = """
Generate only multiple-choice questions.

Each question must contain:
- question
- type: "mcq"
- options: an object with A, B, C, D
- correct_answer: A, B, C, or D
- explanation

Do not generate essay questions.
"""

    elif exam_type == "Essay Questions":

        question_instructions = """
Generate only essay questions.

Each question must contain:
- question
- type: "essay"
- sample_answer: a model answer
- grading_criteria: criteria for evaluating the answer

Do not generate multiple-choice questions.
"""

    else:

        question_instructions = """
Generate a mixed exam containing both question types.

Use approximately half multiple-choice questions
and half essay questions.

Each MCQ must contain:
- question
- type: "mcq"
- options: an object with A, B, C, D
- correct_answer: A, B, C, or D
- explanation

Each essay question must contain:
- question
- type: "essay"
- sample_answer: a model answer
- grading_criteria: criteria for evaluating the answer
"""

    prompt = f"""
You are an expert university examiner.

Create exactly {question_count} exam questions.

Exam difficulty: {difficulty}

Response language: {language}

Use ONLY the supplied study material.
Do not introduce facts that are not supported by the material.

{question_instructions}

IMPORTANT RULES:

1. Questions must be clear and educational.
2. Avoid duplicate questions.
3. Cover different topics in the material.
4. MCQ options must be meaningful and distinct.
5. Only one MCQ option must be correct.
6. Do not include answers outside the JSON structure.
7. Return valid JSON only.
8. Do not use Markdown code fences.

Required JSON format:

{{
    "questions": [
        {{
            "question": "Question text",
            "type": "mcq",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "explanation": "Explanation"
        }},
        {{
            "question": "Essay question",
            "type": "essay",
            "sample_answer": "Model answer",
            "grading_criteria": "Grading criteria"
        }}
    ]
}}

Study Material:
{material[:30000]}
"""

    response = generate_response(
        prompt,
        json_mode=True
    )

    if not response:
        return None

    data = parse_json_response(response)

    if not isinstance(data, dict):
        st.error("Could not read the generated exam. Please try again.")
        return None

    questions = data.get("questions")

    if not isinstance(questions, list) or not questions:
        st.error("Gemini did not return valid exam questions.")
        return None

    # Validate and normalize questions

    valid_questions = []

    for question in questions:

        if not isinstance(question, dict):
            continue

        q_type = question.get("type")

        if q_type == "mcq":

            options = question.get("options", {})

            if not isinstance(options, dict):
                continue

            if not all(
                key in options
                for key in ["A", "B", "C", "D"]
            ):
                continue

            correct = str(
                question.get("correct_answer", "")
            ).strip().upper()

            if correct not in ["A", "B", "C", "D"]:
                continue

            valid_questions.append(question)

        elif q_type == "essay":

            valid_questions.append(question)

    if not valid_questions:

        st.error("No valid questions were generated.")

        return None

    if len(valid_questions) < question_count:

        st.warning(
            f"Requested {question_count} questions, "
            f"but Gemini generated {len(valid_questions)} valid questions."
        )

    return valid_questions


def evaluate_essay_answers(essay_submissions, language):

    if not essay_submissions:
        return []

    prompt = f"""
You are a fair and professional university examiner.

Evaluate the student's essay answers.

Evaluation language: {language}

Each answer must receive a score from 0 to 10.

Evaluate based on:
- Accuracy
- Understanding
- Completeness
- Relevance to the question

Be fair. Accept alternative correct explanations.

Return valid JSON only, without Markdown.

Required format:

{{
    "evaluations": [
        {{
            "index": 0,
            "score": 8,
            "feedback": "Detailed feedback",
            "strengths": ["Point 1"],
            "improvements": ["Point 1"]
        }}
    ]
}}

Student submissions:

{json.dumps(essay_submissions, ensure_ascii=False)}
"""

    response = generate_response(
        prompt,
        json_mode=True
    )

    if not response:
        return None

    data = parse_json_response(response)

    if not isinstance(data, dict):
        st.error("Could not read the essay evaluation.")
        return None

    evaluations = data.get("evaluations", [])

    if not isinstance(evaluations, list):
        return None

    return evaluations


# ==========================================
# 12. GENERATE MCQ QUIZ / EXAM
# ==========================================

if task == "Generate MCQ Quiz":

    st.subheader("📝 Exam Center")

    st.write(
        "Create your own exam from your uploaded study material."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        exam_type = st.selectbox(
            "Exam Type",
            [
                "Multiple Choice",
                "Essay Questions",
                "Mixed Exam"
            ]
        )

    with col2:

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        )

    number_of_questions = st.number_input(
        "Number of Questions",
        min_value=1,
        max_value=100,
        value=10,
        step=1
    )

    if number_of_questions >= 50:

        st.warning(
            "Large exams may take longer to generate. "
            "If generation fails, try a smaller number of questions."
        )

    st.divider()

    if st.button(
        "🚀 Generate Exam",
        use_container_width=True
    ):

        if not study_material.strip():

            st.warning(
                "Please upload a PDF/TXT file or enter study notes first."
            )

        else:

            # Clear previous exam

            st.session_state.pop("exam_data", None)
            st.session_state.pop("exam_result", None)

            with st.spinner(
                "Creating your exam... Please wait."
            ):

                questions = generate_exam_questions(
                    material=study_material,
                    question_count=int(number_of_questions),
                    difficulty=difficulty,
                    exam_type=exam_type,
                    language=language
                )

            if questions:

                st.session_state.exam_data = {
                    "id": str(uuid.uuid4()),
                    "questions": questions,
                    "exam_type": exam_type,
                    "difficulty": difficulty
                }

                st.success(
                    f"Your exam is ready! "
                    f"{len(questions)} questions generated."
                )

                st.rerun()

    # ======================================
    # 13. DISPLAY INTERACTIVE EXAM
    # ======================================

    exam_data = st.session_state.get("exam_data")

    exam_result = st.session_state.get("exam_result")

    if exam_data and not exam_result:

        questions = exam_data["questions"]

        exam_id = exam_data["id"]

        st.divider()

        st.subheader("📋 Your Exam")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Questions", len(questions))

        with col2:
            st.metric("Difficulty", exam_data["difficulty"])

        with col3:
            st.metric("Exam Type", exam_data["exam_type"])

        st.info(
            "Answer all questions, then submit your exam. "
            "Correct answers will appear only after submission."
        )

        with st.form(
            key=f"exam_form_{exam_id}"
        ):

            submitted_answers = {}

            for index, question in enumerate(questions):

                st.divider()

                q_type = question.get("type")

                st.markdown(
                    f"### Question {index + 1}"
                )

                st.markdown(
                    question.get("question", "")
                )

                if q_type == "mcq":

                    options = question["options"]

                    choices = [
                        f"{key}. {options[key]}"
                        for key in ["A", "B", "C", "D"]
                    ]

                    selected = st.radio(
                        "Choose your answer:",
                        choices,
                        index=None,
                        key=f"answer_{exam_id}_{index}"
                    )

                    submitted_answers[index] = selected

                elif q_type == "essay":

                    answer = st.text_area(
                        "Write your answer:",
                        placeholder="Type your answer here...",
                        height=150,
                        key=f"answer_{exam_id}_{index}"
                    )

                    submitted_answers[index] = answer

            st.divider()

            submit_exam = st.form_submit_button(
                "📤 Submit Exam",
                use_container_width=True
            )

        # ==================================
        # 14. PROCESS EXAM SUBMISSION
        # ==================================

        if submit_exam:

            mcq_correct = 0
            mcq_total = 0

            essay_submissions = []

            question_results = []

            unanswered = 0

            for index, question in enumerate(questions):

                student_answer = submitted_answers.get(index)

                if question["type"] == "mcq":

                    mcq_total += 1

                    selected_key = None

                    if student_answer:

                        selected_key = student_answer.split(
                            ".",
                            1
                        )[0].strip().upper()

                    else:

                        unanswered += 1

                    correct_key = question[
                        "correct_answer"
                    ].strip().upper()

                    is_correct = (
                        selected_key == correct_key
                    )

                    if is_correct:
                        mcq_correct += 1

                    question_results.append({
                        "index": index,
                        "type": "mcq",
                        "student_answer": selected_key,
                        "correct_answer": correct_key,
                        "is_correct": is_correct
                    })

                elif question["type"] == "essay":

                    if not student_answer or not student_answer.strip():

                        unanswered += 1

                    essay_submissions.append({
                        "index": index,
                        "question": question["question"],
                        "student_answer": student_answer or "",
                        "sample_answer": question.get(
                            "sample_answer",
                            ""
                        ),
                        "grading_criteria": question.get(
                            "grading_criteria",
                            ""
                        )
                    })

            # Evaluate essay questions

            essay_evaluations = []

            if essay_submissions:

                with st.spinner(
                    "Gemini is evaluating your essay answers..."
                ):

                    essay_evaluations = evaluate_essay_answers(
                        essay_submissions,
                        language
                    )

            if essay_evaluations is None:

                essay_evaluations = []

                st.warning(
                    "Essay evaluation failed. "
                    "Your MCQ answers have still been corrected."
                )

            # Calculate score

            essay_scores = {}

            for evaluation in essay_evaluations:

                try:

                    index = int(evaluation["index"])

                    score = max(
                        0,
                        min(
                            10,
                            float(evaluation["score"])
                        )
                    )

                    essay_scores[index] = {
                        "score": score,
                        "feedback": evaluation.get(
                            "feedback",
                            ""
                        ),
                        "strengths": evaluation.get(
                            "strengths",
                            []
                        ),
                        "improvements": evaluation.get(
                            "improvements",
                            []
                        )
                    }

                except (ValueError, TypeError, KeyError):
                    continue

            # Every question has equal weight.
            # MCQ = 10/10 if correct, otherwise 0/10.
            # Essay = AI score out of 10.

            total_score = 0.0
            graded_questions = 0

            for index, question in enumerate(questions):

                if question["type"] == "mcq":

                    result = next(
                        (
                            item for item in question_results
                            if item["index"] == index
                        ),
                        None
                    )

                    if result:

                        total_score += (
                            10 if result["is_correct"] else 0
                        )

                        graded_questions += 1

                elif question["type"] == "essay":

                    if index in essay_scores:

                        total_score += essay_scores[index]["score"]

                        graded_questions += 1

            if graded_questions:

                percentage = (
                    total_score / (graded_questions * 10)
                ) * 100

            else:

                percentage = 0

            # Save results

            st.session_state.exam_result = {
                "total_score": total_score,
                "graded_questions": graded_questions,
                "total_questions": len(questions),
                "percentage": percentage,
                "mcq_correct": mcq_correct,
                "mcq_total": mcq_total,
                "essay_scores": essay_scores,
                "question_results": question_results,
                "unanswered": unanswered
            }

            st.rerun()

    # ======================================
    # 15. EXAM RESULTS AND CORRECTION
    # ======================================

    exam_result = st.session_state.get("exam_result")

    if exam_result and exam_data:

        st.divider()

        st.subheader("🏆 Exam Results")

        percentage = exam_result["percentage"]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Final Score",
                f"{exam_result['total_score']:.1f} / "
                f"{exam_result['graded_questions'] * 10}"
            )

        with col2:

            st.metric(
                "Percentage",
                f"{percentage:.1f}%"
            )

        with col3:

            st.metric(
                "Correct MCQs",
                f"{exam_result['mcq_correct']} / "
                f"{exam_result['mcq_total']}"
            )

        st.progress(
            int(max(0, min(100, percentage)))
        )

        if percentage >= 85:

            st.success("Excellent work! 🌟")

        elif percentage >= 70:

            st.success("Good job! Keep improving.")

        elif percentage >= 50:

            st.warning("You passed, but there is room to improve.")

        else:

            st.error("Keep studying and try again!")

        if exam_result["unanswered"]:

            st.warning(
                f"You left {exam_result['unanswered']} "
                "question(s) unanswered."
            )

        st.divider()

        st.subheader("📖 Detailed Correction")

        questions = exam_data["questions"]

        for index, question in enumerate(questions):

            with st.expander(
                f"Question {index + 1}: "
                f"{question['question'][:70]}"
            ):

                if question["type"] == "mcq":

                    result = next(
                        (
                            item
                            for item in exam_result["question_results"]
                            if item["index"] == index
                        ),
                        None
                    )

                    options = question["options"]

                    if result:

                        student_key = result["student_answer"]

                        correct_key = result["correct_answer"]

                        if result["is_correct"]:

                            st.success("Correct answer!")

                        else:

                            st.error("Incorrect answer.")

                        if student_key:

                            st.write(
                                "**Your answer:** "
                                f"{student_key}. {options[student_key]}"
                            )

                        else:

                            st.write("**Your answer:** Not answered")

                        st.write(
                            "**Correct answer:** "
                            f"{correct_key}. {options[correct_key]}"
                        )

                        st.info(
                            question.get(
                                "explanation",
                                "No explanation provided."
                            )
                        )

                elif question["type"] == "essay":

                    essay_result = exam_result[
                        "essay_scores"
                    ].get(index)

                    student_answer = st.session_state.get(
                        f"answer_{exam_data['id']}_{index}",
                        ""
                    )

                    st.write("**Your answer:**")

                    st.write(
                        student_answer if student_answer else "Not answered"
                    )

                    if essay_result:

                        st.metric(
                            "Your essay score",
                            f"{essay_result['score']:.1f} / 10"
                        )

                        st.write("**Examiner feedback:**")

                        st.write(
                            essay_result["feedback"]
                        )

                        if essay_result["strengths"]:

                            st.write("**Strengths:**")

                            for item in essay_result["strengths"]:
                                st.write(f"- {item}")

                        if essay_result["improvements"]:

                            st.write("**Areas to improve:**")

                            for item in essay_result["improvements"]:
                                st.write(f"- {item}")

                    else:

                        st.warning(
                            "This essay answer was not evaluated."
                        )

                    with st.expander("View Model Answer"):

                        st.write(
                            question.get(
                                "sample_answer",
                                "No model answer available."
                            )
                        )

        st.divider()

        if st.button(
            "🔄 Start a New Exam",
            use_container_width=True
        ):

            st.session_state.pop("exam_data", None)
            st.session_state.pop("exam_result", None)

            st.rerun()
