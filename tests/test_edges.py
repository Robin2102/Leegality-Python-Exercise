def test_create_edge(client):
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    r = client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 12.5})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5}


def test_create_edge_errors(client):
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 1})

    bad_bodies = [
        {"destination": "ServerB", "latency": 1},                                 # missing source
        {"source": "ServerA", "latency": 1},                                      # missing destination
        {"source": "ServerA", "destination": "ServerB", "latency": 0},            # latency <= 0
        {"source": "ServerA", "destination": "ServerB", "latency": -3},           # latency <= 0
        {"source": "ServerA", "destination": "ServerB", "latency": "fast"},       # not a number
        {"source": "ServerA", "destination": "ServerB", "latency": 5},            # duplicate
        {"source": "ServerA", "destination": "Nope", "latency": 5},               # node not found
        {"source": "ServerA", "destination": "ServerA", "latency": 5},            # self loop
    ]
    for body in bad_bodies:
        r = client.post("/edges", json=body)
        assert r.status_code == 400, body
        assert "error" in r.json()


def test_reverse_edge_is_not_a_duplicate(client):
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 1})
    r = client.post("/edges", json={"source": "ServerB", "destination": "ServerA", "latency": 2})
    assert r.status_code == 201

