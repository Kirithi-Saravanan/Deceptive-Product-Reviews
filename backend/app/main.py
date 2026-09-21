from fastapi import FastAPI

app = FastAPI(
    title="ReviewGuard AI API",
    description="Backend API for ReviewGuard AI, a platform to detect deceptive reviews.",
    version="0.1.0",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to ReviewGuard AI API"}
