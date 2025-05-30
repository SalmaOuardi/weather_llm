
# Guided Weather ☀️

A minimalist weather dashboard and favorites tracker with **live scraping, weather caching, authentication, and LLM-powered summaries** — built with FastAPI, Streamlit, SQLite, and Ollama.

---

## Features

- **🔒 User Signup & Login** — Secure JWT-based authentication (passwords hashed).
- **🌍 Live Weather Search** — Scrapes up-to-date weather for any city via weather.com.
- **⭐ Favorites** — Save, view, and remove your favorite cities (persisted in SQLite).
- **⚡ Weather Caching** — Avoids excessive scraping (configurable TTL, default 15min).
- **🤖 LLM Summaries & Q&A** — Summarize or query your weather using local Ollama models (no OpenAI API required!).
- **🧪 Full Test Suite** — Pytest for backend, with robust coverage for endpoints and logic.
- **🚦 CI/CD** — Automated with GitHub Actions (linting, formatting, tests).
- **🐳 Dockerized** — Easily run backend, UI, and Ollama via `docker-compose`.

---

## Directory Structure

```
.
├── app/                  # FastAPI backend & core logic
│   ├── auth.py           # Auth/JWT logic
│   ├── country_map.py    # Country name/code mapping
│   ├── db.py             # SQLAlchemy models & DB helpers
│   ├── llm.py            # Ollama LLM integration
│   ├── main.py           # FastAPI app & endpoints
│   ├── scraper.py        # Weather scraping logic
│   ├── utils.py          # City parsing, weather cache, helpers
│   └── data/             # (optional) Static or mock data
│
├── tests/                # All backend tests (pytest)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_favorites.py
│   ├── test_main.py
│   └── test_weather.py
│
├── ui.py                 # Streamlit frontend (minimalist weather UI)
├── weather.db            # SQLite DB (auto-created)
├── requirements.txt      # Python dependencies
├── Dockerfile            # Backend image
├── Dockerfile.ui         # UI image
├── docker-compose.yml    # One command to run all services
├── README.md
└── .github/workflows/ci.yml  # CI pipeline
```

---

## Quickstart

1. **Clone & Install**
    ```bash
    git clone https://github.com/yourusername/weather_llm.git
    cd weather_llm
    pip install -r requirements.txt
    ```

2. **Run Backend**
    ```bash
    uvicorn app.main:app --reload
    ```

3. **Run Streamlit UI**
    ```bash
    streamlit run ui.py
    ```

4. **Run Ollama (for LLM features)**
    ```bash
    ollama run mistral   # or phi3, llama3, etc.
    ```

5. **All in Docker (recommended)**
    ```bash
    docker-compose up --build
    ```

---

## Testing

- Run all tests:
    ```bash
    pytest
    ```
- Lint & format:
    ```bash
    black . && flake8 .
    ```

---

## Usage

- **Signup/Login:** Use the UI to create an account.
- **Search Weather:** Type any city and get live weather.
- **Favorites:** Add/remove cities and view their weather.
- **Summaries/Q&A:** Get LLM-powered natural language summaries or ask questions about your cities.

---

## LLM Integration

- Uses Ollama (local, privacy-safe) for summaries and Q&A. No OpenAI API key required.
- You can swap out the model by changing the model name in `app/llm.py`.

---

## Deployment

- Ready for cloud/container deployment.
- Easily extendable: add new endpoints, change cache TTL, use a remote DB, swap LLMs, etc.

---

## Credits

By [Salma OUARDI](https://github.com/SalmaOuardi) — Inspired by real-world product challenges & a love for weather apps ☁️

---

## License

MIT — see [LICENSE](LICENSE).
