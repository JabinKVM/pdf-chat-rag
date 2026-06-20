<div align="center">

# 📄 DocMind
### Chat with any PDF using AI

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Click_Here-FF4B4B?style=for-the-badge)](https://pdf-chat-rag-9yxrc7mszfwnxvgobdcna3.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-1.0-1C3C3C?style=for-the-badge)](https://langchain.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.4-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

**DocMind** is an AI-powered PDF assistant that lets you have natural conversations with any document.
Upload a PDF, ask questions, and get accurate answers with source references — instantly.

![DocMind Demo](https://raw.githubusercontent.com/JabinKVM/pdf-chat-rag/main/assets/demo.png)

</div>

---

## ✨ Features

- 📤 **Upload any PDF** — textbooks, research papers, legal docs, manuals
- 💬 **Natural conversation** — ask follow-up questions, it remembers context
- 📚 **Source citations** — every answer shows exactly which page it came from
- ⚡ **Fast responses** — powered by Groq's ultra-fast LLM inference
- 🔒 **Privacy first** — your documents are never stored permanently
- 📊 **Document stats** — see chunk count and file size at a glance

---

## 🏗️ Architecture

```
PDF Upload
    │
    ▼
┌─────────────────┐
│  Document Loader │  ← PyPDF
│  + Text Splitter │  ← RecursiveCharacterTextSplitter (500 tokens, 50 overlap)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Embeddings    │  ← sentence-transformers/all-MiniLM-L6-v2 (local, free)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Vector Store  │  ← ChromaDB (in-memory)
└────────┬────────┘
         │
    User Question
         │
         ▼
┌─────────────────┐
│    Retrieval    │  ← Similarity search → top-k unique chunks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Generation │  ← Groq (Llama 3.1 8B) + conversation memory
└────────┬────────┘
         │
         ▼
    Answer + Sources
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM** | Groq — Llama 3.1 8B | Fast answer generation |
| **Embeddings** | sentence-transformers | Convert text to vectors |
| **Vector DB** | ChromaDB | Store and search embeddings |
| **RAG Framework** | LangChain | Pipeline orchestration |
| **PDF Parsing** | PyPDF | Extract text from PDFs |
| **UI** | Streamlit | Web interface |
| **Deployment** | Streamlit Cloud | Free hosting with live URL |

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/JabinKVM/pdf-chat-rag.git
cd pdf-chat-rag
```

**2. Create virtual environment**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate       # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

**5. Run the app**
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 📁 Project Structure

```
pdf-chat-rag/
├── app.py              # Streamlit UI
├── rag_core.py         # RAG pipeline (load, embed, retrieve, generate)
├── requirements.txt    # Dependencies
├── .env                # API keys (not committed)
└── README.md
```

---

## 💡 How RAG Works

Traditional LLMs hallucinate because they rely only on training data. **RAG (Retrieval Augmented Generation)** fixes this by:

1. **Splitting** your document into small chunks
2. **Embedding** each chunk as a vector (semantic fingerprint)
3. **Matching** your question to the most relevant chunks
4. **Grounding** the LLM's answer in those chunks — no hallucination

The result: accurate, document-specific answers with zero hallucination.

---

## 🔮 Roadmap

- [ ] Hybrid search (BM25 + semantic)
- [ ] Re-ranking with cross-encoders
- [ ] Multi-PDF support
- [ ] RAGAS evaluation metrics
- [ ] FastAPI + React version

---

## 👨‍💻 Author

**Jabin KVM**
[![GitHub](https://img.shields.io/badge/GitHub-JabinKVM-181717?style=flat&logo=github)](https://github.com/JabinKVM)

---

<div align="center">
  Built with ❤️ using LangChain · ChromaDB · Groq · Streamlit
</div>
