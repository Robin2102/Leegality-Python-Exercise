"""Pure shortest-path logic."""
import heapq
from collections import defaultdict
from collections.abc import Iterable


def shortest_path(
    edges: Iterable[tuple[str, str, float]],
    source: str,
    destination: str,
) -> tuple[float, list[str]] | None:
    """Dijkstra's algorithm over directed, positively weighted edges.

    Returns (total_latency, path) or None if destination is unreachable.
    Runs in O((V + E) log V) thanks to the binary heap.
    """
    graph: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for src, dst, latency in edges:
        graph[src].append((dst, latency))

    best: dict[str, float] = {source: 0.0}   # cheapest known distance to each node
    previous: dict[str, str] = {}
    queue: list[tuple[float, str]] = [(0.0, source)]

    while queue:
        distance, node = heapq.heappop(queue)
        if node == destination:
            break
        # A node can be pushed several times; skip stale, more expensive entries.
        if distance > best[node]:
            continue
        for neighbour, latency in graph[node]:
            candidate = distance + latency
            if candidate < best.get(neighbour, float("inf")):
                best[neighbour] = candidate
                previous[neighbour] = node
                heapq.heappush(queue, (candidate, neighbour))

    if destination not in best:
        return None

    path = [destination]
    while path[-1] != source:
        path.append(previous[path[-1]])
    path.reverse()
    # Round away float noise
    return round(best[destination], 6), path
