from dataclasses import dataclass

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

from app.metadata.loader import load_schema_metadata


@dataclass
class ValidationResult:
    is_valid: bool
    error: str | None = None


class SQLValidator:

    def __init__(self) -> None:

        metadata = load_schema_metadata()

        self.schema = {
            table_name: set(
                table_data["columns"].keys()
            )
            for table_name, table_data
            in metadata["tables"].items()
        }

        self.allowed_tables = set(
            self.schema.keys()
        )

    def validate(
        self,
        sql: str,
    ) -> ValidationResult:

        if not sql.strip():
            return ValidationResult(
                is_valid=False,
                error="SQL query is empty.",
            )

        try:
            statements = sqlglot.parse(
                sql,
                read="postgres",
            )

        except ParseError as exc:
            return ValidationResult(
                is_valid=False,
                error=f"Invalid SQL syntax: {exc}",
            )

        if len(statements) != 1:
            return ValidationResult(
                is_valid=False,
                error=(
                    "Exactly one SQL statement "
                    "is allowed."
                ),
            )

        statement = statements[0]

        if not isinstance(
            statement,
            exp.Select,
        ):
            return ValidationResult(
                is_valid=False,
                error="Only SELECT queries are allowed.",
            )

        forbidden_types = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Drop,
            exp.Create,
            exp.Alter,
            exp.Command,
        )

        for forbidden_type in forbidden_types:

            if statement.find(
                forbidden_type
            ):
                return ValidationResult(
                    is_valid=False,
                    error=(
                        "Query contains a forbidden "
                        "SQL operation."
                    ),
                )

        # -----------------------------------
        # Validate tables and build aliases
        # -----------------------------------

        alias_to_table: dict[str, str] = {}

        referenced_tables: set[str] = set()

        for table in statement.find_all(
            exp.Table
        ):
            table_name = table.name

            if table_name not in self.allowed_tables:
                return ValidationResult(
                    is_valid=False,
                    error=(
                        f"Unknown table: {table_name}"
                    ),
                )

            referenced_tables.add(
                table_name
            )

            alias = table.alias

            if alias:
                alias_to_table[alias] = table_name

            alias_to_table[table_name] = table_name

        # -----------------------------------
        # Collect SELECT aliases
        #
        # Example:
        # SUM(...) AS revenue
        #
        # ORDER BY revenue
        # -----------------------------------

        select_aliases: set[str] = set()

        for expression in statement.expressions:

            alias = expression.alias

            if alias:
                select_aliases.add(
                    alias
                )

        # -----------------------------------
        # Validate columns
        # -----------------------------------

        for column in statement.find_all(
            exp.Column
        ):

            column_name = column.name
            qualifier = column.table

            # Allow SELECT *
            if column_name == "*":
                continue

            # Allow aliases such as:
            #
            # ORDER BY revenue
            if (
                not qualifier
                and column_name in select_aliases
            ):
                continue

            # -------------------------------
            # Qualified column
            #
            # c.name
            # o.total_amount
            # -------------------------------

            if qualifier:

                table_name = alias_to_table.get(
                    qualifier
                )

                if table_name is None:
                    return ValidationResult(
                        is_valid=False,
                        error=(
                            "Unknown table or alias: "
                            f"{qualifier}"
                        ),
                    )

                if (
                    column_name
                    not in self.schema[table_name]
                ):
                    return ValidationResult(
                        is_valid=False,
                        error=(
                            f"Unknown column: "
                            f"{qualifier}.{column_name}"
                        ),
                    )

                continue

            # -------------------------------
            # Unqualified column
            #
            # category
            # name
            # -------------------------------

            matching_tables = [
                table_name
                for table_name
                in referenced_tables
                if column_name
                in self.schema[table_name]
            ]

            if not matching_tables:
                return ValidationResult(
                    is_valid=False,
                    error=(
                        f"Unknown column: "
                        f"{column_name}"
                    ),
                )

            if len(matching_tables) > 1:
                return ValidationResult(
                    is_valid=False,
                    error=(
                        f"Ambiguous column: "
                        f"{column_name}"
                    ),
                )

        return ValidationResult(
            is_valid=True
        )