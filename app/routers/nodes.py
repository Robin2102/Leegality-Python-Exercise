from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Node
from app.database import get_db
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