from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    
app = FastAPI(title="Network Route Optimization API", description="API for optimizing network routes using advanced algorithms.", version="1.0.0", lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}