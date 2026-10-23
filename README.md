# Network Route Optimization API

A REST API for optimizing network routes, built with [FastAPI](https://fastapi.tiangolo.com/) as part of the Leegality Python Developer Exercise.

> **Status:** complete. All four required endpoints from the exercise spec are implemented (add node, add edge, shortest route, route history), along with the four optional ones (list and delete nodes and edges). Data is stored in a SQLite database.

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
│   ├── models.py      # ORM models (Node, Edge, RouteQuery)
│   ├── schemas.py     # Pydantic request/response schemas
│   ├── errors.py      # Handlers that return errors as {"error": "..."}
│   ├── graph.py       # Shortest-path algorithm (Dijkstra)
│   └── routers/
│       ├── nodes.py   # /nodes endpoints
│       ├── edges.py   # /edges endpoints
│       └── routes.py  # /routes endpoints
├── tests/
│   ├── conftest.py    # client and sample_graph fixtures (fresh in-memory database per test)
│   ├── test_nodes.py  # /nodes tests
│   ├── test_edges.py  # /edges tests
│   ├── test_routes.py # /routes/shortest tests
│   ├── test_history.py # /routes/history tests
│   ├── test_errors.py # invalid JSON and unexpected-error responses
│   └── test_graph.py  # shortest-path algorithm tests
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
| GET    | `/nodes`  | List all nodes |
| DELETE | `/nodes/{id}` | Delete a node and every edge connected to it |
| POST   | `/edges`  | Create a directed edge between two existing nodes. Returns `201` with the new edge |
| GET    | `/edges`  | List all edges |
| DELETE | `/edges/{id}` | Delete an edge |
| POST   | `/routes/shortest` | Find the lowest-latency route between two nodes |
| GET    | `/routes/history` | List past successful route lookups, with optional filters |

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

#### `GET /nodes`

Returns every node, ordered by `id`:

```json
[{"id": 1, "name": "ServerA"}, {"id": 2, "name": "ServerB"}]
```

#### `DELETE /nodes/{id}`

Deletes the node and every edge that starts or ends at it. Route history is kept (see [Route history](#get-routeshistory)).

| Status | When                                          |
| ------ | --------------------------------------------- |
| `204`  | Node deleted. No body |
| `404`  | No node with that id: `Node 99 not found` |
| `400`  | `id` is not an integer |

#### `POST /edges`

Creates a directed edge from one node to another. Nodes are referred to by name, and both must already exist. There can be only one edge for each source → destination pair; an edge in the opposite direction is a separate edge.

Request body:

| Field         | Type   | Rules                                                  |
| ------------- | ------ | ------------------------------------------------------ |
| `source`      | string | Required. Name of an existing node (spaces trimmed, 1–100 characters) |
| `destination` | string | Required. Name of an existing node, different from `source` |
| `latency`     | number | Required. Latency of the link; must be greater than 0 and finite |

```bash
curl -X POST http://127.0.0.1:8000/edges \
  -H "Content-Type: application/json" \
  -d '{"source": "A", "destination": "B", "latency": 5}'
```

Responses:

| Status | When                                          |
| ------ | --------------------------------------------- |
| `201`  | Edge created. Body: `{"id": <id>, "source": <name>, "destination": <name>, "latency": <number>}` |
| `400`  | `source` and `destination` are the same node: `Source and destination must be different nodes` |
| `400`  | One or both nodes don't exist: `Node(s) not found: Z` |
| `400`  | An edge between those nodes in that direction already exists: `Edge from 'A' to 'B' already exists` |
| `400`  | The request body is invalid (for example, a missing field, or `latency` that is 0, negative or not a number) |

#### `GET /edges`

Returns every edge, ordered by `id`, with node names rather than ids:

```json
[{"id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5}]
```

#### `DELETE /edges/{id}`

| Status | When                                          |
| ------ | --------------------------------------------- |
| `204`  | Edge deleted. No body |
| `404`  | No edge with that id: `Edge 99 not found` |
| `400`  | `id` is not an integer |

#### `POST /routes/shortest`

Finds the route from `source` to `destination` with the lowest total latency, following edges in their direction.

Request body:

| Field         | Type   | Rules                                                  |
| ------------- | ------ | ------------------------------------------------------ |
| `source`      | string | Required. Name of an existing node (spaces trimmed, 1–100 characters) |
| `destination` | string | Required. Name of an existing node                     |

With edges A→B (12.5), B→D (10.9), A→C (5), C→D (30) and B→C (10.1):

```bash
curl -X POST http://127.0.0.1:8000/routes/shortest \
  -H "Content-Type: application/json" \
  -d '{"source": "A", "destination": "D"}'
# {"total_latency":23.4,"path":["A","B","D"]}
```

Responses:

| Status | When                                          |
| ------ | --------------------------------------------- |
| `200`  | Route found. Body: `{"total_latency": <number>, "path": [<name>, ...]}`. If `source` and `destination` are the same node, the result is `{"total_latency": 0, "path": [<name>]}` |
| `400`  | One or both nodes don't exist: `Node(s) not found: Ghost` |
| `400`  | The request body is invalid (for example, a missing field) |
| `404`  | Both nodes exist but no route connects them: `No path exists between A and E` |

#### `GET /routes/history`

Every successful lookup (`200`) from `POST /routes/shortest` is saved to the `route_queries` table, and this endpoint lists them. Failed lookups (`400`, `404`) are not saved. Node names and the path are stored as plain values rather than links to the `nodes` table, so the history still shows what was answered at the time even after nodes or edges are deleted.

Query parameters (all optional, and they can be combined):

| Parameter     | Description |
| ------------- | ----------- |
| `source`      | Only lookups from this node name (exact match) |
| `destination` | Only lookups to this node name (exact match) |
| `limit`       | Maximum number of records, 1–1000 |
| `date_from`   | Only lookups at or after this time (ISO 8601, e.g. `2026-02-20T14:00:00Z`) |
| `date_to`     | Only lookups at or before this time |

Times without a timezone are treated as UTC. A date on its own, such as `2026-02-20`, covers the whole day: as `date_from` it means the start of that day, and as `date_to` the end of it. So `date_from=2026-02-20&date_to=2026-02-20` returns every lookup made on 20 February.

Results are ordered oldest first. `limit` therefore returns the oldest matching records.

```bash
curl "http://127.0.0.1:8000/routes/history?source=ServerA&limit=10"
```

```json
[
  {
    "id": 1,
    "source": "ServerA",
    "destination": "ServerD",
    "total_latency": 23.4,
    "path": ["ServerA", "ServerB", "ServerD"],
    "created_at": "2026-02-20T14:32:00Z"
  }
]
```

`created_at` is always in UTC, with a `Z` suffix and whole seconds.

| Status | When                                          |
| ------ | --------------------------------------------- |
| `200`  | A list of records; empty if nothing matches |
| `400`  | `limit` is outside 1–1000, a date can't be parsed, or `date_from` is later than `date_to` |

### How the shortest route is found

The endpoint loads every edge and passes it to `shortest_path(edges, source, destination)` in `app/graph.py`, which can also be used on its own.

- **Input:** an iterable of `(source, destination, latency)` tuples, plus the start and end node names. Edges are directed.
- **Output:** `(total_latency, path)`, where `path` is the list of node names from `source` to `destination`, or `None` if `destination` can't be reached. If `source` and `destination` are the same, the result is `(0, [source])`.
- **Algorithm:** Dijkstra's algorithm with a binary heap, O((V + E) log V). This relies on every latency being positive, which `POST /edges` enforces.
- **Rounding:** the total is rounded to 6 decimal places to remove floating-point noise (for example, `12.5 + 10.9` gives `23.4`, not `23.400000000000002`).

```python
from app.graph import shortest_path

edges = [("A", "B", 1), ("B", "C", 2), ("A", "C", 5), ("C", "D", 1)]
shortest_path(edges, "A", "D")  # (4.0, ["A", "B", "C", "D"])
shortest_path(edges, "D", "A")  # None
```

### Error format

Every error response, including validation errors, has the same shape:

```json
{"error": "Node 'A' already exists."}
```

Request validation errors, in the body, query string or path, return `400` (not FastAPI's default `422`). Each problem is reported as `<field>: <message>`, and several problems are joined by `; `, for example:

```json
{"error": "latency: Field required"}
```

A body that isn't valid JSON returns `400` with `{"error": "Request body is not valid JSON"}`. An unexpected server error returns `500` with `{"error": "Internal server error"}`, and the full traceback goes to the server log.

## Running tests

Run the test suite from the project root:

```bash
pytest
```

Each test gets its own in-memory SQLite database (see `tests/conftest.py`), so tests don't touch `network.db` and don't depend on each other. The suite currently covers:

- **Nodes:** creating a node, trimming whitespace, rejecting missing or blank names, rejecting duplicates, listing nodes, and deleting a node along with its edges.
- **Edges:** creating an edge; rejecting missing fields, invalid latency, duplicates, unknown nodes and self-loops; allowing an edge in the reverse direction; and deleting an edge (`204`, then `404`).
- **`POST /routes/shortest`:** finding the cheapest route in the `sample_graph` fixture, `404` when no route exists, unknown nodes, and missing fields.
- **`GET /routes/history`:** only successful lookups are recorded, the response format, each filter, a date-only `date_to` including the whole day, invalid parameters, and history surviving node deletion.
- **Errors:** invalid JSON bodies and unexpected server errors both return the `{"error": ...}` format.
- **`shortest_path`:** choosing a cheaper multi-hop route over a direct one, unreachable destinations, same source and destination, and rounding of float totals.
