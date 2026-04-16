# AI Assistant (RAG Chatbot)

> 💡 This project demonstrates how to build a real-world AI assistant using Retrieval-Augmented Generation (RAG), combining semantic search with intelligent response generation.

A modern full-stack, local-first RAG chatbot that answers questions from custom document sources (PDFs) and supports smart operations such as recommendations, information retrieval, and contextual responses.

Designed for fast local experimentation using **FastAPI + FAISS + SentenceTransformers + Ollama (phi3)** on the backend and a **React + Vite + TailwindCSS** chat UI on the frontend.

---

## 🚀 Features

- Chat with custom document knowledge base using Retrieval-Augmented Generation (RAG)
- Smart recommendations based on user intent (keywords, preferences)
- Context-aware answers generated from relevant document chunks
- Information lookup and summarization
- Multi-document (PDF) vector search support
- ChatGPT-style interactive UI
- Fully local AI runtime using Ollama

---
## 🧠 How It Works

1. Documents (PDFs) are processed into smaller chunks  
2. Text is converted into embeddings using SentenceTransformers  
3. FAISS stores embeddings for fast similarity search  
4. User queries are matched with relevant document chunks  
5. Ollama (phi3) generates final responses using retrieved context  

---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- FAISS
- SentenceTransformers (`all-MiniLM-L6-v2`)
- Ollama (`phi3:latest`)

### Frontend
- React
- Vite
- TailwindCSS

---

<p align="center">
  <img src="docs/screenshots/UI.png" width="800"/>
</p>

---

## ⚙️ Installation

### 1) Clone the repository

```bash
git clone https://github.com/MuhammedAnas555/rag-chatbot.git
cd rag-chatbot
```

### 2) Backend setup (FastAPI + RAG)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3) Frontend setup (React + Vite + Tailwind)

Open a new terminal:

```powershell
cd frontend
npm install
```

---

## 🤖 Run Ollama (Local LLM)

Make sure Ollama is installed and running.

1. Start Ollama service (if not already running)
2. Pull model:

```powershell
ollama pull phi3:latest
```

3. (Optional) test model:

```powershell
ollama run phi3:latest
```

Backend expects Ollama at:
- `http://localhost:11434`

---

## ▶️ Run the Project

### Terminal 1: Backend API

```powershell
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend

```powershell
cd frontend
npm run dev
```

Open the frontend URL shown by Vite (usually `http://localhost:5173`).

---

## 💬 Example Queries

- "What burgers contain beef and tomato?"
- "Suggest a burger if I like truffle flavor."
- "What is the cheapest item?"
- "Calculate total bill for 2 Classic Street Boss and 1 Bloody Mary."
- "Do you have chicken options?"
- "What drinks are available?"
- "Summarize the Burger Lab menu highlights."

---

## 📁 Project Structure

```text
rag/
├─ backend/
│  ├─ main.py
│  ├─ requirements.txt
│  └─ .venv/                      # local virtual environment (not committed)
├─ frontend/
│  ├─ package.json
│  ├─ vite.config.js
│  ├─ tailwind.config.js
│  ├─ postcss.config.js
│  └─ src/
│     ├─ App.jsx
│     ├─ main.jsx
│     ├─ index.css
│     └─ components/
├─ pdfs/                           # Burger Lab menu PDFs
├─ pdf-vector.py                   # builds vector DB from PDFs
├─ question-vector.py              # RAG + menu logic (billing/recommendations)
├─ vectors.index                   # FAISS index (generated)
└─ chunks.pkl                      # chunk metadata (generated)
```

---

## 🔮 Future Improvements

- Add authentication and per-user chat history
- Stream token-by-token responses from backend to frontend
- Add admin panel for menu updates without code changes
- Add evaluation pipeline for RAG answer quality
- Dockerize backend + frontend for one-command startup
- Add multilingual support and voice input

---

## 👨‍💻 Author

**Muhammed Anas K**  
- GitHub: https://github.com/MuhammedAnas555

