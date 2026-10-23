# Network Route Optimization API

A REST API for optimizing network routes, built with [FastAPI](https://fastapi.tiangolo.com/) as part of the Leegality Python Developer Exercise.

> **Status:** in progress. The API has a health check and an endpoint to create network nodes, backed by a SQLite database. Edges and route optimization endpoints are still to be implemented.

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
│   ├── main.py        # FastAPI app: startup, error handlers, health check, routers
│   ├── database.py    # SQLAlchemy engine, session and get_db dependency
│   ├── models.py      # ORM models (Node)
│   ├── schemas.py     # Pydantic request/response schemas
│   ├── errors.py      # Handlers that return errors as {"error": "..."}
│   └── routers/
│       └── nodes.py   # /nodes endpoints
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

## Configuration

| Variable       | Default                  | Description                     |
| -------------- | ------------------------ | ------------------------------- |
| `DATABASE_URL` | `sqlite:///./network.db` | SQLAlchemy database connection URL |

Tables are created automatically when the app starts. With the default setting, the database is a `network.db` file in the directory you start the server from; it is ignored by git. Delete the file to start with an empty database.

For SQLite, foreign key enforcement is switched on for every connection.

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

| Method | Path      | Description                                   |
| ------ | --------- | --------------------------------------------- |
| GET    | `/health` | Health check. Returns `{"status": "ok"}`      |
| POST   | `/nodes`  | Create a node. Returns `201` with the new node |

Check that the server is running:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

#### `POST /nodes`

Creates a network node. Node names must be unique.

Request body:

| Field  | Type   | Rules                                                        |
| ------ | ------ | ------------------------------------------------------------ |
| `name` | string | Required. Leading and trailing spaces are removed; must then be 1–100 characters |

```bash
curl -X POST http://127.0.0.1:8000/nodes \
  -H "Content-Type: application/json" \
  -d '{"name": "A"}'
# {"id":1,"name":"A"}
```

Responses:

| Status | When                                          |
| ------ | --------------------------------------------- |
| `201`  | Node created. Body: `{"id": <int>, "name": <string>}` |
| `400`  | A node with that name already exists, or the request body is invalid (for example, a missing or empty `name`) |

### Error format

Every error response, including validation errors, has the same shape:

```json
{"error": "Node 'A' already exists."}
```

Request validation errors return `400` (not FastAPI's default `422`), with one message per problem joined by `; `.

## Running tests

pytest is included in the dependencies. Once tests are added, run them from the project root with:

```bash
pytest
```
