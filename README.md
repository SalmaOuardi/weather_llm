
# Guided Weather ☀️

A minimalist, fullstack weather app demo, showcasing:

- Live web scraping from [weather.com](https://weather.com/)
- User authentication (JWT/FastAPI)
- SQLite persistence for users, favorites, and weather caching
- Favorites dashboard with LLM-powered summaries and Q&A
- Local LLM integration (Ollama) for natural language interaction
- Minimal, UX-focused Streamlit frontend

---

## ✨ Features

- **Search live weather** for any city worldwide (robust place matching & country code parsing)
- **Sign up / log in** with JWT-secured API
- **Save and manage favorite cities** (persistent per-user)
- **Weather caching** for efficiency and API-friendliness
- **Natural language weather summary** (`/summary`) via Llama 3 or Mistral 7B (Ollama)
- **Ask anything** about your favorites — e.g., *“Which cities are sunny?”* — with structured JSON answers from an LLM
- **Simple, modern UI** with Streamlit (mobile-friendly, small text, compact, dark/light aware)

---

## 🏗️ Project Structure

```
app/
  ├── auth.py        # Auth logic (signup, login, JWT)
  ├── country_map.py # Maps country names to ISO codes
  ├── db.py          # SQLAlchemy ORM: users, favorites, weather cache
  ├── llm.py         # Ollama LLM client (for /summary and /ask endpoints)
  ├── main.py        # FastAPI app, all endpoints
  ├── scraper.py     # Scraping/parsing logic for weather.com
  ├── utils.py       # City/country parsing, caching helpers
data/
  └── (optional: static data, etc.)
tests/
  └── (add test scripts here)
ui.py                # Streamlit UI for all features
weather.db           # SQLite database
requirements.txt     # All Python dependencies
.env                 # (optional) secrets/keys for prod use
```

---

## 🚀 Quickstart

### 1. **Clone & Install**
```bash
git clone https://github.com/yourusername/guided-weather.git
cd guided-weather
pip install -r requirements.txt
```

### 2. **Start Ollama (LLM API)**
> For best results, use `llama3` (8B) or `Mistral` (7B)  
```bash
ollama pull llama3
ollama run llama3
# or for lighter model:
# ollama pull phi3
# ollama run phi3
```

### 3. **Run Backend API (FastAPI)**
```bash
uvicorn app.main:app --reload
```
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. **Launch Frontend UI**
```bash
streamlit run ui.py
```
- App: [http://localhost:8501](http://localhost:8501)

---

## 💡 How It Works

- **Scraping:** For each city, backend scrapes [weather.com](https://weather.com/) using their internal search API to resolve city/place IDs, then fetches live weather HTML and parses it.
- **Authentication:** Simple JWT token flow; all main endpoints require login.
- **Persistence:** Users, favorites, and weather cache stored in SQLite via SQLAlchemy ORM.
- **LLM Integration:** `/summary` and `/ask` endpoints pass weather context to a local LLM (Ollama) for natural language output, including structured JSON for Q&A.
- **Frontend:** Streamlit app connects to all endpoints, handles login, city search, favorites, summaries, and Q&A.

---

## 🤖 Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **LLM:** Ollama (`llama3` or `phi3` models)
- **Frontend:** Streamlit
- **Other:** BeautifulSoup, requests

---

## 📝 Example API Usage

- **Weather search:** `GET /weather?city=London`
- **Add favorite:** `POST /favorites` with `{"cities": ["London"]}`
- **Get favorites:** `GET /favorites`
- **Summary (LLM):** `GET /summary`
- **Ask:** `POST /ask` with `{"question": "Which cities are sunny now?"}`

---

## 🧩 Scaling & Extensibility

- **Pluggable LLM backend:** swap Ollama for OpenAI/Mistral easily
- **Autocomplete-ready:** design can easily support suggestions/autocomplete for city/country (see scraper logic)
- **Scalable weather cache:** efficient for 100k+ cities with minor tweaks (indexing, async, etc.)

---

## 📚 License

MIT (see LICENSE)

---

## 🙋‍♀️ Author

Built by [Salma OUARDI](https://github.com/SalmaOuardi)

---

**Feel free to fork or reuse for other AI, scraping, or agentic workflow demos!**
