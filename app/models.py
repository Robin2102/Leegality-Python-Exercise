from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)