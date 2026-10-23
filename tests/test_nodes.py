
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