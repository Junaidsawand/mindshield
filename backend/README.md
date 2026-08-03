# MindShield Backend

> **Phase 2.1** — Production-quality FastAPI backend foundation  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh | 2026  
> **Stack**: Python 3.13 · FastAPI 0.115 · Pydantic v2 · Uvicorn

---

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Copy and configure environment
copy .env.example .env        # Windows
cp .env.example .env          # Linux/macOS

# 4. Run the development server
python run.py

# Or directly:
uvicorn app.main:app --reload
```

Server starts at **http://localhost:8000**  
Interactive docs at **http://localhost:8000/docs**

---

## Running Tests

```bash
pytest tests/ -v
```

## Running Linting

```bash
flake8 app/ tests/
black --check app/ tests/
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI application factory
│   ├── core/            # Settings, exceptions, model interface
│   ├── routers/         # HTTP route handlers
│   ├── services/        # Business logic layer
│   ├── schemas/         # Pydantic request/response models
│   ├── middleware/       # CORS, request logging
│   ├── logging/         # Structured log configuration
│   └── utils/           # Pure utility functions
├── tests/               # pytest test suite
├── docs/                # Thesis-ready documentation
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/analyze/status` | API v1 status |
| POST | `/api/v1/analyze` | SMS analysis (placeholder in Phase 2.1) |

---

## Documentation

Full thesis-ready documentation is in [`docs/01_Backend_Setup.md`](docs/01_Backend_Setup.md)
