
def test_create_node(client):
    r = client.post("/nodes", json={"name": "ServerA"})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "name": "ServerA"}


def test_create_node_trims_whitespace(client):
    assert client.post("/nodes", json={"name": "  ServerA  "}).json()["name"] == "ServerA"


def test_create_node_missing_or_blank_name(client):
    for body in [{}, {"name": ""}, {"name": "   "}]:
        r = client.post("/nodes", json=body)
        assert r.status_code == 400
        assert "error" in r.json()


def test_create_node_duplicate(client):
    client.post("/nodes", json={"name": "ServerA"})
    r = client.post("/nodes", json={"name": "ServerA"})
    assert r.status_code == 400
    assert r.json() == {"error": "Node 'ServerA' already exists."}
    
def test_list_and_delete_node_cascades_edges(sample_graph):
    nodes = sample_graph.get("/nodes").json()
    assert [n["name"] for n in nodes] == ["ServerA", "ServerB", "ServerC", "ServerD", "ServerE"]

    server_b = next(n for n in nodes if n["name"] == "ServerB")
    assert sample_graph.delete(f"/nodes/{server_b['id']}").status_code == 204

    edges = sample_graph.get("/edges").json()
    assert all("ServerB" not in (e["source"], e["destination"]) for e in edges)
    assert sample_graph.delete(f"/nodes/{server_b['id']}").status_code == 404