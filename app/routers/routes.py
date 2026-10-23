from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.graph import shortest_path
from app.models import Edge, Node, RouteQuery
from app.schemas import RouteOut, RouteRequest

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/shortest", response_model=RouteOut, responses={404: {"description": "No path exists"}})
def get_shortest_route(payload: RouteRequest, db: Session = Depends(get_db)):
    names = {payload.source, payload.destination}
    found = set(db.scalars(select(Node.name).where(Node.name.in_(names))))
    missing = [n for n in (payload.source, payload.destination) if n not in found]
    if missing:
        raise HTTPException(400, f"Node(s) not found: {', '.join(missing)}")

    edges = [(e.source.name, e.destination.name, e.latency) for e in db.scalars(select(Edge))]
    result = shortest_path(edges, payload.source, payload.destination)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"No path exists between {payload.source} and {payload.destination}"},
        )

    total_latency, path = result
    db.add(RouteQuery(
        source=payload.source,
        destination=payload.destination,
        total_latency=total_latency,
        path=path,
    ))
    db.commit()
    return RouteOut(total_latency=total_latency, path=path)
