from datetime import datetime, timedelta, timezone

def test_history_records_successful_queries_only(sample_graph):
    sample_graph.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerD"})
    sample_graph.post("/routes/shortest", json={"source": "ServerB", "destination": "ServerC"})
    sample_graph.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerE"})  # 404

    history = sample_graph.get("/routes/history").json()
    assert len(history) == 2
    first = history[0]
    assert first["id"] == 1
    assert first["source"] == "ServerA"
    assert first["destination"] == "ServerD"
    assert first["total_latency"] == 23.4
    assert first["path"] == ["ServerA", "ServerB", "ServerD"]
    datetime.strptime(first["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    assert history[1]["path"] == ["ServerB", "ServerC"]


def test_history_filters(sample_graph):
    for src, dst in [("ServerA", "ServerD"), ("ServerB", "ServerC"), ("ServerA", "ServerC")]:
        sample_graph.post("/routes/shortest", json={"source": src, "destination": dst})

    get = lambda **params: sample_graph.get("/routes/history", params=params).json()
    assert len(get(source="ServerA")) == 2
    assert len(get(destination="ServerC")) == 2
    assert len(get(source="ServerA", destination="ServerC")) == 1
    assert len(get(limit=1)) == 1

    now = datetime.now(timezone.utc)
    assert len(get(date_from=(now - timedelta(minutes=5)).isoformat())) == 3
    assert len(get(date_from=(now + timedelta(minutes=5)).isoformat())) == 0
    assert len(get(date_to=(now - timedelta(minutes=5)).isoformat())) == 0


def test_history_invalid_params(client):
    assert client.get("/routes/history", params={"limit": 0}).status_code == 400
    assert client.get("/routes/history", params={"date_from": "yesterday"}).status_code == 400
    r = client.get("/routes/history", params={"date_from": "2026-02-21T00:00:00Z", "date_to": "2026-02-20T00:00:00Z"})
    assert r.status_code == 400


def test_history_survives_node_deletion(sample_graph):
    sample_graph.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerD"})
    sample_graph.delete("/nodes/2")
    assert sample_graph.get("/routes/history").json()[0]["path"] == ["ServerA", "ServerB", "ServerD"]
