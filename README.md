# 🎓 JEE Admission Counselor AI

An AI-powered admission counseling platform that combines **Machine Learning, Retrieval-Augmented Generation (RAG), FAISS Vector Search, and Groq LLMs** to provide personalized college recommendations, admission trend analysis, and intelligent responses using **JoSAA counselling data (2018–2025).**

---

## ✨ Features

- 🎯 College recommendations based on JEE rank, category, and preferred branch
- 📈 Admission trend analysis using historical JoSAA data (2018–2025)
- 🤖 AI chatbot powered by Groq LLM + RAG
- 🔍 Semantic search using FAISS vector database
- 📊 Personalized admission insights
- 💬 Natural language query support

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- LangChain
- FAISS
- Sentence Transformers
- Groq API
- HuggingFace Embeddings

---

## 📂 Project Structure

```text
jee-admission-counselor/
│
├── app.py
├── data/
├── models/
├── assets/
│   └── screenshots/
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 📸 Application Screenshots

### 🏠 Home Page

The landing page of the AI-powered admission counseling platform.

![Home Page](assets/screenshots/homepage.jpeg)

---

### 🎯 College Recommendation

Personalized college recommendations based on JEE rank, category, and preferred branch.

![College Recommendation](assets/screenshots/recommendations.jpeg)

---

### 📈 Trend Analysis

Historical admission trend analysis using JoSAA data (2018–2025).

![Trend Analysis](assets/screenshots/trend_analysis.jpeg)

### 🏠 Home Page

![Home](assets/screenshots/home.png)

---

### 🎯 College Recommendation

![Recommendation](assets/screenshots/recommendation.png)

---

### 📈 Trend Analysis

![Trend](assets/screenshots/trend_analysis.png)

---

### 🤖 AI Chatbot

![Chatbot](assets/screenshots/chatbot.png)

---

### ⚠️ Edge Case Handling

![No Results](assets/screenshots/no_results.png)

---

## 🚀 Installation

```bash
git clone <repository-url>
cd jee-admission-counselor

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

python -m streamlit run app.py
```

---

## 📊 Dataset

- JoSAA Counselling Data (2018–2025)
- Historical opening and closing ranks
- IITs
- NITs
- IIITs
- Branch-wise admission data

---

## 🔮 Future Improvements

- College comparison
- Branch comparison
- Admission probability prediction
- Downloadable counselling report (PDF)
- Dream / Target / Safe college categorization

---

## 👩‍💻 Author

**Keyura Sritha**

B.Tech CSE | AI & Machine Learning Enthusiast
