# Network Route Optimization API

A REST API for optimizing network routes, built with [FastAPI](https://fastapi.tiangolo.com/) as part of the Leegality Python Developer Exercise.

> **Status:** early stage. The application skeleton is in place and currently exposes a health-check endpoint. Data models (`app/models.py`) and route optimization endpoints are still to be implemented.

## Tech stack

- **Python** 3.13
- **FastAPI**: web framework
- **Uvicorn**: ASGI server
- **Pydantic**: request/response validation
- **SQLAlchemy**: ORM for persistence
- **pytest** and **httpx**: testing

## Project structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI application and routes
│   └── models.py      # Data models (to be implemented)
├── requirements.txt   # Pinned dependencies
└── README.md
```

## Setup

**Prerequisites:** Python 3.13 or newer, and `pip`.

1. **Clone the repository** and move into the project directory:

   ```bash
   git clone <repository-url>
   cd "Leegality-Python's Developer Exercise"
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # macOS / Linux
   # .venv\Scripts\activate         # Windows
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Running the application

Start the development server from the project root:

```bash
uvicorn app.main:app --reload
```

The API is then available at `http://127.0.0.1:8000`. `--reload` restarts the server when code changes; leave it off outside development.

To use a different host or port:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### API documentation

FastAPI generates interactive documentation automatically:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Endpoints

| Method | Path      | Description                          |
| ------ | --------- | ------------------------------------ |
| GET    | `/health` | Health check. Returns `{"status": "ok"}` |

Check that the server is running:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

## Running tests

pytest is included in the dependencies. Once tests are added, run them from the project root with:

```bash
pytest
```
