from app.llm.base import LLMProvider
from app.metadata.loader import (
    format_schema_for_llm,
    load_schema_metadata,
)


class SQLRepairAgent:

    def __init__(
        self,
        llm: LLMProvider,
    ) -> None:
        self.llm = llm

        metadata = load_schema_metadata()

        self.schema_context = format_schema_for_llm(
            metadata
        )

    def repair_sql(
        self,
        *,
        question: str,
        failed_sql: str,
        error_message: str,
    ) -> str:

        instructions = """
You are a PostgreSQL SQL repair agent.

A previous SQL query failed validation or execution.

Your job is to repair the SQL while preserving the
meaning of the user's original question.

Rules:

1. Return exactly one SQL query.
2. Return SELECT queries only.
3. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, TRUNCATE, CREATE, GRANT, or REVOKE.
4. Use only tables and columns from the supplied schema.
5. Follow all supplied business rules.
6. Use the provided error message to determine what failed.
7. Do not invent tables or columns.
8. Do not include Markdown code fences.
9. Do not explain your answer.
10. Return the corrected SQL only.
""".strip()

        prompt = f"""
DATABASE SCHEMA
===============

{self.schema_context}


ORIGINAL USER QUESTION
======================

{question}


FAILED SQL
==========

{failed_sql}


ERROR
=====

{error_message}


Return a corrected PostgreSQL SELECT query only.
""".strip()

        repaired_sql = self.llm.generate(
            instructions=instructions,
            prompt=prompt,
        )

        return self._clean_sql_output(
            repaired_sql
        )

    @staticmethod
    def _clean_sql_output(
        sql: str,
    ) -> str:

        sql = sql.strip()

        if sql.startswith("```sql"):
            sql = sql[6:]

        elif sql.startswith("```"):
            sql = sql[3:]

        if sql.endswith("```"):
            sql = sql[:-3]

        return sql.strip()