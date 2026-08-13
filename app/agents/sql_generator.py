from app.llm.base import LLMProvider
from app.metadata.loader import (
    format_schema_for_llm,
    load_schema_metadata,
)


class SQLGenerator:

    def __init__(
        self,
        llm: LLMProvider,
    ) -> None:
        self.llm = llm

        metadata = load_schema_metadata()

        self.schema_context = format_schema_for_llm(
            metadata
        )

    def generate_sql(
        self,
        question: str,
    ) -> str:

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        instructions = """
You are a PostgreSQL SQL generation agent.

Convert the user's natural-language question
into exactly one PostgreSQL query.

Rules:

1. Generate exactly one SQL query.
2. Generate SELECT queries only.
3. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, TRUNCATE, CREATE, GRANT, or REVOKE.
4. Use only tables and columns from the supplied schema.
5. Follow the supplied business rules.
6. Use explicit JOIN conditions.
7. Never invent tables or columns.
8. Do not include Markdown code fences.
9. Do not provide an explanation.
10. Return only the SQL query.
""".strip()

        prompt = f"""
DATABASE SCHEMA
===============

{self.schema_context}


USER QUESTION
=============

{question}


Return the PostgreSQL query only.
""".strip()

        sql = self.llm.generate(
            instructions=instructions,
            prompt=prompt,
        )

        return self._clean_sql_output(sql)

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