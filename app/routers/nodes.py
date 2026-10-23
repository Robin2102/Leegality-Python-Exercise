from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Edge, Node
from app.schemas import NodeCreate, NodeOut

router = APIRouter(prefix="/nodes", tags=["Nodes"])

@router.post("", response_model=NodeOut, status_code=status.HTTP_201_CREATED)
def create_node(payload: NodeCreate, db: Session = Depends(get_db)):
    """
    Create a new node in the database.
    """
    if db.scalar(select(Node).where(Node.name == payload.name)):
        raise HTTPException(400, f"Node '{payload.name}' already exists.")
    
    node = Node(name=payload.name)
    db.add(node)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, f"Node '{payload.name}' already exists.")
    return node

@router.get("", response_model=list[NodeOut])
def list_nodes(db: Session = Depends(get_db)):
    return db.scalars(select(Node).order_by(Node.id)).all()


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if node is None:
        raise HTTPException(404, f"Node {node_id} not found")


    db.execute(delete(Edge).where(or_(Edge.source_id == node_id, Edge.destination_id == node_id)))
    db.delete(node)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)