# 🔍 RozgarCheck

**An NLP-powered tool that detects bias in job descriptions before they go live.**

[![Live App](https://img.shields.io/badge/Live%20App-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://rozgarcheck.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=flat&logo=spacy&logoColor=white)](https://spacy.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

🔗 **Try it live:** [rozgarcheck.streamlit.app](https://rozgarcheck.streamlit.app)

---

## 📌 Overview

Job descriptions often contain subtle, unintentional language that discourages qualified candidates from applying — gendered wording, age-coded phrases, ableist terms, or culture-fit buzzwords that signal exclusion rather than inclusion.

**RozgarCheck** scans job postings using NLP and flags this kind of biased language in real time, helping recruiters and hiring teams write fairer, more inclusive job descriptions — before they're published.

> "Rozgar" means *employment/livelihood* in Hindi/Urdu — the name reflects the project's goal of making job opportunities more accessible and fair for everyone.

---

## ❗ The Problem

Research consistently shows biased language in job postings reduces application rates from underrepresented groups:
- Gendered words (e.g., "ninja," "rockstar," "dominant") skew applicant pools
- Age-coded terms ("young," "digital native") risk age discrimination
- Ableist phrasing ("must be able to stand for long periods" without context) excludes capable candidates
- Vague culture-fit language can mask exclusionary hiring practices

Most hiring teams don't introduce this language intentionally — they simply don't have a fast way to catch it.

---

## ✅ The Solution

RozgarCheck provides instant, automated bias detection:
1. Paste or upload a job description
2. The tool analyzes the text using NLP techniques
3. Flagged words/phrases are highlighted by bias category
4. Get a bias score and suggested alternative phrasing
5. Publish a more inclusive, legally safer job post

---

## 🚀 Features

- 🔎 **Real-time bias detection** across multiple categories (gender, age, ability, culture-fit)
- 📊 **Bias scoring system** for quick assessment of a job description
- 💡 **Suggested alternatives** for flagged words/phrases
- 🖥️ **Simple, no-login web interface** — built with Streamlit
- ⚡ **Instant results** — no waiting, no setup required for end users

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python |
| NLP Processing | spaCy, TextBlob |
| Web Framework | Streamlit |
| Deployment | Streamlit Community Cloud |
| Version Control | Git & GitHub |

---

## ⚙️ Installation & Local Setup

```bash
# Clone the repository
git clone https://github.com/anushkagandhi503/RozgarCheck.git
cd RozgarCheck

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download the spaCy language model
python -m spacy download en_core_web_sm

# Run the app
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

---

## 📂 Project Structure

RozgarCheck/
├── app.py              # Main Streamlit app — UI, layout, and app flow
├── bias_words.py        # Bias detection logic and word/phrase lexicon
├── requirements.txt     # Python dependencies
├── .gitignore            # Files/folders excluded from version control
├── LICENSE               # MIT License
└── README.md             # Project documentation

---

## 📸 Demo

<img width="1917" height="967" alt="Screenshot 2026-06-11 184611" src="https://github.com/user-attachments/assets/229ba10a-f70c-46a4-a33e-53b7ed6de5b9" />

---

## 🧠 How It Works

1. **Text preprocessing** — the input job description is cleaned and tokenized using spaCy
2. **Pattern matching** — `bias_words.py` scans the text against a curated lexicon of biased terms across categories (gender, age, ability, culture-fit)
3. **Sentiment & tone analysis** — TextBlob evaluates overall tone for additional context
4. **Scoring** — a weighted bias score is generated based on frequency and severity of flagged terms in `bias_words.py`
5. **Output** — `app.py` renders the flagged terms with category labels and suggested rewrites in the Streamlit UI

---

## 🗺️ Roadmap

- [ ] Expand bias lexicon to cover more categories (disability, nationality, religion)
- [ ] Add support for multiple languages
- [ ] Browser extension for in-platform scanning (LinkedIn, Naukri, etc.)
- [ ] Model fine-tuning using transformer-based architectures (BERT)
- [ ] API endpoint for integration into ATS (Applicant Tracking Systems)

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the bias lexicon, fix bugs, or add features:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE] file for details.

---

## 👩‍💻 Author

**Anushka Gandhi**
AI & Data Science | IIT Madras (BS) + MMCOE | Chief Engineering Officer, NeuraCryption

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin)](your-linkedin-url)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/anushkagandhi503)

---

⭐ If you find this project useful, consider giving it a star — it helps others discover it too!
