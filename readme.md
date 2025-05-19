# PDF AI Assistant (CLI-based RAG System)

A command-line AI assistant that lets you embed and chat with PDF documents using OpenAI embeddings, pgvector, and GPT-4.

---

## ✨ Features

* Parse and clean PDFs using PyMuPDF
* Generate OpenAI `text-embedding-3-small` vector embeddings
* Store embeddings in PostgreSQL with `pgvector`
* Retrieve semantically similar pages using cosine similarity
* Chat with your PDF using GPT-4 (or GPT-4o), with streamed responses
* Interactive CLI with multi-document support

---

## 📦 Requirements

* Python 3.10+
* PostgreSQL with `pgvector` extension enabled
* OpenAI API key

### Python Dependencies

```
pip install -r requirements.txt
```

---

## ⚙️ Setup

### Database Setup:

1. Create a PostgreSQL database
2. Install the `pgvector` extension:

   ```sql
   CREATE EXTENSION vector;
   ```
3. Configure your database connection in `app/core/postgres.py`

### OR

Just run 
```bash
docker compose up
```
at the root  folder.

### Environments:
POSTGRES_DB -> The database name to be created or used

POSTGRES_URL -> The database url, such as 
```localhost:5432```

POSTGRES_USER -> Database user name

POSTGRES_PASSWORD -> Database password

OPENAI_KEY -> The API Key to be generated from [OpenAI Dashboard](https://platform.openai.com/)

---

## 🚀 Usage

### Embed a PDF:

```
python main.py embed path/to/file.pdf
```

### Chat with your PDFs:

```
python main.py chat
```

You’ll be shown a list of available embedded PDFs to choose from. Once selected, type your questions and get AI-powered answers based on document context.

---

## 💡 Architecture Overview

1. **PDF Parsing** → Clean each page with `PyMuPDF`
2. **Embedding** → Use OpenAI to embed each page’s content
3. **Storage** → Insert into PostgreSQL with `pgvector`
4. **Retrieval** → Find top-N most relevant pages via cosine similarity
5. **Prompt Assembly** → Inject pages as context + user prompt
6. **Response** → Stream answers from OpenAI GPT-4o

---

## 📄 License

MIT — use freely, attribute if you build on it.

---

## 🙌 Author

**Umut Cevdet Koçak**

Built as a weekend project to explore vector search, embeddings, and conversational RAG systems.
