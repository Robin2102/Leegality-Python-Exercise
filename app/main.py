from fastapi import FastAPI

app = FastAPI(title="Network Route Optimization API", description="API for optimizing network routes using advanced algorithms.", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}