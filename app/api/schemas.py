from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description=(
            "Natural-language question about "
            "the database."
        ),
    )


class QueryResponse(BaseModel):
    question: str
    answer: str | None
    sql: str

    rows: list[dict[str, Any]]
    row_count: int

    attempts: int
    was_repaired: bool