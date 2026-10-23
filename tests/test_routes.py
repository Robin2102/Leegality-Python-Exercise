def test_shortest_route(sample_graph):
    r = sample_graph.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerD"})
    assert r.status_code == 200
    assert r.json() == {"total_latency": 23.4, "path": ["ServerA", "ServerB", "ServerD"]}


def test_shortest_route_no_path(sample_graph):
    r = sample_graph.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerE"})
    assert r.status_code == 404
    assert r.json() == {"error": "No path exists between ServerA and ServerE"}


def test_shortest_route_unknown_node(sample_graph):
    r = sample_graph.post("/routes/shortest", json={"source": "ServerA", "destination": "Ghost"})
    assert r.status_code == 400
    assert r.json() == {"error": "Node(s) not found: Ghost"}


def test_shortest_route_missing_field(sample_graph):
    assert sample_graph.post("/routes/shortest", json={"source": "ServerA"}).status_code == 400
