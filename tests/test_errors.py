from fastapi.testclient import TestClient

from app.main import app


def test_invalid_json_body(client):
    r = client.post("/nodes", content="not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 400
    assert r.json() == {"error": "Request body is not valid JSON"}


def test_unexpected_error_uses_error_format(client):
    @app.get("/_boom")
    def boom():
        raise RuntimeError("boom")

    try:
        r = TestClient(app, raise_server_exceptions=False).get("/_boom")
    finally:
        app.router.routes.pop()
    assert r.status_code == 500
    assert r.json() == {"error": "Internal server error"}
