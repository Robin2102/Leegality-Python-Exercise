from app.graph import shortest_path

EDGES = [("A", "B", 1), ("B", "C", 2), ("A", "C", 5), ("C", "D", 1)]


def test_picks_cheaper_multi_hop_route():
    assert shortest_path(EDGES, "A", "D") == (4, ["A", "B", "C", "D"])


def test_unreachable_returns_none():
    assert shortest_path(EDGES, "D", "A") is None


def test_same_source_and_destination():
    assert shortest_path(EDGES, "A", "A") == (0, ["A"])


def test_float_noise_is_rounded():
    assert shortest_path([("A", "B", 12.5), ("B", "C", 10.9)], "A", "C") == (23.4, ["A", "B", "C"])
