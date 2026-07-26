# 🥋 IBJJF Rules Bot

A RAG chatbot (Retrieval-Augmented Generation) that answers questions about
the official IBJJF competition rulebook, which runs entirely locally, no paid
APIs needed and fully open source.

## Tech Stack

- **LLM:** Llama 3.2 3B (via [Ollama](https://ollama.com))
- **Embeddings:** nomic-embed-text (via Ollama)
- **Vector database:** Chroma (local)
- **Framework:** LangChain (+ `langchain-classic` for chain building blocks)
- **UI:** Streamlit (optional; a plain CLI version is also included)

## Setup

### 1. Install Ollama

Download from [ollama.com](https://ollama.com/download), then pull the models:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### 2. Set up the Python environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Get the IBJJF rulebook PDF

Download the official rulebook PDF from the [ibjjf.com](https://ibjjf.com/books-videos) website and save it as:

```
data/IBJJF_Rules.pdf
```

### 4. Build the vector database

```bash
python vector_db.py
```

This loads the PDF, splits it into chunks, embeds them, and stores everything in a local Chroma database
(`chroma_db/`).

### 5. Start chatting

**Command line (no extra dependencies):**
```bash
python main.py
```

**Or with a web UI:**
```bash
streamlit run app.py
```
Opens automatically in your browser at `http://localhost:8501`.
