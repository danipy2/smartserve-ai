# 🤖 SmartServe AI — RAG-Powered Customer Support Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![LangChain](https://img.shields.io/badge/LangChain-0.x-1C3C3C?logo=langchain)
![Gemini](https://img.shields.io/badge/Google%20Gemini-API-8E75B2?logo=google)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-F97316)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render)

---

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Click_Here-0ea5e9)](https://smartserve-ai.onrender.com)

---

## 📌 Description

**SmartServe AI** is a RAG (Retrieval-Augmented Generation) powered customer support platform. Upload your PDF or DOCX knowledge base documents and get an intelligent chatbot that answers customer questions with **source citations**, a **confidence score (0–100%)**, and **automatic escalation** to a human agent whenever confidence drops below 60%.

---

## ⚙️ How It Works

The platform follows a full RAG pipeline:

```
📄 Upload Docs  →  ✂️ Chunk Text  →  🔢 Embed  →  🗃️ Vector Store (ChromaDB)
                                                              ↓
                                               🔍 Query  →  💬 Answer + Source + Score
```

1. **Upload** — Drop in PDF or DOCX files via the UI
2. **Chunk** — Documents are split into semantic chunks
3. **Embed** — Chunks are embedded using Google Gemini embeddings
4. **Vector Store** — Embeddings are indexed in ChromaDB for fast retrieval
5. **Query** — User questions are matched to the most relevant chunks
6. **Answer** — Gemini generates a grounded response with citations and a confidence score

---

## ✨ Features

- 📎 **Source Citations** — Every answer references the exact document sections used
- 📊 **Confidence Scoring** — Each response includes a 0–100% confidence score
- 🚨 **Auto Escalation** — Automatically flags low-confidence answers (< 60%) for human review
- 📁 **Multi-Format Support** — Supports PDF and DOCX document uploads
- 💬 **Conversational Memory** — Maintains context across multi-turn conversations
- 🗄️ **Conversation Logging** — All interactions stored in SQLite for audit and review

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.11** | Core language |
| **LangChain** | RAG pipeline & retrieval chain |
| **Google Gemini** | LLM + embedding model |
| **ChromaDB** | Vector database for semantic search |
| **Streamlit** | Web application frontend |
| **SQLite** | Conversation & escalation logging |
| **Render** | Cloud deployment platform |

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> Get your key at [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/danipy2/smartserve-ai.git
cd smartserve-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your environment variable
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 4. Launch the app
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`.

---

## 🗂️ Project Structure

```
smartserve-ai/
├── streamlit_app.py       # Main application entry point
├── pages/                 # Multi-page Streamlit views
│   ├── upload.py          # Document upload & indexing UI
│   ├── chat.py            # Chatbot interface
│   └── escalations.py     # Human escalation review panel
├── core/                  # RAG pipeline logic
│   ├── rag.py             # Retrieval chain setup
│   ├── embedder.py        # Document chunking & embedding
│   └── escalation.py      # Confidence scoring & escalation logic
├── data/                  # ChromaDB vector store & SQLite DB
├── config.py              # App-wide configuration constants
└── requirements.txt       # Python dependencies
```

---

## 👤 Author

**Daniel Molla**  
GitHub: [@danipy2](https://github.com/danipy2)
