from fastapi import FastAPI


app = FastAPI(
    title="Agentic NL-to-SQL Assistant",
    description=(
        "A schema-aware, secure, and self-correcting "
        "natural-language-to-SQL system."
    ),
    version="0.1.0",
)


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