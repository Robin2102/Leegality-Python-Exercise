from datetime import datetime, timezone

from sqlalchemy import JSON, CheckConstraint, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

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
    
class RouteQuery(Base):
    """A record of every successful shortest-route lookup.

    Names and the path are stored as plain values (not foreign keys) on purpose:
    history is a log of what was answered at that time, so it must survive the
    nodes being deleted or the graph changing afterwards.
    """

    __tablename__ = "route_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(100), index=True)
    destination: Mapped[str] = mapped_column(String(100), index=True)
    total_latency: Mapped[float] = mapped_column(Float)
    path: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
