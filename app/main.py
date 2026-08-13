from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Agentic NL-to-SQL Assistant",
    description=(
        "A schema-aware, secure, and self-correcting "
        "natural-language-to-SQL system."
    ),
    version="0.2.0",
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "project": "Agentic NL-to-SQL Assistant",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }