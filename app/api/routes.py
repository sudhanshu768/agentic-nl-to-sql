from fastapi import APIRouter, HTTPException

from app.agents.result_composer import ResultComposer
from app.agents.sql_generator import SQLGenerator
from app.agents.sql_repair import SQLRepairAgent
from app.api.schemas import QueryRequest, QueryResponse
from app.database.executor import QueryExecutor
from app.llm.gemini_provider import GeminiProvider
from app.security.sql_validator import SQLValidator
from app.services.nl_to_sql import NLToSQLService
from app.security.input_guardrail import InputGuardrail

router = APIRouter(
    prefix="/api/v1",
    tags=["NL-to-SQL"],
)


# -----------------------------------
# Build application components
# -----------------------------------

llm = GeminiProvider()

generator = SQLGenerator(
    llm=llm,
)

repairer = SQLRepairAgent(
    llm=llm,
)

composer = ResultComposer(
    llm=llm,
)

validator = SQLValidator()

executor = QueryExecutor()
input_guardrail = InputGuardrail()

nl_to_sql_service = NLToSQLService(
    generator=generator,
    repairer=repairer,
    validator=validator,
    executor=executor,
    composer=composer,
)


# -----------------------------------
# API endpoint
# -----------------------------------

@router.post(
    "/query",
    response_model=QueryResponse,
)
def query_database(
    request: QueryRequest,
) -> QueryResponse:

    question = request.question.strip()

    guardrail_result = input_guardrail.check(
    question
    )
    if not guardrail_result.is_allowed:
        raise HTTPException(
            status_code=400,
            detail=guardrail_result.reason,
            )

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    result = nl_to_sql_service.process(
        question
    )

    if not result.is_valid:
        raise HTTPException(
            status_code=422,
            detail=(
                "Unable to generate a safe SQL "
                "query for this question."
            ),
        )

    if result.execution_error:
        raise HTTPException(
            status_code=500,
            detail=(
                "The database query failed "
                "after automatic repair attempts."
            ),
        )

    return QueryResponse(
        question=result.question,
        answer=result.answer,
        sql=result.sql,
        rows=result.rows or [],
        row_count=result.row_count,
        attempts=result.attempt_count,
        was_repaired=result.was_repaired,
    )