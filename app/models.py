from sqlalchemy import ForeignKey, String, UniqueConstraint, CheckConstraint, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
class Edge(Base):
    __tablename__ = "edges"
    
    __table_args__ = (
        UniqueConstraint("source_id", "destination_id", name="unique_edge_source_destination"),
        CheckConstraint("latency > 0", name="check_edge_latency_positive"),
        CheckConstraint("source_id <> destination_id", name="check_edge_no_self_loop"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    source_id: Mapped[int] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), index=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), index=True)
    latency: Mapped[float] = mapped_column(Float)
    
    source: Mapped["Node"] = relationship(foreign_keys=[source_id], lazy="joined")
    destination: Mapped["Node"] = relationship(foreign_keys=[destination_id], lazy="joined")