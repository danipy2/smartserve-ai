# 🤖 SmartServe AI

**Intelligent Customer Support Agent Platform**

An AI-powered platform that enables businesses to create intelligent chatbots from their own documents using RAG (Retrieval-Augmented Generation). Upload your FAQs, manuals, and documents — SmartServe AI builds a smart assistant that answers customer questions accurately, with confidence scoring and automatic human escalation.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green?logo=chainlink)
![Gemini](https://img.shields.io/badge/Gemini_AI-2.0_Flash-orange?logo=google)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-red?logo=streamlit)

---

## ✨ Features

- **📄 Document Upload** — Upload PDF, TXT, or DOCX files to build your knowledge base
- **🧠 RAG Pipeline** — Automatic document chunking, embedding, vector storage, and semantic retrieval
- **💬 AI Chat** — Natural language Q&A powered by Google Gemini with conversation memory
- **🎯 Confidence Scoring** — AI self-evaluates answer confidence on every response
- **🚨 Smart Escalation** — Low-confidence answers are flagged for human agent review
- **📎 Source Citation** — Every answer includes which documents were used
- **📊 Analytics Dashboard** — Track conversations, confidence trends, and improvement areas
- **⚡ REST API** — Full FastAPI backend with auto-generated docs at `/docs`

---

## 🏗️ Architecture

```
📄 Upload Documents  →  🔪 Chunk & Embed  →  🗄️ Store in ChromaDB
                                                      ↓
💬 Customer Question  →  🔍 Semantic Search  →  🤖 Gemini AI Answer
                                                      ↓
                                              🎯 Confidence Score
                                                ↓           ↓
                                           ✅ High        🚨 Low
                                          Auto-reply    Escalate to Human
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Google Gemini 2.0 Flash (free tier) |
| **AI Framework** | LangChain |
| **Embeddings** | Google text-embedding-004 |
| **Vector Database** | ChromaDB |
| **Backend API** | FastAPI |
| **Frontend** | Streamlit |
| **Database** | SQLite |
| **Language** | Python 3.10+ |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- A Google Gemini API key (free from [Google AI Studio](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/danipy2/smartserve-ai.git
cd smartserve-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Run the Application

**Option 1: Streamlit Frontend (Recommended)**
```bash
streamlit run streamlit_app.py
```
Open http://localhost:8501 in your browser.

**Option 2: FastAPI Backend Only**
```bash
python main.py
```
API docs available at http://localhost:8000/docs

---

## 📖 Usage Guide

### 1. Upload Documents
Navigate to the **📄 Knowledge Base** page and upload your company documents (PDFs, text files, or DOCX).

### 2. Start Chatting
Go to the **💬 Chat** page and ask questions about your uploaded documents.

### 3. Monitor Performance
Check the **📊 Analytics** dashboard to see confidence scores, escalation rates, and identify areas for improvement.

---

## 📁 Project Structure

```
smartserve-ai/
├── main.py                    # FastAPI application entry point
├── streamlit_app.py           # Streamlit frontend entry point
├── config.py                  # Centralized configuration
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
│
├── core/                      # Core AI modules
│   ├── document_processor.py  # Document loading & chunking
│   ├── vector_store.py        # ChromaDB vector store manager
│   └── rag_chain.py           # RAG chain with confidence scoring
│
├── api/                       # FastAPI REST API
│   ├── models.py              # Pydantic request/response models
│   └── routes/
│       ├── chat.py            # Chat endpoints
│       ├── documents.py       # Document management endpoints
│       └── analytics.py       # Analytics endpoints
│
├── database/                  
│   └── db.py                  # SQLite database manager
│
├── pages/                     # Streamlit pages
│   ├── 1_💬_Chat.py           # Chat interface
│   ├── 2_📄_Knowledge_Base.py # Document management
│   └── 3_📊_Analytics.py      # Analytics dashboard
│
└── data/                      # Runtime data (gitignored)
    └── chroma/                # Vector store data
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/` | Send a message and get AI response |
| `POST` | `/api/documents/upload` | Upload a document to knowledge base |
| `GET` | `/api/documents/` | List all uploaded documents |
| `DELETE` | `/api/documents/` | Delete a document |
| `GET` | `/api/analytics/` | Get analytics data |
| `GET` | `/health` | API health check |

### Example: Chat API Request

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is your return policy?", "session_id": "user-123"}'
```

**Response:**
```json
{
  "answer": "Based on our documentation, the return policy allows...",
  "confidence": 0.85,
  "needs_escalation": false,
  "sources": [
    {
      "document": "company-faq.pdf",
      "chunk_index": 3,
      "preview": "Return Policy: Customers may return..."
    }
  ],
  "session_id": "user-123"
}
```

---

## 🔧 Configuration

Key settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `LLM_MODEL` | `gemini-2.0-flash` | Gemini model for generation |
| `EMBEDDING_MODEL` | `text-embedding-004` | Model for document embeddings |
| `CHUNK_SIZE` | `1000` | Maximum characters per document chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between consecutive chunks |
| `TOP_K_RESULTS` | `5` | Number of relevant chunks to retrieve |
| `CONFIDENCE_THRESHOLD` | `0.6` | Below this, escalate to human agent |

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License.
