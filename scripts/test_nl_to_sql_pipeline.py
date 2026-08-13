from app.agents.result_composer import ResultComposer
from app.agents.sql_generator import SQLGenerator
from app.agents.sql_repair import SQLRepairAgent
from app.database.executor import QueryExecutor
from app.llm.gemini_provider import GeminiProvider
from app.security.sql_validator import SQLValidator
from app.services.nl_to_sql import NLToSQLService


def main() -> None:

    llm = GeminiProvider()

    generator = SQLGenerator(
        llm=llm
    )

    repairer = SQLRepairAgent(
        llm=llm
    )

    composer = ResultComposer(
        llm=llm
    )

    validator = SQLValidator()

    executor = QueryExecutor()

    service = NLToSQLService(
        generator=generator,
        repairer=repairer,
        validator=validator,
        executor=executor,
        composer=composer,
    )

    question = (
        "Which product category generated "
        "the highest revenue?"
    )

    result = service.process(
        question
    )

    print("=" * 60)
    print("QUESTION")
    print("=" * 60)
    print(result.question)

    print()
    print("=" * 60)
    print("FINAL SQL")
    print("=" * 60)
    print(result.sql)

    print()
    print("=" * 60)
    print("PIPELINE STATUS")
    print("=" * 60)

    print("Valid:", result.is_valid)
    print("Attempts:", result.attempt_count)
    print("Was repaired:", result.was_repaired)

    if result.validation_error:
        print(
            "Validation error:",
            result.validation_error,
        )
        return

    if result.execution_error:
        print(
            "Execution error:",
            result.execution_error,
        )
        return

    print()
    print("=" * 60)
    print("RAW DATABASE RESULT")
    print("=" * 60)

    for row in result.rows or []:
        print(row)

    print()
    print("=" * 60)
    print("NATURAL LANGUAGE ANSWER")
    print("=" * 60)
    print(result.answer)


if __name__ == "__main__":
    main()