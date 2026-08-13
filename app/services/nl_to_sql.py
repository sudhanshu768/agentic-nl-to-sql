from dataclasses import dataclass, field
from typing import Any

from app.agents.result_composer import ResultComposer
from app.agents.sql_generator import SQLGenerator
from app.agents.sql_repair import SQLRepairAgent
from app.config import settings
from app.database.executor import QueryExecutor
from app.security.sql_validator import SQLValidator


@dataclass
class SQLAttempt:
    attempt_number: int
    sql: str
    validation_error: str | None = None
    execution_error: str | None = None


@dataclass
class NLToSQLResult:
    question: str
    sql: str
    is_valid: bool

    columns: list[str] | None = None
    rows: list[dict[str, Any]] | None = None
    row_count: int = 0

    answer: str | None = None

    validation_error: str | None = None
    execution_error: str | None = None

    attempts: list[SQLAttempt] = field(
        default_factory=list
    )

    @property
    def attempt_count(self) -> int:
        return len(self.attempts)

    @property
    def was_repaired(self) -> bool:
        return len(self.attempts) > 1


class NLToSQLService:

    def __init__(
        self,
        generator: SQLGenerator,
        repairer: SQLRepairAgent,
        validator: SQLValidator,
        executor: QueryExecutor,
        composer: ResultComposer,
    ) -> None:

        self.generator = generator
        self.repairer = repairer
        self.validator = validator
        self.executor = executor
        self.composer = composer

    def process(
        self,
        question: str,
    ) -> NLToSQLResult:

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        current_sql = self.generator.generate_sql(
            question
        )

        attempts: list[SQLAttempt] = []

        max_attempts = (
            settings.max_sql_retries + 1
        )

        for attempt_index in range(max_attempts):

            attempt_number = attempt_index + 1

            # -----------------------------
            # Validate
            # -----------------------------

            validation = self.validator.validate(
                current_sql
            )

            if not validation.is_valid:

                attempts.append(
                    SQLAttempt(
                        attempt_number=attempt_number,
                        sql=current_sql,
                        validation_error=validation.error,
                    )
                )

                if (
                    attempt_index
                    >= settings.max_sql_retries
                ):
                    return NLToSQLResult(
                        question=question,
                        sql=current_sql,
                        is_valid=False,
                        validation_error=validation.error,
                        attempts=attempts,
                    )

                current_sql = (
                    self.repairer.repair_sql(
                        question=question,
                        failed_sql=current_sql,
                        error_message=(
                            validation.error
                            or "SQL validation failed."
                        ),
                    )
                )

                continue

            # -----------------------------
            # Execute
            # -----------------------------

            try:
                execution = self.executor.execute(
                    current_sql
                )

            except RuntimeError as exc:

                error_message = str(exc)

                attempts.append(
                    SQLAttempt(
                        attempt_number=attempt_number,
                        sql=current_sql,
                        execution_error=error_message,
                    )
                )

                if (
                    attempt_index
                    >= settings.max_sql_retries
                ):
                    return NLToSQLResult(
                        question=question,
                        sql=current_sql,
                        is_valid=True,
                        execution_error=error_message,
                        attempts=attempts,
                    )

                current_sql = (
                    self.repairer.repair_sql(
                        question=question,
                        failed_sql=current_sql,
                        error_message=error_message,
                    )
                )

                continue

            # -----------------------------
            # Successful SQL execution
            # -----------------------------

            attempts.append(
                SQLAttempt(
                    attempt_number=attempt_number,
                    sql=current_sql,
                )
            )

            # -----------------------------
            # Compose natural-language answer
            # -----------------------------

            answer = self.composer.compose(
                question=question,
                sql=current_sql,
                columns=execution.columns,
                rows=execution.rows,
            )

            return NLToSQLResult(
                question=question,
                sql=current_sql,
                is_valid=True,
                columns=execution.columns,
                rows=execution.rows,
                row_count=execution.row_count,
                answer=answer,
                attempts=attempts,
            )

        raise RuntimeError(
            "Unexpected NL-to-SQL pipeline state."
        )