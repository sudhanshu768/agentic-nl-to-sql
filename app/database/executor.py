from dataclasses import dataclass
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings


reader_engine = create_engine(
    settings.read_only_database_url,
    echo=False,
)


@dataclass
class QueryExecutionResult:
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int


class QueryExecutor:

    def execute(
        self,
        sql: str,
    ) -> QueryExecutionResult:

        try:
            with reader_engine.connect() as connection:
                result = connection.execute(
                    text(sql)
                )

                columns = list(
                    result.keys()
                )

                rows = [
                    dict(row)
                    for row in result.mappings().fetchmany(
                        settings.max_result_rows
                    )
                ]

                return QueryExecutionResult(
                    columns=columns,
                    rows=rows,
                    row_count=len(rows),
                )

        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Database query failed: {exc}"
            ) from exc