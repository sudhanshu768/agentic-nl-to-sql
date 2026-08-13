import json
from pathlib import Path
from typing import Any


SCHEMA_PATH = Path(__file__).with_name("schema.json")


def load_schema_metadata() -> dict[str, Any]:
    with SCHEMA_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def format_schema_for_llm(
    metadata: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        f"Database dialect: {metadata['dialect']}"
    )

    lines.append("")
    lines.append("TABLES")
    lines.append("------")

    for table_name, table in metadata["tables"].items():
        lines.append("")
        lines.append(
            f"Table: {table_name}"
        )

        lines.append(
            f"Description: {table['description']}"
        )

        lines.append("Columns:")

        for column_name, column in table["columns"].items():
            description = column.get(
                "description",
                "",
            )

            column_type = column.get(
                "type",
                "unknown",
            )

            line = (
                f"- {column_name} "
                f"({column_type}): "
                f"{description}"
            )

            if column.get("primary_key"):
                line += " [PRIMARY KEY]"

            if "foreign_key" in column:
                line += (
                    f" [FOREIGN KEY -> "
                    f"{column['foreign_key']}]"
                )

            lines.append(line)

    lines.append("")
    lines.append("RELATIONSHIPS")
    lines.append("-------------")

    for relationship in metadata["relationships"]:
        lines.append(
            f"- {relationship['from']} -> "
            f"{relationship['to']} "
            f"({relationship['type']})"
        )

    lines.append("")
    lines.append("BUSINESS RULES")
    lines.append("--------------")

    for rule in metadata["business_rules"]:
        lines.append(
            f"- {rule}"
        )

    return "\n".join(lines)