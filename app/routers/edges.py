from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Edge, Node
from app.schemas import EdgeCreate, EdgeOut


router = APIRouter(prefix="/edges", tags=["edges"])

def to_edge_out(edge: Edge) -> EdgeOut:
    # The table stores node ids; the API exposes node names.
    return EdgeOut(
        id=edge.id,
        source=edge.source.name,
        destination=edge.destination.name,
        latency=edge.latency,
    )


@router.post("", response_model=EdgeOut, status_code=status.HTTP_201_CREATED)
def create_edge(payload: EdgeCreate, db: Session = Depends(get_db)):
    if payload.source == payload.destination:
        raise HTTPException(400, "Source and destination must be different nodes")

    nodes = {n.name: n for n in db.scalars(select(Node).where(Node.name.in_([payload.source, payload.destination])))}
    missing = [name for name in (payload.source, payload.destination) if name not in nodes]
    if missing:
        raise HTTPException(400, f"Node(s) not found: {', '.join(missing)}")

    source, destination = nodes[payload.source], nodes[payload.destination]
    duplicate_msg = f"Edge from '{source.name}' to '{destination.name}' already exists"
    if db.scalar(select(Edge).where(Edge.source_id == source.id, Edge.destination_id == destination.id)):
        raise HTTPException(400, duplicate_msg)

    edge = Edge(source=source, destination=destination, latency=payload.latency)
    db.add(edge)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, duplicate_msg)
    return to_edge_out(edge)