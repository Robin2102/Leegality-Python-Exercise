from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BeforeValidator
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.graph import shortest_path
from app.models import Edge, Node, RouteQuery
from app.schemas import RouteHistoryOut, RouteOut, RouteRequest

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

def _to_utc(value: datetime) -> datetime:
    # Accept "2026-02-20T14:00:00Z", "+05:30" offsets, or naive.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _end_of_day_if_date_only(value):
    # "2026-02-20" as date_to should include the whole day, not stop at midnight.
    if isinstance(value, str) and len(value) == 10:
        return f"{value}T23:59:59.999999"
    return value


@router.get("/history", response_model=list[RouteHistoryOut])
def get_route_history(
    source: str | None = None,
    destination: str | None = None,
    limit: int | None = Query(None, ge=1, le=1000),
    date_from: datetime | None = None,
    date_to: Annotated[datetime | None, BeforeValidator(_end_of_day_if_date_only)] = None,
    db: Session = Depends(get_db),
):
    if date_from and date_to and _to_utc(date_from) > _to_utc(date_to):
        raise HTTPException(400, "date_from must be earlier than or equal to date_to")

    query = select(RouteQuery)
    if source:
        query = query.where(RouteQuery.source == source)
    if destination:
        query = query.where(RouteQuery.destination == destination)
    if date_from:
        query = query.where(RouteQuery.created_at >= _to_utc(date_from))
    if date_to:
        query = query.where(RouteQuery.created_at <= _to_utc(date_to))
    query = query.order_by(RouteQuery.created_at, RouteQuery.id)
    if limit:
        query = query.limit(limit)
    return db.scalars(query).all()
