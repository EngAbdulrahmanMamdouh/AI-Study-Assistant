# 🎓 AI Study Assistant

An AI-powered learning companion built with **Python, Streamlit, and Google Gemini**. Upload your study materials, understand difficult topics, summarize lecture notes, and generate interactive exams.

## ✨ Features

- **📚 Study Material Upload:** Upload PDF and TXT files and extract their text.
- **💬 AI Chat:** Ask questions and get AI-powered answers based on your study materials.
- **🧠 Explain a Topic:** Get simple explanations, detailed descriptions, and practical examples.
- **📝 Smart Summarization:** Turn long lecture notes into organized summaries.
- **📋 Interactive Exam Generator:** Create exams based on your uploaded materials.
- **Multiple Exam Types:** Choose Multiple Choice, Essay Questions, or Mixed Exams.
- **🎯 Custom Difficulty:** Generate Easy, Medium, or Hard exams.
- **📊 AI-Powered Evaluation:** Automatically correct MCQs and evaluate essay answers.
- **🌍 Bilingual Support:** Get responses in English or Arabic.

## 🛠️ Tech Stack

- Python
- Streamlit
- Google Gemini API
- Google Gen AI SDK
- PyPDF
- python-dotenv

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/AI-Study-Assistant.git
cd AI-Study-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/).

**Important:** Never upload your `.env` file or expose your API key publicly.

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 📁 Project Structure

```text
AI-Study-Assistant/
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── .env  # Local only — never commit
```

## 🎯 Project Goal

The goal of this project is to make studying more interactive and efficient by combining AI-powered explanations, document understanding, automatic summarization, and personalized exam generation in one application.

## ⚠️ Notes

- Scanned PDFs may require OCR because text extraction depends on the PDF's content.
- AI-generated explanations and essay evaluations should be reviewed for accuracy.
- Gemini API availability and usage limits may affect response generation.

## 👨‍💻 Author

**Abdulrahman Mamdouh**

AI Engineering Student | Machine Learning & Deep Learning Enthusiast

[GitHub](https://github.com/YOUR_GITHUB_USERNAME)

---

⭐ If you find this project useful, consider giving it a star!