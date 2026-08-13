from app.agents.sql_repair import SQLRepairAgent
from app.database.executor import QueryExecutor
from app.llm.gemini_provider import GeminiProvider
from app.security.sql_validator import SQLValidator
from app.services.nl_to_sql import NLToSQLService


class BrokenSQLGenerator:
    """
    Test generator that deliberately returns
    SQL containing a nonexistent column.
    """

    def generate_sql(
        self,
        question: str,
    ) -> str:

        return """
SELECT
    c.customer_name,
    SUM(o.total_amount) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
WHERE o.status <> 'cancelled'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spending DESC
LIMIT 5;
""".strip()


def main() -> None:

    llm = GeminiProvider()

    generator = BrokenSQLGenerator()

    repairer = SQLRepairAgent(
        llm=llm
    )

    validator = SQLValidator()

    executor = QueryExecutor()

    service = NLToSQLService(
        generator=generator,
        repairer=repairer,
        validator=validator,
        executor=executor,
    )

    question = (
        "Show the top 5 customers "
        "by total spending."
    )

    result = service.process(
        question
    )

    print("=" * 60)
    print("SELF-CORRECTION TEST")
    print("=" * 60)

    print()
    print("Question:")
    print(question)

    print()
    print("Attempts:")

    for attempt in result.attempts:

        print()
        print(
            f"--- Attempt "
            f"{attempt.attempt_number} ---"
        )

        print(attempt.sql)

        if attempt.validation_error:
            print()
            print(
                "Validation error:",
                attempt.validation_error,
            )

        if attempt.execution_error:
            print()
            print(
                "Execution error:",
                attempt.execution_error,
            )

    print()
    print("=" * 60)
    print("FINAL STATUS")
    print("=" * 60)

    print(
        "Succeeded:",
        result.rows is not None,
    )

    print(
        "Total attempts:",
        result.attempt_count,
    )

    print(
        "Was repaired:",
        result.was_repaired,
    )

    print()
    print("Final SQL:")
    print(result.sql)

    if result.rows:

        print()
        print("Results:")

        for row in result.rows:
            print(row)


if __name__ == "__main__":
    main()