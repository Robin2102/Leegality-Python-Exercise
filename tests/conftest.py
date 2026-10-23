import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    # A brand-new in-memory database per test keeps tests independent.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def sample_graph(client):
    """
        A --12.5--> B --10.9--> D
        A --5-----> C --30----> D
        B --10.1--> C
        E (isolated)
    """
    for name in ["ServerA", "ServerB", "ServerC", "ServerD", "ServerE"]:
        client.post("/nodes", json={"name": name})
    for src, dst, latency in [
        ("ServerA", "ServerB", 12.5),
        ("ServerB", "ServerD", 10.9),
        ("ServerA", "ServerC", 5),
        ("ServerC", "ServerD", 30),
        ("ServerB", "ServerC", 10.1),
    ]:
        client.post("/edges", json={"source": src, "destination": dst, "latency": latency})
    return client